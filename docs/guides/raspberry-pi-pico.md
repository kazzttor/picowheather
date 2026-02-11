# Raspberry Pi Pico Padrão - Guia de Instalação

Guia completo para instalação do PicoWeather em Raspberry Pi Pico padrão com display SSD1306.

## 🎯 **Visão Geral**

### **Configuração**

- **Placa**: Raspberry Pi Pico padrão
- **Display**: SSD1306 OLED 128x64 (I2C)
- **Sensores**: AHT20, BMP280 (I2C)
- **WiFi**: Não disponível
- **FM Transmissor**: Opcional (I2C)
- **Botões**: Opcionais (GPIO)

### **Características**

- Configuração mais simples e econômica
- Display OLED de baixo consumo
- Funciona sem WiFi (modo offline)
- Ideal para aprendizado e protótipos

## 🛒 **Lista de Materiais**

### **Componentes Essenciais**

| Componente | Especificação | Quantidade |
| ---------- | ------------ | --------- |
| Raspberry Pi Pico | RP2040, 264KB RAM | 1 |
| Display OLED | SSD1306, 128x64, I2C | 1 |
| Sensor Temp/Umidade | AHT20, I2C | 1 |
| Sensor Pressão | BMP280, I2C | 1 |
| Protoboard | 400 pontos ou maior | 1 |
| Jumper Wires | Fêmea-fêmea | ~20 |

### **Componentes Opcionais**

| Componente | Especificação | Quantidade |
| ---------- | ------------ | --------- |
| FM Transmissor | QN8027, I2C | 1 |
| Botões táteis | 12mm, 6V | 4 |
| Resistores | 10kΩ (pull-up) | 4 |
| Caixa de projeto | Para montagem | 1 |
| Fonte 5V | USB ou adaptador | 1 |

## 🔌 **Diagrama de Conexões**

### **Pinagem Raspberry Pi Pico**

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

### **Conexões Essenciais**

#### **Display SSD1306 (I2C0)**

```text
Display SSD1306    →    Raspberry Pi Pico
VCC (3.3V)         →    3V3 (Pin 36)
GND                →    GND (Pin 38)
SDA                →    GP4 (Pin 6)
SCL                →    GP5 (Pin 4)
```

#### **Sensores (I2C1)**

```text
AHT20/BMP280       →    Raspberry Pi Pico
VCC (3.3V)         →    3V3 (Pin 36)
GND                →    GND (Pin 38)
SDA                →    GP6 (Pin 10)
SCL                →    GP7 (Pin 8)
```

#### **Botões (Opcional)**

```text
Botão              →    Raspberry Pi Pico
UP                 →    GP14 (Pin 16) + 3V3
DOWN               →    GP15 (Pin 18) + 3V3
SELECT             →    GP13 (Pin 14) + 3V3
BACK               →    GP10 (Pin 12) + 3V3
```

#### **FM Transmissor (Opcional)**

```text
QN8027             →    Raspberry Pi Pico
VCC (3.3V)         →    3V3 (Pin 36)
GND                →    GND (Pin 38)
SDA                →    GP6 (Pin 10) - compartilhado
SCL                →    GP7 (Pin 8) - compartilhado
```

## ⚙️ **Configuração do Software**

### **1. Preparar o MicroPython**

```bash
# Baixar MicroPython para Raspberry Pi Pico
# Visite: https://micropython.org/download/rp2-pico/
# Baixe o arquivo .uf2 mais recente

# Procedimento de instalação:
# 1. Conecte o Pico ao computador mantendo BOOTSEL pressionado
# 2. Arraste o arquivo .uf2 para o drive RPI-RP2
# 3. O Pico reiniciará com MicroPython
```

### **2. Upload dos Arquivos do Projeto**

```bash
# Usando Thonny IDE:
# 1. Abra Thonny e conecte-se ao Pico
# 2. Vá em File → Upload
# 3. Selecione todos os arquivos do projeto
# 4. Mantenha a estrutura de diretórios
```

### **3. Configurar o Sistema**

#### **Copiar Configuração Padrão**

```bash
# No console MicroPython:
import os
os.rename("config_pico_standard.json", "config.json")
```

#### **Editar config.json**

```json
{
  "hardware": {
    "board": "pico_standard",
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
  "buttons": {
    "enabled": true,
    "pins": {
      "up": "button_up",
      "down": "button_down",
      "select": "button_select",
      "back": "button_back"
    }
  },
  "system": {
    "locale": "pt_BR",
    "enable_console": true
  }
}
```

