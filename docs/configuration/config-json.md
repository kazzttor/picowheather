# config.json - Guia de Configuração Principal

Documentação completa do arquivo de configuração principal do PicoWeather.

## 📋 Visão Geral

O `config.json` é o arquivo central de configuração do sistema PicoWeather. Ele define:

- Tipo de hardware e placa utilizada
- Configurações de display e interfaces
- Dispositivos e seus parâmetros
- Configurações de rede e WiFi
- Botões e entrada do usuário
- Configurações de tempo e localização
- Opções do sistema e debugging

## 🏗️ Estrutura do Arquivo

```json
{
  "hardware": { ... },
  "display": { ... },
  "i2c_buses": { ... },
  "devices": { ... },
  "wifi": { ... },
  "buttons": { ... },
  "time": { ... },
  "system": { ... }
}
```

## 🔧 Configuração Detalhada

### 1. hardware - Configuração da Placa

Define o tipo de placa e configurações de hardware básicas.

```json
"hardware": {
  "board": "pico_clone",           // Tipo da placa
  "scan_i2c_on_start": true,       // Scan I2C ao iniciar
  "auto_detect_devices": true      // Detecção automática
}
```

#### Tipos de Placa Suportados

| Placa | Valor em config.json | Características |
| --- | --- | --- |
| Pico Padrão | `"pico_standard"` | SSD1306, sem WiFi |
| Pico W | `"pico_w"` | SSD1306, WiFi nativo |
| Pico Clone | `"pico_clone"` | ST7567, ESP8285, FM |

#### Opções de Hardware

- **board**: Identificação da placa (obrigatório)
- **scan_i2c_on_start**: `true/false` - Escanear barramentos I2C na inicialização
- **auto_detect_devices**: `true/false` - Tentar detectar dispositivos automaticamente

### 2. display - Configuração do Display

Define o tipo de display e suas configurações de interface.

#### Display SSD1306 (I2C)

```json
"display": {
  "type": "ssd1306_i2c",
  "i2c_bus": 0,
  "width": 128,
  "height": 64,
  "address": 60,                   // 0x3C em decimal
  "pins": {
    "sda": "i2c0_sda",
    "scl": "i2c0_scl"
  }
}
```

#### Display ST7567 (SPI)

```json
"display": {
  "type": "st7567_spi",
  "spi_bus": 1,
  "spi_settings": {
    "baudrate": 200000,
    "polarity": 1,
    "phase": 1
  },
  "contrast": 31,
  "flip_x": false,
  "flip_y": true,
  "width": 128,
  "height": 64,
  "max_chars": 16,
  "pins": {
    "sck": "spi1_sck",
    "mosi": "spi1_mosi",
    "dc": "spi1_dc",
    "cs": "spi1_cs",
    "rst": "spi1_rst"
  }
}
```

#### Parâmetros do Display

- **type**: Tipo do display (`ssd1306_i2c`, `st7567_spi`)
- **width/height**: Resolução do display (geralmente 128x64)
- **address**: Endereço I2C (para displays I2C)
- **contrast**: Nível de contraste (0-63 para ST7567)
- **flip_x/flip_y**: Inversão horizontal/vertical
- **max_chars**: Máximo de caracteres por linha

### 3. i2c_buses - Configuração dos Barramentos I2C

Define múltiplos barramentos I2C e seus parâmetros.

```json
"i2c_buses": {
  "i2c0": {
    "enabled": true,
    "frequency": 100000,
    "devices": ["sensors"],
    "pins": {
      "sda": "i2c0_sda",
      "scl": "i2c0_scl"
    }
  },
  "i2c1": {
    "enabled": true,
    "frequency": 50000,
    "devices": ["controllers"],
    "pins": {
      "sda": "i2c1_sda",
      "scl": "i2c1_scl"
    }
  }
}
```

#### Parâmetros do Barramento

- **enabled**: `true/false` - Habilitar barramento
- **frequency**: Frequência em Hz (100000 padrão, 50000 para dispositivos sensíveis)
- **devices**: Lista de tipos de dispositivos no barramento
- **pins**: Mapeamento de pinos SDA/SCL

### 4. devices - Configuração de Dispositivos

Define todos os dispositivos conectados e seus parâmetros.

