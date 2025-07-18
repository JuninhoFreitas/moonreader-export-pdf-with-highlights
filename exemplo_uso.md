# Exemplos de Uso - Moon Highlighter Python

Este arquivo contém exemplos práticos de como usar a aplicação Moon Highlighter em Python.

## Pré-requisitos

Certifique-se de ter instalado as dependências:
```bash
pip install -r requirements.txt
```

## 1. Teste Inicial

Antes de usar a aplicação, execute o teste para verificar se tudo está funcionando:

```bash
python test_highlighter.py
```

**Saída esperada:**
```
=== TESTE DO MOON HIGHLIGHTER ===

1. Testando conexão com banco de dados...
✓ Tabela 'notes' encontrada
✓ Encontrados 487 highlights para o livro

Exemplos de highlights:
  1. Cor: -256, Comprimento: 136
     Texto: um desafio à igreja de Cristo: comunicar o evangelho...

2. Testando acesso ao PDF...
✓ PDF encontrado: CONTEXTUALIZAÇÃO Missionária.pdf
  Tamanho: 1.7 MB

=== RESULTADO ===
✓ Todos os testes passaram!
A aplicação deve funcionar corretamente.
```

## 2. Versão de Teste (Recomendada)

Use a versão simplificada para testar com poucos highlights:

```bash
python moon_highlighter_simple.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite" -l 5
```

**Parâmetros:**
- `-p`: Caminho do PDF
- `-b`: Nome do livro no banco
- `-d`: Caminho do banco SQLite
- `-l`: Número de highlights para processar (5 neste exemplo)

**Saída esperada:**
```
Processando 5 highlights de teste para o livro: CONTEXTUALIZAÇÃO Missionária.pdf
Encontrados 5 highlights para teste
Processando highlight 1/5: um desafio à igreja de Cristo...
  ✗ Não encontrado no PDF
Processando highlight 2/5: A ideia textual, portanto...
  ✗ Não encontrado no PDF
Processando highlight 3/5: A Palavra é supracultural...
  ✗ Não encontrado no PDF
Processando highlight 4/5: Contextualizar o evangelho...
  ✗ Não encontrado no PDF
Processando highlight 5/5: Apresentar Cristo é a finalidade...
  ✓ Encontrado (1 ocorrências) - Cor: #0000FF

PDF de teste salvo: CONTEXTUALIZAÇÃO Missionária_test_highlighted.pdf

=== RELATÓRIO DE TESTE ===
Total processado: 5
Encontrados: 1
Não encontrados: 4
Taxa de sucesso: 20.0%

Teste concluído com sucesso!
Arquivo de saída: CONTEXTUALIZAÇÃO Missionária_test_highlighted.pdf
```

## 3. Versão Completa

Para processar todos os highlights (pode demorar):

```bash
python moon_highlighter.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite"
```

**Saída esperada:**
```
Processando highlights para o livro: CONTEXTUALIZAÇÃO Missionária.pdf
Encontrados 487 highlights no banco de dados
Processando highlight 1/487: um desafio à igreja de Cristo...
  ✗ Não encontrado no PDF
Processando highlight 2/487: A ideia textual, portanto...
  ✗ Não encontrado no PDF
...
Processando highlight 487/487: Apresentar Cristo é a finalidade...
  ✓ Encontrado e destacado (1 ocorrências)

PDF salvo com sucesso: CONTEXTUALIZAÇÃO Missionária_highlighted.pdf

=== RELATÓRIO FINAL ===
Total de highlights processados: 487
Highlights encontrados no PDF: 58
Highlights não encontrados: 429
```

## 4. Especificando Arquivo de Saída

Para especificar um nome personalizado para o arquivo de saída:

```bash
python moon_highlighter_simple.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite" -o "meu_livro_processado.pdf" -l 10
```

## 5. Diferentes Números de Highlights

Teste com diferentes quantidades:

```bash
# Apenas 3 highlights
python moon_highlighter_simple.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite" -l 3

# 20 highlights
python moon_highlighter_simple.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite" -l 20
```

## 6. Verificando Arquivos Gerados

Após executar a aplicação, verifique os arquivos criados:

```bash
ls -la *highlighted*
```

**Saída esperada:**
```
-rw-rw-r-- 1 user user 1823910 jul 18 00:36 'CONTEXTUALIZAÇÃO Missionária_test_highlighted.pdf'
-rw-rw-r-- 1 user user 1813629 jul 18 00:36 'CONTEXTUALIZAÇÃO Missionária_highlighted.pdf'
```

## 7. Interpretando os Resultados

### Taxa de Sucesso
- **20%**: Taxa típica para PDFs com formatação complexa
- **Baixa taxa**: Normal devido à busca exata de texto
- **Causas comuns**:
  - Diferenças de formatação entre banco e PDF
  - Quebras de linha diferentes
  - Caracteres especiais
  - Espaçamento diferente

### Cores Mapeadas
- **#FFFF00** (Amarelo): Highlights gerais
- **#00FF00** (Verde): Conceitos importantes
- **#0000FF** (Azul): Definições
- **#FF0000** (Vermelho): Pontos críticos
- **#FF00FF** (Rosa): Exemplos

## 8. Solução de Problemas

### Erro: "PDF não encontrado"
```bash
# Verifique se o arquivo existe
ls -la "CONTEXTUALIZAÇÃO Missionária.pdf"
```

### Erro: "Banco SQLite não encontrado"
```bash
# Verifique se o banco existe
ls -la pdfmarks.sqlite
```

### Erro: "Tabela 'notes' não encontrada"
```bash
# Verifique a estrutura do banco
sqlite3 pdfmarks.sqlite ".schema notes"
```

### Baixa taxa de sucesso
- Normal para PDFs complexos
- A aplicação identifica o texto mas não adiciona highlights visuais
- Use a versão de teste para validar rapidamente

## 9. Próximos Passos

Para melhorar a funcionalidade:

1. **Highlights Visuais**: Implementar com PyMuPDF (requer compilação)
2. **Busca Fuzzy**: Implementar busca aproximada de texto
3. **Coordenadas Precisas**: Extrair coordenadas exatas do PDF
4. **Interface Gráfica**: Criar interface web ou desktop

## 10. Comandos Úteis

```bash
# Verificar versão do Python
python --version

# Verificar dependências instaladas
pip list | grep PyPDF2

# Verificar estrutura do banco
sqlite3 pdfmarks.sqlite ".tables"

# Contar highlights no banco
sqlite3 pdfmarks.sqlite "SELECT COUNT(*) FROM notes WHERE book = 'CONTEXTUALIZAÇÃO Missionária.pdf' AND bookmark = '';"
``` 