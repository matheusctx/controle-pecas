import os
import tempfile
import unittest

import config
from armazenamento import (buscar_peca, cadastrar_peca, carregar_estado, estado,
                           listar_caixas_fechadas, listar_pecas, obter_caixa_aberta,
                           reiniciar_estado, remover_peca, salvar_estado)


def cadastrar_aprovadas(quantidade, prefixo="P"):
    for i in range(1, quantidade + 1):
        cadastrar_peca(f"{prefixo}{i}", 100, "azul", 15)


class BaseComEstadoLimpo(unittest.TestCase):
    def setUp(self):
        reiniciar_estado()


class TestCadastro(BaseComEstadoLimpo):
    def test_aprovada_vai_para_caixa_aberta(self):
        peca, aviso = cadastrar_peca("A1", 100, "  AZUL ", 15)
        self.assertEqual(peca["status"], "aprovada")
        self.assertEqual(peca["cor"], "azul")
        self.assertEqual(peca["caixa"], 1)
        self.assertIsNone(aviso)
        self.assertEqual(obter_caixa_aberta()["pecas"], ["A1"])

    def test_reprovada_nao_vai_para_caixa(self):
        peca, aviso = cadastrar_peca("R1", 50, "preto", 15)
        self.assertEqual(peca["status"], "reprovada")
        self.assertIsNone(peca["caixa"])
        self.assertEqual(len(peca["motivos"]), 2)
        self.assertIsNone(aviso)
        self.assertEqual(obter_caixa_aberta()["pecas"], [])

    def test_id_duplicado_recusado(self):
        cadastrar_peca("A1", 100, "azul", 15)
        with self.assertRaises(ValueError):
            cadastrar_peca("A1", 50, "preto", 99)
        self.assertEqual(len(listar_pecas()), 1)

    def test_id_duplicado_recusado_mesmo_se_reprovada(self):
        cadastrar_peca("R1", 50, "azul", 15)
        with self.assertRaises(ValueError):
            cadastrar_peca("R1", 100, "azul", 15)


class TestCaixas(BaseComEstadoLimpo):
    def test_nove_aprovadas_nao_fecham(self):
        cadastrar_aprovadas(config.CAPACIDADE_CAIXA - 1)
        self.assertEqual(listar_caixas_fechadas(), [])

    def test_dez_aprovadas_fecham_caixa_1(self):
        for i in range(1, config.CAPACIDADE_CAIXA):
            _, aviso = cadastrar_peca(f"P{i}", 100, "azul", 15)
            self.assertIsNone(aviso)
        _, aviso = cadastrar_peca("P10", 100, "azul", 15)

        self.assertIn("Caixa 1 fechada", aviso)
        self.assertIn("Caixa 2 aberta", aviso)
        fechadas = listar_caixas_fechadas()
        self.assertEqual(len(fechadas), 1)
        self.assertEqual(fechadas[0]["numero"], 1)
        self.assertTrue(fechadas[0]["fechada"])
        self.assertEqual(len(fechadas[0]["pecas"]), 10)
        self.assertEqual(obter_caixa_aberta(), {"numero": 2, "pecas": [], "fechada": False})

    def test_decima_primeira_vai_para_caixa_2(self):
        cadastrar_aprovadas(config.CAPACIDADE_CAIXA)
        peca, aviso = cadastrar_peca("P11", 100, "verde", 12)
        self.assertEqual(peca["caixa"], 2)
        self.assertIsNone(aviso)
        self.assertEqual(obter_caixa_aberta()["pecas"], ["P11"])

    def test_reprovadas_nao_contam_para_a_caixa(self):
        cadastrar_aprovadas(config.CAPACIDADE_CAIXA - 1)
        cadastrar_peca("R1", 50, "azul", 15)
        self.assertEqual(listar_caixas_fechadas(), [])
        self.assertEqual(len(obter_caixa_aberta()["pecas"]), config.CAPACIDADE_CAIXA - 1)


class TestRemocao(BaseComEstadoLimpo):
    def test_remover_reprovada(self):
        cadastrar_peca("R1", 50, "azul", 15)
        removida, mensagem = remover_peca("R1")
        self.assertTrue(removida)
        self.assertIsNone(buscar_peca("R1"))
        self.assertIn("removida", mensagem)

    def test_remover_aprovada_em_caixa_aberta(self):
        cadastrar_aprovadas(3)
        removida, _ = remover_peca("P2")
        self.assertTrue(removida)
        self.assertIsNone(buscar_peca("P2"))
        self.assertEqual(obter_caixa_aberta()["pecas"], ["P1", "P3"])

    def test_remover_aprovada_em_caixa_fechada_e_recusada(self):
        cadastrar_aprovadas(config.CAPACIDADE_CAIXA)
        removida, mensagem = remover_peca("P3")
        self.assertFalse(removida)
        self.assertIn("fechada", mensagem)
        self.assertIsNotNone(buscar_peca("P3"))
        self.assertEqual(len(listar_caixas_fechadas()[0]["pecas"]), 10)

    def test_remover_inexistente(self):
        removida, mensagem = remover_peca("Z")
        self.assertFalse(removida)
        self.assertIn("Não existe", mensagem)

    def test_id_pode_ser_reutilizado_apos_remocao(self):
        cadastrar_peca("A1", 100, "azul", 15)
        remover_peca("A1")
        cadastrar_peca("A1", 100, "azul", 15)
        self.assertEqual(len(listar_pecas()), 1)


class TestListagens(BaseComEstadoLimpo):
    def test_listar_por_status(self):
        cadastrar_peca("A1", 100, "azul", 15)
        cadastrar_peca("R1", 50, "azul", 15)
        self.assertEqual([p["id"] for p in listar_pecas("aprovada")], ["A1"])
        self.assertEqual([p["id"] for p in listar_pecas("reprovada")], ["R1"])
        self.assertEqual(len(listar_pecas()), 2)


class TestJson(BaseComEstadoLimpo):
    def test_salvar_e_carregar(self):
        cadastrar_aprovadas(config.CAPACIDADE_CAIXA + 2)
        cadastrar_peca("R1", 50, "preto", 15)
        copia = {chave: valor for chave, valor in estado.items()}
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "estado.json")
            salvar_estado(caminho)
            reiniciar_estado()
            self.assertEqual(listar_pecas(), [])
            carregar_estado(caminho)
        self.assertEqual(dict(estado), copia)

    def test_arquivo_inexistente_mantem_estado(self):
        carregar_estado("nao_existe.json")
        self.assertEqual(listar_pecas(), [])

    def test_formato_invalido(self):
        conteudos = [
            "[]",
            "{invalido",
            "",
            '{"pecas": "x", "caixa_aberta": 1, "caixas_fechadas": 2}',
            '{"pecas": [{"id": "A"}], "caixa_aberta": {"numero": 1, "pecas": [], "fechada": false},'
            ' "caixas_fechadas": []}',
            '{"pecas": [], "caixa_aberta": {"numero": 1}, "caixas_fechadas": []}',
        ]
        for conteudo in conteudos:
            with self.subTest(conteudo=conteudo):
                with tempfile.TemporaryDirectory() as pasta:
                    caminho = os.path.join(pasta, "estado.json")
                    with open(caminho, "w", encoding="utf-8") as arquivo:
                        arquivo.write(conteudo)
                    with self.assertRaises(ValueError):  # JSONDecodeError também é ValueError
                        carregar_estado(caminho)
                self.assertEqual(listar_pecas(), [])  # o estado atual não foi alterado


if __name__ == "__main__":
    unittest.main()
