"""
Controller Driver - Management of control devices (FM Transmitter, etc.)
Handles all control/actuator devices with unified interface
"""

import time
import utime

from machine import I2C, Pin


class ControllerDevice:
    """Base class for controller devices"""
    
    def __init__(self, name, i2c_bus, address):
        self.name = name
        self.i2c_bus = i2c_bus
        self.address = address
        self.detected = False
        self.initialized = False
        self.error_count = 0
        self.last_command = 0
        
    def detect(self):
        """Check if controller is present"""
        try:
            scanned_devices = self.i2c_bus.scan()
            print(f"[FM] I2C scan results: {scanned_devices}")
            print(f"[FM] Looking for address {hex(self.address)}")
            found = self.address in scanned_devices
            print(f"[FM] Device found at {hex(self.address)}: {found}")
            return found
        except Exception as e:
            print(f"[FM] I2C scan error: {e}")
            return False
    
    def initialize(self):
        """Initialize controller - to be implemented by subclasses"""
        return False
    
    def set_frequency(self, freq_mhz):
        """Set frequency - to be implemented by subclasses"""
        return False
    
    def set_volume(self, volume):
        """Set volume - to be implemented by subclasses"""
        return False
    
    def get_status(self):
        """Get controller status - to be implemented by subclasses"""
        return {}


class FMTransmitterRDA5807(ControllerDevice):
    """RDA5807 FM Transmitter"""
    
    def __init__(self, i2c_bus, address = 0x11):
        super().__init__("RDA5807", i2c_bus, address)
        self.frequency = 100.5
        self.volume = 7
        self.muted = False
        
    def initialize(self):
        """Initialize RDA5807 FM transmitter"""
        try:
            # Reset chip
            self._write_reg(0x02, 0x0002)
            time.sleep(0.1)
            
            # Enable output and set default settings
            self._write_reg(0x02, 0x8001)  # Enable, Bass boost off
            self._write_reg(0x03, 0x0000)  # Default
            
            # Set initial frequency and volume
            self.set_frequency(self.frequency)
            self.set_volume(self.volume)
            
            self.initialized = True
            print(f"[FM] RDA5807 initialized at {hex(self.address)}")
            return True
            
        except Exception as e:
            print(f"[FM] RDA5807 init error: {e}")
            return False
    
    def _write_reg(self, reg, value):
        """Write to RDA5807 register"""
        data = bytearray([reg | 0x20, (value >> 8) & 0xFF, value & 0xFF])
        self.i2c_bus.writeto(self.address, data)
        time.sleep(0.01)
    
    def _read_reg(self, reg):
        """Read from RDA5807 register"""
        try:
            data = self.i2c_bus.readfrom_mem(self.address, reg | 0x20, 2)
            return (data[0] << 8) | data[1]
        except:
            return 0
    
    def set_frequency(self, freq_mhz):
        """Set FM frequency (88.0 - 108.0 MHz)"""
        if not self.initialized:
            return False
            
        try:
            freq_mhz = max(88.0, min(108.0, freq_mhz))
            freq_int = int((freq_mhz - 88.0) * 10) + 0x1000
            
            # Read current register 0x03
            reg03 = self._read_reg(0x03)
            reg03 = (reg03 & 0xFE00) | freq_int
            
            self._write_reg(0x03, reg03)
            self.frequency = freq_mhz
            self.last_command = utime.ticks_ms()
            
            print(f"[FM] Frequency set to {freq_mhz:.1f} MHz")
            return True
            
        except Exception as e:
            self.error_count += 1
            print(f"[FM] Frequency set error: {e}")
            return False
    
    def set_volume(self, volume):
        """Set volume (0-15)"""
        if not self.initialized:
            return False
            
        try:
            volume = max(0, min(15, volume))
            
            # Read current register 0x05
            reg05 = self._read_reg(0x05)
            reg05 = (reg05 & 0xFFF0) | volume
            
            self._write_reg(0x05, reg05)
            self.volume = volume
            self.last_command = utime.ticks_ms()
            
            print(f"[FM] Volume set to {volume}")
            return True
            
        except Exception as e:
            self.error_count += 1
            print(f"[FM] Volume set error: {e}")
            return False
    
    def set_mute(self, muted):
        """Mute/unmute output"""
        if not self.initialized:
            return False
            
        try:
            # Read current register 0x02
            reg02 = self._read_reg(0x02)
            if muted:
                reg02 |= 0x4000  # Set mute bit
            else:
                reg02 &= ~0x4000  # Clear mute bit
                
            self._write_reg(0x02, reg02)
            self.muted = muted
            self.last_command = utime.ticks_ms()
            
            print(f"[FM] Mute: {muted}")
            return True
            
        except Exception as e:
            self.error_count += 1
            print(f"[FM] Mute set error: {e}")
            return False
    
    def get_status(self):
        """Get RDA5807 status"""
        if not self.initialized:
            return {
                'name': self.name,
                'address': hex(self.address),
                'detected': self.detected,
                'initialized': False,
                'error_count': self.error_count
            }
        
        try:
            reg0A = self._read_reg(0x0A)  # Status register
            
            return {
                'name': self.name,
                'address': hex(self.address),
                'detected': self.detected,
                'initialized': True,
                'frequency': self.frequency,
                'volume': self.volume,
                'muted': self.muted,
                'error_count': self.error_count,
                'stereo': (reg0A & 0x0400) != 0,
                'rssi': (reg0A >> 9) & 0x7F,
                'last_command': self.last_command
            }
        except Exception as e:
            print(f"[FM] Status read error: {e}")
            return {
                'name': self.name,
                'address': hex(self.address),
                'detected': self.detected,
                'initialized': True,
                'frequency': self.frequency,
                'volume': self.volume,
                'muted': self.muted,
                'error_count': self.error_count,
                'read_error': True
            }


