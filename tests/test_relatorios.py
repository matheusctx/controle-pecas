import unittest

import config
from armazenamento import cadastrar_peca, listar_pecas, reiniciar_estado
from relatorios import contar_motivos


class TestContarMotivos(unittest.TestCase):
    def test_agrupa_por_tipo_ignorando_o_valor(self):
        reiniciar_estado()
        cadastrar_peca("A", 110, "azul", 15)
        cadastrar_peca("B", 50, "preto", 15)
        cadastrar_peca("C", 100, "vermelho", 5)
        self.assertEqual(contar_motivos(listar_pecas()), {
            config.MOTIVO_PESO: 2,
            config.MOTIVO_COR: 2,
            config.MOTIVO_COMPRIMENTO: 1,
        })


if __name__ == "__main__":
    unittest.main()
