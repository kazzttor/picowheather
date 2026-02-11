# display_layouts.json - Guia de Layout de Telas

Documentação completa do arquivo de configuração de layout das telas do PicoWeather.

## 📋 **Visão Geral**

O `display_layouts.json` define como as informações são organizadas e exibidas no display. Ele permite:

- Criar múltiplas telas/páginas
- Organizar elementos visuais
- Definir tempo de exibição
- Configurar formatação de dados
- Criar layouts responsivos

## 🎨 **Estrutura do Arquivo**

```json
{
  "st7567_spi": {
    "pages": [...],
    "fallback": {...}
  },
  "ssd1306_i2c": {
    "pages": [...],
    "fallback": {...}
  }
}
```

Cada tipo de display tem sua própria configuração de layout.

## 📐 **Elementos de Layout**

### **Tipos de Elementos Suportados**

| Tipo | Descrição | Parâmetros |
| --- | --- | --- |
| `date` | Data atual | `x`, `y`, `format` |
| `time` | Hora atual | `x`, `y`, `format` |
| `sensor` | Dados de sensor | `x`, `y`, `name`, `label`, `unit`, `format` |
| `controller` | Dados de controlador | `x`, `y`, `name`, `label`, `unit`, `format` |
| `text` | Texto estático | `x`, `y`, `text` |
| `separator` | Linha separadora | `x`, `y`, `length`, `style` |

### **Posicionamento (x, y)**

- **Valores numéricos**: Posição em pixels (0-127 para x, 0-63 para y)
- **"center"**: Centraliza horizontalmente
- **"left"**, **"right"**: Alinhamento horizontal
- **Exemplos**:

  ```json
  {"x": 0, "y": 10}        // Canto esquerdo, linha 10
  {"x": "center", "y": 20} // Centralizado, linha 20
  {"x": 64, "y": "center"} // Meio da tela, centralizado verticalmente
  ```

### **Formatação (format)**

- **Números**: Especificadores de formato Python
  - `"5.1f"`: 123.4 → 123.4
  - `"3.0f"`: 123.4 → 123
  - `"4.1f"`: 100.5 → 100.5
- **Strings**: Formatos de data/hora
  - `"%d/%m/%Y"`: 25/12/2024
  - `"%H:%M:%S"`: 14:30:25

## 🖼️ **Layouts por Tipo de Display**

### **ST7567 SPI (Layout Completo)**

```json
"st7567_spi": {
  "pages": [
    {
      "name": "complete",
      "duration": 1000,
      "requires_sensors": ["aht20", "temperature", "humidity", "bmp280", "pressure"],
      "requires_controller": ["fm_transmitter"],
      "elements": [
        {"type": "date", "x": "center", "y": 0},
        {"type": "time", "x": "center", "y": 10},
        {"type": "separator", "x": 0, "y": 20, "length": 16, "style": "double"},
        {"type": "sensor", "name": "temperature", "x": "center", "y": 22, "label": "Temp:", "unit": "C", "format": "5.1f"},
        {"type": "sensor", "name": "humidity", "x": "center", "y": 32, "label": "Umid:", "unit": "%", "format": "3.0f"},
        {"type": "sensor", "name": "pressure", "x": "center", "y": 42, "label": "Pres:", "unit": "hPa", "format": "5.1f"},
        {"type": "controller", "name": "fm_frequency", "x": "center", "y": 52, "label": "FM:", "unit": "MHz", "format": "4.1f"}
      ]
    }
  ],
  "fallback": {
    "name": "time_only",
    "duration": 1000,
    "elements": [
      {"type": "date", "x": "center", "y": 10},
      {"type": "time", "x": "center", "y": 25},
      {"type": "separator", "x": 0, "y": 35, "length": 16, "style": "single"},
      {"type": "text", "x": "center", "y": 45, "text": "Sem sensor"}
    ]
  }
}
```

### **SSD1306 I2C (Layout Múltiplas Páginas)**

