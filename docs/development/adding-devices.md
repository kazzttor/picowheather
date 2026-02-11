# Adicionando Novos Dispositivos - Guia de Expansão

Guia completo para adicionar novos dispositivos ao PicoWeather, seguindo a arquitetura estabelecida.

## 📋 **Visão Geral**

O PicoWeather foi projetado para ser facilmente extensível. Para adicionar um novo dispositivo, você precisa:

1. Adicionar a biblioteca controladora na pasta `lib/`
2. Criar classes específicas no driver apropriado
3. Atualizar configurações de hardware
4. Adicionar suporte a locales se necessário
5. Testar e documentar o novo dispositivo

## 🏗️ **Arquitetura de Expansão**

```text
PicoWeather/
├── lib/                          # Bibliotecas de dispositivos
│   ├── aht20.py                  # Sensor AHT20
│   ├── bmp280.py                 # Sensor BMP280
│   ├── qn8027.py                 # FM Transmissor
│   ├── st7567.py                 # Display ST7567
│   ├── ssd1306.py                # Display SSD1306
│   └── [novo_dispositivo].py     # ← Biblioteca do novo dispositivo
├── drivers/                      # Drivers de hardware
│   ├── sensors_driver.py         # Driver de sensores
│   ├── controller_driver.py      # Driver de controladores
│   ├── display_driver.py         # Driver de displays
│   └── networking_driver.py      # Driver de rede
└── config.json                   # Configuração do sistema
```

## 🎯 **Tipos de Dispositivos e Drivers**

| Tipo de Dispositivo | Driver Correspondente | Exemplos |
| --- | --- | --- |
| **Sensores** | `sensors_driver.py` | AHT20, BMP280, DHT22, BME280 |
| **Controladores** | `controller_driver.py` | QN8027, PCA9685, MCP23017 |
| **Displays** | `display_driver.py` | ST7567, SSD1306, SH1106 |
| **Rede** | `networking_driver.py` | ESP8285, W5500, SIM800L |

## 🔧 **Passo a Passo: Adicionando Novo Dispositivo**

### **Exemplo: Adicionar Sensor BME280 (Temperatura, Umidade, Pressão, Altitude)**

#### **Passo 1: Criar Biblioteca do Dispositivo**

Crie `lib/bme280.py`:

```python
# BME280 Temperature, Humidity, Pressure Sensor Driver
# Baseado na biblioteca Adafruit BME280 para MicroPython

import time
import machine
import struct

class BME280:
    """BME280 Environmental Sensor"""
    
    # Endereços I2C
    BME280_I2CADDR = 0x76
    BME280_I2CADDR_ALT = 0x77
    
    # Registradores
    BME280_CHIP_ID = 0xD0
    BME280_RESET = 0xE0
    BME280_STATUS = 0xF3
    BME280_CTRL_MEAS = 0xF4
    BME280_CONFIG = 0xF5
    BME280_PRESS_MSB = 0xF7
    BME280_PRESS_LSB = 0xF8
    BME280_PRESS_XLSB = 0xF9
    BME280_TEMP_MSB = 0xFA
    BME280_TEMP_LSB = 0xFB
    BME280_TEMP_XLSB = 0xFC
    BME280_HUM_MSB = 0xFD
    BME280_HUM_LSB = 0xFE
    
    # Chip ID
    BME280_CHIP_ID_VAL = 0x60
    
    def __init__(self, i2c, address=0x76):
        self.i2c = i2c
        self.address = address
        self.initialized = False
        self._temperature = None
        self._humidity = None
        self._pressure = None
        self._altitude = None
        
        # Calibração data
        self.calibration_data = {}
        
        # Inicializar sensor
        if self._initialize():
            self.initialized = True
    
    def _initialize(self):
        """Inicializar o sensor BME280"""
        try:
            # Verificar chip ID
            chip_id = self.i2c.readfrom_mem(self.address, self.BME280_CHIP_ID, 1)[0]
            if chip_id != self.BME280_CHIP_ID_VAL:
                print(f"[BME280] Chip ID incorreto: {chip_id:02x}")
                return False
            
            # Reset
            self.i2c.writeto_mem(self.address, self.BME280_RESET, b'\xB6')
            time.sleep(0.1)
            
            # Ler dados de calibração
            self._read_calibration_data()
            
            # Configurar para modo normal
            # Oversampling: temp 1x, press 1x, hum 1x
            ctrl_meas = (0x01 << 5) | (0x01 << 2) | 0x01
            self.i2c.writeto_mem(self.address, self.BME280_CTRL_MEAS, bytes([ctrl_meas]))
            
            # Config: standby 1000ms, filter off
            config = (0x04 << 5) | (0x00 << 2)
            self.i2c.writeto_mem(self.address, self.BME280_CONFIG, bytes([config]))
            
            time.sleep(0.1)
            return True
            
        except Exception as e:
            print(f"[BME280] Erro na inicialização: {e}")
            return False
    
    def _read_calibration_data(self):
        """Ler dados de calibração"""
        try:
            # Ler todos os dados de calibração (88 bytes from 0x88)
            cal_data = self.i2c.readfrom_mem(self.address, 0x88, 24)
            cal_data += self.i2c.readfrom_mem(self.address, 0xA1, 1)
            cal_data += self.i2c.readfrom_mem(self.address, 0xE1, 7)
            
            # Parse calibration data
            self.calibration_data = {
                'dig_T1': (cal_data[1] << 8) | cal_data[0],
                'dig_T2': self._signed_int16((cal_data[3] << 8) | cal_data[2]),
                'dig_T3': self._signed_int16((cal_data[5] << 8) | cal_data[4]),
                'dig_P1': (cal_data[7] << 8) | cal_data[6],
                'dig_P2': self._signed_int16((cal_data[9] << 8) | cal_data[8]),
                'dig_P3': self._signed_int16((cal_data[11] << 8) | cal_data[10]),
                'dig_P4': self._signed_int16((cal_data[13] << 8) | cal_data[12]),
                'dig_P5': self._signed_int16((cal_data[15] << 8) | cal_data[14]),
                'dig_P6': self._signed_int16((cal_data[17] << 8) | cal_data[16]),
                'dig_P7': self._signed_int16((cal_data[19] << 8) | cal_data[18]),
                'dig_P8': self._signed_int16((cal_data[21] << 8) | cal_data[20]),
                'dig_P9': self._signed_int16((cal_data[23] << 8) | cal_data[22]),
                'dig_H1': cal_data[24],
                'dig_H2': self._signed_int16((cal_data[26] << 8) | cal_data[25]),
                'dig_H3': cal_data[27],
                'dig_H4': self._signed_int16((cal_data[28] << 4) | (cal_data[29] & 0x0F)),
                'dig_H5': self._signed_int16((cal_data[30] << 4) | (cal_data[29] >> 4)),
                'dig_H6': cal_data[31]
            }
            
        except Exception as e:
            print(f"[BME280] Erro lendo calibração: {e}")
    
    def _signed_int16(self, value):
        """Converter para signed 16-bit"""
        if value > 32767:
            value -= 65536
        return value
    
    def read_raw_data(self):
        """Ler dados brutos do sensor"""
        try:
            # Ler pressão (3 bytes)
            press_data = self.i2c.readfrom_mem(self.address, self.BME280_PRESS_MSB, 3)
            press_raw = (press_data[0] << 12) | (press_data[1] << 4) | (press_data[2] >> 4)
            
            # Ler temperatura (3 bytes)
            temp_data = self.i2c.readfrom_mem(self.address, self.BME280_TEMP_MSB, 3)
            temp_raw = (temp_data[0] << 12) | (temp_data[1] << 4) | (temp_data[2] >> 4)
            
            # Ler umidade (2 bytes)
            hum_data = self.i2c.readfrom_mem(self.address, self.BME280_HUM_MSB, 2)
            hum_raw = (hum_data[0] << 8) | hum_data[1]
            
            return {
                'pressure_raw': press_raw,
                'temperature_raw': temp_raw,
                'humidity_raw': hum_raw
            }
            
        except Exception as e:
            print(f"[BME280] Erro lendo dados: {e}")
            return None
    
    def read_compensated_data(self):
        """Ler dados compensados"""
        raw_data = self.read_raw_data()
        if not raw_data:
            return None
        
        try:
            # Compensar temperatura
            var1 = (raw_data['temperature_raw'] / 16384.0 - self.calibration_data['dig_T1'] / 1024.0) * self.calibration_data['dig_T2']
            var2 = ((raw_data['temperature_raw'] / 131072.0 - self.calibration_data['dig_T1'] / 8192.0) * 
                    (raw_data['temperature_raw'] / 131072.0 - self.calibration_data['dig_T1'] / 8192.0)) * self.calibration_data['dig_T3']
            self._temperature = var1 + var2
            
            # Compensar pressão
            var1 = self._temperature / 2.0 - 64000.0
            var2 = var1 * var1 * self.calibration_data['dig_P6'] / 32768.0
            var2 = var2 + var1 * self.calibration_data['dig_P5'] * 2.0
            var2 = var2 / 4.0 + self.calibration_data['dig_P4'] * 65536.0
            var1 = (self.calibration_data['dig_P3'] * var1 * var1 / 524288.0 + 
                    self.calibration_data['dig_P2'] * var1) / 524288.0
            var1 = (1.0 + var1 / 32768.0) * self.calibration_data['dig_P1']
            if var1 == 0:
                return None  # Evitar divisão por zero
            
            pressure = 1048576.0 - raw_data['pressure_raw']
            pressure = (pressure - (var2 / 4096.0)) * 6250.0 / var1
            var1 = self.calibration_data['dig_P9'] * pressure * pressure / 2147483648.0
            var2 = pressure * self.calibration_data['dig_P8'] / 32768.0
            pressure = pressure + (var1 + var2 + self.calibration_data['dig_P7']) / 16.0
            self._pressure = pressure
            
            # Compensar umidade
            var_h = self._temperature - 76800.0
            var_h = (raw_data['humidity_raw'] << 14) - (self.calibration_data['dig_H4'] << 20) - \
                     (self.calibration_data['dig_H5'] * var_h)
            var_h = var_h + (var_h * var_h * self.calibration_data['dig_H6']) / 16384.0
            var_h = var_h + ((var_h * var_h * var_h * self.calibration_data['dig_H3']) / 524288.0)
            var_h = var_h + self.calibration_data['dig_H2'] * 4.0
            var_h = var_h / 4194304.0
            
            if var_h > 1.0:
                var_h = 1.0
            elif var_h < 0.0:
                var_h = 0.0
            
            self._humidity = var_h * 100.0
            
            # Calcular altitude (aproximado)
            sea_level_pressure = 1013.25  # hPa
            self._altitude = 44330.0 * (1.0 - pow(self._pressure / sea_level_pressure, 0.1903))
            
            return {
                'temperature': self._temperature,
                'humidity': self._humidity,
                'pressure': self._pressure,
                'altitude': self._altitude
            }
            
        except Exception as e:
            print(f"[BME280] Erro na compensação: {e}")
            return None
    
    def read_all(self):
        """Ler todos os dados do sensor"""
        if not self.initialized:
            return None
        
        data = self.read_compensated_data()
        if data:
            return {
                'temperature': round(data['temperature'], 1),
                'humidity': round(data['humidity'], 1),
                'pressure': round(data['pressure'], 2),
                'altitude': round(data['altitude'], 1)
            }
        return None
    
    def get_status(self):
        """Obter status do sensor"""
        return {
            'initialized': self.initialized,
            'address': hex(self.address),
            'last_reading': {
                'temperature': self._temperature,
                'humidity': self._humidity,
                'pressure': self._pressure,
                'altitude': self._altitude
            }
        }
```