#### Sensores

```json
"devices": {
  "sensors": {
    "enabled": true,
    "i2c_bus": 0,
    "aht20": {
      "enabled": true,
      "address": 56                  // 0x38 em decimal
    },
    "bmp280": {
      "enabled": true,
      "address": 119                 // 0x77 em decimal
    }
  }
}
```

#### Controladores (FM Transmissor)

```json
"devices": {
  "controllers": {
    "enabled": true,
    "i2c_bus": 1,
    "fm_transmitter": {
      "enabled": true,
      "address": 62,                 // 0x3E em decimal
      "default_frequency": 100.5,
      "default_volume": 7,
      "rds": {
        "enabled": true,
        "station_name": "PicoWeather",
        "program_type": "Weather",
        "text": "Temp: 26.5°C Umid: 65%",
        "repeat_text": true,
        "text_repeat_interval": 30
      }
    }
  }
}
```

#### Endereços I2C Comuns

| Dispositivo | Endereço Hex | Decimal |
| --- | --- | --- |
| SSD1306 | 0x3C / 0x3D | 60 / 61 |
| AHT20 | 0x38 | 56 |
| BMP280 | 0x76 / 0x77 | 118 / 119 |
| QN8027 | 0x3E | 62 |

### 5. wifi - Configuração de Rede

Define as configurações de WiFi e rede.

#### WiFi Pico W (Nativo)

```json
"wifi": {
  "enabled": true,
  "type": "cyw43",
  "networks": [
    {
      "ssid": "SUA_REDE",
      "password": "SUA_SENHA",
      "priority": 1
    }
  ],
  "ntp_server": "pool.ntp.br",
  "timezone": -3
}
```

#### WiFi ESP8285 (UART)

```json
"wifi": {
  "enabled": true,
  "type": "esp8285",
  "uart_bus": 0,
  "pins": {
    "tx": "uart0_tx",
    "rx": "uart0_rx",
    "enable": "esp_enable"
  },
  "networks": [
    {
      "ssid": "SUA_REDE",
      "password": "SUA_SENHA",
      "priority": 1
    }
  ],
  "ntp_server": "pool.ntp.br",
  "timezone": -3
}
```

#### Parâmetros WiFi

- **enabled**: `true/false` - Habilitar WiFi
- **type**: Tipo de WiFi (`cyw43`, `esp8285`)
- **networks**: Lista de redes com prioridade
- **ntp_server**: Servidor NTP para sincronização
- **timezone**: Fuso horário em horas (ex: -3 para Brasil)

### 6. buttons - Configuração de Botões

Define os botões de entrada do usuário.

```json
"buttons": {
  "enabled": true,
  "debounce_ms": 50,
  "long_press_ms": 2000,
  "pins": {
    "up": "button_up",
    "down": "button_down",
    "select": "button_select",
    "back": "button_back"
  }
}
```

#### Parâmetros dos Botões

- **enabled**: `true/false` - Habilitar sistema de botões
- **debounce_ms**: Tempo de debounce em milissegundos
- **long_press_ms**: Tempo para pressionamento longo
- **pins**: Mapeamento de botões para pinos GPIO

### 7. time - Configuração de Tempo

Define as configurações de tempo e sincronização.

```json
"time": {
  "auto_sync": true,
  "timezone": -3,
  "manual_hour": 12,
  "manual_minute": 0,
  "manual_day": 1,
  "manual_month": 1,
  "manual_year": 2024
}
```

#### Parâmetros de Tempo

- **auto_sync**: `true/false` - Sincronização automática via NTP
- **timezone**: Fuso horário em horas
- **manual_***: Valores manuais para quando auto_sync=false

### 8. system - Configurações do Sistema

Define opções gerais do sistema.

```json
"system": {
  "locale": "pt_BR",
  "enable_console": true,
  "enable_diagnostic": true,
  "log_level": "INFO"
}
```

#### Parâmetros do Sistema

- **locale**: Código do idioma (`pt_BR`, `en_US`)
- **enable_console**: `true/false` - Habilitar console interativo
- **enable_diagnostic**: `true/false` - Habilitar modo diagnóstico
- **log_level**: Nível de log (`DEBUG`, `INFO`, `ERROR`)

