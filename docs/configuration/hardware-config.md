# hardware_config.py - Guia de Configuração de Hardware

Documentação completa do sistema de configuração de hardware do PicoWeather.

## 📋 **Visão Geral**

O `hardware_config.py` define perfis de hardware para diferentes tipos de placas e dispositivos. Ele permite:

- Suportar múltiplas placas de desenvolvimento
- Mapear pinos GPIO para nomes lógicos
- Definir características específicas de cada placa
- Facilitar portabilidade para novos hardwares
- Manter compatibilidade com configurações existentes

## 🏗️ **Estrutura do Arquivo**

```python
HARDWARE_CONFIGS = {
    "pico": { ... },
    "pico_clone": { ... },
    "pico_w": { ... },
    # Novas placas podem ser adicionadas aqui
}

def get_hardware_config(config_name="pico"):
    return HARDWARE_CONFIGS.get(config_name, HARDWARE_CONFIGS["pico"])
```

## 🔧 **Configurações de Hardware Disponíveis**

### **1. pico - Raspberry Pi Pico Padrão**

```python
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
}
```

**Características:**

- Display SSD1306 via I2C0
- Sensores via I2C1
- Sem WiFi integrado
- FM transmissor opcional via I2C1

### **2. pico_clone - RP2040 + ESP8285**

```python
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
}
```

**Características:**

- Display ST7567 via SPI1
- WiFi ESP8285 via UART0
- Sensores via I2C0
- FM transmissor via I2C1
- Pinos alternativos disponíveis

### **3. pico_w - Raspberry Pi Pico W**

```python
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
        "led": "LED"  # LED integrado do CYW43
    }
}
```

**Características:**

- Display SSD1306 via I2C0
- WiFi nativo CYW43
- Sensores via I2C1
- LED integrado especial

## 🎯 **Estrutura da Configuração**

### **Campos Obrigatórios**

| Campo | Tipo | Descrição |
| ------ | ------ | ----------- |
| `name` | string | Nome amigável da placa |
| `description` | string | Descrição detalhada |
| `features` | object | Características específicas |
| `pins` | object | Mapeamento de pinos GPIO |

### **Features - Características da Placa**

```python
"features": {
    "wifi_internal": False,    # WiFi nativo (CYW43)
    "wifi_esp8285": False,     # WiFi ESP8285 via UART
    "display_st7567": False,   # Display ST7567 via SPI
    "has_fm": False,          # Suporte a FM transmissor
    "has_ethernet": False,    # Suporte a Ethernet
    "has_can": False,         # Suporte a CAN bus
    "has_spi2": False,        # Segundo barramento SPI
    "has_uart1": False,       # Segunda UART
    "max_i2c_freq": 100000,   # Frequência máxima I2C
    "max_spi_freq": 2000000,  # Frequência máxima SPI
    "gpio_count": 28          # Número de GPIOs disponíveis
}
```

### **Pins - Mapeamento de GPIO**

#### **Interfaces Padrão**

```python
"pins": {
    # UART0
    "uart0_tx": 0,            # Transmissão UART0
    "uart0_rx": 1,            # Recepção UART0
    
    # I2C0
    "i2c0_sda": 4,            # Dados I2C0
    "i2c0_scl": 5,            # Clock I2C0
    
    # I2C1
    "i2c1_sda": 6,            # Dados I2C1
    "i2c1_scl": 7,            # Clock I2C1
    
    # SPI0
    "spi0_sck": 18,           # Clock SPI0
    "spi0_mosi": 19,          # Master Out SPI0
    "spi0_miso": 16,          # Master In SPI0
    "spi0_cs": 17,            # Chip Select SPI0
    
    # SPI1
    "spi1_sck": 14,           # Clock SPI1
    "spi1_mosi": 15,          # Master Out SPI1
    "spi1_miso": 12,          # Master In SPI1
    "spi1_cs": 13,            # Chip Select SPI1
    "spi1_dc": 11,            # Data/Command (display)
    "spi1_rst": 10,           # Reset (display)
    
    # Botões
    "button_up": 20,          # Botão para cima
    "button_down": 21,        # Botão para baixo
    "button_select": 22,      # Botão selecionar
    "button_back": 23,        # Botão voltar
    
    # Controle
    "led": 25,                # LED onboard
    "esp_enable": 24,         # Enable ESP8285
    
    # Especiais
    "vsys_monitor": 29,       # Monitor de VSYS
    "temp_sensor": "internal" # Sensor de temperatura
}
```

## 🚀 **Adicionando Novas Placas**

