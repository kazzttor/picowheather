# Console Failsafe System - PicoWeather

Sistema inteligente que seleciona automaticamente o tipo de console baseado no hardware, com mecanismo de failsafe para garantir funcionamento.

## 🎯 **Objetivo**

- **Hardware limitado**: Pico padrão (264KB RAM) usa console ultra-leve
- **Hardware com recursos**: Pico W, Pico Clone usam console completo
- **Failsafe automático**: Se console full falhar, fallback para light
- **Zero configuração**: Determinado automaticamente pelo hardware_config

## 🏗️ **Arquitetura**

### 1. Configuração no hardware_config.py

```json
{
  "pico": {
    "features": {
      "console": "light"     // 264KB RAM
    }
  },
  "pico_w": {
    "features": {
      "console": "full"      // 264KB + WiFi RAM
    }
  },
  "pico_clone": {
    "features": {
      "console": "full"      // Mais RAM disponível
    }
  }
}
```

### 2. Fluxo de Decisão

```text
1. Ler configuração do hardware
2. Determinar tipo de console: full ou light
3. Tentar carregar console configurado
   ├── Success: Usar console configurado
   └── Fail: Fallback automático para light
4. Inicializar console com configuração adequada
```

## 📱 **Tipos de Console**

### Console Light (Pico Padrão)

- **Memória**: ~2KB
- **Histórico**: 2 comandos
- **Autocompletar**: `?` trigger apenas
- **Comandos**: Essenciais (help, status, sensors, scan, exit)
- **Features**: Mínimas para funcionamento

### Console Full (Pico W/Clone)

- **Memória**: ~8KB  
- **Histórico**: 8 comandos
- **Autocompletar**: `?` + `TAB` (se suportado)
- **Comandos**: Todos disponíveis
- **Features**: Completas com subcomandos

### Emergency Failsafe

- **Memória**: ~1KB
- **Histórico**: 1 comando
- **Autocompletar**: Nenhum
- **Comandos**: Básicos
- **Features**: Mínimas absolutas

## 🔄 **Mecanismo de Failsafe**

### Detecção de Falha

```python
try:
    # Tentar carregar console full
    from utils.simple_console import SimpleTabConsole
    self.enhanced_console = SimpleTabConsole()
    console_type = 'full'
except Exception as e:
    print(f"[CONSOLE] Full console failed: {e}")
    # Fallback automático
    console_type = 'light_failsafe'
```

### Tipos de Falha Tratados

1. **MemoryError**: Alocação de memória falhou
2. **ImportError**: Módulo não disponível
3. **Exception**: Outros erros de inicialização

### Log do Sistema

```text
[CONSOLE] Board: pico, Console type: light
[CONSOLE] Light console loaded

Ou em caso de falha:
[CONSOLE] Board: pico_w, Console type: full
[CONSOLE] Full console failed: MemoryError: memory allocation failed
[CONSOLE] Fallback to light console
[CONSOLE] Light console loaded
```

## 🛠️ **Implementação Técnica**

### Método Principal

```python
def _setup_console_with_failsafe(self):
    """Setup console type with failsafe mechanism"""
    try:
        # Obter configuração do hardware
        board_type = self.config.get('hardware', {}).get('board', 'pico')
        hardware = get_hardware_config(board_type)
        console_type = hardware.get('features', {}).get('console', 'light')
        
        if console_type == 'full':
            # Tentar console completo
            try:
                from utils.simple_console import SimpleTabConsole
                self.enhanced_console = SimpleTabConsole()
                self.max_history = 8
                return 'full'
            except Exception as e:
                print(f"[CONSOLE] Full console failed: {e}")
                # Continuar para light console
        
        # Console light ou fallback
        self.enhanced_console = None
        self.max_history = 2
        return 'light'
        
    except Exception as e:
        print(f"[CONSOLE] Console setup failed: {e}")
        # Emergency fallback
        self.enhanced_console = None
        self.max_history = 1
        return 'emergency'
```

