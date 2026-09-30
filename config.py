"""Constantes do sistema. Para mudar uma regra, altere apenas este arquivo."""

# Critérios de aprovação (limites inclusivos)
PESO_MINIMO = 95.0          # em gramas
PESO_MAXIMO = 105.0
COMPRIMENTO_MINIMO = 10.0   # em centímetros
COMPRIMENTO_MAXIMO = 20.0
CORES_VALIDAS = ("azul", "verde")

# Caixas
CAPACIDADE_CAIXA = 10

# Status possíveis de uma peça
STATUS_APROVADA = "aprovada"
STATUS_REPROVADA = "reprovada"

# Início das mensagens de reprovação. A mensagem completa acrescenta ": <valor lido>".
# Os relatórios agrupam os motivos por este início (texto antes dos dois-pontos).
MOTIVO_PESO = f"Peso fora do intervalo ({PESO_MINIMO:g}–{PESO_MAXIMO:g}g)"
MOTIVO_COR = f"Cor inválida (aceitas: {', '.join(CORES_VALIDAS)})"
MOTIVO_COMPRIMENTO = f"Comprimento fora do intervalo ({COMPRIMENTO_MINIMO:g}–{COMPRIMENTO_MAXIMO:g}cm)"

# Arquivo onde as peças são salvas
ARQUIVO_DADOS = "pecas.json"