### **Exemplo: Pico 2**

```python
"pico2": {
    "name": "Raspberry Pi Pico 2",
    "description": "Raspberry Pi Pico 2 com RP2350 e melhorias",
    "features": {
        "wifi_internal": False,
        "wifi_esp8285": False,
        "has_dual_core": True,
        "has_coprocessor": True,
        "max_i2c_freq": 400000,
        "max_spi_freq": 4000000,
        "gpio_count": 48,
        "has_usb_host": True
    },
    "pins": {
        # Mantém compatibilidade com Pico 1
        "uart0_tx": 0,
        "uart0_rx": 1,
        "i2c0_sda": 4,
        "i2c0_scl": 5,
        "i2c1_sda": 6,
        "i2c1_scl": 7,
        
        # Novos pinos do Pico 2
        "i2c2_sda": 40,
        "i2c2_scl": 41,
        "spi2_sck": 42,
        "spi2_mosi": 43,
        "spi2_miso": 44,
        "spi2_cs": 45,
        
        # Botões adicionais
        "button_extra1": 46,
        "button_extra2": 47,
        
        # Controle
        "led": 25,
        "led_rgb": 26
    }
}
```

### **Exemplo: ESP32-S3**

```python
"esp32_s3": {
    "name": "ESP32-S3 Dev Board",
    "description": "ESP32-S3 com WiFi nativo e processador dual core",
    "features": {
        "wifi_internal": True,
        "wifi_esp8285": False,
        "has_bluetooth": True,
        "has_ethernet": True,
        "has_usb_otg": True,
        "has_touch": True,
        "max_i2c_freq": 1000000,
        "max_spi_freq": 80000000,
        "gpio_count": 48
    },
    "pins": {
        # I2C nativo do ESP32
        "i2c0_sda": 8,
        "i2c0_scl": 9,
        
        # SPI nativo VSPI
        "spi0_sck": 18,
        "spi0_mosi": 23,
        "spi0_miso": 19,
        "spi0_cs": 5,
        
        # Botões touch
        "button_up": 2,      # Touch 2
        "button_down": 12,   # Touch 3
        "button_select": 14, # Touch 6
        "button_back": 15,   # Touch 4
        
        # LED RGB
        "led_r": 21,
        "led_g": 22,
        "led_b": 23,
        
        # Controle
        "esp_enable": 4
    }
}
```

### **Exemplo: STM32F4**

```python
"stm32f4": {
    "name": "STM32F4 Discovery",
    "description": "STM32F407VG Discovery board",
    "features": {
        "wifi_internal": False,
        "wifi_esp8285": False,
        "has_ethernet": True,
        "has_usb_host": True,
        "has_can": True,
        "max_i2c_freq": 400000,
        "max_spi_freq": 42000000,
        "gpio_count": 100,
        "has_adc": True,
        "has_dac": True
    },
    "pins": {
        # I2C1 (PB6/PB7)
        "i2c0_sda": "PB6",
        "i2c0_scl": "PB7",
        
        # I2C2 (PB10/PB11)
        "i2c1_sda": "PB10",
        "i2c1_scl": "PB11",
        
        # SPI1 (PA5/PA6/PA7)
        "spi0_sck": "PA5",
        "spi0_miso": "PA6",
        "spi0_mosi": "PA7",
        "spi0_cs": "PA4",
        
        # Botões (usuário)
        "button_up": "PA0",
        "button_down": "PC13",
        
        # LED onboard
        "led": "PD12",
        "led_green": "PD13",
        "led_orange": "PD14",
        "led_red": "PD15",
        
        # ADC
        "adc_temp": "PA0",
        "adc_vref": "PA1"
    }
}
```

## 🔄 **Funções de Suporte**

### **get_hardware_config()**

```python
def get_hardware_config(config_name="pico"):
    """Obter configuração de hardware"""
    return HARDWARE_CONFIGS.get(config_name, HARDWARE_CONFIGS["pico"])
```

**Uso:**

```python
from drivers.hardware_config import get_hardware_config

# Obter configuração específica
hardware = get_hardware_config("pico_clone")

# Obter configuração padrão
hardware = get_hardware_config()

# Verificar features
if hardware["features"]["wifi_esp8285"]:
    print("Placa com ESP8285")

# Obter pino específico
sda_pin = hardware["pins"]["i2c0_sda"]
```

### **Funções Adicionais (Sugestão)**

