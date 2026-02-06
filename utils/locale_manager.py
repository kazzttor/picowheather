"""
Locale Manager - Gerenciamento de internacionalização
Suporte para múltiplos idiomas com fallback para inglês
"""

import json

# English fallback (hardcoded)
ENGLISH_FALLBACK = {
    "display": {
        "units": {
            "temperature": "°C",
            "humidity": "%", 
            "pressure": "hPa",
            "frequency": "MHz"
        },
        "formats": {
            "date": "mm/dd/yyyy",
            "time": "HH:MM:SS",
            "datetime": "mm/dd/yyyy HH:MM",
            "decimal": ".",
            "thousands": ","
        },
        "labels": {
            "temperature": "Temperature",
            "humidity": "Humidity",
            "pressure": "Pressure", 
            "frequency": "Frequency",
            "fm_radio": "FM Radio",
            "volume": "Volume",
            "mono": "Mono",
            "stereo": "Stereo",
            "muted": "Muted",
            "unmuted": "Active",
            "signal": "Signal",
            "wifi": "WiFi",
            "connected": "Connected",
            "disconnected": "Disconnected",
            "ip_address": "IP",
            "no_signal": "No Signal"
        },
        "pages": {
            "main": "Main",
            "weather": "Weather",
            "radio": "Radio", 
            "network": "Network",
            "system": "System"
        },
        "messages": {
            "initializing": "Initializing...",
            "loading": "Loading...",
            "ready": "Ready",
            "error": "Error",
            "no_data": "No Data",
            "connecting": "Connecting...",
            "synchronizing": "Synchronizing..."
        }
    },
    "console": {
        "messages": {
            "main_loaded": "[MAIN] Configuration loaded for {board}",
            "system_startup": "[MAIN] Initializing system components...",
            "init_display": "[INIT] Initializing DISPLAY...",
            "init_display_hardware": "[INIT] Initializing DISPLAY HARDWARE...",
            "init_networking": "[INIT] Initializing NETWORKING...",
            "init_ntp": "[INIT] Initializing NTP...",
            "init_sensors": "[INIT] Initializing SENSORS...",
            "init_controllers": "[INIT] Initializing CONTROLLERS...",
            "init_buttons": "[INIT] Initializing BUTTONS...",
            "ok": "OK",
            "fail": "FAIL",
            "skip": "SKIPPED",
            "status_ok": "OK",
            "status_fail": "FAIL ({error})",
            "status_skip": "SKIPPED ({reason})",
            "display_driver_ready": "[INIT] Display driver ready for framebuffer reception",
            "display_showing_status": "[INIT] Display showing initialization status",
            "display_update_success": "[INIT] Display update successful",
            "display_update_failed": "[INIT] Display update failed",
            "wifi_initialized": "[WIFI] ESP8285WifiManager ready",
            "wifi_connecting": "[WIFI] Connection attempt {attempt}/{max_attempts}",
            "wifi_connected": "[WIFI] Connection successful",
            "wifi_already_connected": "[WIFI] Already connected to configured network: {ssid}",
            "wifi_using_existing": "[WIFI] Using existing connection - IP: {ip}",
            "wifi_connection_lost": "[WIFI] Connection lost",
            "wifi_connection_restored": "[WIFI] Connection restored",
            "wifi_time_sync": "[WIFI] Time synchronized successfully",
            "time_has_valid_time": "[TIME] RTC has valid time: {datetime}",
            "time_driver_init": "[TIME] Time driver initialized, timezone: {timezone}",
            "sensors_init": "[SENSORS] {sensor} initialized at {address}",
            "sensors_reading": "[SENSORS] Reading {count} sensors",
            "sensors_first_read": "[SENSORS] First successful read: {data}",
            "sensors_sync_updated": "[SENSORS_SYNC] Updated: {data}",
            "controller_fm_detected": "[CONTROLLER] FM Transmitter detected: {detected}",
            "controller_fm_init": "[CONTROLLER] FM Transmitter initialized successfully",
            "input_button_init": "[INPUT] Button {button} initialized on pin {pin}",
            "input_buttons_count": "[INPUT] {count} buttons initialized",
            "input_callback_registered": "[INPUT] Callback registered for {button}",
            "main_callback_registered": "[MAIN] Callback registered for {button} button",
            "main_init_sensor_cache": "[MAIN] Initializing sensor cache synchronously...",
            "main_controller_data_init": "[MAIN] Controller data initialized: {data}",
            "main_init_drivers_failed": "[MAIN] Failed to initialize drivers",
            "main_error_startup": "[MAIN] Error during system startup: {error}",
            "main_loop_error": "[MAIN] Main loop error: {error}",
            "main_too_many_errors": "[MAIN] Too many errors, entering console mode",
            "main_entering_console": "[MAIN] KeyboardInterrupt received - entering console mode",
            "sensors_read_error": "[SENSORS] Read error: {error}",
            "sensors_sync_read_error": "[SENSORS] Sync read error: {error}",
            "time_update_error": "[TIME] Update error: {error}",
            "display_update_error": "[DISPLAY] Update error: {error}",
            "display_show_error": "[DISPLAY] Failed to show framebuffer",
            "wifi_check_error": "[WIFI] Check error: {error}",
            "time_sync_error": "[TIME] Sync error: {error}",
            "button_event": "[BUTTON] {action} (DisplayManager)",
            "button_display_unavailable": "[BUTTON] DisplayManager not available",
            "button_toggle_mute": "[BUTTON] Mute toggled to {state}",
            "button_toggle_mute_error": "[BUTTON] Toggle mute error: {error}",
            "input_events": "[INPUT] Events: {events}",
            "init_complete": "INITIALIZATION COMPLETE",
            "init_status_lines": "INITIALIZING...",
            "fatal_startup_failed": "[FATAL] System startup failed: {error}",
            "fatal_console_failed": "[FATAL] Console mode failed: {error}",
            "fatal_resetting": "[FATAL] Resetting system...",
            "fatal_attempting_console": "[FATAL] Attempting console mode...",
            "console_mode_error": "[MAIN] Console mode error: {error}",
            "init_failed_sensor_cache": "[INIT] Failed to initialize sensor cache",
            "init_time_data": "[INIT] Time data: {time} {date}",
            "init_time_data_fail": "[INIT] Time data: FAIL ({error})",
            "button_events": "[BUTTON] {action}",
            "main_console": "[MAIN] Entering console mode..."
        },
        "menu": {
            "main_menu": "=== PicoWeather Console Menu ===",
            "sensor_menu": "--- Sensor Commands ---",
            "display_menu": "--- Display Commands ---", 
            "radio_menu": "--- Radio Commands ---",
            "network_menu": "--- Network Commands ---",
            "system_menu": "--- System Commands ---",
            "exit": "Exit console",
            "back_to_main": "Back to main menu",
            "read_sensors": "Read all sensors",
            "read_temperature": "Read temperature",
            "read_humidity": "Read humidity",
            "read_pressure": "Read pressure",
            "show_status": "Show display status",
            "clear_display": "Clear display",
            "refresh_display": "Refresh display",
            "show_info": "Show radio info",
            "tune_frequency": "Tune frequency",
            "set_volume": "Set volume",
            "toggle_mute": "Toggle mute",
            "scan_stations": "Scan stations",
            "wifi_status": "WiFi status",
            "wifi_connect": "Connect to WiFi",
            "wifi_disconnect": "Disconnect WiFi",
            "sync_time": "Sync time with NTP",
            "show_time": "Show current time",
            "run_diagnostics": "Run full diagnostics",
            "reboot_system": "Reboot system",
            "show_config": "Show configuration",
            "invalid_option": "Invalid option",
            "choose_option": "Choose an option: "
        },
        "prompts": {
            "enter_frequency": "Enter frequency (MHz): ",
            "enter_volume": "Enter volume (0-15): ",
            "enter_ssid": "Enter SSID: ",
            "enter_password": "Enter password: ",
            "confirm_reboot": "Are you sure you want to reboot? (y/N): "
        },
        "responses": {
            "temperature_reading": "Temperature: {value}°C",
            "humidity_reading": "Humidity: {value}%",
            "pressure_reading": "Pressure: {value} hPa",
            "frequency_set": "Frequency set to {value} MHz",
            "volume_set": "Volume set to {value}",
            "muted": "Radio muted",
            "unmuted": "Radio unmuted", 
            "wifi_connected": "Connected to {ssid}",
            "wifi_disconnected": "Disconnected from WiFi",
            "time_synced": "Time synchronized: {time}",
            "system_rebooting": "System rebooting...",
            "operation_cancelled": "Operation cancelled"
        },
        "errors": {
            "command_not_found": "Command not found: {command}",
            "invalid_frequency": "Invalid frequency. Must be between {min} and {max} MHz",
            "invalid_volume": "Invalid volume. Must be between 0 and 15",
            "sensor_error": "Sensor error: {error}",
            "display_error": "Display error: {error}",
            "radio_error": "Radio error: {error}",
            "network_error": "Network error: {error}",
            "time_error": "Time error: {error}",
            "system_error": "System error: {error}"
        }
    }
}


