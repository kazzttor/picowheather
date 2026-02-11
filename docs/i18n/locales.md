# Sistema de Locales - Guia de Internacionalização

Documentação completa do sistema de internacionalização do PicoWeather.

## 📋 **Visão Geral**

O sistema de locales permite que o PicoWeather suporte múltiplos idiomas e formatações regionais. Ele inclui:

- Tradução de textos para display e console
- Formatação de números, datas e horas
- Suporte a caracteres especiais (português, etc.)
- Sistema de fallback automático
- Fácil adição de novos idiomas

## 🌍 **Estrutura dos Locales**

```text
locales/
├── display_pt_BR.json    # Textos do display em português brasileiro
├── console_pt_BR.json     # Textos do console em português brasileiro
├── display_es_ES.json     # Textos do display em espanhol (exemplo)
├── console_es_ES.json     # Textos do console em espanhol (exemplo)
└── [outros idiomas]...
```

Cada idioma tem dois arquivos:

- **display_**: Textos mostrados no display
- **console_**: Textos mostrados no console interativo

## 📝 **Arquivos de Locale**

### **display_pt_BR.json - Display em Português**

```json
{
  "units": {
    "temperature": "°C",
    "humidity": "%",
    "pressure": "hPa",
    "frequency": "MHz"
  },
  "formats": {
    "date": "dd/mm/yyyy",
    "time": "HH:MM:SS",
    "datetime": "dd/mm/yyyy HH:MM",
    "decimal": ",",
    "thousands": "."
  },
  "labels": {
    "temperature": "Temperatura",
    "humidity": "Umidade",
    "pressure": "Pressão",
    "frequency": "Frequência",
    "fm_radio": "Rádio FM",
    "volume": "Volume",
    "signal": "Sinal",
    "status": "Status",
    "time": "Hora",
    "date": "Data"
  },
  "messages": {
    "no_sensor": "Sem sensor",
    "no_data": "Sem dados",
    "connecting": "Conectando...",
    "connected": "Conectado",
    "error": "Erro",
    "loading": "Carregando..."
  }
}
```

### **console_pt_BR.json - Console em Português**

```json
{
  "commands": {
    "help": "help",
    "status": "status",
    "sensors": "sensors",
    "scan": "scan",
    "time": "time",
    "settime": "settime",
    "wifi": "wifi",
    "fm": "fm",
    "diagnostic": "diagnostic",
    "config": "config",
    "save": "save",
    "quit": "quit"
  },
  "descriptions": {
    "help": "Mostrar ajuda",
    "status": "Status do sistema",
    "sensors": "Ler sensores",
    "scan": "Escanear I2C",
    "time": "Mostrar hora",
    "settime": "Ajustar hora",
    "wifi": "Status WiFi",
    "fm": "Informações FM",
    "diagnostic": "Diagnóstico completo",
    "config": "Mostrar configuração",
    "save": "Salvar configuração",
    "quit": "Sair do console"
  },
  "menus": {
    "main": "=== Menu Console PicoWeather ===",
    "sensors": "--- Comandos de Sensores ---",
    "display": "--- Comandos de Display ---",
    "radio": "--- Comandos de Rádio ---",
    "network": "--- Comandos de Rede ---",
    "system": "--- Comandos de Sistema ---"
  },
  "messages": {
    "main_loaded": "Sistema PicoWeather carregado (placa: {board})",
    "system_startup": "Iniciando sistema...",
    "init_display": "Inicializando DISPLAY... ",
    "init_sensors": "Inicializando SENSORES... ",
    "init_networking": "Inicializando REDE... ",
    "init_fm": "Inicializando FM... ",
    "ok": "OK",
    "fail": "FALHOU",
    "status_fail": "FALHOU ({error})",
    "entering_console": "Entrando no modo console",
    "exiting_console": "Saindo do modo console"
  },
  "errors": {
    "command_not_found": "Comando não encontrado: {cmd}",
    "invalid_arguments": "Argumentos inválidos",
    "device_not_found": "Dispositivo não encontrado",
    "operation_failed": "Operação falhou",
    "permission_denied": "Permissão negada"
  }
}
```

## 🎨 **Sistema de Formatação**

### **Formatadores de Números**

O sistema inclui formatadores específicos para cada locale:

```python
# Formatação de temperatura
fmt_temp(26.5)  # pt_BR: "26,5°C", en_US: "26.5°C"

# Formatação de umidade
fmt_humidity(75.2)  # pt_BR: "75,2%", en_US: "75.2%"

# Formatação de pressão
fmt_pressure(1013.25)  # pt_BR: "1.013,25 hPa", en_US: "1,013.25 hPa"

# Formatação de frequência
fmt_frequency(100.5)  # pt_BR: "100,5 MHz", en_US: "100.5 MHz"
```

### **Formatadores de Data/Hora**

```python
# Formatação de data
fmt_date(datetime.now())  # pt_BR: "25/12/2024", en_US: "12/25/2024"

# Formatação de hora
fmt_time(datetime.now())  # pt_BR: "14:30:25", en_US: "02:30:25 PM"

# Formatação completa
fmt_datetime(datetime.now())  # pt_BR: "25/12/2024 14:30", en_US: "12/25/2024 02:30 PM"
```

