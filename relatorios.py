"""Tabelas e relatórios exibidos no terminal (tudo montado com f-strings)."""

import config
from armazenamento import listar_caixas_fechadas, listar_pecas, obter_caixa_aberta


def contar_motivos(pecas):
    """Devolve {tipo de motivo: quantidade}. Cada mensagem começa com o texto do seu tipo
    (config.MOTIVO_*), seguido do valor lido; contamos pelo tipo, ignorando o valor."""
    tipos = [config.MOTIVO_PESO, config.MOTIVO_COR, config.MOTIVO_COMPRIMENTO]
    contagem = {}
    for peca in pecas:
        for motivo in peca["motivos"]:
            for tipo in tipos:
                if motivo.startswith(tipo):
                    contagem[tipo] = contagem.get(tipo, 0) + 1
    return contagem


def detalhe_da_peca(peca):
    """Texto da última coluna: a caixa (se aprovada) ou os motivos (se reprovada)."""
    if peca["caixa"] is not None:
        return f"caixa {peca['caixa']}"
    return "; ".join(peca["motivos"])


def mostrar_tabela_pecas(pecas):
    """Imprime as peças numa tabela com colunas alinhadas."""
    if not pecas:
        print("Nenhuma peça para mostrar.")
        return

    larg_id = max([len("ID")] + [len(peca["id"]) for peca in pecas])
    larg_cor = max([len("Cor")] + [len(peca["cor"]) for peca in pecas])
    larg_status = len(config.STATUS_REPROVADA)

    cabecalho = (f"{'ID':<{larg_id}} | {'Peso (g)':>8} | {'Cor':<{larg_cor}} | "
                 f"{'Compr. (cm)':>11} | {'Status':<{larg_status}} | Caixa / Motivos")
    print(cabecalho)
    print("-" * len(cabecalho))
    for peca in pecas:
        print(f"{peca['id']:<{larg_id}} | {peca['peso']:>8.2f} | {peca['cor']:<{larg_cor}} | "
              f"{peca['comprimento']:>11.2f} | {peca['status']:<{larg_status}} | "
              f"{detalhe_da_peca(peca)}")


def mostrar_caixa(caixa):
    """Imprime uma caixa: situação, ocupação e IDs das peças."""
    situacao = "FECHADA" if caixa["fechada"] else "aberta"
    ids = ", ".join(caixa["pecas"]) if caixa["pecas"] else "(vazia)"
    print(f"Caixa {caixa['numero']} [{situacao}] "
          f"{len(caixa['pecas'])}/{config.CAPACIDADE_CAIXA}: {ids}")


def mostrar_caixas_fechadas():
    """Lista as caixas fechadas."""
    caixas = listar_caixas_fechadas()
    print(f"\n=== Caixas fechadas ({len(caixas)}) ===")
    if not caixas:
        print("Nenhuma caixa fechada ainda.")
    for caixa in caixas:
        mostrar_caixa(caixa)


def mostrar_totais(pecas):
    """Mostra total, aprovadas, reprovadas e taxa de aprovação."""
    total = len(pecas)
    aprovadas = len(listar_pecas(config.STATUS_APROVADA))
    print(f"Total de peças: {total}")
    print(f"Aprovadas: {aprovadas}")
    print(f"Reprovadas: {total - aprovadas}")
    if total > 0:
        print(f"Taxa de aprovação: {aprovadas / total * 100:.1f}%")


def mostrar_motivos(pecas):
    """Mostra quantas vezes cada tipo de motivo de reprovação apareceu."""
    contagem = contar_motivos(pecas)
    if contagem:
        print("\nMotivos de reprovação (uma peça pode ter mais de um):")
        for motivo, quantidade in sorted(contagem.items(), key=lambda item: -item[1]):
            print(f"  {quantidade}x {motivo}")


def mostrar_relatorio_final():
    """Mostra totais, motivos de reprovação e situação das caixas."""
    pecas = listar_pecas()
    print("\n=== RELATÓRIO FINAL ===")
    mostrar_totais(pecas)
    mostrar_motivos(pecas)

    print(f"\nCaixas fechadas: {len(listar_caixas_fechadas())}")
    for caixa in listar_caixas_fechadas():
        mostrar_caixa(caixa)
    print("Caixa aberta no momento:")
    mostrar_caixa(obter_caixa_aberta())
