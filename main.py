"""
PicoWeather Main - Async orchestrator
Coordinates all drivers and manages system lifecycle
"""

import json
import time
import utime
import machine
import sys

# Import drivers
from drivers.hardware_config import get_hardware_config
from drivers.sensors_driver import SensorsDriver
from drivers.controller_driver import ControllerDriver
from drivers.input_driver import InputDriver
from drivers.display_driver import DisplayDriver
from drivers.time_driver import TimeDriver
from drivers.networking_driver import NetworkingDriver

# Import display architecture
from lib.display_manager import DisplayManager

# Import utilities
from utils.console import run_console
from utils.diagnostic import run_diagnostics
from utils.locale_manager import init_locale, t_console


class PicoWeatherSystem:
    """Main system orchestrator"""
    
    def __init__(self):
        self.config = None
        self.hardware = None
        self.drivers = {}
        self.display_manager = None  # DisplayManager for content generation
        self.running = False
        self.error_count = 0
        self.max_errors = 10
        
        # Data storage for synchronous access - SEM THREADS
        self.sensor_cache = {}  # Cache persistente dos sensores
        self.sensor_data = {'temperature': 0.0, 'humidity': 0.0, 'pressure': 0.0}  # Fallback inicial
        self.controller_data = {}
        self.time_data = {'time_only': '00:00:00', 'date': '2024-01-01'}
        self.data_lock = None  # Removido lock - modo síncrono não precisa de lock
        self.last_sensor_update = 0
        self.sensor_update_count = 0
        self.first_sensor_read = True  # Flag para primeira leitura
        
        # Load configuration
        if not self._load_configuration():
            raise RuntimeError("Failed to load configuration")
        
        # Initialize locale system
        locale_code = self.config.get("system", {}).get("locale", "en_US")
        init_locale(locale_code)  # Custom font handles charset issues automatically
    
    def _load_configuration(self):
        """Load system configuration"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            
            # Get hardware configuration
            board_type = self.config.get("hardware", {}).get("board", "pico_standard")
            self.hardware = get_hardware_config(board_type)
            
            if not self.hardware:
                print(f"[MAIN] Failed to get hardware config for {board_type}")
                return False
            
            print(t_console("messages.main_loaded", board=board_type))
            return True
            
        except Exception as e:
            print(f"[MAIN] Configuration error: {e}")
            return False
    
    def initialize_drivers(self):
        """Initialize all system drivers with status checklist on display"""
        print(t_console("messages.system_startup"))
        
        # Store initialization status for display
        init_status = []
        
        # Initialize DisplayManager first (always OK - software only)
        try:
            print(t_console("messages.init_display"), end=" ")
            self.display_manager = DisplayManager(self.config, self.hardware)
            print(t_console("messages.ok"))
            init_status.append("DISPLAY: OK")
        except Exception as e:
            print(t_console("messages.status_fail", error=e))
            init_status.append("DISPLAY: FAIL")
        
        # Initialize display hardware IMMEDIATELY to show initialization status
        display_ready = False
        try:
            print(t_console("messages.init_display_hardware"), end=" ")
            self.drivers['display'] = DisplayDriver(self.config, self.hardware)
            if self.drivers['display'].is_healthy():
                print("OK")
                init_status.append("DISPLAY HW: OK")
                display_ready = True
                
                # No more injection needed - clean separation!
                print("[INIT] Display driver ready for framebuffer reception")
                
                # Show initial screen IMMEDIATELY using new flow
                self._show_init_screen("INITIALIZING...", init_status)
                print("[INIT] Display showing initialization status")
                
                # Small delay to ensure first screen is visible
                import time
                time.sleep(0.5)
            else:
                print("FAIL (hardware not available)")
                init_status.append("DISPLAY HW: FAIL")
        except Exception as e:
            print(f"FAIL ({e})")
            init_status.append("DISPLAY HW: FAIL")
        
        # Initialize networking first (optional)
        wifi_config = self.config.get("wifi", {})
        if wifi_config.get("enabled", False):
            try:
                print("[INIT] Initializing NETWORKING...", end=" ")
                self.drivers['networking'] = NetworkingDriver(self.config)
                # Activate WiFi and sync time if possible
                connected, mode = self.drivers['networking'].activate_and_sync_time()
                if connected and mode == "online":
                    print("OK")
                    init_status.append("NETWORKING: OK")
                elif connected and mode == "online_no_time":
                    print("OK (no time sync)")
                    init_status.append("NETWORKING: OK")
                else:
                    print("FAIL (connection failed)")
                    init_status.append("NETWORKING: FAIL")
                    self.drivers['networking'] = None
                if display_ready:
                    self._show_init_screen("INITIALIZING...", init_status)
            except Exception as e:
                print(f"FAIL ({e})")
                init_status.append("NETWORKING: FAIL")
                self.drivers['networking'] = None
                if display_ready:
                    self._show_init_screen("INITIALIZING...", init_status)
        else:
            print("[INIT] NETWORKING... SKIPPED (disabled)")
            init_status.append("NETWORKING: SKIP")
            self.drivers['networking'] = None
            if display_ready:
                self._show_init_screen("INITIALIZING...", init_status)
        
        # Initialize NTP time sync (only if networking is available)
        if self.drivers.get('networking'):
            try:
                print("[INIT] Initializing NTP...", end=" ")
                time_driver = TimeDriver(self.config, self.drivers.get('networking'))
                if time_driver and time_driver.is_healthy() and time_driver.check_and_sync():
                    print("OK")
                    init_status.append("NTP: OK")
                else:
                    print("FAIL (sync failed)")
                    init_status.append("NTP: FAIL")
                self.drivers['time'] = time_driver
            except Exception as e:
                print(f"FAIL ({e})")
                init_status.append("NTP: FAIL")
                self.drivers['time'] = None
            if display_ready:
                self._show_init_screen("INITIALIZING...", init_status)
        else:
            print("[INIT] NTP... SKIPPED (no networking)")
            init_status.append("NTP: SKIP")
            # Still initialize time driver for local time
            try:
                self.drivers['time'] = TimeDriver(self.config, None)
            except Exception:
                self.drivers['time'] = None
            if display_ready:
                self._show_init_screen("INITIALIZING...", init_status)
        
        # Initialize sensors
        try:
            print("[INIT] Initializing SENSORS...", end=" ")
            self.drivers['sensors'] = SensorsDriver(self.config, self.hardware)
            if self.drivers['sensors'].is_healthy():
                # Leitura IMEDIATA dos sensores para ter dados iniciais
                initial_data = self.drivers['sensors'].read_all()
                if initial_data:
                    self.sensor_data = initial_data.copy()
                    print("OK")
                    init_status.append("SENSORS: OK")
                else:
                    print("FAIL (no data)")
                    init_status.append("SENSORS: FAIL")
            else:
                print("FAIL (unhealthy)")
                init_status.append("SENSORS: FAIL")
        except Exception as e:
            print(f"FAIL ({e})")
            init_status.append("SENSORS: FAIL")
            self.drivers['sensors'] = None
        if display_ready:
            self._show_init_screen("INITIALIZING...", init_status)
        
        # Initialize controllers
        controller_config = self.config.get("controllers", {}).get("fm_transmitter", {})
        if controller_config.get("enabled", False):
            try:
                print("[INIT] Initializing CONTROLLERS...", end=" ")
                self.drivers['controller'] = ControllerDriver(self.config, self.hardware)
                if self.drivers['controller'].is_healthy():
                    # Get initial controller data
                    initial_controller_data = self.drivers['controller'].get_controller_data()
                    self.controller_data = initial_controller_data.copy()
                    print("OK")
                    init_status.append("CONTROLLERS: OK")
                else:
                    print("FAIL (unhealthy)")
                    init_status.append("CONTROLLERS: FAIL")
            except Exception as e:
                print(f"FAIL ({e})")
                init_status.append("CONTROLLERS: FAIL")
                self.drivers['controller'] = None
        else:
            print("[INIT] CONTROLLERS... SKIPPED (disabled)")
            init_status.append("CONTROLLERS: SKIP")
            self.drivers['controller'] = None
        if display_ready:
            self._show_init_screen("INITIALIZING...", init_status)
        
        # Initialize buttons
        try:
            print("[INIT] Initializing BUTTONS...", end=" ")
            self.drivers['input'] = InputDriver(self.config, self.hardware)
            button_count = self.drivers['input'].get_button_count()
            if button_count > 0:
                print(f"OK ({button_count} buttons)")
                init_status.append(f"BUTTONS: OK ({button_count})")
            else:
                print("OK (no buttons)")
                init_status.append("BUTTONS: OK (0)")
        except Exception as e:
            print(f"FAIL ({e})")
            init_status.append("BUTTONS: FAIL")
            self.drivers['input'] = None
        if display_ready:
            self._show_init_screen("INITIALIZING...", init_status)
        
        # Setup button callbacks
        self._setup_button_callbacks()
        
        # Initialize sensor cache with first reading
        if not self._initialize_sensor_cache_sync():
            print("[INIT] Failed to initialize sensor cache")
            return False
        
        # Inicializar dados de tempo
        if self.drivers.get('time'):
            try:
                self.time_data = {
                    'time_only': self.drivers['time'].get_time_only(),
                    'date': self.drivers['time'].get_formatted_date()
                }
                print(f"[INIT] Time data: {self.time_data['time_only']} {self.time_data['date']}")
            except Exception as e:
                print(f"[INIT] Time data: FAIL ({e})")
        
        # Show completion on display
        if display_ready:
            init_status.append("COMPLETE!")
            self._show_init_screen("INITIALIZATION COMPLETE", init_status)
            # Wait a moment before clearing
            import time
            time.sleep(2)
        
        print("="*50)
        print("INITIALIZATION COMPLETED")
        print("="*50)
        return True
        if self.drivers.get('time'):
            try:
                self.time_data = {
                    'time_only': self.drivers['time'].get_time_only(),
                    'date': self.drivers['time'].get_formatted_date()
                }
                print(f"[INIT] Time data: {self.time_data['time_only']} {self.time_data['date']}")
            except Exception as e:
                print(f"[INIT] Time data: FAIL ({e})")
        
        # Show completion on display
        if display_ready:
            init_status.append("COMPLETE!")
            self._show_init_screen("INITIALIZATION COMPLETE", init_status)
            # Wait a moment before clearing
            import time
            time.sleep(2)
        
        print("="*50)
        print("INITIALIZATION COMPLETED")
        print("="*50)
        return True
    
    def run(self):
        """Run the weather system"""
        try:
            if not self.initialize_drivers():
                print("[MAIN] Failed to initialize drivers")
                return False
            
            self.start_main_loop()
            return True
        except Exception as e:
            print(f"[MAIN] Error during system startup: {e}")
            return False
    
    def _show_init_screen(self, title, status_lines):
        """Show initialization status on display using DisplayManager"""
        display_driver = self.drivers.get('display')
        if not display_driver or not display_driver.is_healthy():
            print(f"[INIT] Cannot show on display: {'no driver' if not display_driver else 'driver unhealthy'}")
            return
        
        try:
            print(f"[INIT] Showing on display: {title} with {len(status_lines)} status lines")
            
            # Create content for initialization screen
            content = []
            
            # Add title
            content.append({
                'text': title,
                'x': 0,
                'y': 0,
                'font': 'large',
                'invert': True
            })
            
            # Add status lines
            y_offset = 16
            for i, status in enumerate(status_lines[-6:]):  # Show last 6 lines
                content.append({
                    'text': status,
                    'x': 0,
                    'y': y_offset + (i * 8),
                    'font': 'normal',
                    'invert': 'FAIL' in status or 'SKIP' in status
                })
            
            # Add completion message at bottom if complete
            if "COMPLETE" in title:
                content.append({
                    'text': "Starting system...",
                    'x': 0,
                    'y': 56,
                    'font': 'normal',
                    'invert': False
                })
            
            # Generate custom initialization framebuffer directly and show via DisplayDriver
            if self.display_manager and self.display_manager.framebuffer:
                # Create TEMPORARY framebuffer for initialization screen
                # Do NOT use the DisplayManager's main framebuffer!
                from framebuf import FrameBuffer, MONO_VLSB
                temp_buffer = bytearray(128 * 64 // 8)
                temp_fb = FrameBuffer(temp_buffer, 128, 64, MONO_VLSB)
                
                # Draw initialization screen on temporary framebuffer
                temp_fb.fill(0)
                temp_fb.text(title, 0, 0)
                
                y_offset = 16
                for i, status in enumerate(status_lines[-6:]):
                    temp_fb.text(status[:16], 0, y_offset + (i * 8))
                
                # Show the temporary buffer via DisplayDriver
                success = display_driver.show_framebuffer(temp_buffer)
                print(f"[INIT] Display update {'successful' if success else 'failed'}")
            else:
                print("[INIT] DisplayManager not available - cannot render")
                success = False
            
        except Exception as e:
            print(f"[INIT] Display update failed: {e}")
            # Continue without display to avoid blocking initialization
    
    def _setup_button_callbacks(self):
        """Setup button callbacks for system control"""
        input_driver = self.drivers.get('input')
        if not input_driver:
            return
        
        # Button callbacks
        def next_page():
            # Use only DisplayManager for page navigation
            if self.display_manager:
                self.display_manager.next_page()
                print("[BUTTON] Next page (DisplayManager)")
            else:
                print("[BUTTON] DisplayManager not available")
        
        def prev_page():
            # Use only DisplayManager for page navigation
            if self.display_manager:
                self.display_manager.previous_page()
                print("[BUTTON] Previous page (DisplayManager)")
            else:
                print("[BUTTON] DisplayManager not available")
        
        def toggle_mute():
            if 'controller' in self.drivers and self.drivers['controller']:
                try:
                    status = self.drivers['controller'].get_all_status()
                    fm_status = status.get('fm_transmitter', {})
                    current_mute = fm_status.get('muted', False)
                    self.drivers['controller'].set_mute(not current_mute)
                    print(f"[BUTTON] Mute toggled to {not current_mute}")
                except Exception as e:
                    print(f"[BUTTON] Toggle mute error: {e}")
        
        # Register callbacks if buttons are configured
        buttons_config = self.config.get("buttons", {}).get("pins", {})
        
        # Map button names to functions
        button_mapping = {
            'select': next_page,
            'up': prev_page,
            'down': toggle_mute,
        }
        
        for button_name, callback_func in button_mapping.items():
            if button_name in buttons_config:
                try:
                    input_driver.register_callback(button_name, callback_func)
                    print(f"[MAIN] Callback registered for {button_name} button")
                except Exception as e:
                    print(f"[MAIN] Failed to register callback for {button_name}: {e}")
    
    def _read_sensors_sync(self):
        """Read sensors synchronously"""
        sensors = self.drivers.get('sensors')
        if sensors and sensors.is_healthy():
            try:
                new_data = sensors.read_all()
                if new_data:
                    self.sensor_data = new_data.copy()
                    self.last_sensor_update = utime.ticks_ms()
                    self.sensor_update_count += 1
                    if self.first_sensor_read:
                        self.first_sensor_read = False
                        print(f"[SENSORS] First successful read: {new_data}")
            except Exception as e:
                print(f"[SENSORS] Read error: {e}")
    
    def _update_display(self):
        """Update display with current data"""
        if not self.display_manager:
            return
        
        try:
            # Prepare data for display manager
            display_data = {
                'sensor_data': self.sensor_data,
                'controller_data': self.controller_data,
                'time_data': self.time_data
            }
            
            # Generate framebuffer
            framebuffer = self.display_manager.generate_framebuffer(
                self.sensor_data, 
                self.controller_data, 
                self.time_data
            )
            if framebuffer:
                # Show via display driver
                display_driver = self.drivers.get('display')
                if display_driver and display_driver.is_healthy():
                    success = display_driver.show_framebuffer(framebuffer)
                    if not success:
                        print("[DISPLAY] Failed to show framebuffer")
        except Exception as e:
            print(f"[DISPLAY] Update error: {e}")
    
    def enter_console_mode(self):
        """Enter console mode for debugging"""
        print("[MAIN] Entering console mode...")
        try:
            # Prepare system state for console
            console_state = {
                'drivers': self.drivers,
                'sensor_data': self.sensor_data,
                'controller_data': self.controller_data,
                'time_data': self.time_data,
                'config': self.config,
                'hardware': self.hardware
            }
            
            # Run console
            run_console(console_state, self.drivers)
        except Exception as e:
            print(f"[MAIN] Console mode error: {e}")

# THREAD METHOD REMOVIDO - Sistema agora é completamente síncrono
    
    def start_main_loop(self):
        """Main application loop - synchronous sensor reading for RP2040"""
        print("[MAIN] Starting main loop (synchronous sensor mode)")
        self.running = True
        
        last_display_update = 0
        last_input_check = 0
        last_wifi_check = 0
        last_time_update = 0
        last_sensor_read = 0
        
        display_interval = 1000  # Update display every second
        input_interval = 50      # Check buttons every 50ms
        wifi_interval = 30000    # Check WiFi every 30 seconds
        time_update_interval = 1000  # Update time every second
        sensor_read_interval = 5000  # Read sensors every 5 seconds (async simulation)
        
        try:
            while self.running:
                current_time = utime.ticks_ms()
                
                # Check for button presses
                if utime.ticks_diff(current_time, last_input_check) > input_interval:
                    input_driver = self.drivers.get('input')
                    if input_driver and input_driver.is_enabled():
                        events = input_driver.check_all()
                        if events:
                            print(f"[INPUT] Events: {events}")
                    
                    last_input_check = current_time
                
                # Update time data periodically
                time_driver = self.drivers.get('time')
                if time_driver and utime.ticks_diff(current_time, last_time_update) > time_update_interval:
                    try:
                        self.time_data = {
                            'time_only': time_driver.get_time_only(),
                            'date': time_driver.get_formatted_date()
                        }
                        last_time_update = current_time
                    except Exception as e:
                        print(f"[TIME] Update error: {e}")
                
                # Update sensors (synchronous)
                if utime.ticks_diff(current_time, last_sensor_read) > sensor_read_interval:
                    try:
                        self._read_sensors_sync()
                    except Exception as e:
                        print(f"[SENSORS] Sync read error: {e}")
                    last_sensor_read = current_time
                
                # Update display
                if utime.ticks_diff(current_time, last_display_update) > display_interval:
                    try:
                        self._update_display()
                    except Exception as e:
                        print(f"[DISPLAY] Update error in main loop: {e}")
                    last_display_update = current_time
                
                # Check WiFi connection status (less frequent)
                networking_driver = self.drivers.get('networking')
                if networking_driver and utime.ticks_diff(current_time, last_wifi_check) > wifi_interval:
                    try:
                        was_connected = networking_driver.is_connected()
                        is_connected = networking_driver.check_connection()
                        
                        if was_connected and not is_connected:
                            print("[WIFI] Connection lost")
                        elif not was_connected and is_connected:
                            print("[WIFI] Connection restored")
                        
                        last_wifi_check = current_time
                    except Exception as e:
                        print(f"[WIFI] Check error: {e}")
                
                # Check time sync (every minute)
                if time_driver and utime.ticks_diff(current_time, last_wifi_check) > 60000:
                    try:
                        time_driver.check_and_sync()
                    except Exception as e:
                        print(f"[TIME] Sync error: {e}")
                
                # Small delay to prevent busy waiting
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("[MAIN] KeyboardInterrupt received - entering console mode")
            self.enter_console_mode()
        except Exception as e:
            print(f"[MAIN] Main loop error: {e}")
            self.error_count += 1
            
            if self.error_count >= self.max_errors:
                print("[MAIN] Too many errors, entering console mode")
                self.enter_console_mode()
    
    def _initialize_sensor_cache_sync(self):
        """Initialize sensor cache synchronously before main loop"""
        print("[MAIN] Initializing sensor cache synchronously...")
        
        try:
            sensors = self.drivers.get('sensors')
            controller = self.drivers.get('controller')
            
            # Read sensors synchronously
            if sensors and sensors.is_healthy():
                new_sensor_data = sensors.read_all()
                if new_sensor_data:
                    self.sensor_data = new_sensor_data.copy()
                    self.sensor_cache = new_sensor_data.copy()
                    self.last_sensor_update = utime.ticks_ms()
                    print(f"[SENSORS_SYNC] Updated: {new_sensor_data}")
            
            # Read controllers synchronously
            if controller and controller.is_healthy():
                new_controller_data = controller.get_controller_data()
                self.controller_data = new_controller_data.copy()
                print(f"[MAIN] Controller data initialized: {new_controller_data}")
            return True
                    
        except Exception as e:
            print(f"[MAIN] Sync initialization error: {e}")
            return False
            
            # Try to enter console as last resort
            try:
                print("[FATAL] Attempting console mode...")
                run_console({}, {})
            except Exception as console_error:
                print(f"[FATAL] Console mode failed: {console_error}")
                
            # Reset if all else fails
            print("[FATAL] Resetting system...")
            machine.reset()


def main():
    """Main entry point"""
    try:
        system = PicoWeatherSystem()
        system.run()
    except Exception as e:
        print(f"[FATAL] System startup failed: {e}")
        
        # Try to enter console as last resort
        try:
            print("[FATAL] Attempting console mode...")
            run_console({}, {})
        except Exception as console_error:
            print(f"[FATAL] Console mode failed: {console_error}")
            
        # Reset if all else fails
        print("[FATAL] Resetting system...")
        machine.reset()


if __name__ == "__main__":
    main()
