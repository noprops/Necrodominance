import unittest
import sys
import os

# Add parent directory to path to import modules from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_state import *

class TestMainPhase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create GameState instance once for all tests"""
        cls.game = GameState()
    
    def setUp(self):
        """Reset game state before each test"""
        self.game.reset_game()
    
    def test_vault_dark_necro_mull4(self):
        self.game.mulligan_count = 4
        self.game.hand = [VAULT_OF_WHISPERS, DARK_RITUAL, NECRODOMINANCE]
        
        # Run main phase
        result = self.game.main_phase()
        
        # Assert result is True
        self.assertTrue(result)
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_vault_dark_necro_mull5_false(self):
        self.game.mulligan_count = 5
        self.game.hand = [VAULT_OF_WHISPERS, DARK_RITUAL, NECRODOMINANCE]
        
        # Run main phase
        result = self.game.main_phase()

        self.assertFalse(result)
    
    def test_vault_dark_cabal_beseech(self):
        # Set up initial hand
        self.game.hand = [GEMSTONE_MINE, VAULT_OF_WHISPERS, DARK_RITUAL, CABAL_RITUAL, BESEECH_MIRROR]
        self.game.deck = [NECRODOMINANCE]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_gemstone_dark_cabal_beseech_false(self):
        # Set up initial hand
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CABAL_RITUAL, BESEECH_MIRROR]
        self.game.deck = [NECRODOMINANCE]
        
        # Assert result is True
        self.assertFalse(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_gemstone_dark2_cabal_summoner_beseech(self):
        # Set up initial hand
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, DARK_RITUAL, CABAL_RITUAL, BESEECH_MIRROR, SUMMONERS_PACT]
        self.game.deck = [ELVISH_SPIRIT_GUIDE, NECRODOMINANCE]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_petal3_chrome_summoner_beseech(self):
        # Set up initial hand
        self.game.hand = [LOTUS_PETAL, LOTUS_PETAL, LOTUS_PETAL, CHROME_MOX, SUMMONERS_PACT, BESEECH_MIRROR]
        self.game.deck = [ELVISH_SPIRIT_GUIDE, NECRODOMINANCE]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_vault_summoner_cabal_necro(self):
        # Set up initial hand
        self.game.hand = [VAULT_OF_WHISPERS, SUMMONERS_PACT, CABAL_RITUAL, NECRODOMINANCE]
        self.game.deck = [ELVISH_SPIRIT_GUIDE]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_summoner2_dark_necro(self):
        # Set up initial hand
        self.game.hand = [SUMMONERS_PACT, SUMMONERS_PACT, DARK_RITUAL, NECRODOMINANCE]
        self.game.deck = [ELVISH_SPIRIT_GUIDE, WILD_CANTOR]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_summoner2_mana_cabal_necro(self):
        # Set up initial hand
        self.game.hand = [SUMMONERS_PACT, SUMMONERS_PACT, MANAMORPHOSE, CABAL_RITUAL, NECRODOMINANCE]
        self.game.deck = [DURESS, ELVISH_SPIRIT_GUIDE, ELVISH_SPIRIT_GUIDE]
        
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_summoner2_mana_cabal_necro_false(self):
        # Set up initial hand
        self.game.hand = [SUMMONERS_PACT, SUMMONERS_PACT, MANAMORPHOSE, CABAL_RITUAL, NECRODOMINANCE]
        self.game.deck = [DURESS, ELVISH_SPIRIT_GUIDE, WILD_CANTOR]
        
        self.assertFalse(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_no_necro_beseech_false(self):
        # Set up initial hand
        self.game.hand = [ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, MANAMORPHOSE, DARK_RITUAL, DARK_RITUAL, CABAL_RITUAL]
        self.game.deck = [DURESS]
        
        self.assertFalse(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_beseech_mana_short_false(self):
        self.game.hand = [ELVISH_SPIRIT_GUIDE, VAULT_OF_WHISPERS, CABAL_RITUAL, BESEECH_MIRROR]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertFalse(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_beseech_no_bargain_false(self):
        self.game.hand = [GEMSTONE_MINE, ELVISH_SPIRIT_GUIDE, ELVISH_SPIRIT_GUIDE, CABAL_RITUAL, BESEECH_MIRROR]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertFalse(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_beseech_chrome_no_imprint_true(self):
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CABAL_RITUAL, BESEECH_MIRROR, CHROME_MOX]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_beseech_bargain_petal_true(self):
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CABAL_RITUAL, BESEECH_MIRROR, LOTUS_PETAL]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertTrue(self.game.main_phase())
        print(self.game.mana_pool)
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_beseech_imprint_manamorphose_true(self):
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CHROME_MOX, MANAMORPHOSE, BESEECH_MIRROR]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_beseech_imprint_valakut_true(self):
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CHROME_MOX, VALAKUT_AWAKENING, BESEECH_MIRROR]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_beseech_imprint_wind_true(self):
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CHROME_MOX, BORNE_UPON_WIND, BESEECH_MIRROR]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.get_total(), 0)
    
    def test_necro_UBBB_gemstone_true(self):
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CHROME_MOX, BORNE_UPON_WIND, BESEECH_MIRROR, NECRODOMINANCE]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.U, 1)
    
    def test_necro_BBB_no_chrome_true(self):
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CHROME_MOX, BORNE_UPON_WIND, NECRODOMINANCE]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.U, 0)
    
    def test_necro_UBBB_chrome_true(self):
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CHROME_MOX, BORNE_UPON_WIND, BORNE_UPON_WIND, NECRODOMINANCE]
        self.game.deck = [DURESS, NECRODOMINANCE]
        
        self.assertTrue(self.game.main_phase())
        self.assertEqual(self.game.mana_pool.get_total(), 0)
        self.assertEqual(self.game.mana_source.U, 1)

if __name__ == '__main__':
    unittest.main()
