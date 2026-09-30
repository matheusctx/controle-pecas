# Controle de Qualidade de Peças Industriais

Sistema de terminal em Python para inspecionar peças, separá-las em **aprovadas** e **reprovadas** e organizar as aprovadas em **caixas de 10 unidades**.

Trabalho da disciplina **Algoritmos e Lógica de Programação** — UniFECAF.

## 1. O problema

Numa linha de produção, alguém precisa conferir **cada peça** contra uma lista de critérios (peso, cor, comprimento) e depois separar as boas em caixas. Feito à mão, isso tem três problemas:

- **Erros de conferência:** é fácil esquecer um critério ou errar um limite (a peça de 95 g é boa ou não?).
- **Motivo perdido:** quando a peça é rejeitada, ninguém anota *por quê*, e fica difícil corrigir o processo.
- **Contagem das caixas:** perder a conta de quantas peças já estão em cada caixa.

O programa automatiza isso: o operador digita os dados da peça, o sistema aplica todas as regras, registra **todos** os motivos de uma eventual reprovação, controla as caixas sozinho e gera um relatório no final.

## 2. Regras

### Qualidade (limites inclusivos)

| Característica | Regra para aprovar |
|---|---|
| Peso | de **95 a 105 g** |
| Cor | **azul** ou **verde** (maiúsculas e espaços são ignorados: `" AZUL "` vale como `azul`) |
| Comprimento | de **10 a 20 cm** |

- "Inclusivo" significa que 95 g, 105 g, 10 cm e 20 cm **são aprovados**; 94.9 g e 20.1 cm não são.
- Uma peça pode falhar em **mais de um** critério; todos os motivos são registrados.
- Todos os valores dessas regras ficam em `config.py`, então mudar um limite não exige mexer no resto do código.

### Armazenamento

- Cada peça **tem um ID único**; IDs repetidos são recusados.
- Peças **aprovadas** vão para a **caixa aberta** atual. Cada caixa comporta **10 peças**.
- Ao chegar a 10, a caixa é **fechada** e uma nova é aberta automaticamente.
- Peças **reprovadas** não entram em caixa.

### Remoção de peças

| Situação da peça | O que acontece |
|---|---|
| Reprovada | É removida. |
| Aprovada, em caixa **aberta** | É removida da caixa e da lista. |
| Aprovada, em caixa **fechada** | **Recusada**: o sistema explica que o lote já foi fechado. |

**Por quê?** Uma caixa fechada representa um lote já embalado e conferido. Se fosse possível tirar peças dele, a contagem e a rastreabilidade do lote (quais peças foram para qual caixa) deixariam de ser confiáveis. Por isso, uma caixa fechada é **definitiva** e nunca reabre.

## 3. Estrutura do projeto

```
controle-pecas/
├── main.py             # menu em loop, entrada do usuário e modo --demo
├── config.py           # constantes: limites, cores válidas, capacidade da caixa, textos
├── validacao.py        # leitura segura de entradas e a função avaliar_peca
├── armazenamento.py    # estado do sistema (peças e caixas), cadastro, remoção, JSON
├── relatorios.py       # tabela de peças, caixas e relatório final
├── tests/
│   ├── test_validacao.py
│   ├── test_armazenamento.py
│   ├── test_relatorios.py
│   └── test_main.py
├── CLAUDE.md           # regras do projeto (estilo, convenções)
├── README.md
└── .gitignore
```

| Módulo | Papel |
|---|---|
| `config.py` | Guarda todas as constantes. Nenhum "número mágico" fica espalhado pelo código. |
| `validacao.py` | `ler_texto` e `ler_float` repetem a pergunta até a resposta ser válida. `avaliar_peca` aplica os critérios e devolve `(status, motivos)`. |
| `armazenamento.py` | Mantém o dicionário `estado` (lista de peças, caixa aberta e caixas fechadas). Cadastra, remove, fecha caixas e grava/lê o `pecas.json`. |
| `relatorios.py` | Só exibe informação: tabela alinhada, lista de caixas fechadas e relatório final. |
| `main.py` | Menu, leitura dos dados no terminal, flag `--demo` e tratamento do Ctrl+C. |

O programa é **procedural** (funções, listas e dicionários, sem classes) e usa **apenas a biblioteca padrão**.