## 🔧 **Locale Manager**

### **Funções Principais**

```python
from utils.locale_manager import (
    init_locale,           # Inicializar locale
    t_display,            # Tradução para display
    t_console,            # Tradução para console
    fmt_temp,              # Formatar temperatura
    fmt_humidity,          # Formatar umidade
    fmt_pressure,          # Formatar pressão
    fmt_frequency,         # Formatar frequência
    fmt_date,              # Formatar data
    fmt_time,              # Formatar hora
    fmt_datetime           # Formatar data/hora
)
```

### **Inicialização**

```python
# Inicializar locale (feito no main.py)
init_locale("pt_BR")  # Carrega locale pt_BR

# Se locale não existir, usa fallback inglês
init_locale("fr_FR")  # Carrega fallback inglês se fr_FR não existir
```

### **Uso das Traduções**

```python
# Para display
label = t_display("labels.temperature")  # "Temperatura"
unit = t_display("units.temperature")    # "°C"
msg = t_display("messages.no_sensor")    # "Sem sensor"

# Para console
cmd_desc = t_console("descriptions.help")  # "Mostrar ajuda"
menu_title = t_console("menus.main")       # "=== Menu Console PicoWeather ==="
error_msg = t_console("errors.command_not_found", cmd="teste")  # "Comando não encontrado: teste"
```

## 🌐 **Adicionando Novos Idiomas**

### **Passo 1: Criar Arquivos de Locale**

#### **display_es_ES.json (Espanhol)**

```json
{
  "units": {
    "temperature": "°C",
    "humidity": "%",
    "pressure": "hPa",
    "frequency": "MHz"
  },
  "formats": {
    "date": "dd/mm/yyyy",
    "time": "HH:MM:SS",
    "datetime": "dd/mm/yyyy HH:MM",
    "decimal": ",",
    "thousands": "."
  },
  "labels": {
    "temperature": "Temperatura",
    "humidity": "Humedad",
    "pressure": "Presión",
    "frequency": "Frecuencia",
    "fm_radio": "Radio FM",
    "volume": "Volumen",
    "signal": "Señal",
    "status": "Estado",
    "time": "Hora",
    "date": "Fecha"
  },
  "messages": {
    "no_sensor": "Sin sensor",
    "no_data": "Sin datos",
    "connecting": "Conectando...",
    "connected": "Conectado",
    "error": "Error",
    "loading": "Cargando..."
  }
}
```

#### **console_es_ES.json (Espanhol)**

```json
{
  "commands": {
    "help": "ayuda",
    "status": "estado",
    "sensors": "sensores",
    "scan": "escanear",
    "time": "hora",
    "settime": "ajustar_hora",
    "wifi": "wifi",
    "fm": "fm",
    "diagnostic": "diagnostico",
    "config": "config",
    "save": "guardar",
    "quit": "salir"
  },
  "descriptions": {
    "help": "Mostrar ayuda",
    "status": "Estado del sistema",
    "sensors": "Leer sensores",
    "scan": "Escanear I2C",
    "time": "Mostrar hora",
    "settime": "Ajustar hora",
    "wifi": "Estado WiFi",
    "fm": "Informaciones FM",
    "diagnostic": "Diagnóstico completo",
    "config": "Mostrar configuración",
    "save": "Guardar configuración",
    "quit": "Salir del console"
  },
  "menus": {
    "main": "=== Menú Console PicoWeather ===",
    "sensors": "--- Comandos de Sensores ---",
    "display": "--- Comandos de Display ---",
    "radio": "--- Comandos de Radio ---",
    "network": "--- Comandos de Red ---",
    "system": "--- Comandos de Sistema ---"
  },
  "messages": {
    "main_loaded": "Sistema PicoWeather cargado (placa: {board})",
    "system_startup": "Iniciando sistema...",
    "init_display": "Inicializando DISPLAY... ",
    "init_sensors": "Inicializando SENSORES... ",
    "init_networking": "Inicializando RED... ",
    "init_fm": "Inicializando FM... ",
    "ok": "OK",
    "fail": "FALLÓ",
    "status_fail": "FALLÓ ({error})",
    "entering_console": "Entrando en modo console",
    "exiting_console": "Saliendo del modo console"
  },
  "errors": {
    "command_not_found": "Comando no encontrado: {cmd}",
    "invalid_arguments": "Argumentos inválidos",
    "device_not_found": "Dispositivo no encontrado",
    "operation_failed": "Operación falló",
    "permission_denied": "Permiso denegado"
  }
}
```

### **Passo 2: Atualizar Configuração**

```json
// Em config.json
{
  "system": {
    "locale": "es_ES"  // Mudar para novo idioma
  }
}
```

### **Passo 3: Testar**

```python
# No console PicoWeather
pico> config
# Verificar se locale está correto

pico> help
# Deve mostrar menu em espanhol
```

## 🎯 **Locale Fallback (Inglês)**

O sistema inclui um fallback automático em inglês quando um locale não está disponível:

