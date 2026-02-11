# Arquitetura do Sistema - PicoWeather

Documentação completa da arquitetura interna do PicoWeather, incluindo componentes, fluxos de dados e padrões de design.

## 📋 **Visão Geral**

O PicoWeather segue uma arquitetura em camadas com separação clara de responsabilidades:

```text
┌─────────────────────────────────────────────────────────────┐
│                    Camada de Aplicação                        │
│                        main.py                               │
├─────────────────────────────────────────────────────────────┤
│                    Camada de Drivers                          │
│  sensors_driver.py | display_driver.py | networking_driver │
├─────────────────────────────────────────────────────────────┤
│                    Camada de Abstração                        │
│      DisplayManager | LocaleManager | ConsoleManager       │
├─────────────────────────────────────────────────────────────┤
│                    Camada de Hardware                          │
│    lib/ (dispositivos) | hardware_config.py | utils/        │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ **Componentes Principais**

### **1. main.py - Orquestrador Principal**

**Responsabilidades:**

- Inicialização do sistema
- Coordenação entre drivers
- Gerenciamento do loop principal
- Tratamento de erros e recuperação
- Interface com console

**Fluxo de Inicialização:**

```python
main()
├── PicoWeatherSystem()
│   ├── _load_configuration()
│   ├── init_locale()
│   └── initialize_drivers()
│       ├── DisplayManager
│       ├── DisplayDriver
│       ├── NetworkingDriver
│       ├── TimeDriver
│       ├── SensorsDriver
│       └── InputDriver
└── start_main_loop()
    ├── _read_sensors_sync()
    ├── _update_display()
    ├── _check_buttons()
    └── _update_time()
```

### **2. Drivers - Camada de Abstração de Hardware**

#### **sensors_driver.py**

- **Abstração**: Todos os sensores ambientais
- **Dispositivos**: AHT20, BMP280, BME280, etc.
- **Interface**: `read_all()`, `get_all_status()`
- **Padrão**: Strategy Pattern para diferentes sensores

#### **display_driver.py**

- **Abstração**: Todos os tipos de displays
- **Dispositivos**: SSD1306, ST7567, SH1106, etc.
- **Interface**: `show_framebuffer()`, `clear()`
- **Padrão**: Adapter Pattern para diferentes displays

#### **networking_driver.py**

- **Abstração**: Conectividade de rede
- **Dispositivos**: ESP8285, CYW43, W5500, etc.
- **Interface**: `connect()`, `sync_time()`, `get_status()`
- **Padrão**: Factory Pattern para diferentes tipos de rede

#### **controller_driver.py**

- **Abstração**: Controladores e atuadores
- **Dispositivos**: QN8027, PCA9685, MCP23017, etc.
- **Interface**: `get_controller_data()`, `set_*()`
- **Padrão**: Command Pattern para controle de dispositivos

#### **time_driver.py**

- **Abstração**: Gerenciamento de tempo
- **Fontes**: NTP, manual, RTC
- **Interface**: `get_time()`, `sync_time()`
- **Padrão**: Singleton Pattern para gerenciamento de tempo

#### **input_driver.py**

- **Abstração**: Entrada do usuário
- **Dispositivos**: Botões, encoder, touchscreen
- **Interface**: `check_all()`, `register_callback()`
- **Padrão**: Observer Pattern para eventos de entrada

### **3. Utilitários - Camada de Suporte**

#### **locale_manager.py**

- **Função**: Internacionalização e formatação
- **Componentes**: Traduções, formatação regional
- **Interface**: `t_display()`, `t_console()`, `fmt_*()`

#### **display_manager.py**

- **Função**: Geração de framebuffer
- **Componentes**: Layout engine, renderização
- **Interface**: `generate_framebuffer()`, `next_page()`

#### **console.py**

- **Função**: Console interativo
- **Componentes**: Parser de comandos, interface CLI
- **Interface**: `run_console()`, `execute_command()`

#### **logger.py**

- **Função**: Sistema de logging
- **Componentes**: Formatação de logs, níveis
- **Interface**: `log_info()`, `log_error()`, `log_debug()`

#### **diagnostic.py**

- **Função**: Diagnóstico de hardware
- **Componentes**: Testes de dispositivos, validação
- **Interface**: `run_diagnostics()`, `test_*()`

## 🔄 **Fluxos de Dados**

### **Fluxo Principal de Sensores**

```text
Sensores Físicos
       ↓
lib/[sensor].py (Biblioteca do Dispositivo)
       ↓
sensors_driver.py (Driver de Sensores)
       ↓
main.py (Cache de Dados)
       ↓
display_manager.py (Processamento Visual)
       ↓
