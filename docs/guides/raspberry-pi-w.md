# Raspberry Pi Pico W - Guia de Instalação

Guia completo para instalação do PicoWeather em Raspberry Pi Pico W com WiFi nativo.

## 🎯 **Visão Geral**

### **Configuração**

- **Placa**: Raspberry Pi Pico W
- **Display**: SSD1306 OLED 128x64 (I2C)
- **Sensores**: AHT20, BMP280 (I2C)
- **WiFi**: Nativo CYW43
- **FM Transmissor**: Opcional (I2C)
- **Botões**: Opcionais (GPIO)

### **Características**

- WiFi integrado de alta performance
- Baixo consumo de energia
- Conexão estável 2.4GHz
- Sincronização NTP automática
- Ideal para aplicações conectadas

## 🛒 **Lista de Materiais**

### **Componentes Essenciais**

| Componente | Especificação | Quantidade |
| --- | --- | --- |
| Raspberry Pi Pico W | RP2040 + CYW43 WiFi | 1 |
| Display OLED | SSD1306, 128x64, I2C | 1 |
| Sensor Temp/Umidade | AHT20, I2C | 1 |
| Sensor Pressão | BMP280, I2C | 1 |
| Protoboard | 400 pontos ou maior | 1 |
| Jumper Wires | Fêmea-fêmea | ~20 |

### **Componentes Opcionais**

| Componente | Especificação | Quantidade |
| --- | --- | --- |
| FM Transmissor | QN8027, I2C | 1 |
| Botões táteis | 12mm, 6V | 4 |
| Resistores | 10kΩ (pull-up) | 4 |
| Antena WiFi | 2.4GHz (opcional) | 1 |
| Caixa de projeto | Para montagem | 1 |

## 🔌 **Diagrama de Conexões**

### **Pinagem Raspberry Pi Pico W**

```text
        USB
   +---+---+---+
   |   |   |   |
 3V3-| 1 | 2 |-GND
 GP0-| 3 | 4 |-GP5 (I2C0_SCL)
 GP1-| 5 | 6 |-GP4 (I2C0_SDA)
 GND-| 7 | 8 |-GP7 (I2C1_SCL)
 GP2-| 9 |10 |-GP6 (I2C1_SDA)
 GP3-|11 |12 |-GP10 (BACK)
 GP4-|13 |14 |-GP13 (SELECT)
 GND-|15 |16 |-GP14 (UP)
 GP5-|17 |18 |-GP15 (DOWN)
 GP6-|19 |20 |-LED (WL_GPIO)
 GP7-|21 |22 |-GP8
 GP8-|23 |24 |-GP9
 GND-|25 |26 |-GP11
 GP9-|27 |28 |-GP12
 GP10-|29 |30 |-GP13
 GP11-|31 |32 |-GP14
 GND-|33 |34 |-GND
 GP12-|35 |36 |-GP15
 GP13-|37 |38 |-GP16
 GND-|39 |40 |-GP17
   +---+---+---+
```

### **Conexões Essenciais**

#### **Display SSD1306 (I2C0)**

```text
Display SSD1306    →    Raspberry Pi Pico W
VCC (3.3V)         →    3V3 (Pin 36)
GND                →    GND (Pin 38)
SDA                →    GP4 (Pin 6)
SCL                →    GP5 (Pin 4)
```

#### **Sensores (I2C1)**

```text
AHT20/BMP280       →    Raspberry Pi Pico W
VCC (3.3V)         →    3V3 (Pin 36)
GND                →    GND (Pin 38)
SDA                →    GP6 (Pin 10)
SCL                →    GP7 (Pin 8)
```

#### **Botões (Opcional)**

```text
Botão              →    Raspberry Pi Pico W
UP                 →    GP14 (Pin 16) + 3V3
DOWN               →    GP15 (Pin 18) + 3V3
SELECT             →    GP13 (Pin 14) + 3V3
BACK               →    GP10 (Pin 12) + 3V3
```

#### **FM Transmissor (Opcional)**

```text
QN8027             →    Raspberry Pi Pico W
VCC (3.3V)         →    3V3 (Pin 36)
GND                →    GND (Pin 38)
SDA                →    GP6 (Pin 10) - compartilhado
SCL                →    GP7 (Pin 8) - compartilhado
```

