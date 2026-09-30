"""Leitura segura de entradas do usuário e regras de aprovação das peças."""

import math

import config


def ler_texto(mensagem):
    """Pede um texto e repete enquanto o campo estiver vazio."""
    while True:
        texto = input(mensagem).strip()
        if texto == "":
            print("Erro: o campo não pode ficar vazio.")
        else:
            return texto


def ler_float(mensagem):
    """Pede um número maior que zero (aceita vírgula ou ponto) e repete se for inválido."""
    while True:
        texto = input(mensagem).strip().replace(",", ".")
        if texto == "":
            print("Erro: o campo não pode ficar vazio.")
            continue
        try:
            valor = float(texto)
        except ValueError:
            print("Erro: digite um número válido (ex.: 100 ou 99,5).")
            continue
        if not math.isfinite(valor) or valor <= 0:
            print("Erro: o valor deve ser um número maior que zero.")
            continue
        return valor


def ler_confirmacao(mensagem):
    """Pede 's' ou 'n' e devolve True para sim, False para não."""
    while True:
        resposta = input(mensagem + " (s/n): ").strip().lower()
        if resposta == "s":
            return True
        if resposta == "n":
            return False
        print("Erro: responda apenas com 's' ou 'n'.")


def normalizar_cor(cor):
    """Remove espaços das pontas e deixa a cor em minúsculas."""
    return cor.strip().lower()


def avaliar_peca(peso, cor, comprimento):
    """Avalia a peça e devolve (status, motivos).

    Se todos os critérios forem atendidos, o status é "aprovada" e motivos é [].
    Caso contrário, o status é "reprovada" e motivos traz uma mensagem por critério falho.
    """
    cor = normalizar_cor(cor)
    motivos = []
    if not config.PESO_MINIMO <= peso <= config.PESO_MAXIMO:
        motivos.append(f"{config.MOTIVO_PESO}: {float(peso)}g")
    if cor not in config.CORES_VALIDAS:
        motivos.append(f"{config.MOTIVO_COR}: '{cor}'")
    if not config.COMPRIMENTO_MINIMO <= comprimento <= config.COMPRIMENTO_MAXIMO:
        motivos.append(f"{config.MOTIVO_COMPRIMENTO}: {float(comprimento)}cm")

    if motivos:
        return config.STATUS_REPROVADA, motivos
    return config.STATUS_APROVADA, motivos