```json
"ssd1306_i2c": {
  "pages": [
    {
      "name": "temperature",
      "duration": 3000,
      "requires_sensors": ["aht20", "temperature"],
      "elements": [
        {"type": "date", "x": "center", "y": 0},
        {"type": "time", "x": "center", "y": 10},
        {"type": "separator", "x": "center", "y": 18, "length": 16},
        {"type": "sensor", "name": "temperature", "x": "center", "y": 30, "label": "Temp:", "unit": "C", "format": "5.1f"}
      ]
    },
    {
      "name": "humidity",
      "duration": 3000,
      "requires_sensors": ["aht20", "humidity"],
      "elements": [
        {"type": "date", "x": "center", "y": 0},
        {"type": "time", "x": "center", "y": 10},
        {"type": "separator", "x": "center", "y": 18, "length": 16},
        {"type": "sensor", "name": "humidity", "x": "center", "y": 30, "label": "Umid:", "unit": "%", "format": "3.0f"}
      ]
    },
    {
      "name": "pressure",
      "duration": 3000,
      "requires_sensors": ["bmp280", "pressure"],
      "elements": [
        {"type": "date", "x": "center", "y": 0},
        {"type": "time", "x": "center", "y": 10},
        {"type": "separator", "x": "center", "y": 18, "length": 16},
        {"type": "sensor", "name": "pressure", "x": "center", "y": 30, "label": "Pres:", "unit": "hPa", "format": "5.1f"}
      ]
    },
    {
      "name": "fm",
      "duration": 3000,
      "requires_controller": ["fm_transmitter"],
      "elements": [
        {"type": "date", "x": "center", "y": 0},
        {"type": "time", "x": "center", "y": 10},
        {"type": "separator", "x": "center", "y": 18, "length": 16},
        {"type": "controller", "name": "fm_frequency", "x": "center", "y": 26, "label": "FM:", "unit": "MHz", "format": "4.1f"},
        {"type": "controller", "name": "fm_volume", "x": "center", "y": 36, "label": "Vol:", "unit": "", "format": "1d"}
      ]
    }
  ],
  "fallback": {
    "name": "time_only",
    "duration": 3000,
    "elements": [
      {"type": "date", "x": "center", "y": 10},
      {"type": "time", "x": "center", "y": 25},
      {"type": "separator", "x": "center", "y": 35, "length": 16},
      {"type": "text", "x": "center", "y": 45, "text": "Sem sensor"}
    ]
  }
}
```

## 📝 **Parâmetros Detalhados**

### **Parâmetros da Página**

| Parâmetro | Tipo | Descrição |
| --- | --- | --- |
| `name` | string | Nome identificador da página |
| `duration` | number | Tempo de exibição em milissegundos |
| `requires_sensors` | array | Lista de sensores necessários |
| `requires_controller` | array | Lista de controladores necessários |
| `elements` | array | Lista de elementos visuais |

### **Parâmetros dos Elementos**

#### **Elementos de Data/Hora**

```json
{"type": "date", "x": "center", "y": 0, "format": "%d/%m/%Y"}
{"type": "time", "x": "center", "y": 10, "format": "%H:%M:%S"}
```

#### **Elementos de Sensor**

```json
{
  "type": "sensor",
  "name": "temperature",           // Nome do sensor
  "x": "center",                   // Posição X
  "y": 22,                         // Posição Y
  "label": "Temp:",                // Rótulo
  "unit": "C",                     // Unidade
  "format": "5.1f"                 // Formato numérico
}
```

#### **Elementos de Controlador**

```json
{
  "type": "controller",
  "name": "fm_frequency",          // Nome do controlador
  "x": "center",                   // Posição X
  "y": 52,                         // Posição Y
  "label": "FM:",                  // Rótulo
  "unit": "MHz",                   // Unidade
  "format": "4.1f"                 // Formato numérico
}
```

#### **Elementos de Texto**

```json
{
  "type": "text",
  "x": "center",                   // Posição X
  "y": 45,                         // Posição Y
  "text": "Sem sensor"             // Texto estático
}
```

#### **Elementos de Seção**

```json
{
  "type": "section",
  "requires_sensors": ["temperature", "humidity"],  // Sensores necessários
  "requires_controller": ["fm_transmitter"],        // Controladores necessários
  "elements": [                                     // Elementos da seção
    {
      "type": "sensor",
      "name": "temperature",
      "x": "center",
      "y": 30
    },
    {
      "type": "controller", 
      "name": "fm_frequency",
      "x": "center",
      "y": 40
    }
  ]
}
```

**Nota:** Seções permitem criar layouts condicionais onde elementos são exibidos apenas se os requisitos forem atendidos.

#### **Separadores**

```json
{
  "type": "separator",
  "x": 0,                          // Posição X inicial
  "y": 20,                         // Posição Y
  "length": 16,                    // Comprimento em caracteres
  "style": "double"                // Estilo: "single", "double"
}
```

## 🎯 **Nomes de Sensores e Controladores**

### **Sensores Disponíveis**

| Nome | Descrição | Formato Típico |
| --- | --- | --- |
| `temperature` | Temperatura (°C) | `"5.1f"` |
| `humidity` | Umidade (%) | `"3.0f"` |
| `pressure` | Pressão (hPa) | `"5.1f"` |
| `altitude` | Altitude (m) | `"4.0f"` |

