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

### 📺 **Display LCD ST7567**

- **128x64 pixels**: Display monocromático de alta visibilidade
- **Interface SPI**: Comunicação rápida e eficiente
- **Múltiplas telas**: Navegação entre informações climáticas
- **Fonte customizada**: Suporte completo para caracteres português (ç, ã, é, etc.)

### 📻 **Transmissor FM**

- **Faixa completa**: 88-108 MHz
- **Controle de volume**: 16 níveis de áudio
- **Modo estéreo/mono**: Configurável via console
- **Indicador RSSI**: Monitoramento de sinal

### 🌐 **Conectividade WiFi**

- **ESP8285 integrado**: Conexão estável 2.4GHz
- **Sincronização NTP**: Hora automática via pool.ntp.br
- **Status em tempo real**: Monitoramento de conexão
- **Fuso horário**: Configurável (-3 padrão Brasil)

### 🎮 **Interface Intuitiva**

- **4 botões**: Navegação completa (Cima, Baixo, Selecionar, Voltar)
- **Console interativo**: Sistema completo de comandos
- **Mensagens em português**: Interface 100% localizada
- **Formatação brasileira**: Data DD/MM/YYYY, números com vírgula decimal

## 🏗️ **Arquitetura do Sistema**

### **Estrutura de Diretórios**

```text
├── main.py                 # Ponto de entrada principal
├── config.json            # Configuração do sistema
├── locales/              # Arquivos de localização
│   ├── display_pt_BR.json
│   └── console_pt_BR.json
├── drivers/              # Drivers de hardware
│   ├── sensors_driver.py
│   ├── display_driver.py
│   ├── time_driver.py
│   └── controller_driver.py
├── lib/                  # Bibliotecas de sensores
│   ├── aht20.py
│   ├── bmp280.py
│   └── st7567.py
└── utils/                # Utilitários do sistema
    ├── locale_manager.py  # Sistema de localização
    ├── custom_font.py    # Fonte portuguesa
    └── console.py        # Console interativo
```

### **Sistema de Localização**

- **Display**: Labels em português (Temperatura, Umidade, Pressão)
- **Console**: Menus e comandos em português
- **Formatação**: Padrão brasileiro (26,5°C, 75,2%, 1.013,25 hPa)
- **Data**: Formato DD/MM/YYYY
- **Fallback**: Inglês automático se arquivo não encontrado

## 🚀 **Instalação e Configuração**

### **Hardware Requerido**

- Raspberry Pi Pico (ou compatível)
- Display LCD ST7567 128x64
- Sensor AHT20 (temperatura/umidade)
- Sensor BMP280 (pressão/barômetro)
- Módulo ESP8285 (WiFi)
- Transmissor FM QN8027
- 4 botões táteis
- Fiação e conectores

### **Software Requerido**

- MicroPython para Raspberry Pi Pico
- Thonny IDE (recomendado)
- Bibliotecas incluídas no projeto

### **Passos de Instalação**

1. **Clone do repositório**

   ```bash
   git clone https://github.com/kazzttor/picowheather.git
   cd picowheather
   ```

2. **Upload para Pico**
   - Abra Thonny IDE
   - Conecte o Pico via USB
   - Copie todos os arquivos para o Pico
   - Mantenha a estrutura de diretórios

3. **Configuração**
   - Edite `config.json` para seu hardware
   - Configure WiFi (SSID, senha)
   - Ajuste pinos conforme sua montagem

4. **Execução**

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
```

## ⚙️ **Configuração**

### **Arquivo config.json**

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

### **Pinos GPIO**

Consulte `config.json` para configuração completa de pinos:

- **I2C0**: Sensores (AHT20, BMP280)
- **I2C1**: Controladores (QN8027)
- **SPI1**: Display ST7567
- **UART0**: ESP8285 WiFi
- **GPIO**: Botões de controle

## 🔧 **Solução de Problemas**

### **Problemas Comuns**

#### Display não liga

- Verifique conexões SPI
- Confirme pinos DC, CS, RST
- Ajuste o contraste no config.json

#### Sensores não detectados

- Verifique endereços I2C
- Use comando `scan` para identificar dispositivos
- Confirme alimentação 3.3V

#### WiFi não conecta

- Verifique SSID e senha
- Confirme pino enable do ESP8285
- Teste com rede conhecida

#### Horário incorreto

- Verifique conexão WiFi para NTP
- Use `settime` para ajuste manual
- Confirme fuso horário

### **Modo Console**

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

Para suporte e dúvidas:

- Abra uma Issue no GitHub
- Consulte a documentação
- Verifique seção de solução de problemas

---

**PicoWeather v1.0** - Sistema completo de monitoramento meteorológico para Raspberry Pi Pico

*Feito com ❤️ para a comunidade maker brasileira* por Kazzttor