Cada peça é um dicionário, e cada caixa também:

```python
peca  = {"id": "A100", "peso": 100.0, "cor": "azul", "comprimento": 15.0,
         "status": "aprovada", "motivos": [], "caixa": 2}
caixa = {"numero": 2, "pecas": ["P011", "P012", "..."], "fechada": False}
```

## 4. Como rodar

**1. Verifique se o Python está instalado:**

```
python3 --version
```

No Windows, use `py --version`.

O programa usa apenas a biblioteca padrão e roda a partir do Python 3.9. Recomenda-se o Python 3.12 ou mais recente: as versões 3.9 e 3.10 já chegaram (ou estão chegando) ao fim do suporte oficial e não recebem mais correções de segurança. Instale a versão atual em <https://www.python.org/downloads/>.

**2. Obtenha o projeto:**

```
git clone https://github.com/matheusctx/controle-pecas.git
cd controle-pecas
```

Sem Git, baixe o ZIP do repositório e extraia a pasta.

**3. Execute:**

```
python3 main.py
```

Nenhuma instalação de pacotes é necessária. Os dados ficam salvos em `pecas.json` e são carregados na próxima execução.

**4. Modo demonstração** (carrega 25 peças variadas, sem ler nem gravar `pecas.json`):

```
python3 main.py --demo
```

São 14 aprovadas (incluindo os limites 95, 105, 10 e 20) e 11 reprovadas por motivos diferentes. Com isso, a caixa 1 já vem fechada e a caixa 2 aberta com 4 peças.

**5. Rode os testes:**

```
python3 -m unittest -v
```

Testado com Python 3.9 (versão legada, sem suporte oficial) e 3.12.

## 5. Exemplos reais de execução

Todas as saídas abaixo foram geradas executando o `main.py` de verdade. Os exemplos 1 a 5 usam `python3 main.py --demo`, por isso as peças `P001` a `P025` já existem e a caixa 2 começa com 4 peças. As saídas do programa estão exatamente como foram impressas; o trecho de menu foi omitido onde indicado com `[...]`. No terminal, o que você digita aparece na mesma linha do prompt, como abaixo.

### 5.1 Cadastro de peça aprovada

Note que a cor `" Azul "` (com espaços e maiúscula) é aceita.

```
Escolha uma opção: 1

--- Cadastrar nova peça ---
ID da peça: A100
Peso (g): 100
Cor:  Azul 
Comprimento (cm): 15

Resultado: APROVADA → caixa 2
```

### 5.2 Cadastro de peça reprovada com vários motivos

```
Escolha uma opção: 1

--- Cadastrar nova peça ---
ID da peça: B200
Peso (g): 120
Cor: Preto
Comprimento (cm): 25

Resultado: REPROVADA. Motivos:
  - Peso fora do intervalo (95–105g): 120.0g
  - Cor inválida (aceitas: azul, verde): 'preto'
  - Comprimento fora do intervalo (10–20cm): 25.0cm
```

### 5.3 Fechamento de caixa

Depois de A100, foram cadastradas mais quatro peças aprovadas (C300 a C303, todas na caixa 2). A décima peça da caixa, `C304`, fecha a caixa:

```
Escolha uma opção: 1

--- Cadastrar nova peça ---
ID da peça: C304
Peso (g): 103
Cor: verde
Comprimento (cm): 19

Resultado: APROVADA → caixa 2
*** Caixa 2 fechada com 10 peças. Caixa 3 aberta. ***
```

### 5.4 Tentativa de remover peça de caixa fechada

```
Escolha uma opção: 3

--- Remover peça cadastrada ---
ID da peça a remover: P003

ID   | Peso (g) | Cor  | Compr. (cm) | Status    | Caixa / Motivos
------------------------------------------------------------------
P003 |   105.00 | azul |       20.00 | aprovada  | caixa 1

A peça 'P003' não pode ser removida: a caixa 1 já foi fechada e o lote não pode mais ser alterado.
```

### 5.5 Listagem de reprovadas e caixas fechadas

Parte da tabela (as linhas omitidas estão marcadas com `[...]`):