```python
def get_supported_boards():
    """Retorna lista de placas suportadas"""
    return list(HARDWARE_CONFIGS.keys())

def get_board_features(board_name):
    """Retorna features de uma placa específica"""
    config = get_hardware_config(board_name)
    return config.get("features", {})

def get_board_pins(board_name):
    """Retorna mapeamento de pinos de uma placa"""
    config = get_hardware_config(board_name)
    return config.get("pins", {})

def validate_board_config(board_name):
    """Valida configuração de uma placa"""
    config = get_hardware_config(board_name)
    required_fields = ["name", "description", "features", "pins"]
    return all(field in config for field in required_fields)
```

## 🔍 **Validação e Debug**

### **Verificação de Configuração**

```python
# No console do PicoWeather:
pico> hardware
# Mostra configuração de hardware atual

pico> hardware pins
# Lista todos os pinos mapeados

pico> hardware features
# Mostra features da placa
```

### **Teste de Pinagem**

```python
# Testar se pinos estão disponíveis
from drivers.hardware_config import get_hardware_config

hardware = get_hardware_config()
pins = hardware["pins"]

# Verificar conflitos
pin_usage = {}
for name, pin in pins.items():
    if pin in pin_usage:
        print(f"Conflito: {name} e {pin_usage[pin]} usam GPIO {pin}")
    else:
        pin_usage[pin] = name
```

## 🛠️ **Boas Práticas**

### **Nomenclatura de Pinos**

- Use nomes descritivos: `i2c0_sda` em vez de `sda_pin`
- Mantenha consistência: `uart0_tx`, `uart0_rx`
- Inclua alternativos: `i2c0_alt_sda`, `i2c0_alt_scl`

### **Features da Placa**

- Seja específico: `wifi_esp8285: true` em vez de `wifi: true`
- Documente limitações: `max_i2c_freq: 100000`
- Inclua capacidades especiais: `has_touch: true`

### **Compatibilidade**

- Mantenha pinos básicos consistentes entre placas
- Forneça alternativas quando possível
- Documente diferenças importantes

## 📝 **Migração e Compatibilidade**

### **Mantendo Compatibilidade**

```python
# Configuração antiga (para compatibilidade)
"pico_old": {
    "name": "Pico (Legacy)",
    "description": "Configuração legada para compatibilidade",
    "features": {"wifi_internal": False},
    "pins": {
        "sda": 4,  # Nome antigo
        "scl": 5,  # Nome antigo
        # Mapeamento novo também disponível
        "i2c0_sda": 4,
        "i2c0_scl": 5
    }
}
```

### **Atualização de Configuração**

```python
def migrate_config(old_config):
    """Migra configuração antiga para novo formato"""
    new_config = old_config.copy()
    
    # Atualizar nomes de pinos
    pin_mapping = {
        "sda": "i2c0_sda",
        "scl": "i2c0_scl",
        "tx": "uart0_tx",
        "rx": "uart0_rx"
    }
    
    for old_name, new_name in pin_mapping.items():
        if old_name in new_config["pins"]:
            new_config["pins"][new_name] = new_config["pins"][old_name]
    
    return new_config
```

## 🎯 **Casos de Uso Avançados**

### **Placas com Múltiplas Configurações**

```python
"pico_multi": {
    "name": "Pico Multi-Config",
    "description": "Pico com múltiplas configurações possíveis",
    "variants": {
        "basic": {
            "features": {"wifi_internal": False},
            "pins": {"i2c0_sda": 4, "i2c0_scl": 5}
        },
        "wifi": {
            "features": {"wifi_internal": True},
            "pins": {"i2c0_sda": 4, "i2c0_scl": 5}
        },
        "advanced": {
            "features": {"wifi_internal": True, "has_ethernet": True},
            "pins": {"i2c0_sda": 4, "i2c0_scl": 5}
        }
    }
}
```

### **Configuração Dinâmica**

```python
def get_dynamic_config(board_name, variant=None):
    """Obtém configuração dinamicamente baseada em variantes"""
    base_config = get_hardware_config(board_name)
    
    if variant and "variants" in base_config:
        variant_config = base_config["variants"][variant]
        # Mesclar configuração base com variante
        merged_config = base_config.copy()
        merged_config["features"].update(variant_config["features"])
        merged_config["pins"].update(variant_config["pins"])
        return merged_config
    
    return base_config
```

---

## 📞 **Suporte**

Para problemas com hardware config:

- Use `pico> hardware` para verificar configuração
- Valide mapeamento de pinos antes de usar
- Consulte documentação específica da placa

---

**Guia válido para:** PicoWeather v2.0+  
**Última atualização:** 2024-12-25
