import unittest
from game_state import *

class TestGameState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create GameState instance once for all tests"""
        cls.game = GameState()

    def setUp(self):
        """Reset game state before each test"""
        self.game.reset_game()
    
    def test_try_generate_mana_GBBB(self):
        self.game.battlefield = [CHROME_MOX]
        self.game.hand = [ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, CABAL_RITUAL]

        self.assertTrue(self.game.try_generate_mana('GBBB'))
        
        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_UBBBB(self):
        self.game.battlefield = [CHROME_MOX, WILD_CANTOR]
        self.game.hand = [DARK_RITUAL, DARK_RITUAL]

        self.assertTrue(self.game.try_generate_mana('UBBBB'))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 1)
        self.assertEqual(self.game.mana_pool.B, 5)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_WUBR_after_wind(self):
        self.game.battlefield = []
        self.game.hand = [LOTUS_PETAL, WILD_CANTOR, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, CHROME_MOX, DARK_RITUAL]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('WUBR'))

        self.assertEqual(self.game.mana_pool.W, 1)
        self.assertEqual(self.game.mana_pool.U, 1)
        self.assertEqual(self.game.mana_pool.B, 1)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_WUBG_after_wind(self):
        self.game.battlefield = []
        self.game.hand = [LOTUS_PETAL, WILD_CANTOR, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, CHROME_MOX, DARK_RITUAL]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('WUBG'))

        self.assertEqual(self.game.mana_pool.W, 1)
        self.assertEqual(self.game.mana_pool.U, 1)
        self.assertEqual(self.game.mana_pool.B, 1)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_BBBBBG_after_wind(self):
        ##print('test_try_generate_mana_BBBBBG_after_wind')
        self.game.battlefield = []
        self.game.hand = [WILD_CANTOR, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, DARK_RITUAL, DARK_RITUAL, CHROME_MOX, CHROME_MOX]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('BBBBBG'))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 5)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_BBBBBG(self):
        self.game.battlefield = []
        self.game.hand = [WILD_CANTOR, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, DARK_RITUAL, DARK_RITUAL, CHROME_MOX, CHROME_MOX]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = False
        self.assertFalse(self.game.try_generate_mana('BBBBBG'))
    
    def test_try_generate_mana_BBBRG_after_wind(self):
        self.game.battlefield = []
        self.game.hand = [WILD_CANTOR, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, DARK_RITUAL, DARK_RITUAL, CHROME_MOX]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('BBBRG'))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_WBBBB_after_wind(self):
        self.game.battlefield = []
        self.game.hand = [WILD_CANTOR, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, CABAL_RITUAL, CABAL_RITUAL, CABAL_RITUAL, CHROME_MOX]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('WBBBB'))

        self.assertEqual(self.game.mana_pool.W, 1)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 4)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_2R_after_wind(self):
        self.game.battlefield = []
        self.game.hand = [LOTUS_PETAL, LOTUS_PETAL, LOTUS_PETAL]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('2R'))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 2)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 0)

if __name__ == '__main__':
    unittest.main()
