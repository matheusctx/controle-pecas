"""Mantém o estado do sistema: peças, caixa aberta atual e caixas fechadas.

O estado é um único dicionário (`estado`) que as funções deste módulo alteram.
Cada caixa é um dicionário: {"numero": int, "pecas": [ids], "fechada": bool}.
Uma caixa fechada é definitiva: suas peças não podem mais ser removidas.
"""

import json
import os

import config
from validacao import avaliar_peca, normalizar_cor


def criar_caixa(numero):
    """Cria uma caixa nova, aberta e vazia."""
    return {"numero": numero, "pecas": [], "fechada": False}


def reiniciar_estado():
    """Zera o estado: nenhuma peça, nenhuma caixa fechada e a caixa 1 aberta."""
    estado["pecas"] = []
    estado["caixa_aberta"] = criar_caixa(1)
    estado["caixas_fechadas"] = []


estado = {}
reiniciar_estado()


# ---------- arquivo JSON ----------

CAMPOS_PECA = {"id", "peso", "cor", "comprimento", "status", "motivos", "caixa"}
CAMPOS_CAIXA = {"numero", "pecas", "fechada"}


def estado_valido(dados):
    """Confere se o conteúdo lido do JSON tem a forma esperada (evita erros mais adiante)."""
    if not isinstance(dados, dict) or set(dados) != set(estado):
        return False
    if not isinstance(dados["pecas"], list) or not isinstance(dados["caixas_fechadas"], list):
        return False
    caixas = dados["caixas_fechadas"] + [dados["caixa_aberta"]]
    for caixa in caixas:
        if not isinstance(caixa, dict) or set(caixa) != CAMPOS_CAIXA:
            return False
    for peca in dados["pecas"]:
        if not isinstance(peca, dict) or set(peca) != CAMPOS_PECA:
            return False
    return True


def carregar_estado(caminho=config.ARQUIVO_DADOS):
    """Lê o estado do arquivo JSON. Se o arquivo não existir, mantém o estado atual.
    Levanta ValueError se o conteúdo não tiver o formato esperado."""
    if not os.path.exists(caminho):
        return
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not estado_valido(dados):
        raise ValueError("formato de arquivo não reconhecido")
    estado.update(dados)


def salvar_estado(caminho=config.ARQUIVO_DADOS):
    """Grava o estado em JSON. Escreve num arquivo temporário e troca no final,
    para não corromper os dados se o programa for interrompido no meio."""
    caminho_temporario = caminho + ".tmp"
    with open(caminho_temporario, "w", encoding="utf-8") as arquivo:
        json.dump(estado, arquivo, ensure_ascii=False, indent=2)
    os.replace(caminho_temporario, caminho)


# ---------- consultas ----------

def buscar_peca(id_peca):
    """Devolve a peça com esse ID, ou None se não existir."""
    for peca in estado["pecas"]:
        if peca["id"] == id_peca:
            return peca
    return None


def id_existe(id_peca):
    """Diz se já existe uma peça com esse ID."""
    return buscar_peca(id_peca) is not None


def obter_caixa_aberta():
    """Devolve a caixa aberta atual."""
    return estado["caixa_aberta"]


def listar_pecas(status=None):
    """Devolve as peças com o status indicado (todas, se status for None)."""
    return [peca for peca in estado["pecas"]
            if status is None or peca["status"] == status]


def listar_caixas_fechadas():
    """Devolve a lista de caixas fechadas."""
    return list(estado["caixas_fechadas"])


# ---------- alterações ----------

def montar_peca(id_peca, peso, cor, comprimento):
    """Avalia os dados e monta o dicionário da peça (ainda sem caixa)."""
    cor = normalizar_cor(cor)
    status, motivos = avaliar_peca(peso, cor, comprimento)
    return {
        "id": id_peca,
        "peso": peso,
        "cor": cor,
        "comprimento": comprimento,
        "status": status,
        "motivos": motivos,
        "caixa": None,
    }


def colocar_na_caixa_aberta(peca):
    """Coloca a peça na caixa aberta. Se a caixa encher, fecha e devolve o aviso (senão, None)."""
    caixa = estado["caixa_aberta"]
    caixa["pecas"].append(peca["id"])
    peca["caixa"] = caixa["numero"]
    if len(caixa["pecas"]) >= config.CAPACIDADE_CAIXA:
        return fechar_caixa_aberta()
    return None


def cadastrar_peca(id_peca, peso, cor, comprimento):
    """Cadastra a peça. Devolve (peca, aviso); o aviso é None, a menos que uma caixa tenha fechado.
    Levanta ValueError se o ID já existir."""
    if id_existe(id_peca):
        raise ValueError(f"já existe uma peça com o ID '{id_peca}'")

    peca = montar_peca(id_peca, peso, cor, comprimento)
    estado["pecas"].append(peca)

    aviso = None
    if peca["status"] == config.STATUS_APROVADA:
        aviso = colocar_na_caixa_aberta(peca)
    return peca, aviso


def fechar_caixa_aberta():
    """Fecha a caixa aberta, abre a próxima e devolve a mensagem de aviso."""
    caixa = estado["caixa_aberta"]
    caixa["fechada"] = True
    estado["caixas_fechadas"].append(caixa)
    estado["caixa_aberta"] = criar_caixa(caixa["numero"] + 1)
    return (f"Caixa {caixa['numero']} fechada com {config.CAPACIDADE_CAIXA} peças. "
            f"Caixa {caixa['numero'] + 1} aberta.")


def motivo_bloqueio_remocao(peca):
    """Devolve a mensagem que explica por que a peça não pode ser removida (ou None se pode)."""
    if peca["caixa"] is not None and peca["caixa"] != estado["caixa_aberta"]["numero"]:
        return (f"A peça '{peca['id']}' não pode ser removida: a caixa {peca['caixa']} "
                "já foi fechada e o lote não pode mais ser alterado.")
    return None


def remover_peca(id_peca):
    """Remove a peça. Devolve (removida, mensagem).
    Reprovada ou aprovada em caixa aberta: removida. Aprovada em caixa fechada: recusada."""
    peca = buscar_peca(id_peca)
    if peca is None:
        return False, f"Não existe peça com o ID '{id_peca}'."

    bloqueio = motivo_bloqueio_remocao(peca)
    if bloqueio is not None:
        return False, bloqueio

    if peca["caixa"] is not None:
        estado["caixa_aberta"]["pecas"].remove(id_peca)
    estado["pecas"].remove(peca)
    return True, f"Peça '{id_peca}' removida."
