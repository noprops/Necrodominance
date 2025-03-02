import unittest
from game_state import *

class TestMainPhase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create GameState instance once for all tests"""
        cls.game = GameState()
    
    def setUp(self):
        """Reset game state before each test"""
        self.game.reset_game()
    
    def test_vault_dark_necro(self):
        # Set up initial hand
        self.game.hand = [GEMSTONE_MINE, VAULT_OF_WHISPERS, DARK_RITUAL, NECRODOMINANCE]
        
        # Run main phase
        result = self.game.main_phase()
        
        # Assert result is True
        self.assertTrue(result, "main_phase should return True with Vault of Whispers, Dark Ritual, and Necrodominance")
    
    def test_vault_dark_cabal_beseech(self):
        # Set up initial hand
        self.game.hand = [GEMSTONE_MINE, VAULT_OF_WHISPERS, DARK_RITUAL, CABAL_RITUAL, BESEECH_MIRROR]
        self.game.deck = [NECRODOMINANCE]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
    
    def test_gemstone_dark_cabal_beseech_false(self):
        # Set up initial hand
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, CABAL_RITUAL, BESEECH_MIRROR]
        self.game.deck = [NECRODOMINANCE]
        
        # Assert result is True
        self.assertFalse(self.game.main_phase())
    
    def test_gemstone_dark2_cabal_summoner_beseech(self):
        # Set up initial hand
        self.game.hand = [GEMSTONE_MINE, DARK_RITUAL, DARK_RITUAL, CABAL_RITUAL, BESEECH_MIRROR, SUMMONERS_PACT]
        self.game.deck = [ELVISH_SPIRIT_GUIDE, NECRODOMINANCE]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
    
    def test_petal3_chrome_summoner_beseech(self):
        # Set up initial hand
        self.game.hand = [LOTUS_PETAL, LOTUS_PETAL, LOTUS_PETAL, CHROME_MOX, SUMMONERS_PACT, BESEECH_MIRROR]
        self.game.deck = [ELVISH_SPIRIT_GUIDE, NECRODOMINANCE]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
    
    def test_vault_summoner_cabal_necro(self):
        # Set up initial hand
        self.game.hand = [VAULT_OF_WHISPERS, SUMMONERS_PACT, CABAL_RITUAL, NECRODOMINANCE]
        self.game.deck = [ELVISH_SPIRIT_GUIDE]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
    
    def test_summoner2_dark_necro(self):
        # Set up initial hand
        self.game.hand = [SUMMONERS_PACT, SUMMONERS_PACT, DARK_RITUAL, NECRODOMINANCE]
        self.game.deck = [ELVISH_SPIRIT_GUIDE, WILD_CANTOR]
        
        # Assert result is True
        self.assertTrue(self.game.main_phase())
    
    def test_summoner2_mana_cabal_necro(self):
        # Set up initial hand
        self.game.hand = [SUMMONERS_PACT, SUMMONERS_PACT, MANAMORPHOSE, CABAL_RITUAL, NECRODOMINANCE]
        self.game.deck = [DURESS, ELVISH_SPIRIT_GUIDE, ELVISH_SPIRIT_GUIDE]
        
        self.assertTrue(self.game.main_phase())
    
    def test_summoner2_mana_cabal_necro_false(self):
        # Set up initial hand
        self.game.hand = [SUMMONERS_PACT, SUMMONERS_PACT, MANAMORPHOSE, CABAL_RITUAL, NECRODOMINANCE]
        self.game.deck = [DURESS, ELVISH_SPIRIT_GUIDE, WILD_CANTOR]
        
        self.assertFalse(self.game.main_phase())
    
    def test_no_necro_beseech_false(self):
        # Set up initial hand
        self.game.hand = [ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, MANAMORPHOSE, DARK_RITUAL, DARK_RITUAL, CABAL_RITUAL]
        self.game.deck = [DURESS]
        
        self.assertFalse(self.game.main_phase())
    
if __name__ == '__main__':
    unittest.main()
