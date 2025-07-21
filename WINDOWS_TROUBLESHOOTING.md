# Troubleshooting para Windows

## Problema: "Por favor, digite seu nome" mesmo com campo preenchido

### Sintomas
- Campo nome preenchido na interface
- Sistema ainda pede para preencher o nome
- Não consegue criar conta nem fazer login

### Diagnóstico Implementado
Adicionamos logs detalhados para identificar exatamente onde está o problema:

```
REGISTRO - Nome: '{valor}' (len: X, type: tipo)
REGISTRO - Email: '{valor}' (len: X, type: tipo)
```

### Como verificar no Windows
1. Abra o prompt de comando (cmd) ou PowerShell
2. Navegue até a pasta do aplicativo
3. Execute: `python main.py`
4. Tente criar uma conta
5. Verifique as mensagens no console

### Possíveis Causas
1. **Codificação de caracteres**: Windows pode ter problemas com UTF-8
2. **Captura de dados**: tkinter pode se comportar diferente no Windows
3. **Tipos de dados**: StringVar pode retornar tipos inesperados
4. **Paths do banco**: Caminho do SQLite pode estar incorreto

### Correções Implementadas
1. **Tratamento robusto de tipos**: Conversão explícita para string
2. **Validação defensiva**: Verificação de None antes do processamento
3. **Logs detalhados**: Informações completas sobre valores capturados
4. **Error handling**: Captura de exceções com stack trace

### Testando a Correção
Execute o aplicativo e tente:
1. Criar conta com nome "João Silva" e email "joao@teste.com"
2. Observe as mensagens no console
3. Se ainda falhar, envie os logs para análise

### Solução Temporária
Se o problema persistir, você pode:
1. **Modo Emergência**: Execute `python emergency_backup_windows.py` (versão sem login)
2. **Interface web**: http://localhost:5000 (precisa executar `python web_backup.py`)
3. **CLI**: `python backup_cli.py --help` (linha de comando)
4. Reportar os logs do console para correção definitiva

### Arquivo de Emergência
O arquivo `emergency_backup_windows.py` é uma versão simplificada que:
- Não precisa de login
- Interface simples para backup
- Funciona independente do sistema de usuários
- Ideal para uso imediato enquanto resolve o problema principal