### Configuração Dinâmica

```python
# Baseado no console type selecionado
if self.console_type == 'full':
    self.max_history = 8        # Mais histórico
    # ... mais features
else:
    self.max_history = 2        # Mínimo histórico
    # ... features essenciais
```

## 📊 **Comparação de Recursos**

| Feature | Light | Full | Emergency |
| --- | --- | --- | --- |
| Memória | ~2KB | ~8KB | ~1KB |
| Histórico | 2 comandos | 8 comandos | 1 comando |
| Autocompletar | `?` | `?` + `TAB` | Nenhum |
| Subcomandos | Não | Sim | Não |
| Fallback | N/A | Light | N/A |

## 🧪 **Teste e Validação**

### Teste de Seleção

```python
# Teste para cada hardware
for board, expected in [('pico', 'light'), ('pico_w', 'full')]:
    console = PicoWeatherConsole({}, {'hardware': {'board': board}})
    assert console.console_type == expected
```

### Teste de Failsafe

```python
# Simular falha de memória
def test_memory_failsafe():
    # Mock MemoryError
    with patch('utils.simple_console.SimpleTabConsole', side_effect=MemoryError):
        console = PicoWeatherConsole({}, {'hardware': {'board': 'pico_w'}})
        assert console.console_type in ['light', 'emergency']
```

### Teste de Memória

```python
import gc

# Testar uso de memória
gc.collect()
mem_before = gc.mem_free()
console = PicoWeatherConsole({}, config)
gc.collect()
mem_after = gc.mem_free()

memory_used = mem_before - mem_after
assert memory_used < 10000  # Menos de 10KB
```

## 🎯 **Casos de Uso**

### 1. Pico Padrão (264KB)

```text
Config: board: "pico" → console: "light"
Resultado: Console light carregado
Memória: ~2KB usada
Histórico: 2 comandos
```

### 2. Pico W (Mais RAM)

```text
Config: board: "pico_w" → console: "full"
Resultado: Console full carregado
Memória: ~8KB usada
Histórico: 8 comandos
```

### 3. Pico W com Falha de Memória

```text
Config: board: "pico_w" → console: "full"
Tentativa: Full console → MemoryError
Fallback: Light console carregado
Resultado: Console light_failsafe
Memória: ~2KB usada
```

## 🚀 **Vantagens**

### 1. **Automático**

- Zero configuração manual
- Detecção automática de hardware
- Fallback transparente

### 2. **Robusto**

- Funciona mesmo em hardware limitado
- Trata todos os tipos de falha
- Garante funcionamento mínimo

### 3. **Adaptativo**

- Aproveita recursos disponíveis
- Não desperdiça hardware com mais RAM
- Escalável para diferentes configurações

### 4. **Debugável**

- Logs claros do processo
- Identifica tipo de console usado
- Informa sobre fallbacks

## 🔧 **Extensão Futura**

### Novos Tipos de Console

```json
{
  "pico_2": {
    "features": {
      "console": "enhanced"  // Futuro console intermediário
    }
  }
}
```

### Configuração Manual

```python
# Override automático (para desenvolvimento)
config['hardware']['console_override'] = 'full'
```

### Métricas de Performance

```python
# Coletar métricas
console_stats = {
    'type': self.console_type,
    'memory_used': memory_used,
    'history_size': len(self.command_history),
    'features': list_available_features()
}
```

## 📈 **Resultados Esperados**

### Pico Padrão

- ✅ Console light sem erros
- ✅ < 3KB de memória usada
- ✅ Funcionalidades essenciais

### Pico W/Clone

- ✅ Console full quando possível
- ✅ < 10KB de memória usada
- ✅ Todas as funcionalidades

### Falha de Memória

- ✅ Fallback automático para light
- ✅ Sistema continua funcionando
- ✅ Usuário notificado do fallback

O sistema de failsafe garante que o PicoWeather funcione em qualquer configuração de hardware, com ou sem recursos limitados, de forma totalmente automática e transparente.
