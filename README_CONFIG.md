# PicoWeather - Arquivos de Configuração

Este diretório contém configurações pré-definidas para diferentes hardwares.

## Arquivos Disponíveis

### 📁 config_pico_standard.json
Configuração para Raspberry Pi Pico padrão:

**Hardware Conectado:**
- **Display**: SSD1306 OLED (128x64) - I2C
  - SDA: GP4
  - SCL: GP5
  - Endereço: 0x3C (60 decimal)

- **Sensores**: AHT20 + BMP280 - I2C0
  - SDA: GP6  
  - SCL: GP7
  - AHT20: Endereço 0x38 (56)
  - BMP280: Endereço 0x77 (119)

**Recursos:**
- ❌ Sem WiFi
- ✅ Display OLED
- ✅ Sensores temperatura/umidade/pressão
- ❌ Sem botões
- ❌ Sem transmissor FM

---

### 📁 config_pico_clone.json  
Configuração para Raspberry Pi Pico Clone:

**Hardware Conectado:**
- **Display**: ST7567 LCD (128x64) - SPI
  - SCK: GP18 (spi1_sck)
  - MOSI: GP19 (spi1_mosi)  
  - DC: GP20 (spi1_dc)
  - CS: GP21 (spi1_cs)
  - RST: GP22 (spi1_rst)

- **Sensores**: AHT20 + BMP280 - I2C0
  - SDA: GP8
  - SCL: GP9
  - AHT20: Endereço 0x38 (56)
  - BMP280: Endereço 0x77 (119)

- **Transmissor FM**: RDA5807 - I2C1
  - SDA: GP6
  - SCL: GP7
  - Endereço: 0x11 (17)

- **Botões**: 4 botões com debouncing
  - Select: GP2
  - Up: GP3  
  - Down: GP4
  - Back: GP5

- **WiFi**: Detecção automática
  - **Pico W**: WiFi nativo via CYW43
  - **Pico Clone**: ESP8285 via UART
    - TX: GP0 (uart0_tx)
    - RX: GP1 (uart0_rx)
    - Enable: GP23 (esp_enable)

**Redes WiFi Configuradas:**
1. **HomeNetwork_5G** (prioridade 1)
   - Senha: `home_password_2024`
2. **MobileHotspot** (prioridade 2) - Backup
   - Senha: `mobile123`

**Sistema de WiFi:**
- **Detecção automática** do tipo de hardware
- **Pico W**: Usa WiFi nativo CYW43
- **Pico Clone**: Usa ESP8285 externo via UART
- **Pico Padrão**: Sem WiFi (opcional)
- **Auto-conexão** com múltiplas redes em ordem de prioridade
- **Reconexão automática** em caso de perda de sinal
- **Scan de redes** sem fio (para Pico W e ESP8285)

**Recursos:**
- ✅ Display LCD SPI
- ✅ Sensores temperatura/umidade/pressão
- ✅ Transmissor FM
- ✅ Botões interativos
- ✅ WiFi com múltiplas redes
- ✅ Sincronização NTP

---

## Como Usar

### 1. Copiar Configuração Desejada

```bash
# Para Pico Padrão:
cp config_pico_standard.json config.json

# Para Pico Clone:
cp config_pico_clone.json config.json
```

### 2. Ajustar Conexões Físicas

Verifique se os pinos correspondem às conexões físicas do seu hardware.

### 3. Personalizar (Opcional)

Edite `config.json` para ajustar:
- Senhas WiFi
- Endereços I2C
- Frequências FM
- Fuso horário (timezone)

### 4. Executar

```python
python main.py
```

---

## 📋 Referência de Pinagem

### Pico Padrão (GP4-GP7 para sensores)
```
GP4 ──┬── SDA (Display SSD1306)
GP5 ──┼── SCL (Display SSD1306)
GP6 ──┼── SDA (Sensores)
GP7 ──┴── SCL (Sensores)
```

### Pico Clone
```
Display SPI (ST7567):
GP18 ── SCK
GP19 ── MOSI
GP20 ── DC
GP21 ── CS
GP22 ── RST

Sensores I2C0:
GP8  ── SDA (AHT20 + BMP280)
GP9  ── SCL (AHT20 + BMP280)

Transmissor FM I2C1:
GP6  ── SDA (RDA5807)
GP7  ── SCL (RDA5807)

Botões:
GP2 ── Select
GP3 ── Up
GP4 ── Down
GP5 ── Back

WiFi ESP8285:
GP0  ── TX
GP1  ── RX  
GP23 ── Enable
```

---

## 🔧 Configurações Avançadas

### Sensores
- **AHT20**: Sensor de temperatura e umidade
- **BMP280**: Sensor de pressão barométrica
  
### Display
- **SSD1306**: Display OLED monocromático I2C
- **ST7567**: Display LCD monocromático SPI

### Redes WiFi
- Configure até 5 redes com prioridades
- **Prioridade 1**: Conexão preferencial
- **Prioridade 2-5**: Backup em ordem

### Transmissor FM
- **RDA5807**: Suporta 88-108 MHz
- Controle de volume 0-15
- Suporte a estéreo

---

## ⚠️ Notas Importantes

1. **Endereços I2C**: Use valores decimais (56 = 0x38)
2. **Pull-ups**: Lembre de usar resistores pull-up em I2C
3. **Alimentação**: Verifique voltagem dos sensores
4. **Compatibilidade**: Verifique compatibilidade de pinos para sua placa

---

## 📝 Personalização

Para criar sua própria configuração:

1. Copie o arquivo mais próximo do seu hardware
2. Ajuste os pinos conforme sua montagem
3. Adicione/remova dispositivos conforme necessário
4. Salve como `config.json`

Exemplo de sensor adicional:
```json
"extra_sensor": {
  "enabled": true,
  "i2c_bus": 0,
  "address": 72
}
```

---

## 🚀 Teste de Configuração

Use o console para testar:

```python
# Após iniciar, pressione Ctrl+C para entrar no console
pico> scan          # Escanear dispositivos I2C
pico> sensors        # Verificar sensores
pico> display test   # Testar display
pico> wifi           # Verificar WiFi (se disponível)
```