### **Controladores Disponíveis**

| Nome | Descrição | Formato Típico |
| --- | --- | --- |
| `fm_frequency` | Frequência FM (MHz) | `"4.1f"` |
| `fm_volume` | Volume FM (0-15) | `"1d"` |
| `fm_rssi` | Sinal FM (dBm) | `"4d"` |
| `fm_stereo` | Modo estéreo | `"s"` |

## 🎨 **Exemplos de Layout Personalizados**

### **Layout Minimalista**

```json
{
  "name": "minimal",
  "duration": 2000,
  "elements": [
    {"type": "time", "x": "center", "y": 8},
    {"type": "sensor", "name": "temperature", "x": "center", "y": 24, "label": "", "unit": "°C", "format": "4.1f"},
    {"type": "sensor", "name": "humidity", "x": "center", "y": 40, "label": "", "unit": "%", "format": "3.0f"}
  ]
}
```

### **Layout Detalhado**

```json
{
  "name": "detailed",
  "duration": 5000,
  "elements": [
    {"type": "date", "x": 0, "y": 0, "format": "%d/%m"},
    {"type": "time", "x": "right", "y": 0, "format": "%H:%M"},
    {"type": "separator", "x": 0, "y": 10, "length": 16, "style": "single"},
    {"type": "text", "x": 0, "y": 18, "text": "Temp:"},
    {"type": "sensor", "name": "temperature", "x": "right", "y": 18, "label": "", "unit": "°C", "format": "5.1f"},
    {"type": "text", "x": 0, "y": 26, "text": "Umid:"},
    {"type": "sensor", "name": "humidity", "x": "right", "y": 26, "label": "", "unit": "%", "format": "3.0f"},
    {"type": "text", "x": 0, "y": 34, "text": "Pres:"},
    {"type": "sensor", "name": "pressure", "x": "right", "y": 34, "label": "", "unit": "hPa", "format": "5.1f"},
    {"type": "separator", "x": 0, "y": 42, "length": 16, "style": "single"},
    {"type": "controller", "name": "fm_frequency", "x": 0, "y": 50, "label": "FM:", "unit": "MHz", "format": "4.1f"},
    {"type": "controller", "name": "fm_volume", "x": "right", "y": 50, "label": "Vol:", "unit": "", "format": "1d"}
  ]
}
```

### **Layout com Ícones**

```json
{
  "name": "with_icons",
  "duration": 3000,
  "elements": [
    {"type": "time", "x": "center", "y": 0},
    {"type": "separator", "x": 0, "y": 10, "length": 16, "style": "double"},
    {"type": "text", "x": 0, "y": 18, "text": "🌡"},
    {"type": "sensor", "name": "temperature", "x": 20, "y": 18, "label": "", "unit": "°C", "format": "4.1f"},
    {"type": "text", "x": 0, "y": 26, "text": "💧"},
    {"type": "sensor", "name": "humidity", "x": 20, "y": 26, "label": "", "unit": "%", "format": "3.0f"},
    {"type": "text", "x": 0, "y": 34, "text": "📊"},
    {"type": "sensor", "name": "pressure", "x": 20, "y": 34, "label": "", "unit": "hPa", "format": "5.1f"},
    {"type": "text", "x": 0, "y": 42, "text": "📻"},
    {"type": "controller", "name": "fm_frequency", "x": 20, "y": 42, "label": "", "unit": "MHz", "format": "4.1f"}
  ]
}
```

### **Layout com Seções Condiionais**

```json
{
  "name": "inteligente",
  "duration": 3000,
  "elements": [
    {"type": "date", "x": "center", "y": 0},
    {"type": "time", "x": "center", "y": 10},
    {"type": "separator", "x": "center", "y": 18, "length": 16},
    
    {
      "type": "section",
      "requires_sensors": ["temperature"],
      "elements": [
        {"type": "sensor", "name": "temperature", "x": "center", "y": 30, "label": "Temp:"}
      ]
    },
    
    {
      "type": "section",
      "requires_sensors": ["humidity"], 
      "elements": [
        {"type": "sensor", "name": "humidity", "x": "center", "y": 40, "label": "Umid:"}
      ]
    },
    
    {
      "type": "section",
      "requires_controller": ["fm_transmitter"],
      "elements": [
        {"type": "controller", "name": "fm_frequency", "x": "center", "y": 50, "label": "FM:"}
      ]
    }
  ]
}
```

## 🔄 **Sistema de Páginas**

### **Navegação Automática**

