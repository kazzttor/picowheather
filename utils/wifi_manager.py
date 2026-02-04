"""
WiFi Manager - Interface que usa NetworkingDriver
Suporta ESP8285, CYW43 (Pico W) ou nenhum
"""

import time
import utime
import json
# Removed typing module for MicroPython compatibility

try:
    from drivers.networking_driver import NetworkingDriver
    NETWORKING_AVAILABLE = True
except ImportError:
    NETWORKING_AVAILABLE = False

class WiFiManager:
    """Simplified WiFi manager that uses NetworkingDriver internally"""
    
    def __init__(self, config):
        self.config = config
        self.networking_driver = None
        self.enabled = config.get("wifi", {}).get("enabled", False)
        
        self.connected = False
        self.ip_address = "0.0.0.0"
        self.current_ssid = None
        self.time_synced = False
        self.last_networks = []
        
        if self.enabled and NETWORKING_AVAILABLE:
            self.networking_driver = NetworkingDriver(config)
            print("[WIFI] WiFi Manager initialized with NetworkingDriver")
        elif self.enabled:
            print("[WIFI] WiFi enabled but NetworkingDriver not available")
        else:
            print("[WIFI] WiFi disabled in configuration")