```
Escolha uma opção: 2

--- Listar peças ---
  1. Aprovadas
  2. Reprovadas
  3. Todas
Ver quais? (1-3): 2

12 peça(s):

ID   | Peso (g) | Cor      | Compr. (cm) | Status    | Caixa / Motivos
----------------------------------------------------------------------
P015 |   110.00 | azul     |       15.00 | reprovada | Peso fora do intervalo (95–105g): 110.0g
P016 |    94.90 | verde    |       15.00 | reprovada | Peso fora do intervalo (95–105g): 94.9g
[...]
P022 |    90.00 | amarelo  |       15.00 | reprovada | Peso fora do intervalo (95–105g): 90.0g; Cor inválida (aceitas: azul, verde): 'amarelo'
[...]
B200 |   120.00 | preto    |       25.00 | reprovada | Peso fora do intervalo (95–105g): 120.0g; Cor inválida (aceitas: azul, verde): 'preto'; Comprimento fora do intervalo (10–20cm): 25.0cm
```

Opção 4:

```
Escolha uma opção: 4

=== Caixas fechadas (2) ===
Caixa 1 [FECHADA] 10/10: P001, P002, P003, P004, P005, P006, P007, P008, P009, P010
Caixa 2 [FECHADA] 10/10: P011, P012, P013, P014, A100, C300, C301, C302, C303, C304
```

### 5.6 Relatório final

Ao final da mesma sessão (25 peças do demo + A100, B200 e C300 a C304):

```
Escolha uma opção: 5

=== RELATÓRIO FINAL ===
Total de peças: 32
Aprovadas: 20
Reprovadas: 12
Taxa de aprovação: 62.5%

Motivos de reprovação (uma peça pode ter mais de um):
  7x Peso fora do intervalo (95–105g)
  6x Comprimento fora do intervalo (10–20cm)
  5x Cor inválida (aceitas: azul, verde)

Caixas fechadas: 2
Caixa 1 [FECHADA] 10/10: P001, P002, P003, P004, P005, P006, P007, P008, P009, P010
Caixa 2 [FECHADA] 10/10: P011, P012, P013, P014, A100, C300, C301, C302, C303, C304
Caixa aberta no momento:
Caixa 3 [aberta] 0/10: (vazia)
```

### 5.7 Entradas inválidas (o programa não quebra)

ID repetido, campo vazio, texto no lugar de número, número negativo e cor em branco:

```
Escolha uma opção: 1

--- Cadastrar nova peça ---
ID da peça: P001
Erro: já existe uma peça com o ID 'P001'.
ID da peça: 
Erro: o campo não pode ficar vazio.
ID da peça: N50
Peso (g): abc
Erro: digite um número válido (ex.: 100 ou 99,5).
Peso (g): -5
Erro: o valor deve ser um número maior que zero.
Peso (g): 
Erro: o campo não pode ficar vazio.
Peso (g): 100
Cor:    
Erro: o campo não pode ficar vazio.
Cor: azul
Comprimento (cm): 15

Resultado: APROVADA → caixa 2
```

### 5.8 Arquivo `pecas.json`

Gerado ao executar sem `--demo` e cadastrar uma peça (ID `X1`, 100 g, azul, 15 cm):

```json
{
  "pecas": [
    {
      "id": "X1",
      "peso": 100.0,
      "cor": "azul",
      "comprimento": 15.0,
      "status": "aprovada",
      "motivos": [],
      "caixa": 1
    }
  ],
  "caixa_aberta": {
    "numero": 1,
    "pecas": [
      "X1"
    ],
    "fechada": false
  },
  "caixas_fechadas": []
}
```

## 6. Conceitos de lógica aplicados

### Decisões (`if` / `elif` / `else`)

- **Aprovar ou reprovar:** `avaliar_peca` (`validacao.py`) testa cada critério com um `if` independente. Como não usa `elif`, uma peça pode acumular vários motivos. Ao final, `if motivos:` decide o status.
- **Intervalos inclusivos:** `if not config.PESO_MINIMO <= peso <= config.PESO_MAXIMO` (`avaliar_peca`). O operador `<=` dos dois lados é o que torna os limites inclusivos.
- **Menu:** a cadeia `if opcao == "1": ... elif opcao == "2": ... else:` em `executar_menu` (`main.py`).
- **Regra de remoção:** `motivo_bloqueio_remocao` e `remover_peca` (`armazenamento.py`) decidem entre os três cenários (reprovada, caixa aberta, caixa fechada).
- **Fechar caixa:** `if len(caixa["pecas"]) >= config.CAPACIDADE_CAIXA` em `colocar_na_caixa_aberta`.

