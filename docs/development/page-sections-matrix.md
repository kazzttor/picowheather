# Matriz de Comportamento - Páginas vs Seções

## Combinações Possíveis

| Tipo de Página | Tem Requisitos? | Tem Seções? | Comportamento |
| --- | --- | --- | --- |
| **Universal** | ❌ Não | ✅ Sim | Sempre válida, renderiza apenas seções atendidas |
| **Específica com Seções** | ✅ Sim | ✅ Sim | Válida só se requisitos atendidos, depois renderiza seções |
| **Básica com Requisitos** | ✅ Sim | ❌ Não | Válida só se requisitos atendidos, renderiza tudo |
| **Básica sem Requisitos** | ❌ Não | ❌ Não | Sempre válida, sempre renderiza tudo |

## Exemplos Práticos

### 1. **Universal** - Adapta-se a qualquer hardware

```json
{
  "name": "universal",
  "elements": [
    {"type": "date", "x": "center", "y": 0},
    {"type": "time", "x": "center", "y": 10},
    {"type": "section", "requires_sensors": ["temperature"], "elements": [...]},
    {"type": "section", "requires_sensors": ["pressure"], "elements": [...]}
  ]
}
```

**Resultado**: Sempre exibida. Mostra apenas seções cujos dispositivos estão presentes.

### 2. **Específica com Seções** - Hardware completo necessário

```json
{
  "name": "completa",
  "requires_sensors": ["temperature"],
  "requires_controller": ["fm_transmitter"],
  "elements": [
    {"type": "date", "x": "center", "y": 0},
    {"type": "time", "x": "center", "y": 10},
    {"type": "section", "requires_sensors": ["humidity"], "elements": [...]}
  ]
}
```

**Resultado**: Exibida só se temperatura E FM presentes. Depois ainda verifica umidade na seção.

### 3. **Básica com Requisitos** - Página inteira condicional

```json
{
  "name": "meteo",
  "requires_sensors": ["temperature", "pressure"],
  "elements": [
    {"type": "date", "x": "center", "y": 0},
    {"type": "sensor", "name": "temperature", "x": "center", "y": 20},
    {"type": "sensor", "name": "pressure", "x": "center", "y": 30}
  ]
}
```

**Resultado**: Exibida só se temperatura E pressão presentes.

### 4. **Básica sem Requisitos** - Sempre visível

```json
{
  "name": "status",
  "elements": [
    {"type": "date", "x": "center", "y": 0},
    {"type": "time", "x": "center", "y": 10},
    {"type": "text", "x": "center", "y": 20, "text": "Sistema OK"}
  ]
}
```

**Resultado**: Sempre exibida.

## Quando Usar Cada Tipo

### **Universal** ✅

- **Ideal para**: Sistemas com hardware variável
- **Vantagem**: Funciona com qualquer configuração
- **Uso**: página principal que sempre mostra algo útil

### **Específica com Seções** ⚠️

- **Ideal para**: Funcionalidades específicas que requerem hardware mínimo
- **Cuidado**: Requisitos em página + seções podem ser redundantes
- **Uso**: página avançada só para usuários com hardware completo

### **Básica com Requisitos** 🔧

- **Ideal para**: Funcionalidades específicas sem necessidade de granularidade
- **Vantagem**: Simples, direto
- **Uso**: página de diagnóstico específica, página de calibração

### **Básica sem Requisitos** 📋

- **Ideal para**: Informações de sistema, status, debugging
- **Vantagem**: Sempre disponível
- **Uso**: página de status, página de ajuda, página inicial

## Decisão de Fallback

```text
1. Tentar encontrar página válida:
   ├── Página com requisitos não atendidos → PULAR
   └── Página válida → CONTINUAR

2. Renderizar página encontrada:
   ├── Página sem seções → SEMPRE OK
   └── Página com seções:
       ├── Alguma seção renderizada → OK
       └── Nenhuma seção renderizada → USAR FALLBACK
```

## Recomendações

### ✅ **Boas Práticas**

- Use páginas **universais** como fallback principal
- Combine páginas **básicas sem requisitos** para informações do sistema
- Use **seções** para granularidade quando necessário
- Mantenha pelo menos uma página sempre visível

### ❌ **Evitar**

- Requisitos redundantes (página + seção para o mesmo dispositivo)
- Páginas muito específicas que nunca serão exibidas
- Aninhamento complexo de seções
- Dependência total de hardware sem fallback

### 🎯 **Estratégia Recomendada**

1. **Página Universal** (com seções) - página principal adaptativa
2. **Página Básica sem Requisitos** - status do sistema  
3. **Páginas Específicas** - funcionalidades avançadas
4. **Fallback mínimo** - data/hora + mensagem básica
