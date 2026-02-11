# Console Avançado PicoWeather - Guia de Uso

## 🚀 Recursos Disponíveis

### 1. Autocompletar (TAB ou ?)

O console agora suporta duas formas de autocompletar:

#### Método 1: TAB (se suportado pelo terminal)

```bash
pico> hel[TAB]      # Completa para "help"
pico> fm s[TAB]      # Mostra sugestões para subcomandos
```

#### Método 2: ? (funciona em qualquer terminal)

```bash
pico> help?         # Mostra sugestões para "help"
pico> fm s?         # Mostra subcomandos começando com "s"
pico> ?             # Mostra todos os comandos disponíveis
```

### 2. Histórico de Comandos

- Últimos 15 comandos são armazenados
- Evita duplicações automaticamente
- Acesso rápido a comandos frequentes

## 📖 Comandos e Subcomandos

### Comandos Principais

```bash
help                 # Mostrar ajuda
status               # Status do sistema
sensors              # Leitura dos sensores
scan                 # Buscar dispositivos I2C
display              # Controles do display
time                 # Informações de tempo
fm                   # Controles do transmissor FM
wifi                 # Controles WiFi
diagnostic           # Diagnóstico do sistema
config               # Configuração
save                 # Salvar configuração
exit/quit            # Sair do console
```

### Subcomandos FM

```bash
fm status            # Status do transmissor
fm frequency 99.7    # Definir frequência
fm volume 10         # Definir volume
fm mute              # Silenciar
fm unmute            # Ativar áudio
fm rds               # Comandos RDS
```

### Subcomandos WiFi

```bash
wifi status          # Status da conexão
wifi scan            # Buscar redes
wifi connect SSID    # Conectar à rede
wifi disconnect      # Desconectar
wifi networks        # Redes salvas
```

### Subcomandos Display

```bash
display status       # Status do display
display page         # Mudar página
display brightness   # Ajustar brilho
display test         # Testar display
```

### Subcomandos Config

```bash
config show          # Mostrar configuração
config set key val   # Definir valor
config reset         # Resetar configuração
config save          # Salvar configuração
```

### Subcomandos Diagnostic

```bash
diagnostic all       # Diagnóstico completo
diagnostic sensors   # Apenas sensores
diagnostic display   # Apenas display
diagnostic system    # Apenas sistema
```

## 🎯 Exemplos Práticos

### Cenário 1: Verificar Status Rápido

```bash
pico> stat?           # Usar ? para autocompletar
# Sugestões: status
pico> status           # Executar comando
```

### Cenário 2: Configurar FM

```bash
pico> fm fre?         # Autocompletar "frequency"
pico> fm frequency 99.7
```

### Cenário 3: Buscar Redes WiFi

```bash
pico> wifi sc?        # Autocompletar "scan"
pico> wifi scan
```

### Cenário 4: Verificar Todos os Comandos

```bash
pico> ?               # Mostrar todos os comandos disponíveis
```

## 🔧 Como Funciona o Autocompletar

### Fluxo com TAB

1. Digite parte do comando: `fm s`
2. Pressione TAB
3. Sistema mostra sugestões: `status`, `scan`
4. Se houver apenas uma sugestão, autocompleta automaticamente

### Fluxo com ?

1. Digite parte do comando: `fm s`
2. Digite `?`: `fm s?`
3. Sistema mostra sugestões disponíveis
4. Se houver apenas uma sugestão, mostra o comando completo

### Prioridade

1. **TAB** tentado primeiro (se suportado)
2. **?** usado como fallback (funciona sempre)

## 📱 Limitações e Soluções

### Limitações do MicroPython

- **Terminal input limitado**: `input()` não captura todas as teclas especiais
- **Sem setas nativas**: Histórico com setas requer terminal específico
- **Tab dependente**: Alguns terminais não enviam TAB corretamente

### Soluções Implementadas

- **Fallback com ?**: Funciona em qualquer terminal
- **Sugestões limitadas**: Máximo 5 sugestões para não sobrecarregar
- **Memory efficient**: Uso mínimo de RAM

## 🛠️ Debug e Troubleshooting

### Se TAB não funcionar

1. **Use ? como alternativa**: `help?` funciona sempre
2. **Verifique o terminal**: Alguns terminais web não suportam TAB
3. **Teste no REPL**: `input("test\t")` no REPL do MicroPython

### Se autocompletar não mostrar sugestões

1. **Verifique o comando**: `fm?` deve mostrar subcomandos
2. **Verifique a digitação**: `fm s?` (com espaço)
3. **Use ? sem parâmetros**: `?` mostra todos os comandos

### Se histórico não funcionar

1. **Comandos vazios**: Comandos em branco não são salvos
2. **Limite atingido**: Apenas últimos 15 comandos
3. **Duplicatas**: Comandos repetidos removem cópias anteriores

## 🚀 Dicas de Uso

### Produtividade

- Use `?` para explorar comandos desconhecidos
- Combine com subcomandos: `fm r?` para comandos RDS
- Use histórico para comandos repetitivos

### Comandos Úteis

```bash
# Ver tudo de uma vez
diagnostic all

# Status completo
status

# Ajuda específica
help fm
fm ?

# Testar hardware
display test
sensors
scan
```

### Fluxo de Trabalho Típico

1. `status` - Verificar sistema
2. `sensors` - Verificar sensores
3. `fm frequency 99.7` - Ajustar rádio
4. `save` - Salvar configuração

## ✅ Compatibilidade

### 100% Compatível

- **MicroPython**: Funciona em qualquer versão
- **Hardware**: Pico, Pico W, Pico 2, etc.
- **Terminal**: Qualquer terminal com suporte básico

### Testado em

- **Thonny**: TAB funciona, ? funciona
- **minicom**: TAB funciona, ? funciona
- **picocom**: TAB funciona, ? funciona
- **Web REPL**: TAB pode não funcionar, ? funciona

## 🎉 Conclusão

O console avançado do PicoWeather oferece experiência superior mantendo 100% de compatibilidade. Use TAB quando disponível, ou ? como fallback universal para máxima produtividade.
