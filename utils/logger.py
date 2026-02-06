"""
Sistema de logging limpo e formatado para PicoWeather
"""

import utime


def log_info(component, message):
    """Log informativo formatado"""
    timestamp = utime.ticks_ms()
    print(f"[{timestamp:08d}] {component.upper()} - {message}")


def log_error(component, error):
    """Log de erro formatado"""
    timestamp = utime.ticks_ms()
    print(f"[{timestamp:08d}] {component.upper()} - ERROR: {error}")


def log_debug(component, message):
    """Log de debug (pode ser desabilitado)"""
    # timestamp = utime.ticks_ms()
    # print(f"[{timestamp:08d}] {component.upper()} - DEBUG: {message}")
    pass  # Debug desabilitado para logs limpos


def log_sensor_update(sensor_data):
    """Log específico para atualização de sensores"""
    timestamp = utime.ticks_ms()
    temp = sensor_data.get('temperature', 0)
    humidity = sensor_data.get('humidity', 0) 
    pressure = sensor_data.get('pressure', 0)
    print(f"[{timestamp:08d}] SENSORES - Temp:{temp:.1f}°C Umid:{humidity:.1f}% Press:{pressure:.1f}hPa")


def log_system_event(event):
    """Log para eventos do sistema"""
    timestamp = utime.ticks_ms()
    print(f"[{timestamp:08d}] SISTEMA - {event}")


def log_console_event(event):
    """Log para eventos do console"""
    timestamp = utime.ticks_ms()
    print(f"[{timestamp:08d}] CONSOLE - {event}")