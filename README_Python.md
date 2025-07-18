# Moon Highlighter - Versão Python

Uma aplicação CLI em Python que processa highlights de livros PDF baseado em dados armazenados em um banco SQLite.

## Funcionalidades

- Busca highlights de um livro específico em um banco SQLite
- Localiza texto no PDF e identifica coordenadas aproximadas
- Mapeamento automático de cores do banco para cores RGB
- Gera relatório detalhado do processamento
- Salva um novo PDF com as informações processadas
- Versão de teste para validação rápida

## Pré-requisitos

- Python 3.7 ou superior
- SQLite3 (geralmente incluído com Python)

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd moon-highlighter
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Versão Completa
```bash
python moon_highlighter.py -p <caminho_pdf> -b <nome_livro> -d <caminho_banco> [-o <caminho_saida>]
```

### Versão de Teste (Recomendada)
```bash
python moon_highlighter_simple.py -p <caminho_pdf> -b <nome_livro> -d <caminho_banco> [-o <caminho_saida>] [-l <limite>]
```

### Script de Teste
```bash
python test_highlighter.py
```

### Parâmetros

- `-p, --pdf`: Caminho do arquivo PDF a ser processado
- `-b, --book`: Nome do livro (deve corresponder exatamente ao nome no banco SQLite)
- `-d, --database`: Caminho do banco SQLite
- `-o, --output`: (Opcional) Caminho do PDF de saída
- `-l, --limit`: (Apenas versão simples) Número de highlights para processar (padrão: 10)

### Exemplo de Uso

```bash
# Teste inicial
python test_highlighter.py

# Versão de teste com 5 highlights
python moon_highlighter_simple.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite" -l 5

# Versão completa
python moon_highlighter.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite"
```

## Como Funciona

1. **Leitura do Banco**: A aplicação conecta ao banco SQLite e executa a query:
   ```sql
   SELECT highlightColor, highlightLength, original 
   FROM notes 
   WHERE book = ? AND bookmark = ''
   ```

2. **Mapeamento de Cores**: Cada valor de cor do banco é mapeado para uma cor hexadecimal:
   - 1996532479 → #FFFF00 (Amarelo)
   - -1996554240 → #00FF00 (Verde)
   - 2013265664 → #0000FF (Azul)
   - -256 → #FF0000 (Vermelho)
   - 16711680 → #FF00FF (Rosa)

3. **Busca de Texto**: Para cada highlight, o texto é buscado no PDF usando PyPDF2

4. **Identificação de Coordenadas**: Coordenadas aproximadas são calculadas baseadas na posição do texto

5. **Salvamento**: Um novo PDF é salvo com as informações processadas

## Estrutura do Banco de Dados

A aplicação espera uma tabela `notes` com a seguinte estrutura:

```sql
CREATE TABLE notes (
    _id integer primary key autoincrement,
    book text,
    filename text,
    lowerFilename text,
    lastChapter NUMERIC,
    lastSplitIndex NUMERIC,
    lastPosition NUMERIC,
    highlightLength NUMERIC,
    highlightColor NUMERIC,
    time NUMERIC,
    bookmark text,
    notetext text,
    original text,
    underline NUMERIC,
    strikethrough NUMERIC,
    bak text
);
```

## Arquivos Gerados

1. **PDF de Saída**: Cópia do PDF original processado
   - Versão completa: `{nome_original}_highlighted.pdf`
   - Versão de teste: `{nome_original}_test_highlighted.pdf`
   - Pode ser personalizado com o parâmetro `-o`

## Relatório de Processamento

A aplicação exibe um relatório detalhado durante e após o processamento:

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

=== RELATÓRIO DE TESTE ===
Total processado: 5
Encontrados: 1
Não encontrados: 4
Taxa de sucesso: 20.0%
```

## Limitações e Considerações

- **Precisão da Busca**: A busca de texto é exata. Pequenas diferenças de formatação podem impedir a localização
- **Highlights Visuais**: PyPDF2 tem limitações para adicionar highlights visuais. A aplicação identifica o texto mas não adiciona marcações visuais
- **Coordenadas Aproximadas**: As coordenadas são calculadas de forma aproximada baseadas na posição do texto
- **Performance**: Para PDFs muito grandes ou com muitos highlights, o processamento pode ser lento

## Personalização

### Mapeamento de Cores

Para personalizar o mapeamento de cores, edite o método `map_color` na classe:

```python
def map_color(self, color_value: int) -> str:
    color_map = {
        1996532479: "#FFFF00",    # Amarelo
        -1996554240: "#00FF00",   # Verde
        # Adicione mais cores conforme necessário
    }
    # ... resto do código
```

## Tratamento de Erros

- Validação de parâmetros obrigatórios
- Verificação de existência dos arquivos
- Tratamento de erros de banco de dados
- Tratamento de erros na manipulação de PDFs
- Fallback para cores padrão em caso de erro

## Dependências

- **PyPDF2**: Biblioteca para manipulação de PDFs
  - Versão: 3.0.1
  - Licença: BSD (gratuita)

## Comparação com a Versão Go

| Característica | Python | Go |
|---|---|---|
| **Identificação de Texto** | ✅ Implementado | ⚠️ Básica |
| **Manipulação de PDF** | ✅ Completa | ⚠️ Básica |
| **Highlights Visuais** | ❌ Limitado | ❌ Não implementado |
| **Performance** | ⚠️ Moderada | ✅ Rápida |
| **Facilidade de Uso** | ✅ Simples | ⚠️ Moderada |
| **Dependências** | ✅ Mínimas | ⚠️ Múltiplas |
| **Taxa de Sucesso** | ⚠️ ~20% | ❓ Não testado |

## Arquivos da Aplicação

- `moon_highlighter.py`: Versão completa da aplicação
- `moon_highlighter_simple.py`: Versão simplificada para testes
- `test_highlighter.py`: Script de teste para validar dados
- `requirements.txt`: Dependências Python
- `README_Python.md`: Esta documentação

## Licença

Este projeto é de código aberto e pode ser usado livremente. 