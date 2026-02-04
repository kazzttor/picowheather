"""
Diagnostic - Hardware and system diagnostic tools for PicoWeather
Comprehensive testing and troubleshooting utilities
"""

import time
import utime
# Removed typing module for MicroPython compatibility
from machine import I2C, SPI, Pin


class ButtonInterface:
    """Button interface for console interaction"""
    
    def __init__(self):
        self._buttons = {}
        self._callbacks= {}

    def register(self, name, pin_num, pull=None, callback=None):
        """Register a button with optional callback"""
        self._buttons[name] = Pin(pin_num, Pin.IN, pull) if pull else Pin(pin_num, Pin.IN)
        if callback:
            self._callbacks[name] = callback

    def press_simulate(self, name):
        """Simulate button press for testing"""
        callback = self._callbacks.get(name)
        if callback:
            callback()


class SystemDiagnostic:
    """Comprehensive system diagnostic tool"""
    
    def __init__(self, drivers, config, hardware):
        self.drivers = drivers
        self.config = config
        self.hardware = hardware
        self.results = {}
        
    def run_full_diagnostic(self):
        """Run complete system diagnostic"""
        print("="*60)
        print("PICOWEATHER SYSTEM DIAGNOSTIC")
        print("="*60)
        
        self.results = {
            'timestamp': utime.ticks_ms(),
            'board': self.config.get('hardware', {}).get('board', 'unknown'),
            'tests': {}
        }
        
        # Run all diagnostic tests
        self._test_hardware_config()
        self._test_i2c_buses()
        self._test_spi_buses()
        self._test_pins()
        self._test_sensors()
        self._test_controllers()
        self._test_display()
        self._test_input()
        self._test_time()
        self._test_wifi()
        
        self._print_summary()
        return self.results
    
    def _test_hardware_config(self):
        """Test hardware configuration"""
        print("\n1. HARDWARE CONFIGURATION TEST")
        print("-" * 40)
        
        try:
            board = self.config.get('hardware', {}).get('board', 'unknown')
            print(f"Board type: {board}")
            
            pins_config = self.hardware.get('pins', {})
            print(f"Pins defined: {len(pins_config)}")
            
            # Check for essential pins
            essential_pins = []
            if 'display' in self.config:
                display_pins = self.config['display'].get('pins', {})
                for pin_name in display_pins.values():
                    if isinstance(pin_name, str):
                        essential_pins.append(pin_name)
            
            missing_pins = []
            for pin in essential_pins:
                if pin not in pins_config:
                    missing_pins.append(pin)
            
            if missing_pins:
                print(f"❌ Missing pins: {missing_pins}")
                self.results['tests']['hardware_config'] = {'status': 'fail', 'missing_pins': missing_pins}
            else:
                print("✅ Hardware configuration OK")
                self.results['tests']['hardware_config'] = {'status': 'pass'}
                
        except Exception as e:
            print(f"❌ Hardware config error: {e}")
            self.results['tests']['hardware_config'] = {'status': 'error', 'error': str(e)}
    
    def _test_i2c_buses(self):
        """Test I2C buses"""
        print("\n2. I2C BUS TEST")
        print("-" * 40)
        
        i2c_results = {}
        
        try:
            i2c_config = self.config.get('i2c_buses', {})
            
            for bus_name, bus_config in i2c_config.items():
                if not bus_config.get('enabled', False):
                    print(f"  {bus_name}: Disabled")
                    i2c_results[bus_name] = {'status': 'disabled'}
                    continue
                
                print(f"  Testing {bus_name}...")
                
                try:
                    bus_num = int(bus_name.replace('i2c', ''))
                    pins_config = bus_config.get('pins', {})
                    
                    if 'sda' in pins_config and 'scl' in pins_config:
                        sda_pin = self.hardware['pins'][pins_config['sda']]
                        scl_pin = self.hardware['pins'][pins_config['scl']]
                        freq = bus_config.get('frequency', 100000)
                        
                        i2c = I2C(bus_num, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)
                        devices = i2c.scan()
                        
                        print(f"    SDA={sda_pin}, SCL={scl_pin}, Freq={freq}")
                        print(f"    Devices found: {[hex(d) for d in devices]}")
                        
                        i2c_results[bus_name] = {
                            'status': 'pass',
                            'devices': devices,
                            'count': len(devices)
                        }
                    else:
                        print(f"    ❌ Missing pin configuration")
                        i2c_results[bus_name] = {'status': 'fail', 'error': 'missing pins'}
                        
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    i2c_results[bus_name] = {'status': 'error', 'error': str(e)}
            
            self.results['tests']['i2c_buses'] = i2c_results
            
        except Exception as e:
            print(f"❌ I2C test error: {e}")
            self.results['tests']['i2c_buses'] = {'status': 'error', 'error': str(e)}
    
    def _test_spi_buses(self):
        """Test SPI buses"""
        print("\n3. SPI BUS TEST")
        print("-" * 40)
        
        try:
            display_config = self.config.get('display', {})
            if display_config.get('type') == 'st7567_spi':
                print("  Testing SPI for ST7567 display...")
                
                try:
                    spi_bus = display_config.get('spi_bus', 1)
                    pins_config = display_config.get('pins', {})
                    
                    sck_pin = self.hardware['pins'][pins_config['sck']]
                    mosi_pin = self.hardware['pins'][pins_config['mosi']]
                    
                    spi = SPI(
                        spi_bus,
                        baudrate=display_config.get('spi_settings', {}).get('baudrate', 200000),
                        polarity=display_config.get('spi_settings', {}).get('polarity', 1),
                        phase=display_config.get('spi_settings', {}).get('phase', 1),
                        sck=Pin(sck_pin),
                        mosi=Pin(mosi_pin)
                    )
                    
                    print(f"    SCK={sck_pin}, MOSI={mosi_pin}")
                    print("    ✅ SPI initialized successfully")
                    
                    self.results['tests']['spi_buses'] = {'status': 'pass', 'spi_bus': spi_bus}
                    
                except Exception as e:
                    print(f"    ❌ SPI error: {e}")
                    self.results['tests']['spi_buses'] = {'status': 'error', 'error': str(e)}
            else:
                print("  No SPI devices configured")
                self.results['tests']['spi_buses'] = {'status': 'not_configured'}
                
        except Exception as e:
            print(f"❌ SPI test error: {e}")
            self.results['tests']['spi_buses'] = {'status': 'error', 'error': str(e)}
    
    def _test_pins(self):
        """Test individual pins"""
        print("\n4. PIN TEST")
        print("-" * 40)
        
        try:
            pins_config = self.hardware.get('pins', {})
            pin_results = {}
            
            # Test a few pins to check if they respond
            test_pins = list(pins_config.items())[:5]  # Test first 5 pins
            
            for pin_name, pin_num in test_pins:
                try:
                    pin = Pin(pin_num, Pin.OUT)
                    pin.value(1)
                    time.sleep(0.01)
                    pin.value(0)
                    print(f"  Pin {pin_name} ({pin_num}): ✅ OK")
                    pin_results[pin_name] = {'status': 'pass', 'pin': pin_num}
                except Exception as e:
                    print(f"  Pin {pin_name} ({pin_num}): ❌ Error: {e}")
                    pin_results[pin_name] = {'status': 'error', 'error': str(e)}
            
            self.results['tests']['pins'] = pin_results
            
        except Exception as e:
            print(f"❌ Pin test error: {e}")
            self.results['tests']['pins'] = {'status': 'error', 'error': str(e)}
    
    def _test_sensors(self):
        """Test sensor drivers"""
        print("\n5. SENSOR TEST")
        print("-" * 40)
        
        sensors_driver = self.drivers.get('sensors')
        if not sensors_driver:
            print("  Sensors driver not available")
            self.results['tests']['sensors'] = {'status': 'not_available'}
            return
        
        try:
            # Test sensor health
            is_healthy = sensors_driver.is_healthy()
            print(f"  Sensor health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
            
            # Get sensor status
            sensor_status = sensors_driver.get_sensor_status()
            print(f"  Configured sensors: {len(sensor_status)}")
            
            sensor_results = {}
            for status in sensor_status:
                name = status['name']
                detected = status['detected']
                initialized = status['initialized']
                errors = status['error_count']
                
                if detected and initialized and errors < 5:
                    print(f"    {name} ({status['address']}): ✅ OK")
                    sensor_results[name] = {'status': 'pass', 'address': status['address']}
                else:
                    print(f"    {name} ({status['address']}): ❌ Issues detected")
                    sensor_results[name] = {
                        'status': 'fail', 
                        'address': status['address'],
                        'detected': detected,
                        'initialized': initialized,
                        'errors': errors
                    }
            
            # Test reading sensors
            print("  Testing sensor readings...")
            sensor_data = sensors_driver.read_all()
            if sensor_data:
                print(f"    Data received: {list(sensor_data.keys())}")
                for key, value in sensor_data.items():
                    print(f"      {key}: {value}")
                sensor_results['reading'] = {'status': 'pass', 'data': sensor_data}
            else:
                print("    ❌ No sensor data received")
                sensor_results['reading'] = {'status': 'fail'}
            
            self.results['tests']['sensors'] = sensor_results
            
        except Exception as e:
            print(f"❌ Sensor test error: {e}")
            self.results['tests']['sensors'] = {'status': 'error', 'error': str(e)}
    
    def _test_controllers(self):
        """Test controller drivers"""
        print("\n6. CONTROLLER TEST")
        print("-" * 40)
        
        controller_driver = self.drivers.get('controller')
        if not controller_driver:
            print("  Controller driver not available")
            self.results['tests']['controllers'] = {'status': 'not_available'}
            return
        
        try:
            is_healthy = controller_driver.is_healthy()
            print(f"  Controller health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
            
            controller_status = controller_driver.get_all_status()
            print(f"  Configured controllers: {len(controller_status)}")
            
            controller_results = {}
            for name, status in controller_status.items():
                detected = status.get('detected', False)
                initialized = status.get('initialized', False)
                errors = status.get('error_count', 0)
                
                if detected and initialized and errors < 5:
                    print(f"    {name} ({status.get('address', 'N/A')}): ✅ OK")
                    controller_results[name] = {'status': 'pass'}
                else:
                    print(f"    {name} ({status.get('address', 'N/A')}): ❌ Issues")
                    controller_results[name] = {
                        'status': 'fail',
                        'detected': detected,
                        'initialized': initialized,
                        'errors': errors
                    }
            
            self.results['tests']['controllers'] = controller_results
            
        except Exception as e:
            print(f"❌ Controller test error: {e}")
            self.results['tests']['controllers'] = {'status': 'error', 'error': str(e)}
    
    def _test_display(self):
        """Test display driver"""
        print("\n7. DISPLAY TEST")
        print("-" * 40)
        
        display_driver = self.drivers.get('display')
        if not display_driver:
            print("  Display driver not available")
            self.results['tests']['display'] = {'status': 'not_available'}
            return
        
        try:
            is_healthy = display_driver.is_healthy()
            print(f"  Display health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
            
            status = display_driver.get_status()
            print(f"  Type: {status.get('type', 'Unknown')}")
            print(f"  Resolution: {status.get('width', 0)}x{status.get('height', 0)}")
            print(f"  Pages: {status.get('pages', 0)}")
            
            # Test display rendering
            print("  Testing display rendering...")
            if display_driver.test_display():
                print("    ✅ Display test successful")
                display_results = {'status': 'pass', 'test': 'ok'}
            else:
                print("    ❌ Display test failed")
                display_results = {'status': 'fail', 'test': 'failed'}
            
            self.results['tests']['display'] = display_results
            
        except Exception as e:
            print(f"❌ Display test error: {e}")
            self.results['tests']['display'] = {'status': 'error', 'error': str(e)}
    
    def _test_input(self):
        """Test input driver"""
        print("\n8. INPUT TEST")
        print("-" * 40)
        
        input_driver = self.drivers.get('input')
        if not input_driver:
            print("  Input driver not available")
            self.results['tests']['input'] = {'status': 'not_available'}
            return
        
        try:
            is_enabled = input_driver.is_enabled()
            button_count = input_driver.get_button_count()
            
            print(f"  Input enabled: {'✅ Yes' if is_enabled else '❌ No'}")
            print(f"  Buttons configured: {button_count}")
            
            if button_count > 0:
                button_status = input_driver.get_all_status()
                for name, status in button_status.items():
                    detected = status.get('detected', False)
                    errors = status.get('error_count', 0)
                    
                    if detected and errors < 10:
                        print(f"    {name} (Pin {status.get('pin')}): ✅ OK")
                    else:
                        print(f"    {name} (Pin {status.get('pin')}): ❌ Issues")
            
            self.results['tests']['input'] = {
                'status': 'pass' if is_enabled else 'not_enabled',
                'button_count': button_count
            }
            
        except Exception as e:
            print(f"❌ Input test error: {e}")
            self.results['tests']['input'] = {'status': 'error', 'error': str(e)}
    
    def _test_time(self):
        """Test time driver"""
        print("\n9. TIME TEST")
        print("-" * 40)
        
        time_driver = self.drivers.get('time')
        if not time_driver:
            print("  Time driver not available")
            self.results['tests']['time'] = {'status': 'not_available'}
            return
        
        try:
            is_healthy = time_driver.is_healthy()
            status = time_driver.get_status()
            
            print(f"  Time health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
            print(f"  Current time: {status.get('current_time', 'Unknown')}")
            print(f"  Auto-sync: {'Enabled' if status.get('auto_sync') else 'Disabled'}")
            print(f"  Manual time set: {'Yes' if status.get('manual_time_set') else 'No'}")
            
            # Test time adjustment
            print("  Testing time adjustment...")
            if time_driver.adjust_time(minutes=1):
                print("    ✅ Time adjustment successful")
                # Adjust back
                time_driver.adjust_time(minutes=-1)
                time_results = {'status': 'pass', 'adjustment': 'ok'}
            else:
                print("    ❌ Time adjustment failed")
                time_results = {'status': 'fail', 'adjustment': 'failed'}
            
            self.results['tests']['time'] = time_results
            
        except Exception as e:
            print(f"❌ Time test error: {e}")
            self.results['tests']['time'] = {'status': 'error', 'error': str(e)}
    
    def _test_wifi(self):
        """Test WiFi connectivity"""
        print("\n10. WIFI TEST")
        print("-" * 40)
        
        wifi_manager = self.drivers.get('wifi')
        if not wifi_manager:
            print("  WiFi manager not available")
            self.results['tests']['wifi'] = {'status': 'not_available'}
            return
        
        print("  WiFi functionality would be tested here")
        print("    - WiFi module detection")
        print("    - Network scanning")
        print("    - Connection test")
        print("    - NTP sync test")
        
        self.results['tests']['wifi'] = {'status': 'not_implemented'}
    
    def _print_summary(self):
        """Print diagnostic summary"""
        print("\n" + "="*60)
        print("DIAGNOSTIC SUMMARY")
        print("="*60)
        
        test_results = self.results.get('tests', {})
        passed = sum(1 for test in test_results.values() 
                    if test.get('status') == 'pass')
        failed = sum(1 for test in test_results.values() 
                    if test.get('status') in ['fail', 'error'])
        disabled = sum(1 for test in test_results.values() 
                      if test.get('status') in ['disabled', 'not_available', 'not_configured'])
        
        print(f"Total tests: {len(test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Disabled/Not available: {disabled}")
        
        if failed == 0:
            print("\n🎉 All critical systems are operational!")
        else:
            print(f"\n⚠️  {failed} test(s) failed - check detailed results above")
        
        print("="*60)


def run_startup_diagnostic():
    """Run basic startup diagnostic"""
    print("Running startup diagnostic...")
    # This would be called during system startup
    print("Startup diagnostic complete")


def run_diagnostics(drivers, config, hardware):
    """Convenience function to run full diagnostics"""
    diagnostic = SystemDiagnostic(drivers, config, hardware)
    return diagnostic.run_full_diagnostic()