- O sistema alterna entre páginas automaticamente
- Tempo de cada página definido por `duration`
- Páginas com dispositivos não disponíveis são puladas
- Seções dentro de páginas são exibidas condicionalmente

### **Navegação Manual**

- **Botão UP/SELECT**: Próxima página
- **Botão DOWN**: Página anterior
- **Botão BACK**: Voltar à primeira página

### **Prioridade de Páginas e Seções**

1. **Nível de Página**: Verifica `requires_sensors` e `requires_controller`
2. **Nível de Seção**: Verifica requisitos de cada seção individualmente
3. Páginas com todos os dispositivos disponíveis têm prioridade
4. Seções sem requisitos são ignoradas, mas a página continua sendo exibida
5. Se nenhuma página estiver completa, usa `fallback`

## 🛠️ **Personalização Avançada**

### **Layout Condicional**

```json
{
  "name": "conditional",
  "duration": 2000,
  "requires_sensors": ["temperature"],
  "elements": [
    {"type": "sensor", "name": "temperature", "x": "center", "y": 20, "label": "", "unit": "°C", "format": "4.1f"},
    {"type": "text", "x": "center", "y": 40, "text": "Apenas temperatura disponível"}
  ]
}
```

### **Layout Dinâmico**

```json
{
  "name": "dynamic",
  "duration": 1000,
  "elements": [
    {"type": "time", "x": "center", "y": 0},
    {"type": "separator", "x": 0, "y": 10, "length": 16, "style": "single"},
    {"type": "sensor", "name": "temperature", "x": 0, "y": 18, "label": "T:", "unit": "", "format": "4.1f"},
    {"type": "sensor", "name": "humidity", "x": 64, "y": 18, "label": "H:", "unit": "", "format": "3.0f"},
    {"type": "sensor", "name": "pressure", "x": 0, "y": 26, "label": "P:", "unit": "", "format": "4.0f"},
    {"type": "controller", "name": "fm_frequency", "x": 64, "y": 26, "label": "F:", "unit": "", "format": "3.1f"}
  ]
}
```

## 🔍 **Validação e Debug**

### **Verificação de Layout**

```python
# No console do PicoWeather:
pico> display status
# Mostra página atual e elementos

pico> display next
# Testa navegação para próxima página

pico> diagnostic
# Verifica todos os elementos e dispositivos
```

### **Erros Comuns**

#### **Posição Inválida**

```json
// ERRADO:
{"x": 200, "y": 100}  // Fora do display (128x64)

// CORRETO:
{"x": "center", "y": 32}  // Centralizado
```

#### **Formato Incorreto**

```json
// ERRADO:
{"format": "%.2f"}  // Formato inválido para MicroPython

// CORRETO:
{"format": "5.2f"}  // Formato válido
```

#### **Nome de Sensor Incorreto**

```json
// ERRADO:
{"name": "temp"}  // Nome não reconhecido

// CORRETO:
{"name": "temperature"}  // Nome válido
```

## 📝 **Dicas de Design**

### **Princípios de Layout**

1. **Hierarquia Visual**: Informações mais importantes no topo
2. **Espaçamento**: Deixe espaço entre elementos
3. **Consistência**: Use alinhamento consistente
4. **Legibilidade**: Tamanho de texto adequado para display

### **Otimização para Display Pequeno**

1. **Máximo de 4-5 elementos por página**
2. **Use abreviações em rótulos**
3. **Centralize informações importantes**
4. **Evite sobreposição de elementos**

### **Acessibilidade**

1. **Contraste adequado entre texto e fundo**
2. **Tamanho de texto legível**
3. **Informações críticas sempre visíveis**
4. **Navegação intuitiva**

## 🔄 **Atualização de Layout**

### **Método 1: Editar Arquivo**

1. Edite `display_layouts.json` no computador
2. Faça upload para o Pico
3. Reinicie o sistema

### **Método 2: Runtime**

```python
# Programaticamente:
import json
with open('display_layouts.json', 'r') as f:
    layouts = json.load(f)

# Modificar layout
layouts['ssd1306_i2c']['pages'][0]['duration'] = 5000

with open('display_layouts.json', 'w') as f:
    json.dump(layouts, f)
```

### **Método 3: Console**

```python
# No console PicoWeather:
pico> display reload
# Recarrega layouts do arquivo
```

---

## 📞 **Suporte**

Para problemas com layout:

- Use `pico> display status` para verificar
- Teste layouts incrementalmente
- Consulte exemplos neste guia

---

**Guia válido para:** PicoWeather v2.0+  
**Última atualização:** 2024-12-25