## 🚀 **Procedimento de Instalação**

### **Passo 1: Montagem do Hardware**

1. **Montagem na Protoboard**
   - Insira o Raspberry Pi Pico na protoboard
   - Deixe espaço para jumpers e componentes

2. **Conectar Display**
   - Conecte o SSD1306 usando jumpers
   - Verifique conexões VCC e GND
   - Confirme SDA em GP4 e SCL em GP5

3. **Conectar Sensores**
   - Conecte AHT20 e BMP280 no mesmo barramento I2C
   - Use GP6 para SDA e GP7 para SCL
   - Verifique alimentação 3.3V

4. **Conectar Botões (Opcional)**
   - Conecte botões com resistores pull-up
   - Use GPIOs conforme pinagem

### **Passo 2: Instalação do Software**

1. **Instalar MicroPython**
   - Siga procedimento BOOTSEL
   - Verifique instalação no Thonny

2. **Upload do Projeto**
   - Copie todos os arquivos
   - Mantenha estrutura de diretórios

3. **Configuração Inicial**
   - Copie config_pico_standard.json para config.json
   - Edite configurações conforme necessário

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

3. **Testar Sensores**

   ```python
   pico> sensors
   ```

## 🔧 **Solução de Problemas**

### **⚠️ Verificação de Barramento I2C (Importante!)**

Antes de conectar dispositivos, verifique conflitos de endereços:

```python
# Scan completo do barramento I2C
pico> scan
# Saída esperada para esta configuração:
# I2C0 (GP4/GP5): [0x3C] - Display SSD1306
# I2C1 (GP6/GP7): [0x38, 0x77] - AHT20, BMP280

# Se algum endereço estiver faltando:
# - Verifique conexões físicas
# - Confirme alimentação 3.3V
# - Teste dispositivo isoladamente
```

**Conflitos Comuns:**

- **Display SSD1306**: Pode ser 0x3C ou 0x3D
- **AHT20**: Sempre 0x38
- **BMP280**: Pode ser 0x76 ou 0x77
- **FM Transmissor**: Geralmente 0x3E (QN8027)

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

# Verificar configuração
pico> config
# Confirmar display.type = "ssd1306_i2c"
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

# Testar individualmente
pico> sensors
```

### **Conflitos de Endereços I2C**

```python
# Se dois dispositivos aparecerem com mesmo endereço:
# 1. Desconecte um dispositivo
# 2. Faça scan novamente
# 3. Identifique qual dispositivo está em conflito
# 4. Verifique se dispositivo tem endereço alternativo
# 5. Use barramentos I2C separados se necessário

# Exemplo de solução:
# - Display: I2C0 (GP4/GP5)
# - Sensores: I2C1 (GP6/GP7)
# - FM Transmissor: I2C1 (mesmo barramento, endereço diferente)
```

### **Botões Não Respondem**

```python
# Verificar configuração
pico> config
# Confirmar buttons.enabled = true

# Testar GPIOs
pico> diagnostic
```

## 📊 **Performance e Limitações**

### **Recursos Utilizados**

- **RAM**: ~50KB de 264KB disponível
- **Flash**: ~200KB de 2MB disponível
- **CPU**: ~20% de utilização em modo normal
- **Energia**: ~50mA sem display, ~80mA com display

### **Limitações**

- Sem conectividade WiFi
- Display monocromático
- Sem sincronização de tempo automática
- Memória limitada para expansões

## 🔄 **Manutenção**

### **Atualizações**

```bash
# Para atualizar o sistema:
# 1. Faça backup do config.json
# 2. Substitua arquivos do projeto
# 3. Restaure config.json
# 4. Teste funcionamento
```

### **Limpeza**

- Desligue alimentação antes de limpar
- Use álcool isopropílico para contatos
- Verifique conexões periodicamente

## 🎯 **Próximos Passos**

### **Expansões Possíveis**

- Adicionar cartão SD para logging
- Implementar comunicação serial
- Adicionar mais sensores I2C
- Criar interface web (com hardware adicional)

### **Melhorias**

- Calibração de sensores
- Otimização de consumo
- Implementar modo sleep
- Adicionar bateria para mobilidade

---

## 📞 **Suporte**

Para problemas específicos desta configuração:

- Verifique [solução de problemas](../../README.md#solução-de-problemas)
- Consulte [console commands](../../README.md#comandos-do-console)
- Abra uma Issue no GitHub descrevendo seu hardware

---

**Guia válido para:** PicoWeather v2.0+  
**Última atualização:** 2024-12-25