### Repetição (`while` / `for`)

- **Menu:** `while True` em `executar_menu` roda até o usuário digitar `0` (`return`).
- **Validação de entrada:** `ler_texto`, `ler_float` e `ler_confirmacao` (`validacao.py`) usam `while True` e só saem (`return`) quando o valor é válido. É o padrão "pedir de novo em caso de erro".
- **Busca por ID:** `for peca in estado["pecas"]` em `buscar_peca`, que devolve a peça ao achar e `None` se o laço terminar sem achar.
- **Relatórios:** `for` em `mostrar_tabela_pecas` (uma linha por peça) e em `contar_motivos` (laço dentro de laço: peças → motivos → tipos).
- **Dados de demonstração:** `for ... in enumerate(PECAS_DEMO)` em `carregar_demo` (`main.py`).

### Funções

- **Uma responsabilidade por função:** ler dados (`validacao.py`), avaliar (`avaliar_peca`), guardar (`armazenamento.py`), mostrar (`relatorios.py`), coordenar (`main.py`).
- **Retorno de mais de um valor (tupla):** `avaliar_peca` devolve `(status, motivos)`; `cadastrar_peca` devolve `(peca, aviso)`; `remover_peca` devolve `(removida, mensagem)`.
- **Parâmetros com valor padrão:** `listar_pecas(status=None)` e `carregar_estado(caminho=config.ARQUIVO_DADOS)`.
- **Funções pequenas reaproveitadas:** `normalizar_cor`, `buscar_peca`, `mostrar_caixa`.

### Estruturas de dados

- **Dicionário:** cada peça e cada caixa (`montar_peca` e `criar_caixa`), o `estado` geral (`armazenamento.py`), o mapa de filtros da opção 2 (`filtros` em `opcao_listar`) e o contador de motivos (`contagem` em `contar_motivos`).
- **Lista:** `estado["pecas"]`, `caixa["pecas"]` (IDs) e `motivos`. Usa-se `append` para adicionar e `remove` para retirar.
- **Tupla:** `config.CORES_VALIDAS` (valores fixos) e os itens de `PECAS_DEMO` (`main.py`).
- **Lista de dicionários como "banco de dados":** as caixas guardam só os IDs, e cada peça guarda o número da caixa. Os dois lados se referenciam.
- **Texto formatado:** f-strings com alinhamento e largura dinâmica (`{campo:<{largura}}`) em `mostrar_tabela_pecas`.

### Tratamento de erros e persistência

- **`try` / `except`:** `ler_float` captura `ValueError` ao converter o texto em número. `main` captura `KeyboardInterrupt` (Ctrl+C) para sair com mensagem.
- **Erros de gravação e arquivo corrompido:** `gravar_dados` (`main.py`) captura `OSError` e avisa sem encerrar; `estado_valido` (`armazenamento.py`) recusa um JSON com formato errado em vez de quebrar mais tarde.
- **Arquivo JSON:** `salvar_estado` e `carregar_estado` usam o módulo `json`. A gravação passa por um arquivo temporário e `os.replace`, para não corromper os dados se o programa for interrompido.

## 7. Possíveis evoluções

- **Novos critérios** de qualidade (por exemplo, diâmetro ou acabamento): bastaria um novo par de constantes em `config.py` e mais um `if` em `avaliar_peca`.
- **Relatório exportado** em CSV ou em arquivo de texto, para levar para planilha.
- **Busca e filtros** na listagem (por cor, por faixa de peso, por caixa).
- **Histórico e data/hora** de cada inspeção e de cada fechamento de caixa.
- **Mais de um operador ou linha de produção**, com estado separado por linha.
- **Edição de peça** (corrigir um valor digitado errado) mantendo as regras de caixa.
- **Interface gráfica ou web**, reaproveitando `validacao.py` e `armazenamento.py` sem alterações.
- **Banco de dados** (SQLite, também na biblioteca padrão) no lugar do JSON, para volumes maiores.