## 🎯 Configurações Pré-definidas

### Configuração Mínima (Pico Padrão)

```json
{
  "hardware": {"board": "pico_standard"},
  "display": {
    "type": "ssd1306_i2c",
    "i2c_bus": 0,
    "address": 60
  },
  "devices": {
    "sensors": {
      "enabled": true,
      "i2c_bus": 1,
      "aht20": {"enabled": true, "address": 56},
      "bmp280": {"enabled": true, "address": 119}
    }
  },
  "system": {"locale": "pt_BR"}
}
```

### Configuração Completa (Pico Clone)

```json
{
  "hardware": {"board": "pico_clone"},
  "display": {
    "type": "st7567_spi",
    "spi_bus": 1,
    "contrast": 31
  },
  "i2c_buses": {
    "i2c0": {"enabled": true, "frequency": 100000},
    "i2c1": {"enabled": true, "frequency": 50000}
  },
  "devices": {
    "sensors": {"enabled": true, "i2c_bus": 0},
    "controllers": {"enabled": true, "i2c_bus": 1}
  },
  "wifi": {"enabled": true, "type": "esp8285"},
  "buttons": {"enabled": true},
  "system": {"locale": "pt_BR"}
}
```

## 🔍 Validação e Debug

### Verificação de Configuração

```python
# No console do PicoWeather:
pico> config
# Mostra configuração atual e valida

pico> diagnostic
# Testa todos os dispositivos conforme config
```

### Erros Comuns

#### Endereço I2C Incorreto

```json
// ERRADO:
"address": 56  // Para SSD1306 (deveria ser 60)

// CORRETO:
"address": 60  // 0x3C para SSD1306
```

#### Pino Não Mapeado

```json
// ERRADO:
"pins": {"sda": "gp4"}  // Pino não existe no hardware

// CORRETO:
"pins": {"sda": "i2c0_sda"}  // Usa mapeamento do hardware
```

#### Barramento I2C Inexistente

```json
// ERRADO:
"i2c_bus": 2  // Só existem i2c0 e i2c1

// CORRETO:
"i2c_bus": 0  // ou 1
```

## 🛠️ Personalização Avançada

### Múltiplas Redes WiFi

```json
"wifi": {
  "networks": [
    {"ssid": "Casa", "password": "senha1", "priority": 1},
    {"ssid": "Trabalho", "password": "senha2", "priority": 2},
    {"ssid": "Mobile", "password": "senha3", "priority": 3}
  ]
}
```

### RDS FM Personalizado

```json
"fm_transmitter": {
  "rds": {
    "station_name": "WeatherStation",
    "program_type": "Info",
    "text": "Temp: {temp}°C Umid: {hum}%",
    "repeat_text": true,
    "text_repeat_interval": 45
  }
}
```

### Display Customizado

```json
"display": {
  "contrast": 40,
  "flip_x": true,
  "flip_y": false,
  "max_chars": 20
}
```

## 📝 Dicas de Boas Práticas

1. **Use Configurações Pré-definidas**: Comece com `config_pico_*.json`
2. **Valide Endereços I2C**: Use `pico> scan` antes de configurar
3. **Teste Incrementalmente**: Habilite dispositivos um por vez
4. **Backup Configuração**: Mantenha cópia do config.json funcional
5. **Documente Mudanças**: Anote alterações para referência futura

## 🔄 Atualização de Configuração

### Método 1: Editar Arquivo

1. Edite `config.json` no computador
2. Faça upload para o Pico
3. Reinicie o sistema

### Método 2: Console

```python
# No console PicoWeather:
pico> config
# Edite valores conforme necessário
pico> save
# Salva configuração atual
```

### Método 3: Runtime

```python
# Programaticamente:
import json
with open('config.json', 'r') as f:
    config = json.load(f)

config['display']['contrast'] = 35

with open('config.json', 'w') as f:
    json.dump(config, f)
```

---

## 📞 Suporte

Para problemas com configuração:

- Use `pico> diagnostic` para validar
- Verifique [solução de problemas](../../README.md#solução-de-problemas)
- Consulte guias específicos de hardware em `docs/guides/`

---

**Guia válido para:** PicoWeather v2.0+  
**Última atualização:** 2024-12-25
