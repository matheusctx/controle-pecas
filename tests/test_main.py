import contextlib
import io
import unittest
from unittest.mock import patch

import config
from armazenamento import listar_caixas_fechadas, listar_pecas, obter_caixa_aberta, reiniciar_estado
from main import carregar_demo, main


def executar(entradas):
    """Roda main(--demo) com as entradas simuladas e devolve tudo o que foi impresso."""
    saida = io.StringIO()
    with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida):
        main(["--demo"])
    return saida.getvalue()


class TestDemo(unittest.TestCase):
    def setUp(self):
        reiniciar_estado()

    def test_demo_tem_25_pecas_variadas(self):
        carregar_demo()
        self.assertEqual(len(listar_pecas()), 25)
        self.assertEqual(len(listar_pecas(config.STATUS_APROVADA)), 14)
        self.assertEqual(len(listar_pecas(config.STATUS_REPROVADA)), 11)
        self.assertEqual(len(listar_caixas_fechadas()), 1)
        self.assertEqual(len(obter_caixa_aberta()["pecas"]), 4)


class TestMenu(unittest.TestCase):
    def test_opcao_invalida_nao_quebra(self):
        saida = executar(["9", "", "abc", "-1", "0"])
        self.assertEqual(saida.count("Opção inválida"), 4)
        self.assertIn("Até logo", saida)

    def test_ctrl_c_sai_limpo(self):
        saida = executar([KeyboardInterrupt()])
        self.assertIn("interrompido", saida)

    def test_ctrl_c_no_meio_de_um_cadastro(self):
        saida = executar(["1", "X1", KeyboardInterrupt()])
        self.assertIn("interrompido", saida)

    def test_listar_aprovadas_em_tabela(self):
        saida = executar(["2", "x", "1", "0"])
        self.assertIn("Erro: escolha 1, 2 ou 3.", saida)
        self.assertIn("14 peça(s)", saida)
        self.assertIn("caixa 1", saida)

    def test_listar_reprovadas_mostra_motivos(self):
        saida = executar(["2", "2", "0"])
        self.assertIn("11 peça(s)", saida)
        self.assertIn("Peso fora do intervalo (95–105g): 110.0g", saida)

    def test_tabela_alinhada(self):
        saida = executar(["2", "3", "0"])
        linhas = [linha for linha in saida.splitlines() if linha.startswith("P0") or linha.startswith("ID ")]
        self.assertEqual(len(linhas), 26)
        posicoes = {tuple(i for i, letra in enumerate(linha) if letra == "|") for linha in linhas}
        self.assertEqual(len(posicoes), 1)

    def test_cadastro_mostra_resultado_e_aviso_de_caixa(self):
        # caixa 2 tem 4 peças; 6 aprovadas novas a fecham
        entradas = []
        for i in range(6):
            entradas += ["1", f"N{i}", "100", "azul", "15"]
        saida = executar(entradas + ["0"])
        self.assertIn("APROVADA → caixa 2", saida)
        self.assertIn("Caixa 2 fechada", saida)

    def test_cadastro_reprovada_mostra_motivos(self):
        saida = executar(["1", "N1", "50", "preto", "15", "0"])
        self.assertIn("REPROVADA", saida)
        self.assertIn("Cor inválida", saida)

    def test_cadastro_repete_entradas_invalidas(self):
        saida = executar(["1", "P001", "", "N1", "abc", "", "100", "azul", "x", "15", "0"])
        self.assertIn("já existe uma peça com o ID 'P001'", saida)
        self.assertIn("digite um número válido", saida)
        self.assertIn("APROVADA", saida)

    def test_remover_em_caixa_fechada_e_recusada(self):
        saida = executar(["3", "P003", "0"])
        self.assertIn("já foi fechada", saida)

    def test_remover_em_caixa_aberta_com_confirmacao(self):
        executar(["3", "P012", "s", "0"])
        self.assertIsNone(next((p for p in listar_pecas() if p["id"] == "P012"), None))

    def test_remover_cancelado(self):
        executar(["3", "P012", "n", "0"])
        self.assertEqual(len(listar_pecas()), 25)

    def test_caixas_fechadas_e_relatorio(self):
        saida = executar(["4", "5", "0"])
        self.assertIn("Caixas fechadas (1)", saida)
        self.assertIn("RELATÓRIO FINAL", saida)
        self.assertIn("Taxa de aprovação: 56.0%", saida)


class TestCasosExtremos(unittest.TestCase):
    """Situações que poderiam quebrar o programa: lista vazia, ID inexistente, falha ao gravar."""

    def setUp(self):
        reiniciar_estado()

    def executar_sem_demo(self, entradas):
        """Roda o menu sem --demo, mas com o arquivo JSON simulado (nada é lido nem gravado)."""
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida), \
                patch("main.carregar_estado"), patch("main.salvar_estado") as salvar:
            main([])
        return saida.getvalue(), salvar

    def test_tudo_vazio_nao_quebra(self):
        saida, _ = self.executar_sem_demo(["2", "1", "2", "2", "2", "3", "4", "5", "0"])
        self.assertEqual(saida.count("Nenhuma peça para mostrar."), 3)
        self.assertIn("Nenhuma caixa fechada ainda.", saida)
        self.assertIn("Total de peças: 0", saida)
        self.assertNotIn("Taxa de aprovação", saida)  # evita divisão por zero

    def test_remover_id_inexistente(self):
        saida, salvar = self.executar_sem_demo(["3", "ZZ", "0"])
        self.assertIn("Não existe peça com o ID 'ZZ'.", saida)
        salvar.assert_not_called()

    def test_cadastro_e_remocao_salvam_no_arquivo(self):
        _, salvar = self.executar_sem_demo(["1", "A1", "100", "azul", "15", "3", "A1", "s", "0"])
        self.assertEqual(salvar.call_count, 2)

    def test_falha_ao_gravar_nao_quebra(self):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=["1", "A1", "100", "azul", "15", "0"]), \
                contextlib.redirect_stdout(saida), patch("main.carregar_estado"), \
                patch("main.salvar_estado", side_effect=PermissionError("sem permissão")):
            main([])
        self.assertIn("AVISO: não foi possível gravar", saida.getvalue())
        self.assertIn("APROVADA", saida.getvalue())
        self.assertEqual(len(listar_pecas()), 1)

    def test_arquivo_corrompido_avisa_e_encerra(self):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=AssertionError("o menu não deveria abrir")), \
                contextlib.redirect_stdout(saida), \
                patch("main.carregar_estado", side_effect=ValueError("formato de arquivo não reconhecido")):
            main([])
        self.assertIn("Não foi possível ler", saida.getvalue())

    def test_entradas_numericas_estranhas(self):
        entradas = ["1", "E1", "1e400", "nan", "inf", "-0", "0", " 99,5 ", "azul", "1e1", "0"]
        saida = executar(entradas)
        self.assertEqual(saida.count("maior que zero"), 5)
        self.assertIn("APROVADA", saida)


if __name__ == "__main__":
    unittest.main()
