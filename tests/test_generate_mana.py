import unittest
import sys
import os

# Add parent directory to path to import modules from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_state import *

class TestGenerateMana(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create GameState instance once for all tests"""
        cls.game = GameState()

    def setUp(self):
        """Reset game state before each test"""
        self.game.reset_game()
    
    def test_try_generate_mana_GR(self):
        self.game.battlefield = []
        self.game.hand = [ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE]

        self.assertTrue(self.game.try_generate_mana('GR', []))
        
        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 0)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_GR_summoner_pact(self):
        self.game.battlefield = []
        self.game.hand = [SUMMONERS_PACT, SIMIAN_SPIRIT_GUIDE]
        self.game.deck = [ELVISH_SPIRIT_GUIDE]

        self.assertTrue(self.game.try_generate_mana('GR', []))
        
        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 0)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_BGR(self):
        self.game.battlefield = []
        self.game.hand = [SUMMONERS_PACT, SIMIAN_SPIRIT_GUIDE, CHROME_MOX, DURESS]
        self.game.deck = [ELVISH_SPIRIT_GUIDE]
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('BGR', []))
        
        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 1)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_BBBGR(self):
        self.game.battlefield = []
        self.game.hand = [SUMMONERS_PACT, SIMIAN_SPIRIT_GUIDE, CHROME_MOX, DURESS, DARK_RITUAL]
        self.game.deck = [ELVISH_SPIRIT_GUIDE]
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('BBBGR', []))
        
        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_GBBB(self):
        self.game.mana_source.B = 1
        self.game.battlefield = [CHROME_MOX]
        self.game.hand = [ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, CABAL_RITUAL]

        self.assertTrue(self.game.try_generate_mana('GBBB', []))
        
        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_UBBBB(self):
        self.game.mana_source.B = 1
        self.game.add_any_mana_source(WILD_CANTOR)
        self.game.battlefield = [CHROME_MOX, WILD_CANTOR]
        self.game.hand = [DARK_RITUAL, DARK_RITUAL]

        self.assertTrue(self.game.try_generate_mana('UBBBB', []))

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

        self.assertTrue(self.game.try_generate_mana('WUBR', []))

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

        self.assertTrue(self.game.try_generate_mana('WUBG', []))

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

        self.assertTrue(self.game.try_generate_mana('BBBBBG', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 5)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_UBBBG_after_wind(self):
        self.game.battlefield = []
        self.game.hand = [WILD_CANTOR, ELVISH_SPIRIT_GUIDE, ELVISH_SPIRIT_GUIDE, DARK_RITUAL, CHROME_MOX, DURESS]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('UBBBG', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 1)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_BBBBBG(self):
        self.game.battlefield = []
        self.game.hand = [WILD_CANTOR, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, DARK_RITUAL, DARK_RITUAL, CHROME_MOX, CHROME_MOX]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = False
        self.assertFalse(self.game.try_generate_mana('BBBBBG', []))
    
    def test_try_generate_mana_BBBRG_after_wind(self):
        self.game.battlefield = []
        self.game.hand = [WILD_CANTOR, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, DARK_RITUAL, DARK_RITUAL, CHROME_MOX]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('BBBRG', []))

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

        self.assertTrue(self.game.try_generate_mana('WBBBB', []))

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

        self.assertTrue(self.game.try_generate_mana('2R', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 2)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_UBRG_4chrome(self):
        self.game.battlefield = []
        self.game.hand = [CHROME_MOX, CHROME_MOX, CHROME_MOX, CHROME_MOX, BORNE_UPON_WIND, MANAMORPHOSE, MANAMORPHOSE, SUMMONERS_PACT, CABAL_RITUAL]
        self.game.did_cast_wind = True
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('UBRG', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 1)
        self.assertEqual(self.game.mana_pool.B, 1)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_UBBB_in_main_phase(self):
        self.game.battlefield = []
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CHROME_MOX, BORNE_UPON_WIND, BORNE_UPON_WIND, NECRODOMINANCE]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = True
        self.game.set_land(GEMSTONE_MINE)

        self.assertTrue(self.game.try_generate_mana('UBBB', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 1)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_W_in_main_phase(self):
        self.game.battlefield = []
        self.game.hand = [DARK_RITUAL, CHROME_MOX, BORNE_UPON_WIND, CHANCELLOR_OF_ANNEX]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('W', []))

        self.assertEqual(self.game.mana_pool.W, 1)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 0)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_BBB_with_petal_dark(self):
        self.game.battlefield = []
        self.game.hand = [LOTUS_PETAL, DARK_RITUAL]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('BBB', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_BBB_with_petal_elvish_cabal(self):
        self.game.battlefield = []
        self.game.hand = [LOTUS_PETAL, ELVISH_SPIRIT_GUIDE, CABAL_RITUAL]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('BBB', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_GBBB_with_petal2_elvish_cabal(self):
        self.game.battlefield = []
        self.game.hand = [LOTUS_PETAL, LOTUS_PETAL, ELVISH_SPIRIT_GUIDE, CABAL_RITUAL]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('GBBB', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 1)
    
    def test_try_generate_mana_UR3_with_petal4_cabal(self):
        self.game.battlefield = []
        self.game.hand = [LOTUS_PETAL, LOTUS_PETAL, LOTUS_PETAL, LOTUS_PETAL, CABAL_RITUAL]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = True

        self.assertTrue(self.game.try_generate_mana('UR3', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 1)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 1)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_BBB_with_land_chrome_cabal(self):
        self.game.battlefield = []
        self.game.hand = [VAULT_OF_WHISPERS, CHROME_MOX, PACT_OF_NEGATION, CABAL_RITUAL]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = True
        self.game.set_land(VAULT_OF_WHISPERS)
        self.game.cast_chrome_mox(PACT_OF_NEGATION)

        self.assertTrue(self.game.try_generate_mana('BBB', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 0)
    
    def test_try_generate_mana_BBB_with_land_chrome_cabal2(self):
        self.game.battlefield = []
        self.game.hand = [VAULT_OF_WHISPERS, CHROME_MOX, CABAL_RITUAL, CABAL_RITUAL]
        self.game.did_cast_wind = False
        self.game.can_cast_sorcery = True
        self.game.set_land(VAULT_OF_WHISPERS)
        self.game.cast_chrome_mox(CABAL_RITUAL)

        self.assertTrue(self.game.try_generate_mana('BBB', []))

        self.assertEqual(self.game.mana_pool.W, 0)
        self.assertEqual(self.game.mana_pool.U, 0)
        self.assertEqual(self.game.mana_pool.B, 3)
        self.assertEqual(self.game.mana_pool.R, 0)
        self.assertEqual(self.game.mana_pool.G, 0)

if __name__ == '__main__':
    unittest.main()
