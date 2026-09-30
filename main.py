"""Sistema de controle de qualidade de peças industriais (menu de terminal).

Uso:
    python main.py          # uso normal (dados salvos em pecas.json)
    python main.py --demo   # carrega 25 peças de exemplo, sem ler nem gravar pecas.json
"""

import argparse

import config
from armazenamento import (buscar_peca, cadastrar_peca, carregar_estado, id_existe,
                           listar_pecas, motivo_bloqueio_remocao, reiniciar_estado,
                           remover_peca, salvar_estado)
from relatorios import mostrar_caixas_fechadas, mostrar_relatorio_final, mostrar_tabela_pecas
from validacao import ler_confirmacao, ler_float, ler_texto

MENU = """
===== CONTROLE DE QUALIDADE DE PEÇAS =====
1. Cadastrar nova peça
2. Listar peças aprovadas/reprovadas
3. Remover peça cadastrada
4. Listar caixas fechadas
5. Gerar relatório final
0. Sair
"""

# Peças do modo demonstração: (peso, cor, comprimento). Os IDs são P001, P002, ...
PECAS_DEMO = [
    # --- 14 aprovadas (as 10 primeiras fecham a caixa 1; as outras 4 ficam na caixa 2) ---
    (100, "azul", 15),
    (95, "verde", 10),          # limites mínimos
    (105, " AZUL ", 20),        # limites máximos, cor com maiúsculas e espaços
    (98.5, "verde", 12.3),
    (102, "  Verde  ", 18),
    (95, "azul", 20),
    (105, "verde", 10),
    (100, "azul", 14.5),
    (99.9, "verde", 17),
    (101.2, "azul", 11),        # 10ª aprovada: fecha a caixa 1
    (97, "verde", 19.9),
    (103.5, "azul", 13),
    (100, "verde", 16),
    (96.4, "azul", 10.5),
    # --- 11 reprovadas, por motivos variados ---
    (110, "azul", 15),          # peso alto
    (94.9, "verde", 15),        # peso logo abaixo do limite
    (105.1, "azul", 15),        # peso logo acima do limite
    (100, "vermelho", 15),      # cor inválida
    (100, "Preto", 15),         # cor inválida (normalizada)
    (100, "azul", 9.9),         # comprimento logo abaixo do limite
    (100, "verde", 20.1),       # comprimento logo acima do limite
    (90, "amarelo", 15),        # peso + cor
    (120, "azul", 25),          # peso + comprimento
    (50, "cinza", 5),           # os três critérios
    (100, "verde", 30),         # comprimento alto
]


def carregar_demo():
    """Zera o estado e cadastra as peças de demonstração."""
    reiniciar_estado()
    for numero, (peso, cor, comprimento) in enumerate(PECAS_DEMO, start=1):
        cadastrar_peca(f"P{numero:03d}", peso, cor, comprimento)


def gravar_dados(persistir):
    """Salva o estado em JSON (se permitido). Se falhar, avisa e o programa continua."""
    if not persistir:
        return
    try:
        salvar_estado()
    except OSError as erro:
        print(f"AVISO: não foi possível gravar '{config.ARQUIVO_DADOS}': {erro}")
        print("Os dados continuam na memória, mas serão perdidos se o programa for fechado.")


def ler_dados_da_peca():
    """Pergunta ID (que não pode repetir), peso, cor e comprimento. Devolve os quatro valores."""
    while True:
        id_peca = ler_texto("ID da peça: ")
        if id_existe(id_peca):
            print(f"Erro: já existe uma peça com o ID '{id_peca}'.")
        else:
            break
    peso = ler_float("Peso (g): ")
    cor = ler_texto("Cor: ")
    comprimento = ler_float("Comprimento (cm): ")
    return id_peca, peso, cor, comprimento


def mostrar_resultado_cadastro(peca, aviso):
    """Mostra na hora se a peça foi aprovada (e em qual caixa) ou reprovada (e por quê)."""
    if peca["status"] == config.STATUS_APROVADA:
        print(f"\nResultado: APROVADA → caixa {peca['caixa']}")
    else:
        print("\nResultado: REPROVADA. Motivos:")
        for motivo in peca["motivos"]:
            print(f"  - {motivo}")
    if aviso:
        print(f"*** {aviso} ***")