#### **Passo 2: Integrar no Sensors Driver**

Modifique `drivers/sensors_driver.py`:

```python
# Adicionar import no topo
from lib.bme280 import BME280

# Na classe SensorsDriver, adicionar método para BME280
class BME280Sensor(SensorDevice):
    """BME280 Environmental Sensor"""
    
    def __init__(self, name, i2c_bus, address):
        super().__init__(name, i2c_bus, address)
        self.sensor = None
    
    def detect(self):
        """Verificar se BME280 está presente"""
        try:
            self.sensor = BME280(self.i2c_bus, self.address)
            self.detected = self.sensor.initialized
            return self.detected
        except Exception as e:
            print(f"[BME280] Erro na detecção: {e}")
            return False
    
    def initialize(self):
        """Inicializar BME280"""
        if self.detected and self.sensor:
            self.initialized = self.sensor.initialized
            return self.initialized
        return False
    
    def read(self):
        """Ler dados do BME280"""
        if not self.is_healthy():
            return {}
        
        try:
            data = self.sensor.read_all()
            if data:
                self.last_read = time.time()
                return data
        except Exception as e:
            print(f"[BME280] Erro na leitura: {e}")
            self.error_count += 1
        
        return {}
    
    def get_status(self):
        """Obter status detalhado"""
        status = super().get_status()
        if self.sensor:
            status.update(self.sensor.get_status())
        return status

# No método __init__ do SensorsDriver, adicionar:
def __init__(self, config, hardware):
    # ... código existente ...
    
    # Adicionar suporte a BME280
    self.bme280 = None
    bme280_config = config.get("devices", {}).get("sensors", {}).get("bme280", {})
    if bme280_config.get("enabled", False):
        i2c_bus_num = config.get("devices", {}).get("sensors", {}).get("i2c_bus", 0)
        i2c_bus = self.i2c_buses.get(f"i2c{i2c_bus_num}")
        if i2c_bus:
            address = bme280_config.get("address", 118)  # 0x76
            self.bme280 = BME280Sensor("bme280", i2c_bus, address)

# No método read_all, adicionar:
def read_all(self):
    data = {}
    
    # ... código existente para AHT20 e BMP280 ...
    
    # Ler BME280
    if self.bme280 and self.bme280.is_healthy():
        bme280_data = self.bme280.read()
        if bme280_data:
            data.update(bme280_data)
    
    return data

# No método get_all_status, adicionar:
def get_all_status(self):
    status = {}
    
    # ... código existente ...
    
    if self.bme280:
        status["bme280"] = self.bme280.get_status()
    
    return status
```

