# Seções de Página - PicoWeather

As seções de página permitem criar layouts dinâmicos onde partes da tela são exibidas condicionalmente baseado na disponibilidade de sensores e controladores.

## Conceito

Uma seção é um agrupamento de elementos que só serão renderizados se seus requisitos forem atendidos. Isso permite criar páginas flexíveis que se adaptam ao hardware disponível.

## Estrutura JSON

### Seção Básica

```json
{
  "type": "section",
  "requires_sensors": ["temperature", "humidity"],
  "requires_controller": ["fm_transmitter"],
  "elements": [
    {"type": "sensor", "name": "temperature", "x": "center", "y": 20},
    {"type": "controller", "name": "fm_frequency", "x": "center", "y": 30}
  ]
}
```

### Atributos da Seção

- **type**: sempre `"section"`
- **requires_sensors**: array de tipos de sensores necessários
- **requires_controller**: array de tipos de controladores necessários  
- **elements**: array de elementos a serem exibidos se requisitos forem atendidos

## Requisitos Suportados

### Sensores

- `"aht20"` - Sensor AHT20 detectado
- `"bmp280"` - Sensor BMP280 detectado
- `"bme280"` - Sensor BME280 detectado
- `"temperature"` - Qualquer sensor com dados de temperatura
- `"humidity"` - Qualquer sensor com dados de umidade
- `"pressure"` - Qualquer sensor com dados de pressão

### Controladores

- `"fm_transmitter"` - Transmissor FM detectado
- Outros tipos baseados no nome do controlador

## Exemplos de Uso

### 1. Página com Múltiplas Seções

```json
{
  "name": "dashboard_inteligente",
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

### 2. Seção com Múltiplos Requisitos

```json
{
  "type": "section",
  "requires_sensors": ["temperature", "humidity"],
  "elements": [
    {"type": "text", "x": "center", "y": 30, "text": "Ambiente Completo"},
    {"type": "sensor", "name": "temperature", "x": 0, "y": 40, "label": "T:"},
    {"type": "sensor", "name": "humidity", "x": 70, "y": 40, "label": "U:"}
  ]
}
```

### 3. Página sem Seções mas com Requisitos

```json
{
  "name": "pagina_especifica_sem_secoes",
  "requires_sensors": ["temperature", "pressure"],
  "elements": [
    {"type": "date", "x": "center", "y": 0},
    {"type": "time", "x": "center", "y": 10},
    {"type": "text", "x": "center", "y": 20, "text": "Meteo Completa"},
    {"type": "sensor", "name": "temperature", "x": "center", "y": 30, "label": "Temp:"},
    {"type": "sensor", "name": "pressure", "x": "center", "y": 40, "label": "Press:"}
  ]
}
```

**Resultado**: Página só é exibida se temperatura E pressão estiverem disponíveis.

### 4. Página sem Seções e sem Requisitos

```json
{
  "name": "pagina_sistema",
  "elements": [
    {"type": "date", "x": "center", "y": 0},
    {"type": "time", "x": "center", "y": 10},
    {"type": "text", "x": "center", "y": 20, "text": "PicoWeather"},
    {"type": "text", "x": "center", "y": 30, "text": "Sistema Ativo"},
    {"type": "text", "x": "center", "y": 40, "text": "Verifique Console"}
  ]
}
```

**Resultado**: Página SEMPRE exibida, independente de hardware disponível.

### 5. Placeholder para Hardware Ausente

## Comportamento

### Regras de Exibição

1. **Seção só é exibida se TODOS os requisitos forem atendidos**
2. **Elementos fora de seções são sempre exibidos**
3. **Seções podem ser aninhadas (não recomendado)**
4. **Página continua sendo exibida mesmo se algumas seções forem ocultadas**
5. **Páginas sem seções não precisam de validação de hardware**

### Tipos de Páginas

#### 🎯 **Páginas Universais (Seções Only)**

- Todas as informações estão dentro de seções
- Adaptam-se a qualquer configuração de hardware
- **Podem dispensar fallback** - sempre exibem algo válido
- Ideal para sistemas com hardware variável

#### 📋 **Páginas Básicas (Sem Seções)**

- Não usam seções
- **Se não tiverem `requires_sensors/requires_controller`: sempre exibidas**
- **Se tiverem `requires_sensors/requires_controller`: só exibidas se dispositivos presentes**
- Conteúdo fixo independente de seções
- Úteis para informações de sistema, status, debugging

#### 🔄 **Páginas Híbridas**

- Combinam elementos fixos + seções condicionais
- Elementos fixos sempre visíveis (título, data, hora)
- Seções dinâmicas para hardware específico
- Máximo de flexibilidade

#### 🎯 **Páginas Específicas (Com Requisitos)**

- Usam `requires_sensors/requires_controller` no nível da página
- Só exibidas se hardware completo estiver presente
- Para funcionalidades específicas que exigem todos os dispositivos

### Fallback Inteligente

- **Nível de Página**: Se página tem `requires_sensors/requires_controller` e não atendidos → pula página inteira
- **Nível de Seção**: Se seção tem requisitos e não atendidos → pula apenas a seção
- **Página com Seções**: Se NENHUMA seção for renderizada → usa fallback
- **Página sem Seções**: Nunca usa fallback (a menos que página inteira seja pulada por requisitos)

### Fluxo de Decisão

```text
1. Verificar requisitos da PÁGINA
   ├── Se página tem requisitos não atendidos → PULAR PÁGINA
   └── Se página não tem requisitos ou atendidos → CONTINUAR

