"""
Console - Interactive console interface for PicoWeather
Provides comprehensive system management and diagnostics
"""

import sys
import json
# Removed typing module for MicroPython compatibility

# Import locale manager
from utils.locale_manager import get_locale, fmt_temp, fmt_humidity, fmt_pressure, fmt_frequency

try:
    from machine import Pin
    HAS_PIN = True
except Exception:
    # Fallback for non-MicroPython environments (host testing)
    HAS_PIN = False
    class Pin:
        IN = 0
        PULL_UP = 0
        def __init__(self, *args, **kwargs):
            pass
        def value(self):
            return 0


class ButtonInterface:
    """Button interface for console interaction"""
    
    def __init__(self):
        self._buttons = {}
        self._callbacks= {}

    def register(self, name, pin_num, pull=None, callback=None):
        """Register a button with optional callback"""
        if HAS_PIN:
            self._buttons[name] = Pin(pin_num, Pin.IN, pull) if pull else Pin(pin_num, Pin.IN)
        if callback:
            self._callbacks[name] = callback

    def press_simulate(self, name):
        """Simulate button press for testing"""
        callback = self._callbacks.get(name)
        if callback:
            callback()


class PicoWeatherConsole:
    """Main console interface for PicoWeather system"""
    
    def __init__(self, drivers, config):
        self.drivers = drivers
        self.config = config
        self.running = True
        
        # Use global locale manager or create fallback
        self.locale = get_locale()
        if not self.locale:
            from utils.locale_manager import LocaleManager
            locale_code = config.get('system', {}).get('locale', 'pt_BR')
            self.locale = LocaleManager(locale_code)
        
        # Component references
        self.sensors_driver = drivers.get("sensors")
        self.controller_driver = drivers.get("controller")
        self.input_driver = drivers.get("input")
        self.display_driver = drivers.get("display")
        self.time_driver = drivers.get("time")
        self.wifi_manager = drivers.get("wifi")
        
        # Setup commands
        self._setup_commands()
    
    def t(self, key, **kwargs):
        """Get localized console text"""
        return self.locale.get_console_text(key, **kwargs)
    
    def _validate_config(self):
        """Validate configuration structure"""
        if not self.config:
            return False
        
        # Check required top-level keys
        required_keys = ['hardware', 'system', 'display']
        for key in required_keys:
            if key not in self.config:
                self.config[key] = {}
        
        # Ensure hardware has pins
        if 'pins' not in self.config.get('hardware', {}):
            self.config['hardware']['pins'] = {}
        
        return True
    
    def _setup_commands(self):
        """Setup console commands"""
        self.commands = {
            'help': self._cmd_help,
            'exit': self._cmd_exit,
            'quit': self._cmd_exit,
            'status': self._cmd_status,
            'sensors': self._cmd_sensors,
            'scan': self._cmd_scan,
            'display': self._cmd_display,
            'time': self._cmd_time,
            'settime': self._cmd_settime,
            'adjust': self._cmd_adjust_time,
            'fm': self._cmd_fm,
            'wifi': self._cmd_wifi,
            'buttons': self._cmd_buttons,
            'diagnostic': self._cmd_diagnostic,
            'config': self._cmd_config,
            'save': self._cmd_save_config,
            'return': self._cmd_return,
            'reboot': self._cmd_reboot
        }
    
    def enter_console(self):
        """Enter interactive console mode"""
        self.show_banner()
        print("="*50)
        print(self.t("messages.console_mode"))
        print(self.t("messages.console_help"))
        print("="*50)
        
        while self.running:
            try:
                line = input("pico> ").strip()
                if not line:
                    continue
                
                parts = line.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd in self.commands:
                    result = self.commands[cmd](args)
                    # Check if return command was processed
                    if result == "resume":
                        return "resume"
                    # Check if exit command was processed
                    if not self.running:
                        break
                else:
                    print(self.t("errors.unknown_command", command=cmd))
                    
            except KeyboardInterrupt:
                print(self.t("messages.use_exit"))
            except EOFError:
                print(self.t("messages.exiting_console"))
                break
            except Exception as e:
                print(self.t("errors.console_error", error=str(e)))
    
    def show_banner(self):
        """Show system banner"""
        print("="*60)
        print(self.t("messages.system_console"))
        print("="*60)
        print(self.t("messages.board", board=self.config.get('hardware', {}).get('board', 'desconhecido')))
        if self.time_driver:
            print(self.t("messages.current_time", time=self.time_driver.get_formatted_time()))
        print("="*60)
    
    def _cmd_return(self, args):
        """Return to normal routine (main)"""
        current_time = self.time_driver.get_formatted_time() if self.time_driver else "unknown"
        print(self.t("messages.returning_to_main", time=current_time))
        print(self.t("messages.resuming_operation"))
        self.running = False
        # Return flag to indicate normal resume
        return "resume"
    
    def _cmd_reboot(self, args):
        """Reboot the device"""
        print(self.t("messages.rebooting_device"))
        
        # Save any pending changes first
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            print(self.t("messages.configuration_saved"))
        except Exception as save_error:
            print(self.t("messages.configuration_error", error=str(save_error)))
        
        print(self.t("messages.rebooting"))
        
        # Import machine module for reboot
        try:
            import machine
            machine.reset()
        except ImportError:
            # Fallback for testing
            print("[MOCK] Dispositivo reiniciado")
            self.running = False
    
    # Command implementations
    def _cmd_help(self, args):
        """Show help information"""
        print(self.t("menu.main_menu"))
        print(self.t("menu.sensor_menu"))
        print(f"  help         - {self.t('menu.help_command')}")
        print(f"  status       - {self.t('menu.show_status')}")
        print(f"  sensors      - {self.t('menu.read_sensors')}")
        print(f"  scan         - {self.t('menu.scan')}")
        print(self.t("menu.display_menu"))
        print(f"  time         - {self.t('menu.show_time')}")
        print(f"  settime      - {self.t('menu.set_time')}")
        print(f"  adjust       - {self.t('menu.adjust_time')}")
        print(self.t("menu.radio_menu"))
        print(f"  fm           - {self.t('menu.fm_controls')}")
        print(self.t("menu.network_menu"))
        print(f"  wifi         - {self.t('menu.wifi_status')}")
        print("--- Input Commands ---")
        print(f"  buttons      - {self.t('menu.button_status')}")
        print(self.t("menu.system_menu"))
        print(f"  diagnostic   - {self.t('menu.run_diagnostics')}")
        print(f"  config       - {self.t('menu.config_show')}")
        print(f"  save         - {self.t('menu.save_config')}")
        print(f"  {self.t('menu.exit')} or quit    - {self.t('menu.exit_console')}")
        print(f"  return       - {self.t('menu.return_main')}")
        print(f"  reboot       - {self.t('menu.reboot_device')}")
    
    def _cmd_exit(self, args):
        """Exit console mode"""
        print(self.t("responses.operation_cancelled"))
        self.running = False
    
    def _cmd_status(self, args):
        """Show system status using display_driver"""
        display_driver = self.drivers.get('display')
        controller_driver = self.drivers.get('controller')
        input_driver = self.drivers.get('input')
        
        # Display status
        if display_driver:
            try:
                status = display_driver.get_status()
                print("DISPLAY STATUS:")
                print(f"  Detected: {'Yes' if status.get('detected') else 'No'}")
                print(f"  Initialized: {'Yes' if status.get('initialized') else 'No'}")
                print(f"  Type: {status.get('type', 'Unknown')}")
                print(f"  Resolution: {status.get('width', 0)}x{status.get('height', 0)}")
                print(f"  Healthy: {'Yes' if status.get('healthy') else 'No'}")
            except Exception as e:
                print(self.t("messages.driver_error", error=str(e)))
        else:
            print(self.t("messages.not_configured"))
        
        # Controller status
        if controller_driver:
            try:
                controller_status = controller_driver.get_all_status()
                print(f"\nCONTROLLER STATUS:")
                print(f"  Healthy: {'Yes' if controller_driver.is_healthy() else 'No'}")
                print(f"  Controllers: {len(controller_status)}")
                for name, ctrl_status in controller_status.items():
                    print(f"    {name}: {'OK' if ctrl_status.get('detected') else 'Not detected'}")
            except Exception as e:
                print(self.t("messages.driver_error", error=str(e)))
        else:
            print(self.t("messages.not_configured"))
        
        # Input status
        if input_driver:
            try:
                print(f"\nINPUT STATUS:")
                print(f"  Enabled: {'Yes' if input_driver.is_enabled() else 'No'}")
                print(f"  Buttons: {input_driver.get_button_count()}")
            except Exception as e:
                print(self.t("messages.driver_error", error=str(e)))
        else:
            print(self.t("messages.not_configured"))
        
        print("="*50)
    
    def _cmd_sensors(self, args):
        """Show sensor readings using sensors_driver"""
        sensors_driver = self.drivers.get('sensors')
        
        if not sensors_driver:
            print(self.t("messages.not_configured"))
            return
        
        print("\nSENSOR READINGS:")
        # Use sensors_driver to read all sensors
        try:
            data = sensors_driver.read_all()
            
            if not data:
                print("  No sensor data available")
            else:
                for key, value in data.items():
                    if key == 'pressure':
                        value = f"{value:.2f} hPa"
                    elif key == 'temperature':
                        value = f"{value:.1f}°C"
                    elif key == 'humidity':
                        value = f"{value:.1f}%"
                    print(f"  {key.capitalize()}: {value}")
            
            # Get sensor status from sensors_driver
            print("\nSENSOR STATUS:")
            status_list = sensors_driver.get_sensor_status()
            for status in status_list:
                health = "OK" if status.get('initialized') and status.get('error_count', 0) < 5 else "ERROR"
                print(f"  {status['name']} ({status['address']}): {health}")
                print(f"    Detected: {status.get('detected', False)}")
                print(f"    Errors: {status.get('error_count', 0)}")
        except Exception as e:
            print(self.t("messages.error_reading", component="sensors", error=str(e)))
    
    def _cmd_scan(self, args):
        """Scan I2C buses using utils/diagnostic.py"""
        print("\nI2C BUS SCAN:")
        
        # Import diagnostic utilities
        try:
            from utils.diagnostic import SystemDiagnostic
            diagnostic = SystemDiagnostic(self.drivers, self.config, self.drivers.get('hardware', {}))
            
            # Use diagnostic to scan I2C buses
            diagnostic._test_i2c_buses()
            
        except Exception as e:
            print(f"Error during I2C scan: {e}")
            
            # Fallback to individual driver scans
            if self.sensors_driver:
                try:
                    scan_results = self.sensors_driver.scan_i2c()
                    for bus_num, devices in scan_results.items():
                        print(f"  I2C{bus_num}: {devices}")
                except Exception as e:
                    print(f"  Sensors I2C scan error: {e}")
            
            if self.controller_driver:
                try:
                    scan_results = self.controller_driver.scan_i2c()
                    for bus_num, devices in scan_results.items():
                        print(f"  Controller I2C{bus_num}: {devices}")
                except Exception as e:
                    print(f"  Controller I2C scan error: {e}")
    
    def _cmd_display(self, args):
        """Display operations"""
        if not self.display_driver:
            print("Display driver not available")
            return
        
        if not args:
            print(f"{self.t('menu.display_commands')}:")
            print(f"  display test    - {self.t('menu.display_test')}")
            print(f"  display status  - {self.t('menu.display_status_cmd')}")
            print(f"  display next    - {self.t('menu.display_next')}")
            print(f"  display prev    - {self.t('menu.display_prev')}")
            return
        
        cmd = args[0].lower()
        
        if cmd == "test":
            print("Running display test...")
            if self.display_driver.test_display():
                print("  Display test successful")
            else:
                print("  Display test failed")
        
        elif cmd == "status":
            status = self.display_driver.get_status()
            print(f"Display Status:")
            print(f"  Detected: {'Yes' if status.get('detected') else 'No'}")
            print(f"  Initialized: {'Yes' if status.get('initialized') else 'No'}")
            print(f"  Type: {status.get('type', 'Unknown')}")
            print(f"  {self.t('messages.resolution')}: {status.get('width', 0)}x{status.get('height', 0)}")
            print(f"  Pages: {status.get('pages', 0)}")
            print(f"  Current page: {status.get('current_page', 0)}")
        
        elif cmd == "next":
            self.display_driver.next_page()
            print("  Switched to next page")
        
        elif cmd == "prev":
            self.display_driver.previous_page()
            print("  Switched to previous page")
        
        else:
            print(f"Unknown display command: {cmd}")
    
    def _cmd_time(self, args):
        """Show time information using time_driver"""
        time_driver = self.drivers.get('time')
        
        if not time_driver:
            print(self.t("messages.not_configured"))
            return
        
        # Get time status from time_driver
        try:
            status = time_driver.get_status()
            
            print("\nTIME INFORMATION:")
            print(f"  Current time: {status.get('current_time', 'Unknown')}")
            print(f"  Date: {status.get('date', 'Unknown')}")
            print(f"  Timezone: UTC{status.get('timezone', 0):+d}")
            print(f"  Auto-sync: {'Enabled' if status.get('auto_sync') else 'Disabled'}")
            
            if status.get('auto_sync'):
                print(f"  NTP server: {status.get('ntp_server', 'Unknown')}")
                print(f"  Time since sync: {status.get('time_since_sync', 'Never')}")
            
            print(f"  Manual time set: {'Yes' if status.get('manual_time_set') else 'No'}")
            print(f"  Healthy: {'Yes' if time_driver.is_healthy() else 'No'}")
        except Exception as e:
            print(self.t("messages.driver_error", error=str(e)))
    
    def _cmd_settime(self, args):
        """Set time manually using time_driver"""
        time_driver = self.drivers.get('time')
        
        if not time_driver:
            print(self.t("messages.not_configured"))
            return
        
        if len(args) < 5:
            print(self.t("prompts.enter_date"))
            print(self.t("examples.time_example"))
            return
        
        try:
            year = int(args[0])
            month = int(args[1])
            day = int(args[2])
            hour = int(args[3])
            minute = int(args[4])
            second = int(args[5]) if len(args) > 5 else 0
            
            # Use time_driver to set manual time
            if time_driver.set_manual_time(year, month, day, hour, minute, second):
                print(self.t("responses.time_set_success", time=time_driver.get_formatted_time()))
            else:
                print(self.t("responses.time_set_failed"))
                
        except ValueError:
            print(self.t("errors.invalid_time_format"))
        except Exception as e:
            print(self.t("errors.time_set_error", error=str(e)))
    
    def _cmd_adjust_time(self, args):
        """Adjust time using time_driver"""
        time_driver = self.drivers.get('time')
        
        if not time_driver:
            print(self.t("messages.not_configured"))
            return
        
        if not args:
            print("Usage: adjust +/-30m +/-1h +/-1d")
            print("Examples: adjust +30m, adjust -1h, adjust +1d")
            return
        
        minutes = hours = days = 0
        
        for arg in args:
            if arg.endswith('m') or arg.endswith('M'):
                minutes = int(arg[:-1])
            elif arg.endswith('h') or arg.endswith('H'):
                hours = int(arg[:-1])
            elif arg.endswith('d') or arg.endswith('D'):
                days = int(arg[:-1])
            else:
                # Assume minutes if no suffix
                minutes = int(arg)
        
        # Use time_driver to adjust time
        if time_driver.adjust_time(minutes, hours, days):
            print(f"Time adjusted by: {minutes:+d}m {hours:+d}h {days:+d}d")
            print(f"New time: {time_driver.get_formatted_time()}")
        else:
            print("Failed to adjust time")
    
    def _cmd_fm(self, args):
        """FM transmitter controls using controller_driver"""
        controller_driver = self.drivers.get('controller')
        
        if not controller_driver:
            print(self.t("messages.not_configured"))
            return
        
        if not args:
            print(f"{self.t('menu.fm_controls')}:")
            print("  fm status    - Show FM status")
            print("  fm freq X.X  - Set frequency")
            print("  fm vol X     - Set volume")
            print("  fm mute      - Mute/unmute")
            print(f"  fm rds       - {self.t('menu.rds_commands')}")
            print("  fm rds status           - Show RDS status")
            print("  fm rds text <text>      - Set RDS text")
            print("  fm rds station <name>   - Set station name")
            print("  fm rds type <type>       - Set program type")
            print("  fm rds enable            - Enable RDS")
            print("  fm rds disable           - Disable RDS")
            return
        
        cmd = args[0].lower()
        
        if cmd == "status":
            # Use controller_driver to get FM status
            status = controller_driver.get_all_status()
            if "fm_transmitter" in status:
                fm_status = status["fm_transmitter"]
                print("FM STATUS:")
                print(f"  Frequency: {fm_status.get('frequency', 'Unknown')} MHz")
                print(f"  Volume: {fm_status.get('volume', 'Unknown')}")
                print(f"  Muted: {'Yes' if fm_status.get('muted') else 'No'}")
                print(f"  Stereo: {'Yes' if fm_status.get('stereo') else 'No'}")
                print(f"  RSSI: {fm_status.get('rssi', 'Unknown')}")
            else:
                print("No FM transmitter detected")
        
        elif cmd == "freq" and len(args) >= 2:
            try:
                freq = float(args[1])
                # Use controller_driver to set frequency
                if controller_driver.set_frequency(freq):
                    print(f"Frequency set to {freq:.1f} MHz")
                else:
                    print("Failed to set frequency")
            except ValueError:
                print("Invalid frequency format")
        
        elif cmd in ["vol", "volume"] and len(args) >= 2:
            try:
                vol = int(args[1])
                # Use controller_driver to set volume
                if controller_driver.set_volume(vol):
                    print(f"Volume set to {vol}")
                else:
                    print("Failed to set volume")
            except ValueError:
                print("Invalid volume format")
        
        elif cmd == "mute":
            # Use controller_driver to toggle mute
            current_status = controller_driver.get_all_status()
            fm_status = current_status.get("fm_transmitter", {})
            current_mute = fm_status.get("muted", False)
            
            if controller_driver.set_mute(not current_mute):
                print(f"FM {'muted' if not current_mute else 'unmuted'}")
            else:
                print("Failed to toggle mute")
        
        elif cmd == "rds":
            if len(args) < 2:
                print("RDS commands:")
                print("  fm rds status           - Show RDS status")
                print("  fm rds text <text>    - Set RDS text")
                print("  fm rds station <name>  - Set station name")
                print("  fm rds type <type>      - Set program type")
                print("  fm rds enable           - Enable RDS")
                print("  fm rds disable          - Disable RDS")
                return
            
            rds_cmd = args[1].lower()
            
            if rds_cmd == "status":
                self._show_rds_status()
            
            elif rds_cmd == "text" and len(args) >= 3:
                text = " ".join(args[2:])
                self._set_rds_text(text)
            
            elif rds_cmd == "station" and len(args) >= 3:
                station = " ".join(args[2:])
                self._set_rds_station(station)
            
            elif rds_cmd == "type" and len(args) >= 3:
                ptype = " ".join(args[2:])
                self._set_rds_type(ptype)
            
            elif rds_cmd == "enable":
                self._enable_rds(True)
            
            elif rds_cmd == "disable":
                self._enable_rds(False)
            
            else:
                print(f"Unknown RDS command: {rds_cmd}")
        
        else:
            print(f"Unknown FM command: {cmd}")
    
    def _show_rds_status(self):
        """Show current RDS configuration"""
        controller = self.drivers.get('controller')
        if not controller:
            print(self.t("messages.rds_not_available"))
            return
        
        # Get RDS configuration from config
        fm_config = self.config.get('controllers', {}).get('fm_transmitter', {})
        rds_config = fm_config.get('rds', {})
        
        print(self.t("messages.rds_status"))
        print(f"  {self.t('messages.enabled')}: {'Yes' if rds_config.get('enabled', False) else 'No'}")
        print(f"  Station Name: {rds_config.get('station_name', 'Not set')}")
        print(f"  Program Type: {rds_config.get('program_type', 'Not set')}")
        print(f"  Text: {rds_config.get('text', 'Not set')}")
        print(f"  Repeat Text: {'Yes' if rds_config.get('repeat_text', False) else 'No'}")
        print(f"  Repeat Interval: {rds_config.get('text_repeat_interval', 0)}s")
    
    def _set_rds_text(self, text):
        """Set RDS text"""
        controller = self.drivers.get('controller')
        if not controller:
            print(self.t("messages.rds_not_available"))
            return
        
        try:
            # Update config
            fm_config = self.config.get('controllers', {}).get('fm_transmitter', {})
            if 'rds' not in fm_config:
                fm_config['rds'] = {}
            fm_config['rds']['text'] = text
            
            # Try to set in hardware
            if hasattr(controller, 'set_rds_text'):
                if controller.set_rds_text(text):
                    print(self.t("messages.rds_text_set", text=text))
                else:
                    print("Failed to set RDS text")
            else:
                print(self.t("messages.rds_text_set", text=text))
                
        except Exception as e:
            print(self.t("messages.error_setting_rds", error=str(e)))
    
    def _set_rds_station(self, station):
        """Set RDS station name"""
        controller = self.drivers.get('controller')
        if not controller:
            print(self.t("messages.rds_not_available"))
            return
        
        try:
            # Update config
            fm_config = self.config.get('controllers', {}).get('fm_transmitter', {})
            if 'rds' not in fm_config:
                fm_config['rds'] = {}
            fm_config['rds']['station_name'] = station
            
            # Try to set in hardware
            if hasattr(controller, 'set_rds_station'):
                if controller.set_rds_station(station):
                    print(self.t("messages.rds_station_set", station=station))
                else:
                    print("Failed to set RDS station")
            else:
                print(self.t("messages.rds_station_set", station=station))
                
        except Exception as e:
            print(self.t("messages.error_setting_rds", error=str(e)))
    
    def _set_rds_type(self, ptype):
        """Set RDS program type"""
        controller = self.drivers.get('controller')
        if not controller:
            print(self.t("messages.rds_not_available"))
            return
        
        try:
            # Update config
            fm_config = self.config.get('controllers', {}).get('fm_transmitter', {})
            if 'rds' not in fm_config:
                fm_config['rds'] = {}
            fm_config['rds']['program_type'] = ptype
            
            # Try to set in hardware
            if hasattr(controller, 'set_rds_type'):
                if controller.set_rds_type(ptype):
                    print(self.t("messages.rds_type_set", type=ptype))
                else:
                    print("Failed to set RDS program type")
            else:
                print(self.t("messages.rds_type_set", type=ptype))
                
        except Exception as e:
            print(self.t("messages.error_setting_rds", error=str(e)))
    
    def _enable_rds(self, enable):
        """Enable or disable RDS"""
        controller = self.drivers.get('controller')
        if not controller:
            print(self.t("messages.rds_not_available"))
            return
        
        try:
            # Update config
            fm_config = self.config.get('controllers', {}).get('fm_transmitter', {})
            if 'rds' not in fm_config:
                fm_config['rds'] = {}
            fm_config['rds']['enabled'] = enable
            
            # Try to set in hardware
            if hasattr(controller, 'enable_rds'):
                if controller.enable_rds(enable):
                    print(self.t("messages.rds_enabled" if enable else "messages.rds_disabled"))
                else:
                    print(f"Failed to {'enable' if enable else 'disable'} RDS")
            else:
                print(self.t("messages.rds_enabled" if enable else "messages.rds_disabled"))
                
        except Exception as e:
            print(self.t("messages.error_setting_rds", error=str(e)))
    
    def _cmd_wifi(self, args):
        """WiFi information and control using networking_driver"""
        networking_driver = self.drivers.get('networking')
        if not networking_driver:
            print(self.t("messages.not_configured"))
            return
        
        if not args:
            print("WiFi commands:")
            print("  wifi status    - Show WiFi status")
            print("  wifi scan      - Scan for networks")
            print("  wifi connect   - Connect to network")
            print("  wifi disconnect - Disconnect from network")
            return
        
        cmd = args[0].lower()
        
        if cmd == "status":
            # Use networking_driver to get WiFi status
            try:
                status = networking_driver.get_status()
                print("WIFI STATUS:")
                print(f"  Available: {'Yes' if status.get('available') else 'No'}")
                print(f"  Type: {status.get('type', 'Unknown')}")
                print(f"  Connected: {'Yes' if status.get('connected') else 'No'}")
                
                if status.get('connected'):
                    print(f"  Current SSID: {status.get('current_ssid', 'Unknown')}")
                    print(f"  IP Address: {status.get('ip_address', 'Unknown')}")
                else:
                    print("  Current SSID: Not connected")
                    print("  IP Address: Not connected")
                
                print(f"  Last scan: {status.get('last_scan_count', 0)} networks found")
                print(f"  Board type: {status.get('board_type', 'Unknown')}")
                print(f"  Healthy: {'Yes' if networking_driver.is_healthy() else 'No'}")
            except Exception as e:
                print(self.t("messages.driver_error", error=str(e)))
                return
        
        elif cmd == "scan":
            print("Scanning for WiFi networks...")
            try:
                # Use networking_driver to scan networks
                networks = networking_driver.scan_networks()
                
                if not networks:
                    print("  No networks found")
                    return
                
                print(f"  Found {len(networks)} networks:")
                for i, network in enumerate(networks[:10]):  # Show top 10
                    ssid = network.get('ssid', 'Unknown')
                    rssi = network.get('rssi', 0)
                    channel = network.get('channel', 0)
                    print(f"    {i+1}. {ssid} (RSSI: {rssi}, CH: {channel})")
            except Exception as e:
                print(self.t("messages.error_scanning", error=str(e)))
        
        elif cmd == "connect":
            networks = networking_driver.get_available_networks()
            if not networks:
                print("  No networks available. Run 'wifi scan' first.")
                return
            
            print("Available networks:")
            for i, network in enumerate(networks[:10]):
                ssid = network.get('ssid', 'Unknown')
                print(f"    {i+1}. {ssid}")
            
            print("  Usage: wifi connect <number>")
            if len(args) >= 2:
                try:
                    network_num = int(args[1]) - 1
                    if 0 <= network_num < len(networks):
                        network_list = self.config.get("wifi", {}).get("networks", [])
                        # Use networking_driver to auto-connect
                        try:
                            if networking_driver.auto_connect():
                                print("  Connection successful")
                            else:
                                print("  Connection failed")
                        except Exception as e:
                            print(self.t("messages.error_connecting", error=str(e)))
                    else:
                        print("  Invalid network number")
                except ValueError:
                    print("  Invalid network number")
        
        elif cmd == "disconnect":
            # Use networking_driver to disconnect
            try:
                networking_driver.disconnect()
                print("  Disconnected from WiFi")
            except Exception as e:
                print(self.t("messages.error_disconnecting", error=str(e)))
        
        else:
            print(f"Unknown WiFi command: {cmd}")
    
    def _cmd_buttons(self, args):
        """Show button status using input_driver"""
        input_driver = self.drivers.get('input')
        
        if not input_driver:
            print(self.t("messages.not_configured"))
            return
        
        # Use input_driver to get button status
        try:
            status = input_driver.get_all_status()
            if not status:
                print("No buttons configured")
                return
            
            print("\nBUTTON STATUS:")
            for name, button_status in status.items():
                pressed = "PRESSED" if button_status.get('pressed') else "RELEASED"
                presses = button_status.get('press_count', 0)
                print(f"  {name} (Pin {button_status.get('pin')}): {pressed}")
                print(f"    Press count: {presses}")
                print(f"    Errors: {button_status.get('error_count', 0)}")
                print(f"    Detected: {button_status.get('detected', False)}")
        except Exception as e:
            print(self.t("messages.driver_error", error=str(e)))
    
    def _cmd_diagnostic(self, args):
        """Run system diagnostics using utils/diagnostic.py"""
        print("Running system diagnostics...")
        
        try:
            # Import and use diagnostic utilities
            from utils.diagnostic import run_diagnostics
            hardware_config = self.config.get('hardware', {})
            
            # Run full diagnostics
            try:
                results = run_diagnostics(self.drivers, self.config, hardware_config)
                
                if results:
                    print("Diagnostics completed successfully")
                else:
                    print("Diagnostics failed")
            except Exception as e:
                print(self.t("messages.error_diagnostics", error=str(e)))
                
        except Exception as e:
            print(f"Error running diagnostics: {e}")
            
            # Fallback manual diagnostics
            print("\nFALLBACK DIAGNOSTICS:")
            print("- Hardware tests")
            print("- Communication tests") 
            print("- Performance tests")
            print("- Error analysis")
    
    def _cmd_config(self, args):
        """Configuration management"""
        if not args:
            print("Configuration commands:")
            print("  config show    - Show current configuration")
            print("  config reload  - Reload configuration")
            return
        
        cmd = args[0].lower()
        
        if cmd == "show":
            print("CURRENT CONFIGURATION:")
            try:
                print(json.dumps(self.config, indent=2))
            except Exception as e:
                print(self.t("messages.config_display_error", error=str(e)))
        
        elif cmd == "reload":
            print("Configuration reload would be implemented here")
            # TODO: Implement configuration reload functionality
        
        else:
            print(f"Unknown config command: {cmd}")
    
    def _cmd_save_config(self, args):
        """Save current configuration"""
        try:
            # Validate config before saving
            if not self.config:
                print("Configuration is empty - nothing to save")
                return
            
            # Ensure config has valid structure
            if not self._validate_config():
                print("Invalid configuration structure")
                return
            
            # Create a backup first
            try:
                with open('config.json', 'r') as f:
                    backup_config = json.load(f)
                with open('config.json.backup', 'w') as f:
                    json.dump(backup_config, f, indent=2)
                print("Configuration backup created")
            except:
                pass  # Backup might not exist yet
            
            # Save current configuration
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            print(self.t("messages.configuration_saved"))
            
        except Exception as e:
            print(self.t("messages.configuration_error", error=str(e)))
            # Try to restore from backup if save failed
            try:
                with open('config.json.backup', 'r') as f:
                    backup_config = json.load(f)
                with open('config.json', 'w') as f:
                    json.dump(backup_config, f, indent=2)
                print("Configuration restored from backup")
            except:
                print("Could not restore from backup")


def run_console(drivers, config):
    """Convenience function to run console"""
    try:
        console = PicoWeatherConsole(drivers, config)
        console.enter_console()
    except KeyboardInterrupt:
        print("\nConsole interrupted by user")
    except Exception as e:
        print(f"Console error: {e}")
    finally:
        print("Returning to MicroPython prompt...")