display_driver.py (Renderização no Display)
```

### **Fluxo de Atualização do Display**

```text
Dados do Sistema (Sensores, Tempo, Controladores)
       ↓
display_manager.generate_framebuffer()
       ├── Processa layout JSON
       ├── Aplica formatação (locale)
       ├── Renderiza texto (fonte customizada)
       └── Gera framebuffer final
       ↓
display_driver.show_framebuffer()
       ├── Envia dados via SPI/I2C
       ├── Configura display se necessário
       └── Atualiza tela
```

### **Fluxo de Entrada do Usuário**

```text
Botão Físico
       ↓
input_driver.check_all()
       ├── Debounce
       ├── Detecta evento
       └── Chama callback
       ↓
Callback Registrado
       ├── next_page() (DisplayManager)
       ├── toggle_mute() (ControllerDriver)
       └── enter_console() (Main)
```

## 🎨 **Padrões de Design Utilizados**

### **1. Strategy Pattern**

**Uso**: Drivers de sensores e displays
**Implementação**: Classes específicas herdam de classes base

```python
# Exemplo em sensors_driver.py
class SensorDevice:
    def read(self): pass  # Interface base

class AHT20Sensor(SensorDevice):
    def read(self):  # Implementação específica
        # Lógica AHT20
```

### **2. Factory Pattern**

**Uso**: Criação de drivers baseada em configuração
**Implementação**: Funções factory em drivers

```python
# Exemplo em display_driver.py
def create_display_driver(config, hardware):
    display_type = config.get("display", {}).get("type")
    if display_type == "ssd1306_i2c":
        return SSD1306Driver(config, hardware)
    elif display_type == "st7567_spi":
        return ST7567Driver(config, hardware)
```

### **3. Observer Pattern**

**Uso**: Sistema de eventos e callbacks
**Implementação**: Registro de callbacks para botões

```python
# Exemplo em input_driver.py
def register_callback(self, button_name, callback):
    self.callbacks[button_name] = callback

# Quando botão é pressionado
if button_name in self.callbacks:
    self.callbacks[button_name]()
```

### **4. Singleton Pattern**

**Uso**: Gerenciadores globais (locale, time)
**Implementação**: Módulos com estado global

```python
# Exemplo em locale_manager.py
_current_locale = None
_locale_data = {}

def init_locale(locale_code):
    global _current_locale
    _current_locale = locale_code
    # Carrega dados...
```

### **5. Adapter Pattern**

**Uso**: Adaptação de diferentes displays
**Implementação**: Interface unificada para displays diferentes

```python
# Exemplo em display_driver.py
class DisplayDriver:
    def show_framebuffer(self, buffer):
        pass  # Interface unificada

class SSD1306Driver(DisplayDriver):
    def show_framebuffer(self, buffer):
        # Implementação específica SSD1306
```

## 📊 **Estruturas de Dados**

### **Cache de Sensores**

```python
# Em main.py
self.sensor_data = {
    'temperature': 0.0,
    'humidity': 0.0,
    'pressure': 0.0,
    'altitude': 0.0  # Opcional
}

self.sensor_cache = {}  # Cache persistente
self.last_sensor_update = 0
self.sensor_update_count = 0
```

### **Dados de Controlador**

```python
# Em main.py
self.controller_data = {
    'fm_frequency': 100.5,
    'fm_volume': 7,
    'fm_muted': False,
    'fm_stereo': True,
    'fm_rssi': -45
}
```

### **Dados de Tempo**

```python
# Em main.py
self.time_data = {
    'time_only': '14:30:25',
    'date': '25/12/2024',
    'timestamp': 1703505025,
    'timezone': -3
}
```

## 🔧 **Gerenciamento de Estado**

### **Estado do Sistema**

```python
# Em PicoWeatherSystem
class SystemState:
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"
    CONSOLE = "console"
    SHUTDOWN = "shutdown"

self.state = SystemState.INITIALIZING
self.error_count = 0
self.max_errors = 10
```

### **Estado dos Drivers**

```python
# Cada driver mantém seu próprio estado
class DriverState:
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"
    ERROR = "error"

# Verificação de saúde
def is_healthy(self):
    return self.state == DriverState.HEALTHY
```

### **Transições de Estado**

```python
# Em main.py
def handle_error(self, error):
    self.error_count += 1
    if self.error_count >= self.max_errors:
        self.state = SystemState.ERROR
        self.enter_console_mode()