#### **Passo 3: Atualizar Configuração**

Modifique `config.json`:

```json
{
  "devices": {
    "sensors": {
      "enabled": true,
      "i2c_bus": 0,
      "aht20": {
        "enabled": false,  // Desabilitar AHT20 se usar BME280
        "address": 56
      },
      "bmp280": {
        "enabled": false,  // Desabilitar BMP280 se usar BME280
        "address": 119
      },
      "bme280": {
        "enabled": true,
        "address": 118      // 0x76
      }
    }
  }
}
```

#### **Passo 4: Atualizar Locales**

Modifique `locales/display_pt_BR.json`:

```json
{
  "labels": {
    // ... labels existentes ...
    "altitude": "Altitude"
  },
  "units": {
    // ... units existentes ...
    "altitude": "m"
  }
}
```

#### **Passo 5: Atualizar Layout de Display**

Modifique `display_layouts.json`:

```json
{
  "st7567_spi": {
    "pages": [
      {
        "name": "complete_bme280",
        "duration": 1000,
        "requires_sensors": ["bme280", "temperature", "humidity", "pressure", "altitude"],
        "elements": [
          {"type": "date", "x": "center", "y": 0},
          {"type": "time", "x": "center", "y": 10},
          {"type": "separator", "x": 0, "y": 20, "length": 16, "style": "double"},
          {"type": "sensor", "name": "temperature", "x": "center", "y": 22, "label": "Temp:", "unit": "C", "format": "5.1f"},
          {"type": "sensor", "name": "humidity", "x": "center", "y": 32, "label": "Umid:", "unit": "%", "format": "3.0f"},
          {"type": "sensor", "name": "pressure", "x": "center", "y": 42, "label": "Pres:", "unit": "hPa", "format": "5.1f"},
          {"type": "sensor", "name": "altitude", "x": "center", "y": 52, "label": "Alt:", "unit": "m", "format": "4.0f"}
        ]
      }
    ]
  }
}
```

## 🎯 **Exemplos de Outros Dispositivos**

### **Adicionar Sensor de Luz BH1750**

#### **lib/bh1750.py**

