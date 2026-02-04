# Hardware Configuration for Raspberry Pi Pico
# Perfis organizados por tipo de placa somente

HARDWARE_CONFIGS = {
    "pico": {
        "name": "Raspberry Pi Pico Padrão",
        "description": "Configuração padrão para Raspberry Pi Pico",
        "features": {
            "wifi_internal": False,
            "wifi_esp8285": False
        },
        "pins": {
            # UART
            "uart0_tx": 0,
            "uart0_rx": 1,
            # I2C0 - Display SSD1306 (GP4, GP5)
            "i2c0_sda": 4,
            "i2c0_scl": 5,
            # I2C1 - Sensores (GP6, GP7) - SEM FM TRANSMITTER
            "i2c1_sda": 6,
            "i2c1_scl": 7,
            # Botões
            "button_up": 14,
            "button_down": 15,
            "button_select": 13,
            "button_back": 10,
            # Controle
            "led": 25
        }
    },
    "pico_clone": {
        "name": "Pico Clone com ESP8285",
        "description": "Clones do Pico com WiFi ESP8285 integrado via UART e display ST7567",
        "features": {
            "wifi_internal": False,
            "wifi_esp8285": True,
            "display_st7567": True
        },
        "pins": {
            # UART0 reservado para ESP8285 (GPIO 0/1)
            "uart0_tx": 0,
            "uart0_rx": 1,
            
            # I2C0 - Sensores (GP8, GP9)
            "i2c0_sda": 8,
            "i2c0_scl": 9,
            
            # I2C1 - Transmissor FM (GP6, GP7)
            "i2c1_sda": 6,
            "i2c1_scl": 7,
            
            # SPI para display ST7567 (usando GP14-18 para evitar conflitos)
            "spi1_sck": 14,
            "spi1_mosi": 15,
            "spi1_dc": 12,
            "spi1_cs": 13,
            "spi1_rst": 11,
            
            # I2C alternativos disponíveis
            "i2c0_alt_sda": 26,
            "i2c0_alt_scl": 27,
            "i2c1_alt_sda": 28,
            "i2c1_alt_scl": 29,
            
            # Botões
            "button_up": 21,
            "button_down": 20,
            "button_select": 19,
            "button_back": 18,
            
            # Controle
            "led": 25,
            
            # ESP8285 WiFi enable
            "esp_enable": 22
        }
    },
    "pico_w": {
        "name": "Raspberry Pi Pico W",
        "description": "Raspberry Pi Pico com WiFi interno (CYW43)",
        "features": {
            "wifi_internal": True,
            "wifi_esp8285": False
        },
        "pins": {
            # UART
            "uart0_tx": 0,
            "uart0_rx": 1,
            # I2C0 - Display
            "i2c0_sda": 4,
            "i2c0_scl": 5,
            # I2C1 - Sensores
            "i2c1_sda": 6,
            "i2c1_scl": 7,
            # Botões
            "button_up": 14,
            "button_down": 15,
            "button_select": 13,
            "button_back": 10,
            # Controle
            "led": "LED"
        }
    }
}

def get_hardware_config(config_name="pico"):
    """Obter configuração de hardware"""
    return HARDWARE_CONFIGS.get(config_name, HARDWARE_CONFIGS["pico"])