## ⚙️ **Configuração do Software**

### **1. Preparar o MicroPython**

```bash
# Baixar MicroPython para Raspberry Pi Pico W
# Visite: https://micropython.org/download/rp2-pico-w/
# Baixe o arquivo .uf2 mais recente com suporte WiFi

# Procedimento de instalação:
# 1. Conecte o Pico W ao computador mantendo BOOTSEL pressionado
# 2. Arraste o arquivo .uf2 para o drive RPI-RP2
# 3. O Pico W reiniciará com MicroPython + WiFi
```

### **2. Upload dos Arquivos do Projeto**

```bash
# Usando Thonny IDE:
# 1. Abra Thonny e conecte-se ao Pico W
# 2. Vá em File → Upload
# 3. Selecione todos os arquivos do projeto
# 4. Mantenha a estrutura de diretórios
```

### **3. Configurar o Sistema**

#### **Criar config.json para Pico W**

```json
{
  "hardware": {
    "board": "pico_w",
    "scan_i2c_on_start": true,
    "auto_detect_devices": true
  },
  "display": {
    "type": "ssd1306_i2c",
    "i2c_bus": 0,
    "width": 128,
    "height": 64,
    "address": 60,
    "pins": {
      "sda": "i2c0_sda",
      "scl": "i2c0_scl"
    }
  },
  "i2c_buses": {
    "i2c0": {
      "enabled": true,
      "frequency": 100000,
      "pins": {
        "sda": "i2c0_sda",
        "scl": "i2c0_scl"
      }
    },
    "i2c1": {
      "enabled": true,
      "frequency": 100000,
      "pins": {
        "sda": "i2c1_sda",
        "scl": "i2c1_scl"
      }
    }
  },
  "devices": {
    "sensors": {
      "enabled": true,
      "i2c_bus": 1,
      "aht20": {
        "enabled": true,
        "address": 56
      },
      "bmp280": {
        "enabled": true,
        "address": 119
      }
    }
  },
  "wifi": {
    "enabled": true,
    "type": "cyw43",
    "networks": [
      {
        "ssid": "SUA_REDE_WIFI",
        "password": "SUA_SENHA",
        "priority": 1
      }
    ],
    "ntp_server": "pool.ntp.br",
    "timezone": -3
  },
  "buttons": {
    "enabled": true,
    "pins": {
      "up": "button_up",
      "down": "button_down",
      "select": "button_select",
      "back": "button_back"
    }
  },
  "time": {
    "auto_sync": true,
    "timezone": -3
  },
  "system": {
    "locale": "pt_BR",
    "enable_console": true,
    "enable_diagnostic": true
  }
}
```

## 🚀 **Procedimento de Instalação**

### **Passo 1: Montagem do Hardware**

1. **Montagem na Protoboard**
   - Insira o Raspberry Pi Pico W na protoboard
   - Cuidado com a antena WiFi integrada

2. **Conectar Display**
   - Conecte o SSD1306 usando jumpers
   - Verifique conexões VCC e GND
   - Confirme SDA em GP4 e SCL em GP5

3. **Conectar Sensores**
   - Conecte AHT20 e BMP280 no I2C1
   - Use GP6 para SDA e GP7 para SCL
   - Verifique alimentação 3.3V

4. **Conectar Botões (Opcional)**
   - Conecte botões com resistores pull-up
   - Use GPIOs conforme pinagem

### **Passo 2: Instalação do Software**

1. **Instalar MicroPython**
   - Use arquivo específico para Pico W
   - Verifique suporte WiFi no boot

2. **Upload do Projeto**
   - Copie todos os arquivos
   - Mantenha estrutura de diretórios

3. **Configuração WiFi**
   - Crie config.json com configuração WiFi
   - Insira suas credenciais de rede

### **Passo 3: Teste e Validação**

1. **Teste Básico**

   ```python
   # No console MicroPython:
   import main
   ```

2. **Verificar Hardware**

   ```python
   # Entrar no modo console (Ctrl+C)
   pico> scan
   pico> diagnostic
   ```

3. **Testar WiFi**

   ```python
   pico> wifi status
   # Deve mostrar "Connected" e endereço IP
   ```