```python
# BH1750 Light Sensor Driver
import time

class BH1750:
    """BH1750 Light Sensor"""
    
    BH1750_I2CADDR = 0x23
    BH1750_I2CADDR_ALT = 0x5C
    
    # Commands
    POWER_DOWN = 0x00
    POWER_ON = 0x01
    RESET = 0x07
    CONTINUOUS_HIGH_RES_MODE = 0x10
    CONTINUOUS_HIGH_RES_MODE_2 = 0x11
    CONTINUOUS_LOW_RES_MODE = 0x13
    ONE_TIME_HIGH_RES_MODE = 0x20
    ONE_TIME_HIGH_RES_MODE_2 = 0x21
    ONE_TIME_LOW_RES_MODE = 0x23
    
    def __init__(self, i2c, address=0x23):
        self.i2c = i2c
        self.address = address
        self.initialized = False
        
        if self._initialize():
            self.initialized = True
    
    def _initialize(self):
        try:
            # Power on
            self.i2c.writeto(self.address, bytes([self.POWER_ON]))
            time.sleep(0.1)
            
            # Reset
            self.i2c.writeto(self.address, bytes([self.RESET]))
            time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"[BH1750] Erro na inicialização: {e}")
            return False
    
    def read_light(self):
        """Ler luminosidade em lux"""
        try:
            # Start continuous high resolution mode
            self.i2c.writeto(self.address, bytes([self.CONTINUOUS_HIGH_RES_MODE]))
            time.sleep(0.2)  # Wait for measurement
            
            # Read 2 bytes
            data = self.i2c.readfrom(self.address, 2)
            light_raw = (data[0] << 8) | data[1]
            
            # Convert to lux (resolution 1.2 lux)
            light_lux = light_raw / 1.2
            
            return round(light_lux, 1)
            
        except Exception as e:
            print(f"[BH1750] Erro na leitura: {e}")
            return None
    
    def read_all(self):
        """Interface padrão para compatibilidade"""
        light = self.read_light()
        if light is not None:
            return {"light": light}
        return {}
```

### **Adicionar Servo Motor PCA9685**

#### **lib/pca9685.py**

```python
# PCA9685 16-Channel PWM Driver
import time

class PCA9685:
    """PCA9685 PWM Controller"""
    
    PCA9685_I2CADDR = 0x40
    PCA9685_I2CADDR_ALT = 0x41
    
    # Registers
    MODE1 = 0x00
    MODE2 = 0x01
    PRESCALE = 0xFE
    LED0_ON_L = 0x06
    LED0_ON_H = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09
    ALL_LED_ON_L = 0xFA
    ALL_LED_ON_H = 0xFB
    ALL_LED_OFF_L = 0xFC
    ALL_LED_OFF_H = 0xFD
    
    def __init__(self, i2c, address=0x40, freq=50):
        self.i2c = i2c
        self.address = address
        self.freq = freq
        self.initialized = False
        
        if self._initialize():
            self.initialized = True
    
    def _initialize(self):
        try:
            # Reset
            self.i2c.writeto_mem(self.address, self.MODE1, bytes([0x00]))
            time.sleep(0.01)
            
            # Set sleep mode
            self.i2c.writeto_mem(self.address, self.MODE1, bytes([0x10]))
            time.sleep(0.01)
            
            # Set prescaler
            prescale = int(25000000.0 / (4096.0 * self.freq) - 1)
            self.i2c.writeto_mem(self.address, self.PRESCALE, bytes([prescale]))
            time.sleep(0.01)
            
            # Wake up
            self.i2c.writeto_mem(self.address, self.MODE1, bytes([0x00]))
            time.sleep(0.01)
            
            # Enable auto-increment
            self.i2c.writeto_mem(self.address, self.MODE1, bytes([0x20]))
            
            return True
        except Exception as e:
            print(f"[PCA9685] Erro na inicialização: {e}")
            return False
    
    def set_pwm(self, channel, on, off):
        """Set PWM for specific channel"""
        if channel < 0 or channel > 15:
            return False
        
        try:
            reg = self.LED0_ON_L + 4 * channel
            self.i2c.writeto_mem(self.address, reg, bytes([on & 0xFF]))
            self.i2c.writeto_mem(self.address, reg + 1, bytes([(on >> 8) & 0xFF]))
            self.i2c.writeto_mem(self.address, reg + 2, bytes([off & 0xFF]))
            self.i2c.writeto_mem(self.address, reg + 3, bytes([(off >> 8) & 0xFF]))
            return True
        except Exception as e:
            print(f"[PCA9685] Erro setando PWM: {e}")
            return False
    
    def set_angle(self, channel, angle):
        """Set servo angle (0-180 degrees)"""
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        
        # Convert angle to PWM value
        pulse = int(500 + (angle / 180.0) * 2000)  # 500-2500μs
        pwm_val = int(pulse * 4096.0 / (1000000.0 / self.freq))
        
        return self.set_pwm(channel, 0, pwm_val)
    
    def read_all(self):
        """Interface padrão - retorna status de todos os canais"""
        return {
            "controller": "pca9685",
            "channels": 16,
            "frequency": self.freq,
            "initialized": self.initialized
        }
```