class LocaleManager:
    def __init__(self, locale_code="en_US"):
        self.locale_code = locale_code
        self.display_data = {}
        self.console_data = {}
        self._load_locale_data()
    
    def _load_locale_data(self):
        """Carrega dados de localização dos arquivos JSON"""
        try:
            # Sempre usa UTF-8 - custom font handling charset issues
            display_file = f"locales/display_{self.locale_code}.json"
            console_file = f"locales/console_{self.locale_code}.json"
            
            # Função compatível com MicroPython para verificar arquivo
            def file_exists(filename):
                try:
                    with open(filename, 'r') as f:
                        return True
                except:
                    return False
            
            if file_exists(display_file):
                with open(display_file, 'r', encoding='utf-8') as f:
                    self.display_data = json.load(f)
            else:
                print(f"[LOCALE] Display file not found: {display_file}, using fallback")
                self.display_data = ENGLISH_FALLBACK["display"]
            
            if file_exists(console_file):
                with open(console_file, 'r', encoding='utf-8') as f:
                    self.console_data = json.load(f)
            else:
                print(f"[LOCALE] Console file not found: {console_file}, using fallback")
                self.console_data = ENGLISH_FALLBACK["console"]
                
        except Exception as e:
            print(f"[LOCALE] Error loading locale data: {e}")
            self.display_data = ENGLISH_FALLBACK["display"]
            self.console_data = ENGLISH_FALLBACK["console"]
    
    def get_display_text(self, key_path, **kwargs):
        """
        Obtém texto localizado para display
        key_path: caminho como "labels.temperature" ou "units.temperature"
        """
        try:
            keys = key_path.split('.')
            value = self.display_data
            
            for key in keys:
                value = value[key]
            
            # Formata com kwargs se fornecido
            if kwargs and isinstance(value, str):
                value = value.format(**kwargs)
                
            return value
        except (KeyError, TypeError):
            # Fallback para inglês
            try:
                keys = key_path.split('.')
                value = ENGLISH_FALLBACK["display"]
                
                for key in keys:
                    value = value[key]
                
                if kwargs and isinstance(value, str):
                    value = value.format(**kwargs)
                    
                return value
            except (KeyError, TypeError):
                return key_path  # Último fallback
    
    def get_console_text(self, key_path, **kwargs):
        """
        Obtém texto localizado para console
        key_path: caminho como "messages.main_loaded" ou "menu.main_menu"
        """
        try:
            keys = key_path.split('.')
            value = self.console_data
            
            for key in keys:
                value = value[key]
            
            # Formata com kwargs se fornecido
            if kwargs and isinstance(value, str):
                value = value.format(**kwargs)
                
            return value
        except (KeyError, TypeError):
            # Fallback para inglês
            try:
                keys = key_path.split('.')
                value = ENGLISH_FALLBACK["console"]
                
                for key in keys:
                    value = value[key]
                
                if kwargs and isinstance(value, str):
                    value = value.format(**kwargs)
                    
                return value
            except (KeyError, TypeError):
                return key_path  # Último fallback
    
    def format_number(self, value, decimal_places=None):
        """Formata número de acordo com localização"""
        try:
            decimal_sep = self.get_display_text("formats.decimal")
            thousands_sep = self.get_display_text("formats.thousands")
            
            # Debug
            # Locale configured successfully
            
            if decimal_places is not None:
                format_str = f"{{:.{decimal_places}f}}"
                formatted = format_str.format(value)
            else:
                formatted = str(value)
            
            # Para pt_BR: decimal=, thousands=.
            if '.' in formatted:
                integer_part, decimal_part = formatted.split('.')
                # Adiciona separador de milhar (ponto para pt_BR)
                integer_with_thousands = []
                for i, digit in enumerate(reversed(integer_part)):
                    if i > 0 and i % 3 == 0:
                        integer_with_thousands.append(thousands_sep)
                    integer_with_thousands.append(digit)
                integer_part = ''.join(reversed(integer_with_thousands))
                
                # Junta com separador decimal (vírgula para pt_BR)
                return f"{integer_part}{decimal_sep}{decimal_part}"
            else:
                # Adiciona separador de milhar apenas
                integer_with_thousands = []
                for i, digit in enumerate(reversed(formatted)):
                    if i > 0 and i % 3 == 0:
                        integer_with_thousands.append(thousands_sep)
                    integer_with_thousands.append(digit)
                return ''.join(reversed(integer_with_thousands))
                
        except Exception:
            # Fallback simples
            if decimal_places is not None:
                return f"{value:.{decimal_places}f}"
            return str(value)
    
    def format_temperature(self, temp_celsius):
        """Formata temperatura com unidade localizada"""
        unit = self.get_display_text("units.temperature")
        # Formata número com 1 casa decimal
        formatted_num = self.format_number(temp_celsius, 1)
        # Verifica se já tem ° no unit para evitar duplicação
        unit_str = str(unit)
        if unit_str.startswith('°'):
            return f"{formatted_num}{unit_str}"
        else:
            return f"{formatted_num}°{unit_str}"
    
    def format_humidity(self, humidity):
        """Formata umidade com unidade localizada"""
        unit = self.get_display_text("units.humidity")
        return f"{self.format_number(humidity, 1)}{unit}"
    
    def format_pressure(self, pressure):
        """Formata pressão com unidade localizada"""
        unit = self.get_display_text("units.pressure")
        return f"{self.format_number(pressure, 0)}{unit}"
    
    def format_frequency(self, frequency):
        """Formata frequência com unidade localizada"""
        unit = self.get_display_text("units.frequency")
        return f"{self.format_number(frequency, 1)}{unit}"
    
    def format_volume(self, volume):
        """Formata volume"""
        return self.format_number(volume, 0)


