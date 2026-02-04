"""
Sensors Driver - Centralized sensor management for PicoWeather
Handles all sensor operations with automatic discovery and data caching
"""

import time
import utime

from machine import I2C, Pin


class SensorDevice:
    """Base class for sensor devices"""
    
    def __init__(self, name, i2c_bus, address):
        self.name = name
        self.i2c_bus = i2c_bus
        self.address = address
        self.detected = False
        self.initialized = False
        self.last_read = 0
        self.error_count = 0
        
    def detect(self):
        """Check if sensor is present"""
        return self.address in self.i2c_bus.scan()
    
    def initialize(self):
        """Initialize sensor - to be implemented by subclasses"""
        return False
    
    def read(self):
        """Read sensor data - to be implemented by subclasses"""
        return {}
    
    def get_status(self):
        """Get sensor status"""
        return {
            'name': self.name,
            'address': hex(self.address),
            'detected': self.detected,
            'initialized': self.initialized,
            'error_count': self.error_count,
            'last_read': self.last_read
        }


class AHT20Sensor(SensorDevice):
    """AHT20 Temperature and Humidity Sensor"""
    
    def __init__(self, i2c_bus, address = 0x38):
        super().__init__("AHT20", i2c_bus, address)
        self.sensor = None
        
    def initialize(self):
        """Initialize AHT20 sensor"""
        try:
            from lib.aht20 import AHT20
            self.sensor = AHT20(self.i2c_bus, self.address)
            # Test reading to verify
            temp, humid = self.sensor.read()
            if temp is not None and humid is not None:
                self.initialized = True
                return True
        except Exception as e:
            print(f"[AHT20] Init error: {e}")
        return False
    
    def read(self):
        """Read temperature and humidity"""
        if not self.initialized or not self.sensor:
            self.error_count += 1
            return {}
        
        try:
            temp, humid = self.sensor.read()
            self.last_read = utime.ticks_ms()
            
            if temp is not None and humid is not None:
                return {
                    'temperature': temp,
                    'humidity': humid
                }
            else:
                self.error_count += 1
                return {}
        except Exception as e:
            self.error_count += 1
            print(f"[AHT20] Read error: {e}")
            return {}


class BMP280Sensor(SensorDevice):
    """BMP280 Pressure Sensor"""
    
    def __init__(self, i2c_bus, address = 0x76):
        super().__init__("BMP280", i2c_bus, address)
        self.sensor = None
        
    def initialize(self):
        """Initialize BMP280 sensor"""
        try:
            from lib.bmp280 import BMP280
            self.sensor = BMP280(self.i2c_bus, self.address)
            # Test reading to verify
            temp, pressure = self.sensor.read()
            if temp is not None and pressure is not None:
                self.initialized = True
                return True
        except Exception as e:
            print(f"[BMP280] Init error: {e}")
        return False
    
    def read(self):
        """Read temperature and pressure"""
        if not self.initialized or not self.sensor:
            self.error_count += 1
            return {}
        
        try:
            temp, pressure = self.sensor.read()
            self.last_read = utime.ticks_ms()
            
            if temp is not None and pressure is not None:
                return {
                    'temperature': temp,
                    'pressure': pressure
                }
            else:
                self.error_count += 1
                return {}
        except Exception as e:
            self.error_count += 1
            print(f"[BMP280] Read error: {e}")
            return {}