## 🔍 **Teste e Validação**

### **Teste Unitário do Dispositivo**

```python
# Testar biblioteca do dispositivo isoladamente
import sys
sys.path.append('../lib')

from bme280 import BME280
from machine import I2C, Pin

# Teste básico
i2c = I2C(0, sda=Pin(4), scl=Pin(5))
bme = BME280(i2c, 0x76)

if bme.initialized:
    print("BME280 inicializado com sucesso")
    data = bme.read_all()
    print(f"Dados: {data}")
else:
    print("Falha na inicialização do BME280")
```

### **Teste de Integração**

```python
# No console PicoWeather:
pico> scan
# Verificar se dispositivo aparece no endereço correto

pico> diagnostic
# Testar integração completa

pico> sensors
# Verificar leitura do novo sensor
```

### **Teste de Configuração**

```python
# Verificar configuração
pico> config
# Confirmar que dispositivo está habilitado

# Testar diferentes endereços
# Se dispositivo não for detectado, tente endereço alternativo
```

## 📝 **Boas Práticas**

### **Padrões de Código**

1. **Nome da Classe**: Use nome do dispositivo (ex: `BME280`)
2. **Métodos Padrão**: Implemente `read_all()`, `get_status()`
3. **Tratamento de Erros**: Use try/except com logging
4. **Inicialização**: Retorne `True/False` para sucesso/falha
5. **Compatibilidade**: Mantenha interface consistente

### **Documentação**

1. **Docstrings**: Documente classe e métodos públicos
2. **Comentários**: Explique operações complexas
3. **Exemplos**: Inclua exemplos de uso
4. **Hardware**: Documente requisitos e pinos

### **Testes**

1. **Detecção**: Verifique se dispositivo responde
2. **Inicialização**: Teste setup do dispositivo
3. **Leitura**: Valide dados retornados
4. **Erros**: Teste casos de falha

## 🚀 **Roadmap de Expansão**

### **Sensores Planejados**

- **DHT22**: Temperatura/umidade digital
- **DS18B20**: Temperatura digital (1-wire)
- **MAX30102**: Frequência cardíaca/oxímetro
- **TSL2561**: Sensor de luz digital
- **MPU6050**: Acelerômetro/Giroscópio

### **Controladores Planejados**

- **MCP23017**: Expansor de GPIO (16 bits)
- **ADS1115**: ADC de 16 bits
- **NEO6M**: GPS
- **RC522**: RFID/ NFC

### **Displays Planejados**

- **SH1106**: OLED 128x64 (I2C)
- **ILI9341**: TFT colorido 320x240 (SPI)
- **MAX7219**: Display LED 7-segmentos

### **Rede Planejados**

- **W5500**: Ethernet 10/100
- **SIM800L**: GSM/GPRS
- **LoRa SX1276**: Comunicação longa distância

---

## 📞 **Suporte**

Para problemas na adição de dispositivos:

- Consulte exemplos existentes
- Use `pico> diagnostic` para testes
- Verifique documentação do fabricante
- Abra Issue no GitHub com detalhes

---

**Guia válido para:** PicoWeather v2.0+  
**Última atualização:** 2024-12-25