```python
# Fallback embutido (em locale_manager.py)
ENGLISH_FALLBACK = {
    "display": {
        "units": {
            "temperature": "°C",
            "humidity": "%",
            "pressure": "hPa",
            "frequency": "MHz"
        },
        "labels": {
            "temperature": "Temperature",
            "humidity": "Humidity",
            "pressure": "Pressure",
            "frequency": "Frequency"
        }
    },
    "console": {
        "commands": {
            "help": "help",
            "status": "status",
            "sensors": "sensors"
        },
        "descriptions": {
            "help": "Show help",
            "status": "System status",
            "sensors": "Read sensors"
        }
    }
}
```

## 🔍 **Validação e Debug**

### **Verificação de Locale**

```python
# No console PicoWeather:
pico> locale
# Mostra locale atual e status

pico> locale test
# Testa todas as traduções disponíveis

pico> locale list
# Lista todos os locales disponíveis
```

### **Teste de Traduções**

```python
# Teste programático
from utils.locale_manager import t_display, t_console

# Testar tradução específica
temp_label = t_display("labels.temperature")
print(f"Label: {temp_label}")

# Testar tradução inexistente (deve usar fallback)
unknown = t_display("labels.unknown")
print(f"Unknown: {unknown}")  # Deve retornar "labels.unknown"
```

### **Verificação de Formatação**

```python
# Testar formatadores
from utils.locale_manager import fmt_temp, fmt_date

# Testar formatação de temperatura
temp_str = fmt_temp(26.5)
print(f"Temperature: {temp_str}")

# Testar formatação de data
import datetime
date_str = fmt_date(datetime.datetime.now())
print(f"Date: {date_str}")
```

## 📝 **Boas Práticas**

### **Nomenclatura de Chaves**

- Use nomes descritivos: `labels.temperature` em vez de `temp`
- Mantenha consistência: `units.*`, `labels.*`, `messages.*`
- Use inglês como base das chaves

### **Traduções**

- Mantenha comprimento similar para textos do display
- Use terminologia consistente
- Considere caracteres especiais do idioma

### **Formatação Regional**

- Respeite formatos locais (data, hora, números)
- Considere separadores decimais e de milhar
- Adapte unidades se necessário

## 🚀 **Casos Avançados**

### **Locale Dinâmico**

```python
# Mudar locale em runtime
from utils.locale_manager import init_locale

init_locale("es_ES")  # Mudar para espanhol
# Interface atualizada automaticamente
```

### **Locale por Componente**

```python
# Possível extensão: diferentes locales para display/console
init_display_locale("pt_BR")
init_console_locale("en_US")
```

### **Locale com Parâmetros**

```python
# Traduções com parâmetros
t_console("messages.main_loaded", board="pico_clone")
# Resultado: "Sistema PicoWeather carregado (placa: pico_clone)"
```

## 🔄 **Atualização de Locales**

### **Método 1: Editar Arquivos**

1. Edite arquivos JSON em `locales/`
2. Faça upload para o Pico
3. Reinicie sistema

### **Método 2: Runtime**

```python
# Atualizar locale dinamicamente
import json

# Carregar locale modificado
with open('locales/display_pt_BR.json', 'r') as f:
    locale_data = json.load(f)

# Modificar
locale_data['labels']['new_label'] = 'Novo Rótulo'

# Salvar
with open('locales/display_pt_BR.json', 'w') as f:
    json.dump(locale_data, f)

# Recarregar locale
init_locale("pt_BR")
```

## 📊 **Tabela de Locales Suportados**

| Código | Idioma | Status | Arquivos |
| ------ | ------ | ------ | ---------- |
| `pt_BR` | Português Brasileiro | ✅ Completo | display, console |
| `en_US` | Inglês Americano | ✅ Fallback | embutido |
| `es_ES` | Espanhol | 🔄 Planejado | display, console |
| `fr_FR` | Francês | 🔄 Planejado | display, console |
| `de_DE` | Alemão | 🔄 Planejado | display, console |
| `it_IT` | Italiano | 🔄 Planejado | display, console |

## 🎨 **Personalização Avançada**

### **Cores e Estilos (Futuro)**

```json
{
  "styles": {
    "text_color": "white",
    "background_color": "black",
    "highlight_color": "blue",
    "error_color": "red"
  }
}
```

### **Fontes Específicas**

```json
{
  "fonts": {
    "standard": "font_8x8",
    "large": "font_12x16",
    "small": "font_6x8",
    "special": "font_custom"
  }
}
```

### **Formatação Condicional**

```json
{
  "conditional_formats": {
    "temperature": {
      "cold": {"threshold": 10, "color": "blue"},
      "normal": {"threshold": 25, "color": "green"},
      "hot": {"threshold": 999, "color": "red"}
    }
  }
}
```

---

## 📞 **Suporte**

Para problemas com locales:

- Use `pico> locale test` para validar
- Verifique sintaxe JSON dos arquivos
- Confirme encoding UTF-8

---

**Guia válido para:** PicoWeather v2.0+  
**Última atualização:** 2024-12-25
