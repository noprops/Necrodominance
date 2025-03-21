import unittest
import sys
import os

# Add parent directory to path to import modules from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_state import *

class TestRunGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create GameState instance once for all tests"""
        cls.game = GameState()
        cls.game.shuffle_enabled = False
    
    def setUp(self):
        """Reset game state before each test"""
        self.game.reset_game()
    
    def _run_deck_test(self, filename: str, initial_hand: list[str], draw_count: int, expect_win: bool) -> None:
        """Run test with specified deck file and expected result
        
        Args:
            filename (str): Base filename without path or extension
            initial_hand (list[str]): Initial hand cards
            draw_count (int): Number of cards to draw
            expect_win (bool): True if deck should win, False if should lose
        """
        # Construct full deck file path
        deck_file = os.path.join('decks', f"{filename}.txt")
        
        # Load deck from file
        deck = []
        with open(deck_file, 'r') as file:
            for line in file:
                # Skip empty lines
                if line.strip() == "":
                    continue
                # Add card to deck
                deck.append(line.strip())
        
        # Verify deck is 60 cards
        self.assertEqual(len(deck), 60, f"Deck is not 60 cards ({len(deck)} cards)")
        
        result = self.game.run_with_initial_hand(
            deck=deck, 
            initial_hand=initial_hand, 
            bottom_list=[], 
            draw_count=draw_count, 
            cast_summoners_pact=True
        )
        
        # Assert game result
        if expect_win:
            self.assertTrue(result, f"Game should have won with {deck_file}")
        else:
            self.assertFalse(result, f"Game should have lost with {deck_file}")
    
    def _run_deck_test_with_gemstone_dark_necro(self, filename: str, draw_count: int, expect_win: bool) -> None:
        """Run test with standard initial hand (Gemstone Mine, Dark Ritual, Necrodominance)
        
        Args:
            filename (str): Base filename without path or extension
            draw_count (int): Number of cards to draw
            expect_win (bool): True if deck should win, False if should lose
        """
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
        self._run_deck_test(filename, initial_hand, draw_count, expect_win)
    
    def test_valakut_no_floating_win(self):
        self._run_deck_test_with_gemstone_dark_necro('Valakut_No_Floating_Win', 19, expect_win=True)
    
    def test_valakut_no_floating_lose(self):
        self._run_deck_test_with_gemstone_dark_necro('Valakut_No_Floating_Lose', 19, expect_win=False)
    
    def test_manamorphose_wind_win(self):
        self._run_deck_test_with_gemstone_dark_necro('Manamorphose_Wind_Win', 19, expect_win=True)
    
    def test_manamorphose_wind_lose(self):
        self._run_deck_test_with_gemstone_dark_necro('Manamorphose_Wind_Lose', 19, expect_win=False)
    
    def test_wind_valakut_win(self):
        self._run_deck_test_with_gemstone_dark_necro('Wind_Valakut_Win', 19, expect_win=True)
    
    def test_wind_valakut_lose(self):
        self._run_deck_test_with_gemstone_dark_necro('Wind_Valakut_Lose', 19, expect_win=False)
    
    def test_wind_valakut_cantor_win(self):
        self._run_deck_test_with_gemstone_dark_necro('Wind_Valakut_Cantor_Win', 19, expect_win=True)
    
    def test_petal_wind_win(self):
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL]
        self._run_deck_test('Petal_Wind_Win', initial_hand, 19, expect_win=True)
    
    def test_chrome_wind_win(self):
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, NECRODOMINANCE, CHROME_MOX]
        self._run_deck_test('Chrome_Wind_Win', initial_hand, 19, expect_win=True)
    
    def test_cantor_wind_win(self):
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, WILD_CANTOR]
        self._run_deck_test('Cantor_Wind_Win', initial_hand, 19, expect_win=True)
    
    def test_chrome_imprint_wind_lose(self):
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CHROME_MOX, BORNE_UPON_WIND]
        self._run_deck_test('Chrome_Imprint_Wind_Lose', initial_hand, 19, expect_win=False)
    
    def test_chrome_imprint_wind_win(self):
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CHROME_MOX, BORNE_UPON_WIND, BORNE_UPON_WIND]
        self._run_deck_test('Chrome_Imprint_Wind_Win', initial_hand, 19, expect_win=True)
    
if __name__ == '__main__':
    unittest.main()