4. **Testar Sincronização NTP**

   ```python
   pico> time
   # Deve mostrar hora atualizada
   ```

## 🔧 **Solução de Problemas**

### **⚠️ Verificação de Barramento I2C (Importante!)**

```python
# Scan completo do barramento I2C
pico> scan
# Saída esperada para esta configuração:
# I2C0 (GP4/GP5): [0x3C] - Display SSD1306
# I2C1 (GP6/GP7): [0x38, 0x77] - AHT20, BMP280

# Verificar conflitos antes de conectar dispositivos
```

### **WiFi Não Conecta**

```python
# Verificar status do WiFi
pico> wifi status

# Verificar configuração
pico> config
# Confirmar wifi.enabled = true

# Testar conexão manual
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('SUA_REDE', 'SUA_SENHA')
print(wlan.isconnected())
print(wlan.ifconfig())
```

### **Problemas com NTP**

```python
# Verificar sincronização de tempo
pico> time

# Forçar sincronização manual
pico> settime 2024 12 25 14 30 00

# Verificar servidor NTP
pico> config
# Confirmar ntp_server = "pool.ntp.br"
```

### **Display Não Liga**

```python
# Verificar conexões I2C
pico> scan
# Deve mostrar endereço 0x3C para SSD1306

# Testar diferentes endereços
# Edite config.json se display estiver em 0x3D:
"display": {
  "address": 61  # 0x3D em decimal
}
```

### **Sensores Não Detectados**

```python
# Verificar endereços I2C
pico> scan
# AHT20: 0x38, BMP280: 0x77 ou 0x76

# Se BMP280 não aparecer:
# Tente endereço alternativo no config.json:
"bmp280": {
  "address": 118  # 0x76 em decimal
}
```

## 📊 **Performance e Limitações**

### **Recursos Utilizados**

- **RAM**: ~60KB de 264KB disponível (WiFi consome mais)
- **Flash**: ~250KB de 2MB disponível
- **CPU**: ~30% de utilização (WiFi ativo)
- **Energia**: ~80mA sem display, ~120mA com display + WiFi

### **Limitações**

- WiFi consome mais energia
- Requer configuração de rede
- Menos GPIOs disponíveis (alguns usados pelo WiFi)
- Memória reduzida pelo stack WiFi

### **Vantagens**

- Conectividade nativa estável
- Sincronização NTP automática
- Atualizações remotas possíveis
- Logging via rede

## 🔄 **Manutenção**

### **Atualizações**

```bash
# Para atualizar o sistema:
# 1. Faça backup do config.json
# 2. Substitua arquivos do projeto
# 3. Restaure config.json
# 4. Teste funcionamento
# 5. Verifique conexão WiFi
```

### **Monitoramento WiFi**

```python
# Verificar qualidade do sinal
pico> wifi status
# Observe RSSI para qualidade do sinal

# Configurar redes backup
# Adicione múltiplas redes no config.json:
"networks": [
  {"ssid": "Rede1", "password": "senha1", "priority": 1},
  {"ssid": "Rede2", "password": "senha2", "priority": 2}
]
```

## 🎯 **Próximos Passos**

### **Expansões Possíveis**

- Servidor web para configuração remota
- MQTT para IoT
- Upload de dados para nuvem
- Notificações via rede

### **Melhorias**

- Otimização de consumo WiFi
- Modo deep sleep
- Reconexão automática
- Cache de dados offline

## 🌐 **Configurações WiFi Avançadas**

### **Múltiplas Redes**

```json
"wifi": {
  "networks": [
    {
      "ssid": "Casa",
      "password": "senha_casa",
      "priority": 1
    },
    {
      "ssid": "Trabalho",
      "password": "senha_trabalho",
      "priority": 2
    }
  ]
}
```

### **Configurações de Segurança**

```json
"wifi": {
  "security": {
    "use_wpa3": false,
    "hide_ssid": false,
    "ap_mode": false
  }
}
```

---

## 📞 **Suporte**

Para problemas específicos desta configuração:

- Verifique [solução de problemas](../../README.md#solução-de-problemas)
- Consulte [console commands](../../README.md#comandos-do-console)
- Abra uma Issue no GitHub descrevendo seu hardware

---

**Guia válido para:** PicoWeather v2.0+  
**Última atualização:** 2024-12-25
