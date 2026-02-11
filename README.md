# PicoWeather - Sistema de Monitoramento Meteorológico Completo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Raspberry Pi Pico](https://img.shields.io/badge/Platform-Raspberry%20Pi%20Pico-brightgreen)](https://www.raspberrypi.org/products/raspberry-pi-pico/)
[![Language: MicroPython](https://img.shields.io/badge/Language-MicroPython-blue)](https://micropython.org/)

Sistema completo de monitoramento meteorológico para Raspberry Pi Pico com display LCD, sensores ambientais, transmissor FM, WiFi e localização completa em português brasileiro.

## 🌟 Funcionalidades Principais

### 📊 **Sensores Ambientais**

- **Temperatura**: Sensor AHT20 para alta precisão
- **Umidade**: Medição simultânea com AHT20
- **Pressão**: Barômetro BMP280 com compensação de altitude
- **Atualização contínua**: Leituras a cada 2 segundos

### 📺 **Displays Suportados**

- **ST7567 SPI**: Display LCD 128x64 monocromático (via SPI)
- **SSD1306 I2C**: Display OLED 128x64 monocromático (via I2C)
- **Fonte customizada**: Suporte completo para caracteres português (ç, ã, é, etc.)
- **Layout configurável**: Sistema de telas via JSON

### 📻 **Transmissor FM (Opcional)**

- **QN8027**: Faixa completa 88-108 MHz
- **Controle de volume**: 16 níveis de áudio
- **Modo estéreo/mono**: Configurável via console
- **RDS**: Informações de estação e texto dinâmico

### 🌐 **Conectividade WiFi**

- **ESP8285**: Para clones Pico com WiFi integrado
- **Pico W nativo**: WiFi interno CYW43
- **Sincronização NTP**: Hora automática via pool.ntp.br
- **Status em tempo real**: Monitoramento de conexão

### 🎮 **Interface Intuitiva**

- **4 botões**: Navegação completa (Cima, Baixo, Selecionar, Voltar)
- **Console interativo**: Sistema completo de comandos
- **Mensagens em português**: Interface 100% localizada
- **Formatação brasileira**: Data DD/MM/YYYY, números com vírgula decimal

## 🏗️ **Placas Suportadas**

### **1. Raspberry Pi Pico Padrão**

- **Display**: SSD1306 via I2C
- **Sensores**: AHT20, BMP280 via I2C
- **WiFi**: Não disponível
- **FM Transmissor**: Opcional via I2C

### **2. Raspberry Pi Pico W**

- **Display**: SSD1306 via I2C
- **Sensores**: AHT20, BMP280 via I2C
- **WiFi**: Nativo CYW43
- **FM Transmissor**: Opcional via I2C

### **3. RP2040 + ESP8285 (Clones Pico W)**

- **Display**: ST7567 via SPI
- **Sensores**: AHT20, BMP280 via I2C
- **WiFi**: ESP8285 via UART
- **FM Transmissor**: QN8027 via I2C
- **⚠️ Requer firmware dual especial** - Veja [guia de instalação](docs/guides/rp2040-esp8285.md)

#### **⚠️ AVISO IMPORTANTE - Clones vs Pico W Genuíno**

Muitos vendedores (TZT, etc.) vendem clones de Pico W que usam ESP8285 em vez do chip CYW43. **Estes clones NÃO usam o firmware padrão do Pico W** e requerem procedimento de instalação especial. Veja [guia detalhado](docs/guides/rp2040-esp8285.md) para instalação correta dos firmwares dual.

## 🔌 **Pinagens por Placa**

### **Raspberry Pi Pico Padrão (com SSD1306)**

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
 GP6-|19 |20 |-GP25 (LED)
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

**Conexões:**

- **Display SSD1306**: GP4 (SDA), GP5 (SCL), 3V3, GND
- **Sensores**: GP6 (SDA), GP7 (SCL), 3V3, GND
- **Botões**: GP10 (Back), GP13 (Select), GP14 (Up), GP15 (Down)
- **LED**: GP25

### **RP2040 + ESP8285 (Pico Clone Barato)**

```text
        USB
   +---+---+---+
   |   |   |   |
 3V3-| 1 | 2 |-GND
 GP0-| 3 | 4 |-ESP_TX (UART0_RX)
 GP1-| 5 | 6 |-ESP_RX (UART0_TX)
 GND-| 7 | 8 |-GP7 (I2C1_SCL)
 GP2-| 9 |10 |-GP6 (I2C1_SDA)
 GP3-|11 |12 |-ESP_EN
 GP4-|13 |14 |-GP11 (RST)
 GND-|15 |16 |-GP12 (DC)
 GP5-|17 |18 |-GP13 (CS)
 GP6-|19 |20 |-GP14 (SCK)
 GP7-|21 |22 |-GP15 (MOSI)
 GND-|23 |24 |-GP18 (BACK)
 GP8-|25 |26 |-GP19 (SELECT)
 GP9-|27 |28 |-GP20 (DOWN)
 GP10-|29 |30 |-GP21 (UP)
 GND-|31 |32 |-GP22 (ESP_EN)
 GP11-|33 |34 |-GP25 (LED)
 GP12-|35 |36 |-GP8 (I2C0_SDA)
 GND-|37 |38 |-GP9 (I2C0_SCL)
 GP13-|39 |40 |-GND
   +---+---+---+
```

**Conexões:**

- **Display ST7567**: GP14 (SCK), GP15 (MOSI), GP12 (DC), GP13 (CS), GP11 (RST)
- **Sensores**: GP8 (SDA), GP9 (SCL), 3V3, GND
- **FM Transmissor**: GP6 (SDA), GP7 (SCL), 3V3, GND
- **ESP8285 WiFi**: GP0 (TX), GP1 (RX), GP22 (EN), 3V3, GND
- **Botões**: GP18 (Back), GP19 (Select), GP20 (Down), GP21 (Up)

## ⚙️ **Sistema de Configuração**

### **Arquivos de Configuração**

O sistema utiliza arquivos JSON para configuração completa:

#### **config.json** - Configuração principal do sistema

```json
{
  "hardware": {
    "board": "pico_clone",
    "scan_i2c_on_start": true
  },
  "display": {
    "type": "st7567_spi",
    "width": 128,
    "height": 64,
    "contrast": 31
  },
  "wifi": {
    "enabled": true,
    "ssid": "SUA_REDE",
    "password": "SUA_SENHA",
    "ntp_server": "pool.ntp.br",
    "timezone": -3
  },
  "system": {
    "locale": "pt_BR",
    "enable_console": true
  }
}
```

#### **display_layouts.json** - Layout das telas

```json
{
  "st7567_spi": {
    "pages": [
      {
        "name": "complete",
        "duration": 1000,
        "elements": [
          {"type": "date", "x": "center", "y": 0},
          {"type": "time", "x": "center", "y": 10},
          {"type": "sensor", "name": "temperature", "x": "center", "y": 22, "label": "Temp:", "unit": "C"},
          {"type": "sensor", "name": "humidity", "x": "center", "y": 32, "label": "Umid:", "unit": "%"},
          {"type": "sensor", "name": "pressure", "x": "center", "y": 42, "label": "Pres:", "unit": "hPa"}
        ]
      }
    ]
  }
}
```

### **Configurações Pré-definidas**

- **config_pico_standard.json**: Para Pico padrão com SSD1306
- **config_pico_clone.json**: Para clones com ESP8285 e ST7567

## 🚀 **Instalação e Configuração**

### **Hardware Requerido**

#### **Configuração Mínima (Pico Padrão)**

- Raspberry Pi Pico
- Display SSD1306 128x64 (I2C)
- Sensor AHT20 (temperatura/umidade)
- Sensor BMP280 (pressão)
- Fiação e conectores

#### **Configuração Completa (Pico Clone)**

- RP2040 + ESP8285 (Pico W barato)
- Display ST7567 128x64 (SPI)
- Sensor AHT20 (temperatura/umidade)
- Sensor BMP280 (pressão)
- Transmissor FM QN8027
- 4 botões táteis
- Fiação e conectores

### **Software Requerido**

- MicroPython para Raspberry Pi Pico
- Thonny IDE (recomendado)
- Bibliotecas incluídas no projeto

### **Passos de Instalação**

1. **Download do projeto**

   ```bash
   git clone https://github.com/kazzttor/picowheather.git
   cd picowheather
   ```

2. **Escolha da configuração**
   - Copie `config_pico_standard.json` → `config.json` (para Pico padrão)
   - Copie `config_pico_clone.json` → `config.json` (para clones com ESP8285)

3. **Upload para Pico**
   - Abra Thonny IDE
   - Conecte o Pico via USB
   - Copie todos os arquivos para o Pico
   - Mantenha a estrutura de diretórios

4. **Configuração**
   - Edite `config.json` para seu hardware
   - Configure WiFi (SSID, senha)
   - Ajuste pinos conforme sua montagem

5. **Execução**

   ```python
   # No console MicroPython
   import main
   # Ou resete o Pico para iniciar automaticamente
   ```

## 📋 **Comandos do Console**

O sistema possui um console interativo completo:

```python
pico> help
=== Menu Console PicoWeather ===
--- Comandos de Sensores ---
  help         - Voltar ao menu principal
  status       - Mostrar status do display
  sensors      - Ler todos os sensores
  scan         - Scan I2C buses for devices

--- Comandos de Display ---
  time         - Mostrar hora atual
  settime      - Set time manually
  adjust       - Adjust time (+/-30m, +1h, -1d)

--- Comandos de Rádio ---
  fm           - Mostrar informações do rádio

--- Comandos de Rede ---
  wifi         - Status WiFi

--- Comandos de Sistema ---
  diagnostic   - Executar diagnósticos completos
  config       - Mostrar configuração
  save         - Salvar configuração atual
  Sair do console or quit    - Sair do console
```

### **Comandos Úteis**

```python
pico> sensors              # Ver leituras atuais
pico> wifi status          # Status da conexão
pico> fm status           # Informações do rádio
pico> time                # Hora e data atual
pico> settime 2024 12 25 14 30  # Definir hora manualmente
pico> diagnostic          # Testar hardware completo
```

## 📁 **Estrutura de Diretórios**

```text
├── main.py                 # Ponto de entrada principal
├── config.json            # Configuração do sistema
├── display_layouts.json   # Layout das telas
├── locales/              # Arquivos de localização
│   ├── display_pt_BR.json
│   └── console_pt_BR.json
├── drivers/              # Drivers de hardware
│   ├── sensors_driver.py
│   ├── display_driver.py
│   ├── time_driver.py
│   ├── controller_driver.py
│   └── hardware_config.py
├── lib/                  # Bibliotecas de sensores
│   ├── aht20.py
│   ├── bmp280.py
│   ├── st7567.py
│   ├── ssd1306.py
│   └── display_manager.py
└── utils/                # Utilitários do sistema
    ├── locale_manager.py  # Sistema de localização
    ├── custom_font.py    # Fonte portuguesa
    ├── console.py        # Console interativo
    └── diagnostic.py     # Ferramentas de diagnóstico
```

## 🔍 **Identificação de Hardware**

### **Como Saber se Você Tem um Clone ESP8285**

**Visualmente:**

- **Pico W Genuíno**: Chip retangular grande "CYW43" visível
- **Clone ESP8285**: Dois chips - RP2040 + chip pequeno "ESP8285"
- **Vendedores Comuns**: TZT, AliExpress clones baratos

**Por Software:**

```python
# No console MicroPython:
import machine
print(f"Unique ID: {machine.unique_id()}")
print(f"Freq: {machine.freq()}")

# Testar WiFi:
try:
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("CYW43 detected" if hasattr(wlan, 'config') else "ESP8285 likely")
except:
    print("ESP8285 detected - requires special firmware")
```

**Se Você Comprou um "Pico W" Barato (<$10):**

- Provavelmente é um clone ESP8285
- **NÃO use** firmware Pico W padrão
- **Siga** o [guia de clones ESP8285](docs/guides/rp2040-esp8285.md)

## 🔧 **Solução de Problemas**

### **Problemas Comuns**

#### Display não liga

- Verifique tipo de display (ST7567 vs SSD1306)
- Confirme pinos I2C/SPI
- Ajuste o contraste no config.json
- Use comando `scan` para detectar

#### Sensores não detectados

- Verifique endereços I2C
- Use comando `scan` para identificar dispositivos
- Confirme alimentação 3.3V
- Verifique wiring

#### WiFi não conecta

- Verifique SSID e senha
- Confirme tipo de placa (Pico W vs ESP8285)
- Teste com rede conhecida
- Use `wifi status` para diagnóstico

#### Horário incorreto

- Verifique conexão WiFi para NTP
- Use `settime` para ajuste manual
- Confirme fuso horário

### Modo Console

Se o sistema falhar, ele entrará automaticamente no modo console para diagnóstico:

```python
pico> diagnostic
Running system diagnostics...
  - Hardware tests
  - Communication tests  
  - Performance tests
  - Error analysis
```

## 🌍 **Localização**

O sistema suporta localização completa:

### **Português Brasileiro (pt_BR)**

- **Labels**: Temperatura, Umidade, Pressão
- **Números**: 26,5°C, 75,2%, 1.013,25 hPa
- **Data**: 25/12/2024
- **Console**: Menus e mensagens em português

### **Adicionar Novos Idiomas**

1. Copie arquivo existente: `display_pt_BR.json` → `display_es_ES.json`
2. Traduza as strings
3. Atualize `config.json`: `"locale": "es_ES"`

## 🤝 **Contribuição**

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para o branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### **Áreas para Contribuição**

- Novos sensores e suporte hardware
- Traduções para outros idiomas
- Melhorias na interface
- Otimizações de performance
- Documentação

## 📄 **Licença**

Este projeto está licenciado sob a Licença MIT. Veja [LICENSE](LICENSE) para detalhes.

## 🙏 **Créditos**

- **Raspberry Pi Foundation**: Pico e MicroPython
- **Adafruit**: Bibliotecas de sensores
- **Comunidade MicroPython**: Suporte e exemplos

## 📞 **Suporte**

Para suporte e dúvides:

- Abra uma Issue no GitHub
- Consulte a documentação
- Verifique seção de solução de problemas

---

**PicoWeather v2.0** - Sistema completo de monitoramento meteorológico para Raspberry Pi Pico

*Feito com ❤️ para a comunidade maker brasileira* por Kazzttor