2. Renderizar página (se chegou aqui)
   ├── Elementos normais → SEMPRE renderizados
   └── Seções → verificar requisitos INDIVIDUAIS
       ├── Se requisitos atendidos → renderizar seção
       └── Se requisitos não atendidos → pular seção

3. Verificar se algo foi renderizado
   ├── Página sem seções → sempre OK
   └── Página com seções → se nenhuma seção renderizada → usar fallback
```

### Log

O sistema gera logs quando seções são puladas:

```text
[DISPLAY_MGR] Section requires sensor 'temperature' not available - skipping section
[DISPLAY_MGR] Section requires controller 'fm_transmitter' not available - skipping section
```

## Vantagens

1. **Layouts Adaptativos**: A mesma página funciona com diferentes configurações de hardware
2. **Fácil Manutenção**: Não需要 criar múltiplas páginas para combinações diferentes de hardware
3. **Gradual Deployment**: Adiciona novos elementos sem quebrar layouts existentes
4. **Reuso**: Seções podem ser reutilizadas em diferentes páginas

## Boas Práticas

1. **Teste com diferentes configurações de hardware**
2. **Use nomes descritivos para seções complexas**
3. **Considere o espaço em branco quando seções forem ocultadas**
4. **Combine com páginas de fallback para máxima compatibilidade**
5. **Use logs para debug de requisitos não atendidos**

## Migração de Layouts Existente

Para migrar layouts existentes:

### Antes (página com requisitos fixos)

```json
{
  "name": "completo",
  "requires_sensors": ["temperature", "humidity"],
  "requires_controller": ["fm_transmitter"],
  "elements": [
    {"type": "sensor", "name": "temperature", "x": 0, "y": 20},
    {"type": "sensor", "name": "humidity", "x": 0, "y": 30},
    {"type": "controller", "name": "fm_frequency", "x": 0, "y": 40}
  ]
}
```

### Depois (página com seções)

```json
{
  "name": "flexivel",
  "elements": [
    {
      "type": "section",
      "requires_sensors": ["temperature"],
      "elements": [
        {"type": "sensor", "name": "temperature", "x": 0, "y": 20}
      ]
    },
    {
      "type": "section",
      "requires_sensors": ["humidity"], 
      "elements": [
        {"type": "sensor", "name": "humidity", "x": 0, "y": 30}
      ]
    },
    {
      "type": "section",
      "requires_controller": ["fm_transmitter"],
      "elements": [
        {"type": "controller", "name": "fm_frequency", "x": 0, "y": 40}
      ]
    }
  ]
}
```

Essa abordagem permite que a página seja exibida parcialmente mesmo que alguns dispositivos não estejam disponíveis.
