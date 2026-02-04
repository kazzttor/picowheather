"""
Console - Interactive console interface for PicoWeather
Provides comprehensive system management and diagnostics
"""

import sys
import json
# Removed typing module for MicroPython compatibility

# Import locale manager
from utils.locale_manager import LocaleManager, fmt_temp, fmt_humidity, fmt_pressure, fmt_frequency

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
        
        # Initialize locale manager with config locale
        locale_code = config.get('locale', 'en_US')
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
            'save': self._cmd_save_config
        }
    
    def enter_console(self):
        """Enter interactive console mode"""
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
                    self.commands[cmd](args)
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
    
    # Command implementations
    def _cmd_help(self, args):
        """Show help information"""
        print(self.t("menu.main_menu"))
        print(self.t("menu.sensor_menu"))
        print(f"  help         - {self.t('menu.back_to_main')}")
        print(f"  status       - {self.t('menu.show_status')}")
        print(f"  sensors      - {self.t('menu.read_sensors')}")
        print("  scan         - Scan I2C buses for devices")
        print(self.t("menu.display_menu"))
        print(f"  time         - {self.t('menu.show_time')}")
        print("  settime      - Set time manually")
        print("  adjust       - Adjust time (+/-30m, +1h, -1d)")
        print(self.t("menu.radio_menu"))
        print(f"  fm           - {self.t('menu.show_info')}")
        print(self.t("menu.network_menu"))
        print(f"  wifi         - {self.t('menu.wifi_status')}")
        print("--- Input Commands ---")
        print(f"  buttons      - Show button status")
        print(self.t("menu.system_menu"))
        print(f"  diagnostic   - {self.t('menu.run_diagnostics')}")
        print(f"  config       - {self.t('menu.show_config')}")
        print(f"  save         - Save current configuration")
        print(f"  {self.t('menu.exit')} or quit    - {self.t('menu.exit')}")
    
    def _cmd_exit(self, args):
        """Exit console mode"""
        print(self.t("responses.operation_cancelled"))
        self.running = False
    
    def _cmd_status(self, args):
        """Show display status"""
        status = self.display_driver.get_status()
        print(self.t("menu.display_status"))
        print(f"  {self.t('responses.detected', detected='Sim' if status.get('detected') else 'Não')}")
        print(f"  {self.t('responses.initialized', initialized='Sim' if status.get('initialized') else 'Não')}")
        print(f"  {self.t('responses.type', type=status.get('type', 'Desconhecido'))}")
        print(f"  Resolution: {status.get('width', 0)}x{status.get('height', 0)}")
        
        # Controller status
        if self.controller_driver:
            print(f"Controllers: {'Healthy' if self.controller_driver.is_healthy() else 'Error'}")
            print(f"  Controller count: {len(self.controller_driver.controllers)}")
        
        # Input status
        if self.input_driver:
            print(f"Input: {'Enabled' if self.input_driver.is_enabled() else 'Disabled'}")
            print(f"  Buttons: {self.input_driver.get_button_count()}")
        
        print("="*50)
    
    def _cmd_sensors(self, args):
        """Show sensor readings"""
        if not self.sensors_driver:
            print(self.t("errors.sensors_not_available"))
            return
        
        print(f"\n{self.t('messages.sensor_readings')}:")
        data = self.sensors_driver.read_all()
        
        if not data:
            print(f"  {self.t('messages.no_sensor_data')}")
        else:
            for key, value in data.items():
                if key == 'pressure':
                    value = fmt_pressure(value)
                elif key == 'temperature':
                    value = fmt_temp(value)
                elif key == 'humidity':
                    value = fmt_humidity(value)
                print(f"  {self.t(f'labels.{key}', default=key.capitalize())}: {value}")
        
        print(f"\n{self.t('messages.sensor_status')}:")
        status_list = self.sensors_driver.get_sensor_status()
        for status in status_list:
            health = self.t("status.ok") if status.get('initialized') and status.get('error_count', 0) < 5 else self.t("status.error")
            print(f"  {status['name']} ({status['address']}): {health}")
    
    def _cmd_scan(self, args):
        """Scan I2C buses"""
        print(f"\n{self.t('messages.i2c_scan')}:")
        
        # Scan sensors driver
        if self.sensors_driver:
            scan_results = self.sensors_driver.scan_i2c()
            for bus_num, devices in scan_results.items():
                print(f"  I2C{bus_num}: {devices}")
        
        # Scan controller driver
        if self.controller_driver:
            scan_results = self.controller_driver.scan_i2c()
            for bus_num, devices in scan_results.items():
                print(f"  {self.t('messages.controller_i2c', bus_num=bus_num, devices=devices)}")
    
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
            print(f"  Resolution: {status.get('width', 0)}x{status.get('height', 0)}")
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
        """Show time information"""
        if not self.time_driver:
            print(self.t("responses.system_error", error="Time driver not available"))
            return
        
        status = self.time_driver.get_status()
        
        print("\nTIME INFORMATION:")
        print(f"  Tempo atual: {status.get('current_time', 'Desconhecido')}")
        print(f"  Data: {status.get('date', 'Desconhecido')}")
        print(f"  Fuso horário: UTC{status.get('timezone', 0):+d}")
        print(f"  Sincronização: {'Ativa' if status.get('auto_sync') else 'Desativada'}")
        
        if status.get('auto_sync'):
            print(f"  Servidor NTP: {status.get('ntp_server', 'Desconhecido')}")
            print(f"  Tempo desde sincronização: {status.get('time_since_sync', 'Nunca')}")
        
        print(f"  Tempo manual: {'Sim' if status.get('manual_time_set') else 'Não'}")
        print(f"  Funcionando: {'Sim' if self.time_driver.is_healthy() else 'Não'}")
    
    def _cmd_settime(self, args):
        """Set time manually"""
        if not self.time_driver:
            print(self.t("responses.system_error", error="Time driver not available"))
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
            
            if self.time_driver.set_manual_time(year, month, day, hour, minute, second):
                print(self.t("responses.time_set_success", time=self.time_driver.get_formatted_time()))
            else:
                print(self.t("responses.time_set_failed"))
                
        except ValueError:
            print(self.t("errors.invalid_time_format"))
        except Exception as e:
            print(self.t("errors.time_set_error", error=str(e)))
    
    def _cmd_adjust_time(self, args):
        """Adjust time"""
        if not self.time_driver:
            print(self.t("responses.system_error", error="Time driver not available"))
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
        
        if self.time_driver.adjust_time(minutes, hours, days):
            print(f"Time adjusted by: {minutes:+d}m {hours:+d}h {days:+d}d")
            print(f"New time: {self.time_driver.get_formatted_time()}")
        else:
            print("Failed to adjust time")
    
    def _cmd_fm(self, args):
        """FM transmitter controls"""
        if not self.controller_driver:
            print("Controller driver not available")
            return
        
        if not args:
            print("FM commands:")
            print("  fm status    - Show FM status")
            print("  fm freq X.X  - Set frequency")
            print("  fm vol X     - Set volume")
            print("  fm mute      - Mute/unmute")
            return
        
        cmd = args[0].lower()
        
        if cmd == "status":
            status = self.controller_driver.get_all_status()
            if "fm_transmitter" in status:
                fm_status = status["fm_transmitter"]
                print(f"FM Status:")
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
                if self.controller_driver.set_frequency(freq):
                    print(f"Frequency set to {freq:.1f} MHz")
                else:
                    print("Failed to set frequency")
            except ValueError:
                print("Invalid frequency format")
        
        elif cmd == "vol" and len(args) >= 2:
            try:
                vol = int(args[1])
                if self.controller_driver.set_volume(vol):
                    print(f"Volume set to {vol}")
                else:
                    print("Failed to set volume")
            except ValueError:
                print("Invalid volume format")
        
        elif cmd == "mute":
            current_status = self.controller_driver.get_all_status()
            fm_status = current_status.get("fm_transmitter", {})
            current_mute = fm_status.get("muted", False)
            
            if self.controller_driver.set_mute(not current_mute):
                print(f"FM {'muted' if not current_mute else 'unmuted'}")
            else:
                print("Failed to toggle mute")
        
        else:
            print(f"Unknown FM command: {cmd}")
    
    def _cmd_wifi(self, args):
        """WiFi information and control"""
        networking_driver = self.drivers.get('networking')
        if not networking_driver:
            print("Networking driver not available")
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
            status = networking_driver.get_status()
            print(f"WiFi Status:")
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
        
        elif cmd == "scan":
            print("Scanning for WiFi networks...")
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
                        if networking_driver.auto_connect():
                            print("  Connection successful")
                        else:
                            print("  Connection failed")
                    else:
                        print("  Invalid network number")
                except ValueError:
                    print("  Invalid network number")
        
        elif cmd == "disconnect":
            networking_driver.disconnect()
            print("  Disconnected from WiFi")
        
        else:
            print(f"Unknown WiFi command: {cmd}")
    
    def _cmd_buttons(self, args):
        """Show button status"""
        if not self.input_driver:
            print("Input driver not available")
            return
        
        status = self.input_driver.get_all_status()
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
    
    def _cmd_diagnostic(self, args):
        """Run system diagnostics"""
        print("Running system diagnostics...")
        print("(Full diagnostics would be implemented here)")
        print("  - Hardware tests")
        print("  - Communication tests")
        print("  - Performance tests")
        print("  - Error analysis")
    
    def _cmd_config(self, args):
        """Configuration management"""
        if not args:
            print("Config commands:")
            print("  config show    - Show current configuration")
            print("  config reload  - Reload configuration")
            return
        
        cmd = args[0].lower()
        
        if cmd == "show":
            print("Current configuration:")
            print(json.dumps(self.config, indent=2))
        
        elif cmd == "reload":
            print("Configuration reload would be implemented here")
        
        else:
            print(f"Unknown config command: {cmd}")
    
    def _cmd_save_config(self, args):
        """Save current configuration"""
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            print("Configuration saved to config.json")
        except Exception as e:
            print(f"Failed to save configuration: {e}")


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