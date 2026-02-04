"""
Networking Driver - Unified WiFi management for PicoWeather
Handles both Pico W native WiFi and external ESP8285 via UART
"""

import time
import utime
from machine import UART, Pin


class PicoWWifiManager:
    """WiFi manager for Pico W (native)"""
    
    def __init__(self, config):
        self.config = config
        self.network = None
        self.connected = False
        self.current_ssid = None
        self.ip_address = "0.0.0.0"
        self.error_count = 0
        self.last_scan = []
        self.initialized = False
        
    def initialize(self):
        """Initialize Pico W WiFi"""
        try:
            import network
            self.network = network.WLAN(network.STA_IF)
            self.network.active(True)
            self.initialized = True
            print("[WIFI] Pico W WiFi initialized")
            return True
        except Exception as e:
            print(f"[WIFI] Pico W initialization failed: {e}")
            return False
    
    def scan_networks(self):
        """Scan for WiFi networks"""
        if not self.initialized:
            return []
        
        try:
            networks = self.network.scan()
            formatted_networks = []
            
            for ssid, bssid, channel, rssi, authmode, hidden in networks:
                ssid_str = ssid.decode('utf-8') if isinstance(ssid, bytes) else str(ssid)
                formatted_networks.append({
                    'ssid': ssid_str,
                    'bssid': ':'.join(['{:02x}'.format(b) for b in bssid]),
                    'channel': channel,
                    'rssi': rssi,
                    'authmode': authmode,
                    'hidden': hidden
                })
            
            self.last_scan = formatted_networks
            return formatted_networks
            
        except Exception as e:
            print(f"[WIFI] Scan error: {e}")
            return []
    
    def connect_to_networks(self, network_list):
        """Try to connect to networks in priority order"""
        if not self.initialized or not network_list:
            return False
        
        # Sort networks by priority
        sorted_networks = sorted(network_list, key=lambda x: x.get('priority', 999))
        
        for network_config in sorted_networks:
            ssid = network_config.get('ssid')
            password = network_config.get('password')
            
            if not ssid:
                continue
                
            print(f"[WIFI] Trying to connect to: {ssid}")
            
            if self._connect_single(ssid, password):
                self.connected = True
                self.current_ssid = ssid
                return True
        
        self.connected = False
        return False
    
    def _connect_single(self, ssid, password):
        """Connect to a single network"""
        try:
            # Disconnect if already connected
            if self.network.isconnected():
                self.network.disconnect()
                time.sleep(1)
            
            # Connect to network
            self.network.connect(ssid, password)
            
            # Wait for connection (max 10 seconds)
            for i in range(20):
                if self.network.isconnected():
                    ip = self.network.ifconfig()[0]
                    self.ip_address = ip
                    print(f"[WIFI] Connected to {ssid} - IP: {ip}")
                    return True
                time.sleep(0.5)
            
            print(f"[WIFI] Timeout connecting to {ssid}")
            return False
            
        except Exception as e:
            print(f"[WIFI] Failed to connect to {ssid}: {e}")
            self.error_count += 1
            return False
    
    def check_connection(self):
        """Check if still connected"""
        if not self.initialized or not self.network:
            return False
        
        try:
            was_connected = self.connected
            self.connected = self.network.isconnected()
            
            if self.connected:
                if not was_connected:
                    ip = self.network.ifconfig()[0]
                    self.ip_address = ip
                    self.current_ssid = self._get_current_ssid()
                    print(f"[WIFI] Reconnected - IP: {ip}")
            else:
                if was_connected:
                    print("[WIFI] Connection lost")
                    self.current_ssid = None
                    self.ip_address = "0.0.0.0"
            
            return self.connected
            
        except Exception as e:
            print(f"[WIFI] Connection check failed: {e}")
            self.error_count += 1
            return False
    
    def _get_current_ssid(self):
        """Get current SSID if connected"""
        try:
            # Get SSID from connection info if available
            if hasattr(self.network, 'config'):
                config = self.network.config()
                if 'essid' in config:
                    return config['essid']
            
            # Fallback: scan to find current network with strong signal
            networks = self.network.scan()
            for ssid, bssid, channel, rssi, authmode, hidden in networks:
                ssid_str = ssid.decode('utf-8') if isinstance(ssid, bytes) else str(ssid)
                if rssi > -50:  # Strong signal indicates current network
                    return ssid_str
            return None
        except:
            return None
    
    def sync_ntp_time(self, ntp_server=None):
        """Synchronize time using NTP for Pico W"""
        try:
            import ntptime
            
            # Use default server if none provided
            if not ntp_server:
                ntp_server = "pool.ntp.org"
            
            print(f"[WIFI] Syncing NTP time from {ntp_server}")
            
            # Set NTP server
            ntptime.host = ntp_server
            
            # Synchronize time
            ntptime.settime()
            
            print("[WIFI] NTP time synchronized successfully")
            return True
            
        except Exception as e:
            print(f"[WIFI] NTP sync failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WiFi"""
        if self.network and self.connected:
            try:
                self.network.disconnect()
                self.connected = False
                self.current_ssid = None
                self.ip_address = "0.0.0.0"
                print("[WIFI] Disconnected")
            except Exception as e:
                print(f"[WIFI] Disconnect error: {e}")
    
    def get_status(self):
        """Get WiFi status"""
        return {
            'initialized': self.initialized,
            'connected': self.connected,
            'current_ssid': self.current_ssid,
            'ip_address': self.ip_address,
            'error_count': self.error_count,
            'last_scan_count': len(self.last_scan),
            'type': 'pico_w_native'
        }

class ESP8285WifiManager:
    """Minimal ESP8285 WiFi manager - AT commands only"""
    
    def __init__(self, config):
        self.config = config
        self.uart = None
        self.connected = False
        self.current_ssid = None
        self.ip_address = "0.0.0.0"
        self.error_count = 0
        self.last_scan = []
        self.initialized = False
        self.last_command_time = 0  # To prevent command flooding
        self.command_cooldown = 100  # Minimum ms between commands
        
    def initialize(self):
        """Initialize ESP8285 via UART"""
        try:
            wifi_config = self.config.get("wifi", {})
            uart_config = wifi_config.get("pins", {})
            
            print("[WIFI] Initializing ESP8285 via UART...")
            
            # Get pin numbers
            from drivers.hardware_config import get_hardware_config
            
            board_type = self.config.get("hardware", {}).get("board", "pico_standard")
            hardware = get_hardware_config(board_type)
            
            uart_id = hardware["pins"].get("uart_id", 0)
            tx_pin = hardware["pins"].get("uart0_tx", 0)
            rx_pin = hardware["pins"].get("uart0_rx", 1)
            
            print(f"[WIFI] UART: id={uart_id}, tx={tx_pin}, rx={rx_pin}")
            
            # Initialize UART
            self.uart = UART(uart_id, baudrate=115200, 
                            tx=Pin(tx_pin), 
                            rx=Pin(rx_pin))
            
            # Clear UART buffer
            if self.uart.any():
                self.uart.read()
            
            # Exit transparent mode
            print("[WIFI] Sending exit transparent mode command")
            self.uart.write('+++')
            time.sleep(1)
            
            # Clear buffer again
            if self.uart.any():
                self.uart.read()
            
            # Test communication
            print("[WIFI] Testing AT command")
            success, response = self._send_at_command("AT", timeout_ms=2000)
            
            if success:
                self.initialized = True
                print("[WIFI] ESP8285 initialized successfully")
                
                # Turn off echo
                self._send_at_command("ATE0")
                
                return True
            else:
                print(f"[WIFI] ESP8285 not responding. Response: {response}")
                return False
                
        except Exception as e:
            print(f"[WIFI] ESP8285 initialization failed: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def _send_at_command(self, command, expected="OK", timeout_ms=5000):
        """Send command to ESP8285 and return success, response tuple with cooldown protection"""
        if not self.uart:
            return False, ""
        
        try:
            # Add cooldown between commands to prevent ESP8285 overload
            current_time = utime.ticks_ms()
            time_since_last = utime.ticks_diff(current_time, self.last_command_time)
            if time_since_last < self.command_cooldown:
                time.sleep((self.command_cooldown - time_since_last) / 1000)
            
            self.last_command_time = utime.ticks_ms()
            
            # Clear UART buffer
            if self.uart.any():
                self.uart.read()
            
            # Send command
            print(f"[WIFI] AT: {command}")
            self.uart.write(command + '\r\n')
            
            # Wait for response
            start_time = utime.ticks_ms()
            response = ""
            last_data_time = start_time
            
            while utime.ticks_diff(utime.ticks_ms(), start_time) < timeout_ms:
                if self.uart.any():
                    data = self.uart.read()
                    if data:
                        try:
                            response += data.decode('utf-8', 'ignore')
                        except:
                            response += data.decode('latin-1', 'ignore')
                        last_data_time = utime.ticks_ms()
                    
                    # Check if we have expected response or error
                    if expected in response or "ERROR" in response:
                        break
                
                # If no data received for a while, break to avoid infinite loop
                if utime.ticks_diff(utime.ticks_ms(), last_data_time) > 1000 and response:
                    break
                
                time.sleep(0.01)
            
            response = response.strip()
            if response:
                # Clean up response for logging
                clean_response = response.replace('\r', '\\r').replace('\n', '\\n')
                print(f"[WIFI]   -> {clean_response[:100]}")  # Limit log length
            
            success = expected in response
            # Sometimes response might be OK without the expected string
            if not success and ("OK" in response or "SEND OK" in response):
                success = True
            
            return success, response
            
        except Exception as e:
            print(f"[WIFI] Command '{command}' failed: {e}")
            return False, ""
    
    def scan_networks(self):
        """Scan for WiFi networks using ESP8285"""
        if not self.initialized:
            return []
        
        try:
            # Set to station mode
            success, _ = self._send_at_command("AT+CWMODE=1")
            if not success:
                print("[WIFI] Failed to set station mode")
                return []
            
            # Scan networks (longer timeout for scan)
            success, response = self._send_at_command("AT+CWLAP", timeout_ms=15000)
            
            networks = []
            if success and response:
                lines = response.split('\n')
                for line in lines:
                    line = line.strip()
                    if '+CWLAP:' in line:
                        try:
                            # Parse response format: +CWLAP:(auth,SSID,RSSI,MAC,channel)
                            start_idx = line.find('(')
                            end_idx = line.rfind(')')
                            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                                data_part = line[start_idx+1:end_idx]
                                parts = [part.strip() for part in data_part.split(',')]
                                
                                if len(parts) >= 5:
                                    auth = int(parts[0]) if parts[0].isdigit() else 0
                                    ssid = parts[1].strip('"')
                                    rssi = int(parts[2]) if parts[2].lstrip('-').isdigit() else -100
                                    mac = parts[3].strip('"')
                                    channel = int(parts[4]) if parts[4].isdigit() else 0
                                    
                                    networks.append({
                                        'ssid': ssid,
                                        'bssid': mac,
                                        'channel': channel,
                                        'rssi': rssi,
                                        'authmode': auth,
                                        'hidden': False
                                    })
                        except Exception as e:
                            print(f"[WIFI] Error parsing network info: {e}")
                            continue
            
            # Sort by RSSI (strongest first)
            networks.sort(key=lambda x: x['rssi'], reverse=True)
            self.last_scan = networks
            
            print(f"[WIFI] ESP8285 found {len(networks)} networks")
            return networks
            
        except Exception as e:
            print(f"[WIFI] ESP8285 scan failed: {e}")
            self.error_count += 1
            return []
    
    def connect_to_networks(self, network_list):
        """Try to connect to networks in priority order"""
        if not self.initialized or not network_list:
            return False
        
        # PRIMEIRO: Verificar se já estamos conectados a alguma das redes configuradas
        print("[WIFI] Checking for existing connections to configured networks...")
        connected, connected_ssid = self.check_existing_connection()
        
        if connected and connected_ssid:
            # Verificar se está conectado a uma das redes da lista
            for network_config in network_list:
                ssid = network_config.get('ssid')
                if ssid == connected_ssid:
                    print(f"[WIFI] Already connected to configured network: {ssid}")
                    # Obter IP e atualizar status
                    success, ip_response = self._send_at_command("AT+CIFSR", timeout_ms=3000)
                    if success and ip_response:
                        for line in ip_response.split('\n'):
                            line = line.strip()
                            if 'STAIP' in line or 'CIFSR:STAIP' in line:
                                if '"' in line:
                                    ip = line.split('"')[1]
                                elif ':' in line:
                                    ip = line.split(':')[-1].strip()
                                elif ',' in line:
                                    ip = line.split(',')[-1].strip()
                                else:
                                    continue
                                
                                if ip and ip != '0.0.0.0':
                                    self.ip_address = ip
                                    self.connected = True
                                    self.current_ssid = ssid
                                    print(f"[WIFI] Using existing connection - IP: {ip}")
                                    return True
                    
                    # Se chegou aqui, está conectado mas não tem IP ainda
                    self.ip_address = "Connected (no IP)"
                    self.connected = True
                    self.current_ssid = connected_ssid
                    return True
        
        # SEGUNDO: Se não está conectado, tentar conectar na ordem de prioridade
        print("[WIFI] No existing connection found, attempting new connections...")
        
        # Ordenar redes por prioridade
        sorted_networks = sorted(network_list, key=lambda x: x.get('priority', 999))
        
        for network_config in sorted_networks:
            ssid = network_config.get('ssid')
            password = network_config.get('password')
            
            if not ssid:
                continue
            
            print(f"[WIFI] ESP8285 trying to connect to: {ssid}")
            
            if self._connect_single(ssid, password):
                self.connected = True
                self.current_ssid = ssid
                return True
        
        self.connected = False
        return False
    
    # No arquivo networking_driver.py, na classe ESP8285WifiManager:

    def _connect_single(self, ssid, password):
        """Connect to a single network using ESP8285 - with existing connection check"""
        try:
            print(f"[WIFI] Starting connection process to {ssid}")
            
            # PRIMEIRO: Verificar se já estamos conectados a uma rede
            print("[WIFI] Checking if already connected...")
            success, response = self._send_at_command("AT+CWJAP?", timeout_ms=3000)
            
            if success and response:
                # Analisar resposta para ver a qual rede estamos conectados
                for line in response.split('\n'):
                    line = line.strip()
                    if '+CWJAP:' in line:
                        # Exemplo: +CWJAP:"ssid","mac",channel,rssi
                        parts = line.split(',')
                        if len(parts) > 0:
                            # Extrair SSID da resposta
                            if '"' in parts[0]:
                                connected_ssid = parts[0].split('"')[1]
                                print(f"[WIFI] Already connected to: {connected_ssid}")
                                
                                # Se já estamos conectados à rede desejada
                                if connected_ssid == ssid:
                                    print(f"[WIFI] Already connected to target network {ssid}")
                                    
                                    # Obter IP atual
                                    success, ip_response = self._send_at_command("AT+CIFSR", timeout_ms=3000)
                                    if success and ip_response:
                                        # Extrair IP
                                        for ip_line in ip_response.split('\n'):
                                            ip_line = ip_line.strip()
                                            if 'STAIP' in ip_line or 'CIFSR:STAIP' in ip_line:
                                                if '"' in ip_line:
                                                    ip = ip_line.split('"')[1]
                                                elif ':' in ip_line:
                                                    ip = ip_line.split(':')[-1].strip()
                                                elif ',' in ip_line:
                                                    ip = ip_line.split(',')[-1].strip()
                                                else:
                                                    continue
                                                
                                                if ip and ip != '0.0.0.0':
                                                    self.ip_address = ip
                                                    self.connected = True
                                                    self.current_ssid = ssid
                                                    print(f"[WIFI] Using existing connection to {ssid} - IP: {ip}")
                                                    return True
                                    
                                    # Se chegou aqui, está conectado mas não conseguiu IP
                                    print(f"[WIFI] Already connected to {ssid} (getting IP)")
                                    self.ip_address = "Connected (getting IP)"
                                    self.connected = True
                                    self.current_ssid = ssid
                                    return True
                                else:
                                    print(f"[WIFI] Connected to different network: {connected_ssid}")
                                    print(f"[WIFI] Disconnecting from {connected_ssid}...")
                                    self._send_at_command("AT+CWQAP")
                                    time.sleep(2)
            
            # SEGUNDO: Se não está conectado ou está na rede errada, conectar
            print(f"[WIFI] Not connected to target network, proceeding with connection...")
            
            # Sair do modo transparente
            print("[WIFI] Ensuring command mode...")
            self.uart.write('+++')
            time.sleep(1.5)
            
            # Limpar buffer
            for _ in range(3):
                if self.uart.any():
                    self.uart.read()
                time.sleep(0.1)
            
            # Verificar se está respondendo
            print("[WIFI] Testing AT command...")
            success, response = self._send_at_command("AT", timeout_ms=2000)
            if not success:
                print(f"[WIFI] ESP8285 not responding: {response}")
                return False
            
            # Configurar modo (tentar algumas vezes)
            for attempt in range(3):
                print(f"[WIFI] Setting station mode (attempt {attempt+1}/3)...")
                success, response = self._send_at_command("AT+CWMODE=1")
                if success:
                    print("[WIFI] Station mode set successfully")
                    break
                else:
                    print(f"[WIFI] Failed to set station mode: {response}")
                    if attempt < 2:
                        time.sleep(1)
                    else:
                        return False
            
            # Desabilitar conexões múltiplas
            self._send_at_command("AT+CIPMUX=0")
            
            # Verificar redes disponíveis antes de tentar conectar
            print("[WIFI] Scanning for available networks...")
            success, scan_response = self._send_at_command("AT+CWLAP", timeout_ms=10000)
            
            target_network_found = False
            if success and scan_response:
                for line in scan_response.split('\n'):
                    if ssid in line:
                        print(f"[WIFI] Target network {ssid} found in scan")
                        target_network_found = True
                        break
            
            if not target_network_found:
                print(f"[WIFI] Warning: Network {ssid} not found in scan")
                print("[WIFI] Will attempt connection anyway...")
            
            # Conectar à rede
            print(f"[WIFI] Connecting to {ssid}...")
            cmd = f'AT+CWJAP="{ssid}","{password}"'
            
            # Tentativa de conexão com timeout longo
            success, response = self._send_at_command(cmd, timeout_ms=30000)
            
            # Verificar diferentes respostas de sucesso
            connection_indicators = ["OK", "CONNECTED", "GOT IP", "WIFI CONNECTED"]
            connection_success = success
            
            if not connection_success:
                for indicator in connection_indicators:
                    if indicator in response:
                        connection_success = True
                        print(f"[WIFI] Found success indicator: {indicator}")
                        break
            
            if connection_success:
                print(f"[WIFI] Connection to {ssid} appears successful")
                
                # Esperar um pouco para estabilizar
                print("[WIFI] Waiting for connection to stabilize...")
                time.sleep(3)
                
                # Verificar status da conexão
                print("[WIFI] Verifying connection status...")
                success, status_response = self._send_at_command("AT+CWJAP?", timeout_ms=3000)
                
                if success and status_response and ssid in status_response:
                    print(f"[WIFI] Verified: Connected to {ssid}")
                    
                    # Obter IP
                    success, ip_response = self._send_at_command("AT+CIFSR", timeout_ms=5000)
                    
                    if success and ip_response:
                        # Extrair IP
                        for line in ip_response.split('\n'):
                            line = line.strip()
                            if 'STAIP' in line or 'CIFSR:STAIP' in line:
                                # Extrair IP de diferentes formatos
                                if '"' in line:
                                    ip = line.split('"')[1]
                                elif ':' in line:
                                    ip = line.split(':')[-1].strip()
                                elif ',' in line:
                                    ip = line.split(',')[-1].strip()
                                else:
                                    continue
                                
                                if ip and ip != '0.0.0.0':
                                    self.ip_address = ip
                                    self.connected = True
                                    self.current_ssid = ssid
                                    print(f"[WIFI] Successfully connected to {ssid} - IP: {ip}")
                                    return True
                    
                    # Se chegou aqui mas está conectado
                    print(f"[WIFI] Connected to {ssid} (IP assignment pending)")
                    self.ip_address = "Connected (IP pending)"
                    self.connected = True
                    self.current_ssid = ssid
                    return True
                else:
                    print(f"[WIFI] Could not verify connection to {ssid}")
                    print(f"[WIFI] Status response: {status_response}")
                    return False
            else:
                print(f"[WIFI] Failed to connect to {ssid}")
                print(f"[WIFI] Response: {response[:200]}")
                return False
                
        except Exception as e:
            print(f"[WIFI] Connection to {ssid} failed with exception: {e}")
            import sys
            sys.print_exception(e)
            self.error_count += 1
            return False
    
    # No networking_driver.py, no método check_connection da classe ESP8285WifiManager:

    def check_connection(self):
        """Check if still connected using ESP8285 - optimized"""
        if not self.initialized:
            return False
        
        # Se não acreditamos que estamos conectados, não verificar tão frequentemente
        if not self.connected:
            print("[WIFI] Not connected, skipping detailed check")
            return False
        
        try:
            # Verificação mais rápida usando AT+CWJAP?
            success, response = self._send_at_command("AT+CWJAP?", timeout_ms=2000)
            
            if success and response and self.current_ssid:
                # Verificar se ainda está conectado ao mesmo SSID
                if self.current_ssid in response:
                    print(f"[WIFI] Still connected to {self.current_ssid}")
                    return True
                else:
                    print(f"[WIFI] No longer connected to {self.current_ssid}")
                    self.connected = False
                    self.current_ssid = None
                    self.ip_address = "0.0.0.0"
                    return False
            else:
                print("[WIFI] Connection check failed or no response")
                self.connected = False
                return False
                
        except Exception as e:
            print(f"[WIFI] Connection check error: {e}")
            # Não marcar como desconectado imediatamente em caso de erro
            return self.connected  # Retorna estado atual em vez de False
        
    def check_existing_connection(self):
        """Check if ESP8285 is already connected to a network"""
        if not self.initialized:
            return False, None
        
        try:
            print("[WIFI] Checking for existing connection...")
            success, response = self._send_at_command("AT+CWJAP?", timeout_ms=3000)
            
            if success and response:
                for line in response.split('\n'):
                    line = line.strip()
                    if '+CWJAP:' in line:
                        # Formato: +CWJAP:"ssid","mac",channel,rssi
                        parts = [part.strip() for part in line.split(',')]
                        if len(parts) > 0 and '"' in parts[0]:
                            ssid = parts[0].split('"')[1]
                            print(f"[WIFI] Found existing connection to: {ssid}")
                            return True, ssid
            
            print("[WIFI] No existing connection found")
            return False, None
            
        except Exception as e:
            print(f"[WIFI] Error checking existing connection: {e}")
            return False, None
    
    def sync_ntp_time(self, ntp_server=None, timezone=0):
        """Synchronize time using NTP for ESP8285"""
        try:
            # Use default server if none provided
            if not ntp_server:
                ntp_server = "pool.ntp.org"
            
            print(f"[WIFI] ESP8285 syncing NTP time from {ntp_server}")
            
            # Configure NTP with timezone
            ntp_config_cmd = f'AT+CIPSNTPCFG=1,{timezone},"{ntp_server}"'
            success, response = self._send_at_command(ntp_config_cmd, timeout_ms=10000)
            
            if not success:
                print("[WIFI] ESP8285 NTP configuration failed")
                # Try with default server if custom failed
                if ntp_server != "pool.ntp.org":
                    print("[WIFI] ESP8285 trying with default NTP server...")
                    ntp_config_cmd = 'AT+CIPSNTPCFG=1,0,"pool.ntp.org"'
                    success, response = self._send_at_command(ntp_config_cmd, timeout_ms=10000)
                    if not success:
                        print("[WIFI] ESP8285 NTP configuration failed even with default server")
                        return False
                else:
                    return False
            
            # Get NTP time
            success, time_response = self._send_at_command("AT+CIPSNTPTIME?", timeout_ms=15000)
            
            if success and "+CIPSNTPTIME:" in time_response:
                # Extract time string from response
                for line in time_response.split('\n'):
                    if '+CIPSNTPTIME:' in line:
                        time_str = line.split(':', 1)[1].strip()
                        print(f"[WIFI] ESP8285 NTP time: {time_str}")
                        
                        # For ESP8285, the time is already set in the module
                        # We just need to indicate success
                        print("[WIFI] ESP8285 NTP time synchronized successfully")
                        return True
            
            print("[WIFI] ESP8285 NTP sync failed - no valid time response")
            return False
            
        except Exception as e:
            print(f"[WIFI] ESP8285 NTP sync error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WiFi"""
        if self.initialized and self.connected:
            try:
                self._send_at_command("AT+CWQAP")
                self.connected = False
                self.current_ssid = None
                self.ip_address = "0.0.0.0"
                print("[WIFI] ESP8285 disconnected")
            except Exception as e:
                print(f"[WIFI] ESP8285 disconnect error: {e}")
    
    def get_status(self):
        """Get WiFi status"""
        return {
            'initialized': self.initialized,
            'connected': self.connected,
            'current_ssid': self.current_ssid,
            'ip_address': self.ip_address,
            'error_count': self.error_count,
            'last_scan_count': len(self.last_scan),
            'type': 'esp8285_uart'
        }

class NetworkingDriver:
    """Unified networking driver that auto-detects hardware"""
    
    def __init__(self, config):
        self.config = config
        self.wifi_manager = None
        self.board_type = config.get("hardware", {}).get("board", "pico_standard")
        
        # Auto-detect and initialize appropriate WiFi manager
        self._initialize_wifi()
    
    def _initialize_wifi(self):
        """Auto-detect and initialize WiFi based on board type"""
        wifi_config = self.config.get("wifi", {})
        
        if not wifi_config.get("enabled", False):
            print("[WIFI] WiFi disabled in configuration")
            return
        
        if self.board_type in ["pico_w", "pico_w_usb"]:
            # Pico W - use native WiFi
            print("[WIFI] Initializing Pico W native WiFi...")
            self.wifi_manager = PicoWWifiManager(self.config)
            
        elif wifi_config.get("type") == "esp8285":
            # External ESP8285 via UART
            print("[WIFI] Initializing ESP8285 via UART...")
            self.wifi_manager = ESP8285WifiManager(self.config)
            
        else:
            print("[WIFI] No WiFi configuration found for this board")
            return
        
        # Initialize the selected WiFi manager
        if self.wifi_manager:
            if self.wifi_manager.initialize():
                print(f"[WIFI] {type(self.wifi_manager).__name__} ready")
            else:
                print(f"[WIFI] Failed to initialize {type(self.wifi_manager).__name__}")
                self.wifi_manager = None
    
    def auto_connect(self, max_attempts=3):
        """Automatically connect to configured networks with retry logic"""
        if not self.wifi_manager:
            print("[WIFI] No WiFi manager available")
            return False
        
        network_list = self.config.get("wifi", {}).get("networks", [])
        if not network_list:
            print("[WIFI] No networks configured")
            return False
        
        # Try connecting with retry logic
        for attempt in range(max_attempts):
            print(f"[WIFI] Connection attempt {attempt + 1}/{max_attempts}")
            
            if self.wifi_manager.connect_to_networks(network_list):
                print("[WIFI] Connection successful")
                return True
            
            if attempt < max_attempts - 1:
                print(f"[WIFI] Connection failed, retrying in 2 seconds...")
                time.sleep(2)
        
        print(f"[WIFI] Failed to connect after {max_attempts} attempts")
        return False
    
    def scan_networks(self):
        """Scan for available networks"""
        if not self.wifi_manager:
            return []
        
        return self.wifi_manager.scan_networks()
    
    def check_connection(self):
        """Check current connection status"""
        if not self.wifi_manager:
            return False
        
        return self.wifi_manager.check_connection()
    
    def disconnect(self):
        """Disconnect from current network"""
        if self.wifi_manager:
            self.wifi_manager.disconnect()
    
    def get_status(self):
        """Get comprehensive WiFi status"""
        if not self.wifi_manager:
            return {
                'available': False,
                'type': 'none'
            }
        
        status = self.wifi_manager.get_status()
        status['available'] = True
        status['board_type'] = self.board_type
        
        return status
    
    def get_ip_address(self):
        """Get current IP address"""
        if not self.wifi_manager:
            return "0.0.0.0"
        
        return getattr(self.wifi_manager, 'ip_address', '0.0.0.0')
    
    def is_connected(self):
        """Check if connected to WiFi"""
        if not self.wifi_manager:
            return False
        
        return getattr(self.wifi_manager, 'connected', False)
    
    def sync_ntp_time(self, ntp_server=None):
        """Synchronize time using NTP through available WiFi connection"""
        if not self.wifi_manager or not self.wifi_manager.connected:
            print("[WIFI] Cannot sync NTP - no WiFi connection")
            return False
        
        # Use configured NTP server if none provided
        if not ntp_server:
            ntp_server = self.config.get("wifi", {}).get("ntp_server", "pool.ntp.org")
        
        # Get timezone from config
        timezone = self.config.get("wifi", {}).get("timezone", 0)
        
        try:
            # Call appropriate NTP sync method based on WiFi type
            if hasattr(self.wifi_manager, 'sync_ntp_time'):
                if isinstance(self.wifi_manager, ESP8285WifiManager):
                    return self.wifi_manager.sync_ntp_time(ntp_server, timezone)
                else:
                    return self.wifi_manager.sync_ntp_time(ntp_server)
            else:
                print("[WIFI] NTP sync not supported by this WiFi manager")
                return False
                
        except Exception as e:
            print(f"[WIFI] NTP sync error: {e}")
            return False
    
    def get_available_networks(self):
        """Get list of available networks from last scan"""
        if not self.wifi_manager:
            return []
        
        return getattr(self.wifi_manager, 'last_scan', [])
    
    def reset_error_count(self):
        """Reset error counter"""
        if self.wifi_manager:
            self.wifi_manager.error_count = 0
    
    def activate_and_sync_time(self):
        """Activate WiFi connection and sync time, fallback to offline mode if needed"""
        wifi_enabled = self.config.get("wifi", {}).get("enabled", False)
        
        if not wifi_enabled:
            print("[WIFI] WiFi disabled - operating in offline mode")
            return False, "offline"
        
        if not self.wifi_manager:
            print("[WIFI] WiFi manager not available - operating in offline mode")
            return False, "offline"
        
        if not self.wifi_manager.initialized:
            print("[WIFI] WiFi manager failed to initialize - operating in offline mode")
            return False, "offline"
        
        # Try to connect with retry logic
        if self.auto_connect(max_attempts=3):
            print("[WIFI] Connected successfully")
            
            # Try to sync time
            ntp_server = self.config.get("wifi", {}).get("ntp_server", "pool.ntp.org")
            if self.sync_ntp_time(ntp_server):
                print("[WIFI] Time synchronized successfully")
                return True, "online"
            else:
                print("[WIFI] Connected but time sync failed - operating in online mode without time sync")
                return True, "online_no_time"
        else:
            print("[WIFI] Connection failed after 3 attempts - operating in offline mode")
            return False, "offline"
    
    def is_healthy(self):
        """Check if WiFi manager is healthy"""
        if not self.wifi_manager:
            return True  # WiFi is optional
        
        # Check if initialized and not too many errors
        return (self.wifi_manager.initialized and 
                self.wifi_manager.error_count < 10)