class SensorsDriver:
    """Main sensors driver manager"""
    
    def __init__(self, config, hardware):
        self.config = config
        self.hardware = hardware
        self.sensors = {}
        self.i2c_buses = {}
        self.data_cache = {}
        self.last_update = 0
        self.read_interval = 5000  # 5 seconds default
        
        self._initialize_i2c_buses()
        self._discover_sensors()
    
    def _initialize_i2c_buses(self):
        """Initialize I2C buses based on configuration"""
        i2c_config = self.config.get("i2c_buses", {})
        
        for bus_name, bus_config in i2c_config.items():
            if not bus_config.get("enabled", False):
                continue
                
            try:
                bus_num = int(bus_name.replace("i2c", ""))
                pins_config = bus_config.get("pins", {})
                
                if "sda" in pins_config and "scl" in pins_config:
                    sda_pin = self.hardware["pins"][pins_config["sda"]]
                    scl_pin = self.hardware["pins"][pins_config["scl"]]
                    freq = bus_config.get("frequency", 100000)
                    
                    self.i2c_buses[bus_num] = I2C(
                        bus_num, 
                        sda=Pin(sda_pin), 
                        scl=Pin(scl_pin), 
                        freq=freq
                    )
                    
                    print(f"[SENSORS] I2C{bus_num} initialized: SDA={sda_pin}, SCL={scl_pin}")
                    
            except Exception as e:
                print(f"[SENSORS] Failed to initialize {bus_name}: {e}")
    
    def _discover_sensors(self):
        """Auto-discover and initialize sensors"""
        devices_config = self.config.get("devices", {}).get("sensors", {})
        
        if not devices_config.get("enabled", True):
            print("[SENSORS] Sensors disabled in config")
            return
        
        # AHT20
        if devices_config.get("aht20", {}).get("enabled", True):
            aht20_config = devices_config["aht20"]
            bus_num = devices_config.get("i2c_bus", 0)
            address = aht20_config.get("address", 0x38)
            
            if bus_num in self.i2c_buses:
                aht20 = AHT20Sensor(self.i2c_buses[bus_num], address)
                aht20.detected = aht20.detect()
                
                if aht20.detected:
                    if aht20.initialize():
                        self.sensors["aht20"] = aht20
                        print(f"[SENSORS] AHT20 initialized at {hex(address)}")
                    else:
                        print(f"[SENSORS] AHT20 detected but failed to initialize")
                else:
                    print(f"[SENSORS] AHT20 not found at {hex(address)}")
        
        # BMP280
        if devices_config.get("bmp280", {}).get("enabled", True):
            bmp280_config = devices_config["bmp280"]
            bus_num = devices_config.get("i2c_bus", 0)
            address = bmp280_config.get("address", 0x76)
            
            if bus_num in self.i2c_buses:
                bmp280 = BMP280Sensor(self.i2c_buses[bus_num], address)
                bmp280.detected = bmp280.detect()
                
                if bmp280.detected:
                    if bmp280.initialize():
                        self.sensors["bmp280"] = bmp280
                        print(f"[SENSORS] BMP280 initialized at {hex(address)}")
                    else:
                        print(f"[SENSORS] BMP280 detected but failed to initialize")
                else:
                    print(f"[SENSORS] BMP280 not found at {hex(address)}")
    
    # No arquivo sensors_driver.py, ajuste o método read_all:

    def read_all(self):
        """Read data from all initialized sensors"""
        combined_data = {}
        current_time = utime.ticks_ms()
        
        # Debug: mostrar quais sensores estão inicializados
        print(f"[SENSORS] Reading {len(self.sensors)} sensors")
        
        for sensor_name, sensor in self.sensors.items():
            if sensor.initialized:
                try:
                    print(f"[SENSORS] Reading {sensor_name}...")
                    sensor_data = sensor.read()
                    if sensor_data:
                        print(f"[SENSORS] {sensor_name} data: {sensor_data}")
                        # Mesclar dados
                        for key, value in sensor_data.items():
                            combined_data[key] = value
                    else:
                        print(f"[SENSORS] {sensor_name} returned no data")
                except Exception as e:
                    print(f"[SENSORS] Error reading {sensor_name}: {e}")
                    import sys
                    sys.print_exception(e)
            else:
                print(f"[SENSORS] {sensor_name} not initialized")
        
        self.data_cache = combined_data
        self.last_update = current_time
        
        print(f"[SENSORS] Combined data: {combined_data}")
        return combined_data
    
    def get_sensor_status(self):
        """Get status of all sensors"""
        status_list = []
        
        # Add configured sensors
        for sensor in self.sensors.values():
            status_list.append(sensor.get_status())
        
        # Add detected but not configured sensors
        for bus_num, i2c_bus in self.i2c_buses.items():
            addresses = i2c_bus.scan()
            for addr in addresses:
                # Skip if already configured
                if any(s.address == addr for s in self.sensors.values()):
                    continue
                    
                # Try to identify sensor type
                known_sensors = {
                    0x38: "AHT20",
                    0x76: "BMP280", 
                    0x77: "BMP280/BME280",
                    0x48: "PCF8563 (RTC)",
                    0x68: "MPU6050"
                }
                
                sensor_name = known_sensors.get(addr, f"Unknown_{hex(addr)}")
                status_list.append({
                    'name': sensor_name,
                    'address': hex(addr),
                    'detected': True,
                    'initialized': False,
                    'error_count': 0,
                    'last_read': 0,
                    'unconfigured': True
                })
        
        return status_list
    
    def scan_i2c(self):
        """Scan all I2C buses and return found devices"""
        scan_results = {}
        
        for bus_num, i2c_bus in self.i2c_buses.items():
            devices = i2c_bus.scan()
            scan_results[bus_num] = [hex(addr) for addr in devices]
            
        return scan_results
    
    def set_read_interval(self, interval_ms):
        """Set sensor reading interval"""
        self.read_interval = max(1000, interval_ms)  # Minimum 1 second
    
    def get_read_interval(self):
        """Get current read interval"""
        return self.read_interval
    
    def reset_error_counts(self):
        """Reset error counters for all sensors"""
        for sensor in self.sensors.values():
            sensor.error_count = 0
    
    def is_healthy(self):
        """Check if sensors are healthy"""
        if not self.sensors:
            return False  # No sensors configured
            
        # Check if at least one sensor is working
        working_sensors = sum(1 for s in self.sensors.values() 
                            if s.initialized and s.error_count < 5)
        
        return working_sensors > 0