```

## 🚀 **Performance e Otimização**

### **Estratégias de Otimização**

#### **1. Cache de Dados**

- Sensores lidos a cada 5 segundos
- Display atualizado a cada 1 segundo
- Dados reutilizados entre atualizações

#### **2. Operações Assíncronas**

- Leitura de sensores não bloqueante
- Atualizações em paralelo quando possível
- Pequenos delays para evitar busy waiting

#### **3. Gerenciamento de Memória**

- Reutilização de objetos
- Limpeza de variáveis grandes
- Mínimo de alocações dinâmicas

#### **4. Otimização de Display**

- Framebuffer único reutilizado
- Renderização incremental quando possível
- Fonte customizada em memória

### **Métricas de Performance**

```python
# Em modo de diagnóstico
performance_metrics = {
    'sensor_read_time': 50,      # ms
    'display_update_time': 20,   # ms
    'main_loop_time': 10,        # ms
    'memory_usage': 80,          # KB
    'cpu_usage': 30              # %
}
```

## 🔒 **Tratamento de Erros**

### **Estratégias de Recuperação**

#### **1. Graceful Degradation**

- Dispositivos não essenciais podem falhar
- Sistema continua operando parcialmente
- Fallback para modo básico

#### **2. Auto-recuperação**

- Tentativa de reinicialização automática
- Reconexão automática de rede
- Reset de dispositivos problemáticos

#### **3. Modo de Emergência**

- Console interativo para diagnóstico
- Modo seguro com funcionalidades mínimas
- Reset completo como último recurso

### **Hierarquia de Erros**

```python
# Erros críticos (requerem intervenção)
CRITICAL_ERRORS = [
    "memory_exhausted",
    "system_corrupted",
    "hardware_failure"
]

# Erros de warning (recuperação automática)
WARNING_ERRORS = [
    "sensor_timeout",
    "display_glitch",
    "network_disconnected"
]

# Erros de info (apenas logging)
INFO_ERRORS = [
    "device_not_found",
    "configuration_incomplete"
]
```

## 🧪 **Testes e Validação**

### **Estratégias de Teste**

#### **1. Testes de Unidade**

- Teste individual de cada driver
- Validação de interfaces
- Mock de hardware para testes

#### **2. Testes de Integração**

- Interação entre drivers
- Fluxos de dados completos
- Compatibilidade de hardware

#### **3. Testes de Sistema**

- Funcionalidade end-to-end
- Performance sob carga
- Recuperação de erros

### **Ferramentas de Diagnóstico**

```python
# Em diagnostic.py
class DiagnosticSuite:
    def test_hardware(self):
        # Teste de todos os dispositivos
        pass
    
    def test_communication(self):
        # Teste de barramentos I2C/SPI
        pass
    
    def test_performance(self):
        # Teste de performance e memória
        pass
    
    def test_errors(self):
        # Simulação de condições de erro
        pass
```

## 🔮 **Extensibilidade e Manutenibilidade**

### **Princípios de Design**

#### **1. Baixo Acoplamento**

- Drivers independentes
- Interface clara entre componentes
- Mínimas dependências cruzadas

#### **2. Alta Coesão**

- Cada componente com responsabilidade única
- Funções relacionadas agrupadas
- Lógica centralizada por tipo

#### **3. Aberto/Fechado**

- Aberto para extensão (novos dispositivos)
- Fechado para modificação (interfaces estáveis)
- Configuração externa para personalização

#### **4. Inversão de Dependência**

- Dependência de abstrações, não implementações
- Injeção de dependências via configuração
- Fácil substituição de componentes

### **Manutenibilidade**

#### **1. Documentação**

- Docstrings em todas as classes públicas
- Comentários em lógica complexa
- Exemplos de uso

#### **2. Logging**

- Logs estruturados com contexto
- Níveis apropriados de verbosidade
- Informações úteis para debugging

#### **3. Configuração**

- Configuração externa em JSON
- Valores padrão sensíveis
- Validação de configuração

#### **4. Testabilidade**

- Interfaces mockáveis
- Pontos de injeção para testes
- Cobertura de testes automatizados

## 📈 **Evolução da Arquitetura**

### **Versão 1.0 - Arquitetura Inicial**

- Sistema monolítico
- Drivers acoplados
- Configuração hardcoded

### **Versão 2.0 - Arquitetura Atual**

- Separação em camadas
- Drivers independentes
- Configuração externa
- Sistema de locales

### **Versão 3.0 - Roadmap Futuro**

- Microkernel architecture
- Plugin system
- Configuração dinâmica
- API REST para controle

---

## 📞 **Suporte**

Para questões sobre arquitetura:

- Consulte diagramas de fluxo
- Estude exemplos de drivers
- Verifique padrões estabelecidos

---

**Guia válido para:** PicoWeather v2.0+  
**Última atualização:** 2024-12-25