# Instância global
_locale_manager = None


def init_locale(locale_code):
    """Inicializa o gerenciador de localização global"""
    global _locale_manager
    _locale_manager = LocaleManager(locale_code)


def get_locale():
    """Retorna a instância global do gerenciador de localização"""
    return _locale_manager


def t_display(key_path, **kwargs):
    """Função de atalho para obter texto de display localizado"""
    if _locale_manager:
        return _locale_manager.get_display_text(key_path, **kwargs)
    return key_path


def t_console(key_path, **kwargs):
    """Função de atalho para obter texto de console localizado"""
    if _locale_manager:
        return _locale_manager.get_console_text(key_path, **kwargs)
    return key_path


def fmt_number(value, decimal_places=None):
    """Função de atalho para formatar números localizados"""
    if _locale_manager:
        return _locale_manager.format_number(value, decimal_places)
    if decimal_places is not None:
        return f"{value:.{decimal_places}f}"
    return str(value)


def fmt_temp(value):
    """Função de atalho para formatar temperatura"""
    if _locale_manager:
        return _locale_manager.format_temperature(value)
    return f"{value:.1f}°C"


def fmt_humidity(value):
    """Função de atalho para formatar umidade"""
    if _locale_manager:
        return _locale_manager.format_humidity(value)
    return f"{value:.1f}%"


def fmt_pressure(value):
    """Função de atalho para formatar pressão"""
    if _locale_manager:
        return _locale_manager.format_pressure(value)
    return f"{value:.0f}hPa"


def fmt_frequency(value):
    """Função de atalho para formatar frequência"""
    if _locale_manager:
        return _locale_manager.format_frequency(value)
    return f"{value:.1f}MHz"