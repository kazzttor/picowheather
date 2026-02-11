# 📚 Documentação PicoWeather

Bem-vindo à documentação completa do PicoWeather! Aqui você encontrará guias detalhados para cada aspecto do sistema.

## 📋 **Índice de Documentação**

### **🔧 Guias de Instalação por Hardware**
- [Raspberry Pi Pico Padrão](./guides/raspberry-pi-pico.md) - Configuração com SSD1306
- [Raspberry Pi Pico W](./guides/raspberry-pi-w.md) - Configuração com WiFi nativo
- [RP2040 + ESP8285 (Clones)](./guides/rp2040-esp8285.md) - Configuração completa

### **⚙️ Arquivos de Configuração**
- [config.json](./configuration/config-json.md) - Configuração principal do sistema
- [display_layouts.json](./configuration/display-layouts-json.md) - Layout das telas
- [hardware_config.py](./configuration/hardware-config.md) - Configuração de placas

### **🌍 Localização**
- [Sistema de Locales](./i18n/locales.md) - Internacionalização e tradução

### **🚀 Expansão e Desenvolvimento**
- [Adicionando Novos Dispositivos](./development/adding-devices.md) - Guia de expansão
- [Arquitetura do Sistema](./development/architecture.md) - Estrutura interna
- [Roadmap de Desenvolvimento](./development/roadmap.md) - Futuras implementações

---

## 🎯 **Como Usar Esta Documentação**

### **Para Iniciantes**
1. Comece com o [guia da sua placa](./guides/) específica
2. Siga os passos de instalação e configuração
3. Consulte [solução de problemas](../README.md#solução-de-problemas) se necessário

### **Para Desenvolvedores**
1. Entenda a [arquitetura do sistema](./development/architecture.md)
2. Estude os [arquivos de configuração](./configuration/)
3. Siga o [guia de expansão](./development/adding-devices.md) para adicionar novos dispositivos

### **Para Contribuidores**
1. Revise o [roadmap de desenvolvimento](./development/roadmap.md)
2. Entenda o [sistema de locales](./i18n/locales.md) para tradução
3. Siga os padrões documentados em cada guia

---

## 📁 **Estrutura da Documentação**

```
docs/
├── guides/                    # Guias de instalação por hardware
│   ├── raspberry-pi-pico.md
│   ├── raspberry-pi-w.md
│   └── rp2040-esp8285.md
├── configuration/             # Documentação de arquivos de config
│   ├── config-json.md
│   ├── display-layouts-json.md
│   └── hardware-config.md
├── i18n/                      # Internacionalização
│   └── locales.md
└── development/               # Desenvolvimento e expansão
    ├── adding-devices.md
    ├── architecture.md
    └── roadmap.md
```

---

## 🔍 **Navegação Rápida**

### **Problemas Comuns**
- [Display não funciona](../README.md#display-não-liga)
- [Sensores não detectados](../README.md#sensores-não-detectados)
- [WiFi não conecta](../README.md#wifi-não-conecta)

### **Configuração Rápida**
- [Escolher configuração](../README.md#configurações-pré-definidas)
- [Editar config.json](./configuration/config-json.md)
- [Personalizar telas](./configuration/display-layouts-json.md)

### **Desenvolvimento**
- [Adicionar sensor](./development/adding-devices.md#adicionando-novos-sensores)
- [Suporte a novas placas](./configuration/hardware-config.md#adicionando-novas-placas)
- [Traduzir interface](./i18n/locales.md#adicionando-novos-idiomas)

---

## 💡 **Dicas de Uso**

### **Durante Instalação**
- Tenha em mãos o diagrama de pinagem da sua placa
- Verifique compatibilidade de componentes antes de comprar
- Use o modo console para diagnóstico

### **Para Desenvolvimento**
- Estude os drivers existentes como referência
- Teste novos dispositivos isoladamente antes de integrar
- Use o sistema de hardware config para manter compatibilidade

### **Para Contribuição**
- Mantenha a documentação atualizada com suas mudanças
- Siga os padrões de código estabelecidos
- Teste em múltiplas configurações de hardware

---

**Última atualização:** 2024-12-25  
**Versão:** PicoWeather v2.0

*Esta documentação evolui com o projeto. Verifique atualizações regulares!*