class ControllerDriver:
    """Main controller driver manager"""
    
    def __init__(self, config, hardware):
        self.config = config
        self.hardware = hardware
        self.controllers = {}
        self.i2c_buses = {}
        
        self._initialize_i2c_buses()
        self._discover_controllers()
    
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
                    freq = bus_config.get("frequency", 50000)
                    
                    self.i2c_buses[bus_num] = I2C(
                        bus_num, 
                        sda=Pin(sda_pin), 
                        scl=Pin(scl_pin), 
                        freq=freq
                    )
                    
                    print(f"[CONTROLLER] I2C{bus_num} initialized: SDA={sda_pin}, SCL={scl_pin}")
                    
            except Exception as e:
                print(f"[CONTROLLER] Failed to initialize {bus_name}: {e}")
    
    def _discover_controllers(self):
        """Auto-discover and initialize controllers"""
        # Check controllers configuration
        controllers_config = self.config.get("controllers", {})
        
        # FM Transmitter
        fm_config = controllers_config.get("fm_transmitter", {})
        print(f"[CONTROLLER] FM config: {fm_config}")
        
        if fm_config.get("enabled", True):
            bus_num = 1  # FM Transmitter is always on I2C1 (controllers bus)
            address = fm_config.get("address", 0x11)
            default_freq = fm_config.get("default_frequency", 100.5)
            default_volume = fm_config.get("default_volume", 7)
            
            print(f"[CONTROLLER] Looking for FM Transmitter on I2C{bus_num} at {hex(address)}")
            
            if bus_num in self.i2c_buses:
                print(f"[CONTROLLER] I2C{bus_num} available, scanning...")
                fm = FMTransmitterRDA5807(self.i2c_buses[bus_num], address)
                fm.detected = fm.detect()
                
                print(f"[CONTROLLER] FM Transmitter detected: {fm.detected}")
                
                if fm.detected:
                    if fm.initialize():
                        # Set defaults from config
                        fm.set_frequency(default_freq)
                        fm.set_volume(default_volume)
                        self.controllers["fm_transmitter"] = fm
                        print(f"[CONTROLLER] FM Transmitter initialized successfully")
                    else:
                        print(f"[CONTROLLER] FM Transmitter detected but failed to initialize")
                else:
                    print(f"[CONTROLLER] FM Transmitter not found at {hex(address)}")
            else:
                print(f"[CONTROLLER] I2C{bus_num} not available")
    
    def get_controller(self, name):
        """Get controller by name"""
        return self.controllers.get(name)
    
    def set_frequency(self, freq_mhz):
        """Set frequency for FM transmitter"""
        fm = self.controllers.get("fm_transmitter")
        if fm and isinstance(fm, FMTransmitterRDA5807):
            return fm.set_frequency(freq_mhz)
        return False
    
    def set_volume(self, volume):
        """Set volume for FM transmitter"""
        fm = self.controllers.get("fm_transmitter")
        if fm and isinstance(fm, FMTransmitterRDA5807):
            return fm.set_volume(volume)
        return False
    
    def set_mute(self, muted):
        """Mute/unmute FM transmitter"""
        fm = self.controllers.get("fm_transmitter")
        if fm and isinstance(fm, FMTransmitterRDA5807):
            return fm.set_mute(muted)
        return False
    
    def get_all_status(self):
        """Get status of all controllers"""
        status = {}
        for name, controller in self.controllers.items():
            status[name] = controller.get_status()
        return status
    
    def scan_i2c(self):
        """Scan all I2C buses and return found controllers"""
        scan_results = {}
        
        for bus_num, i2c_bus in self.i2c_buses.items():
            devices = i2c_bus.scan()
            scan_results[bus_num] = [hex(addr) for addr in devices]
            
        return scan_results
    
    def reset_error_counts(self):
        """Reset error counters for all controllers"""
        for controller in self.controllers.values():
            controller.error_count = 0
    
    def is_healthy(self):
        """Check if controllers are healthy"""
        if not self.controllers:
            return True  # No controllers configured is OK
            
        # Check if all configured controllers are working
        for controller in self.controllers.values():
            if not controller.initialized or controller.error_count >= 5:
                return False
                
        return True
    
    def get_controller_data(self):
        """Get data from all controllers for display"""
        data = {}
        
        fm = self.controllers.get("fm_transmitter")
        if fm and isinstance(fm, FMTransmitterRDA5807):
            status = fm.get_status()
            data['fm_frequency'] = status.get('frequency', 100.5)
            data['fm_volume'] = status.get('volume', 7)
            data['fm_muted'] = status.get('muted', False)
            data['fm_stereo'] = status.get('stereo', False)
            data['fm_rssi'] = status.get('rssi', 0)
        
        return data