def opcao_cadastrar(persistir):
    """Lê os dados de uma peça, cadastra, salva e mostra o resultado."""
    print("\n--- Cadastrar nova peça ---")
    id_peca, peso, cor, comprimento = ler_dados_da_peca()
    peca, aviso = cadastrar_peca(id_peca, peso, cor, comprimento)
    gravar_dados(persistir)
    mostrar_resultado_cadastro(peca, aviso)


def opcao_listar():
    """Pergunta qual grupo de peças mostrar e imprime a tabela."""
    print("\n--- Listar peças ---")
    print("  1. Aprovadas")
    print("  2. Reprovadas")
    print("  3. Todas")
    filtros = {"1": config.STATUS_APROVADA, "2": config.STATUS_REPROVADA, "3": None}
    while True:
        escolha = input("Ver quais? (1-3): ").strip()
        if escolha in filtros:
            break
        print("Erro: escolha 1, 2 ou 3.")

    pecas = listar_pecas(filtros[escolha])
    print(f"\n{len(pecas)} peça(s):\n")
    mostrar_tabela_pecas(pecas)


def opcao_remover(persistir):
    """Remove uma peça pelo ID, exceto se ela estiver numa caixa já fechada."""
    print("\n--- Remover peça cadastrada ---")
    id_peca = ler_texto("ID da peça a remover: ")
    peca = buscar_peca(id_peca)
    if peca is None:
        print(f"Não existe peça com o ID '{id_peca}'.")
        return

    print()
    mostrar_tabela_pecas([peca])
    bloqueio = motivo_bloqueio_remocao(peca)
    if bloqueio is not None:
        print(f"\n{bloqueio}")
        return
    if not ler_confirmacao("\nConfirmar a remoção?"):
        print("Remoção cancelada.")
        return

    _, mensagem = remover_peca(id_peca)
    gravar_dados(persistir)
    print(mensagem)


def executar_menu(persistir):
    """Laço principal: mostra o menu e executa a opção escolhida até o usuário sair."""
    while True:
        print(MENU)
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            opcao_cadastrar(persistir)
        elif opcao == "2":
            opcao_listar()
        elif opcao == "3":
            opcao_remover(persistir)
        elif opcao == "4":
            mostrar_caixas_fechadas()
        elif opcao == "5":
            mostrar_relatorio_final()
        elif opcao == "0":
            print("Encerrando. Até logo!")
            return
        else:
            print("Opção inválida. Digite um número de 0 a 5.")


def preparar_dados(modo_demo):
    """Carrega as peças de exemplo (--demo) ou o arquivo JSON. Devolve False se não deu certo."""
    if modo_demo:
        carregar_demo()
        print(f"MODO DEMONSTRAÇÃO: {len(PECAS_DEMO)} peças carregadas "
              f"(nada será gravado em {config.ARQUIVO_DADOS}).")
        return True
    try:
        carregar_estado()
    except (ValueError, OSError) as erro:
        print(f"Não foi possível ler '{config.ARQUIVO_DADOS}': {erro}")
        print("Corrija ou apague o arquivo e execute o programa novamente.")
        return False
    return True


def main(argumentos=None):
    """Lê a flag --demo, prepara os dados e abre o menu."""
    analisador = argparse.ArgumentParser(description="Controle de qualidade de peças industriais.")
    analisador.add_argument("--demo", action="store_true",
                            help="carrega 25 peças de exemplo (sem ler nem gravar pecas.json)")
    opcoes = analisador.parse_args(argumentos)

    if not preparar_dados(opcoes.demo):
        return
    try:
        executar_menu(persistir=not opcoes.demo)
    except (KeyboardInterrupt, EOFError):
        print("\n\nPrograma interrompido pelo usuário. Até logo!")


if __name__ == "__main__":
    main()
