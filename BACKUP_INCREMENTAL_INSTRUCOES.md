# Backup Incremental
## Desktop Backup Manager - PHOENYX TECNOLOGIA © 2025

## 🎯 Visão Geral

O modo de backup incremental permite criar backups que incluem apenas arquivos novos ou modificados desde o último backup, economizando tempo e espaço de armazenamento.

## 🔧 Como Funciona

### Comparação de Datas
- **Data de Modificação**: Compara a data de modificação de cada arquivo
- **Último Backup**: Usa a data do backup mais recente das mesmas pastas
- **Filtro Inteligente**: Inclui apenas arquivos mais novos que o último backup

### Identificação de Arquivos
- ✅ **Arquivos Novos**: Criados após o último backup
- ✅ **Arquivos Modificados**: Alterados após o último backup
- ❌ **Arquivos Inalterados**: Não incluídos no backup incremental

## 🖥️ Interface Gráfica

### Opção de Backup Incremental
- **Localização**: Aba "Backup" → Seção "Opções do Backup"
- **Checkbox**: "Backup Incremental"
- **Tooltip**: Clique com botão direito para ver explicação
- **Prefixo**: Backups incrementais têm prefixo "incremental_" no nome

### Como Usar
1. **Selecione as Pastas**: Adicione as pastas que deseja backup
2. **Marque a Opção**: Ative "Backup Incremental"
3. **Configure Outros**: Título, destino, compactação
4. **Execute**: Clique em "Iniciar Backup"

## 💻 Linha de Comando

### Comando Básico
```bash
python backup_cli.py backup --incremental \
  --title "Documentos_Incremental" \
  --source "C:\Documentos" "C:\Projetos" \
  --destination "D:\Backups" \
  --compression zip
```

### Parâmetros Disponíveis
- `--incremental` ou `-i`: Ativa modo incremental
- `--title`: Título do backup (obrigatório)
- `--source`: Pastas de origem (uma ou mais)
- `--destination`: Pasta de destino
- `--compression`: zip ou tar.gz
- `--verbose`: Mostra progresso detalhado

### Exemplos Práticos

#### Backup Incremental Diário
```bash
# Segunda-feira - Backup completo
python backup_cli.py backup \
  --title "Documentos_Segunda" \
  --source "C:\Documentos" \
  --destination "D:\Backups"

# Terça-feira - Backup incremental
python backup_cli.py backup --incremental \
  --title "Documentos_Terca" \
  --source "C:\Documentos" \
  --destination "D:\Backups"
```

#### Backup de Projeto com Incrementos
```bash
# Backup inicial do projeto
python backup_cli.py backup \
  --title "Projeto_Web_Inicial" \
  --source "C:\Projetos\SiteWeb" \
  --destination "D:\Backups"

# Backup incremental após mudanças
python backup_cli.py backup --incremental \
  --title "Projeto_Web_Atualizacao" \
  --source "C:\Projetos\SiteWeb" \
  --destination "D:\Backups"
```

## 🎯 Cenários de Uso

### 1. Backup Diário de Documentos
- **Situação**: Backup diário da pasta Documentos
- **Estratégia**: Um backup completo semanal + incrementais diários
- **Economia**: 80-90% menos tempo e espaço

### 2. Backup de Desenvolvimento
- **Situação**: Backup de código fonte em desenvolvimento
- **Estratégia**: Incrementais a cada commit importante
- **Economia**: Apenas arquivos alterados são incluídos

### 3. Backup de Fotos/Vídeos
- **Situação**: Backup de mídia pessoal
- **Estratégia**: Incremental mensal para novas fotos
- **Economia**: Não reprocessa arquivos já backupados

## ⚡ Vantagens

### Economia de Tempo
- **Análise Rápida**: Verifica apenas datas de modificação
- **Menos Arquivos**: Processa apenas arquivos alterados
- **Compactação Eficiente**: Menos dados para comprimir

### Economia de Espaço
- **Backups Menores**: Tamanho proporcional às mudanças
- **Armazenamento Eficiente**: Não duplica arquivos inalterados
- **Histórico Inteligente**: Mantém versões apenas dos arquivos modificados

### Flexibilidade
- **Combinação**: Pode alternar entre completo e incremental
- **Restauração**: Funciona normal (restaura do backup selecionado)
- **Automatização**: Ideal para scripts e agendamentos

## 📊 Indicadores Visuais

### Interface Gráfica
- **Progresso**: Mostra "Modo incremental: desde DD/MM/AAAA HH:MM"
- **Contador**: Exibe quantos arquivos novos foram encontrados
- **Resultado**: Informa se nenhum arquivo novo foi encontrado

### Linha de Comando
- **Verboso**: Mostra progresso com `-v`
- **Resumo**: Exibe estatísticas do backup incremental
- **Status**: Informa se backup foi necessário

## 🔍 Logs e Catálogo

### Identificação no Catálogo
- **Prefixo**: Nome começa com "incremental_"
- **Metadados**: Campo "incremental": true no JSON
- **Histórico**: Mantém referência aos backups anteriores

### Informações Registradas
- ✅ Data do último backup usado como referência
- ✅ Número de arquivos novos/modificados
- ✅ Tamanho economizado comparado ao backup completo
- ✅ Tempo de execução reduzido

## 🚀 Automatização com Task Scheduler

### Script Diário (Windows)
```batch
@echo off
echo Executando backup incremental diário...
cd /d "C:\DesktopBackupManager"
python backup_cli.py backup --incremental ^
  --title "Backup_Diario_%date:~-4%%date:~3,2%%date:~0,2%" ^
  --source "C:\Users\%USERNAME%\Documents" ^
  --destination "D:\Backups" ^
  --verbose
pause
```

### Agendamento Recomendado
- **Segunda**: Backup completo
- **Terça a Sexta**: Backup incremental
- **Sábado**: Backup completo (opcional)
- **Domingo**: Manutenção/limpeza

## ⚠️ Considerações Importantes

### Quando Usar Incremental
- ✅ **Backups Frequentes**: Diários ou semanais
- ✅ **Arquivos Grandes**: Pastas com muitos arquivos
- ✅ **Poucas Mudanças**: Quando poucos arquivos mudam
- ✅ **Automação**: Scripts agendados

### Quando Usar Completo
- ✅ **Primeiro Backup**: Backup inicial sempre completo
- ✅ **Backup Mensal**: Para ter pontos de restauração completos
- ✅ **Após Mudanças Grandes**: Reorganização de pastas
- ✅ **Backup de Segurança**: Antes de mudanças importantes

### Limitações
- ⚠️ **Data de Modificação**: Depende da data do sistema
- ⚠️ **Primeira Execução**: Não há backup anterior para comparar
- ⚠️ **Restauração**: Precisa do backup específico, não combina incrementais

## 💡 Dicas de Uso

### Estratégia Híbrida
1. **Backup Completo**: Uma vez por semana
2. **Incrementais**: Todos os outros dias
3. **Limpeza**: Remover incrementais antigos periodicamente

### Nomeação Inteligente
- Use datas no título: `Docs_2025_01_21`
- Identifique incrementais: `Docs_Inc_2025_01_22`
- Mantenha padrão consistente

### Monitoramento
- Verifique logs regularmente
- Confirme que incrementais estão encontrando mudanças
- Teste restaurações periodicamente

---

**PHOENYX TECNOLOGIA © 2025**
*Backup inteligente, economia real*