# Controle de Qualidade de Peças

Trabalho acadêmico de **Algoritmos e Lógica de Programação** (UniFECAF).
Sistema de terminal, em Python, para controle de qualidade de peças industriais.
O código será explicado em vídeo e em documento, então **clareza vale mais que sofisticação**.

## Regras técnicas

- Python 3.9+ e **apenas a biblioteca padrão** (proibido `pip install`).
- Estilo **procedural**: funções, listas e dicionários. **Não usar classes.**
- Código didático: funções curtas, uma responsabilidade por função, sem truques.
- Nomes de variáveis e funções **em português**, em `snake_case`.
- Docstrings curtas, em português.
- Constantes (limites, cores válidas, capacidade da caixa) ficam no topo de `config.py`.
  **Nunca** usar "números mágicos" ou strings soltas pelo código.

## Modelo de dados

Cada peça é um dicionário:

```python
{
    "id": str,
    "peso": float,
    "cor": str,
    "comprimento": float,
    "status": "aprovada" | "reprovada",
    "motivos": list[str],
    "caixa": int | None,
}
```

## Regras de negócio

- Critérios de aprovação (limites **inclusivos**):
  - peso de 95 a 105 g;
  - cor `"azul"` ou `"verde"` (normalizar com `strip().lower()`);
  - comprimento de 10 a 20 cm.
- Uma peça pode ter **vários** motivos de reprovação; registrar **todos** em `motivos`.
- Peças aprovadas vão para caixas de capacidade 10. Ao atingir 10, a caixa é fechada e uma nova é aberta.
- Peças reprovadas têm `caixa = None`.
- IDs são únicos; IDs duplicados são rejeitados.
- Remover peça pelo ID: reprovada → remove; aprovada em caixa **aberta** → remove da caixa e da lista;
  aprovada em caixa **fechada** → **recusado** (o lote já foi fechado). Caixa fechada nunca reabre.
- Estado em `armazenamento.py`: dicionário `estado` com `pecas`, `caixa_aberta` e `caixas_fechadas`.
  Cada caixa é `{"numero": int, "pecas": [ids], "fechada": bool}`.
- Persistência: peças salvas em `pecas.json` (módulo `json`), a cada cadastro ou remoção.

## Entrada do usuário

- Toda entrada é validada (número inválido, campo vazio) **sem quebrar o programa**.
- Em caso de erro, mostrar mensagem clara e **pedir novamente**.

## Organização dos arquivos

- `config.py`: constantes.
- `validacao.py`: leitura e validação de entradas, e regras de aprovação.
- `armazenamento.py`: lista de peças, caixas, cadastro, remoção e leitura/gravação do JSON.
- `relatorios.py`: listagens e estatísticas.
- `main.py`: menu e laço principal.
- `tests/`: testes com `unittest` (biblioteca padrão).
- `README.md`: como executar e explicação do projeto.

## Convenções de trabalho

- Não escrever código novo sem a estrutura estar aprovada pelo usuário.
- Ao alterar regras de negócio, atualizar `config.py`, os testes e o README juntos.
- Rodar os testes com `python3 -m unittest -v`.
