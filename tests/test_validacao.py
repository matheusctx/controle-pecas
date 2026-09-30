import unittest
from unittest.mock import patch

from validacao import avaliar_peca, ler_float, ler_texto, normalizar_cor


class TestAvaliarPeca(unittest.TestCase):
    def test_peca_perfeita(self):
        self.assertEqual(avaliar_peca(100, "azul", 15), ("aprovada", []))

    # --- cada critério falhando isoladamente ---
    def test_so_peso_falha(self):
        status, motivos = avaliar_peca(110.0, "azul", 15)
        self.assertEqual(status, "reprovada")
        self.assertEqual(motivos, ["Peso fora do intervalo (95–105g): 110.0g"])

    def test_so_cor_falha(self):
        status, motivos = avaliar_peca(100, "vermelho", 15)
        self.assertEqual(status, "reprovada")
        self.assertEqual(motivos, ["Cor inválida (aceitas: azul, verde): 'vermelho'"])

    def test_so_comprimento_falha(self):
        status, motivos = avaliar_peca(100, "verde", 25.0)
        self.assertEqual(status, "reprovada")
        self.assertEqual(motivos, ["Comprimento fora do intervalo (10–20cm): 25.0cm"])

    # --- todos falhando juntos ---
    def test_todos_falham(self):
        status, motivos = avaliar_peca(50, "preto", 99)
        self.assertEqual(status, "reprovada")
        self.assertEqual(motivos, [
            "Peso fora do intervalo (95–105g): 50.0g",
            "Cor inválida (aceitas: azul, verde): 'preto'",
            "Comprimento fora do intervalo (10–20cm): 99.0cm",
        ])

    # --- exatamente nos limites: aprovados ---
    def test_limites_inclusivos(self):
        for peso, comprimento in [(95, 10), (105, 20), (95, 20), (105, 10)]:
            with self.subTest(peso=peso, comprimento=comprimento):
                self.assertEqual(avaliar_peca(peso, "azul", comprimento), ("aprovada", []))

    # --- logo fora dos limites: reprovados ---
    def test_logo_abaixo_do_peso(self):
        status, motivos = avaliar_peca(94.9, "azul", 15)
        self.assertEqual(status, "reprovada")
        self.assertEqual(motivos, ["Peso fora do intervalo (95–105g): 94.9g"])

    def test_logo_acima_do_peso(self):
        status, motivos = avaliar_peca(105.1, "azul", 15)
        self.assertEqual(status, "reprovada")
        self.assertEqual(motivos, ["Peso fora do intervalo (95–105g): 105.1g"])

    def test_logo_abaixo_do_comprimento(self):
        status, motivos = avaliar_peca(100, "azul", 9.9)
        self.assertEqual(status, "reprovada")
        self.assertEqual(motivos, ["Comprimento fora do intervalo (10–20cm): 9.9cm"])

    def test_logo_acima_do_comprimento(self):
        status, motivos = avaliar_peca(100, "azul", 20.1)
        self.assertEqual(status, "reprovada")
        self.assertEqual(motivos, ["Comprimento fora do intervalo (10–20cm): 20.1cm"])

    # --- cor com maiúsculas e espaços ---
    def test_cor_com_maiusculas_e_espacos(self):
        for cor in ["AZUL", "  Verde ", "\tAzUl\n"]:
            with self.subTest(cor=cor):
                self.assertEqual(avaliar_peca(100, cor, 15), ("aprovada", []))

    def test_cor_invalida_aparece_normalizada(self):
        _, motivos = avaliar_peca(100, "  VERMELHO ", 15)
        self.assertEqual(motivos, ["Cor inválida (aceitas: azul, verde): 'vermelho'"])

    def test_normalizar_cor(self):
        self.assertEqual(normalizar_cor("  AzUl "), "azul")


class TestLeitura(unittest.TestCase):
    def test_numero_repete_ate_ser_valido(self):
        entradas = ["", "abc", "-5", "0", "nan", "inf", "99,5"]
        with patch("builtins.input", side_effect=entradas), patch("builtins.print"):
            self.assertEqual(ler_float("x"), 99.5)

    def test_texto_repete_se_vazio(self):
        with patch("builtins.input", side_effect=["", "   ", " A1 "]), patch("builtins.print"):
            self.assertEqual(ler_texto("x"), "A1")


if __name__ == "__main__":
    unittest.main()
