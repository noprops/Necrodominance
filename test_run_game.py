import unittest
from game_state import *

class TestRunSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create GameState instance once for all tests"""
        cls.game = GameState()
    
    def setUp(self):
        """Reset game state before each test"""
        self.game.reset_game()
    
    def _run_deck_test(self, deck_file: str, initial_hand: list[str], draw_count: int, expect_win: bool) -> None:
        """Run test with specified deck file and expected result
        
        Args:
            deck_file (str): Path to deck file
            expect_win (bool): True if deck should win, False if should lose
        """
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

        result =  self.game.run(deck, initial_hand, draw_count) 
        
        # Assert game result
        if expect_win:
            self.assertTrue(result, f"Game should have won with {deck_file}")
        else:
            self.assertFalse(result, f"Game should have lost with {deck_file}")
    
    def _run_deck_test_with_gemstone_dark_necro(self, deck_file: str, draw_count: int, expect_win: bool) -> None:
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
        self._run_deck_test(deck_file, initial_hand, draw_count, expect_win)
    
    def test_valakut_no_floating_win(self):
        self._run_deck_test_with_gemstone_dark_necro('test_decks/Valakut_No_Floating_Win.txt', 19, expect_win=True)
    
    def test_valakut_no_floating_lose(self):
        self._run_deck_test_with_gemstone_dark_necro('test_decks/Valakut_No_Floating_Lose.txt', 19, expect_win=False)
    
    def test_manamorphose_wind_win(self):
        self._run_deck_test_with_gemstone_dark_necro('test_decks/Manamorphose_Wind_Win.txt', 19, expect_win=True)
    
    def test_manamorphose_wind_lose(self):
        self._run_deck_test_with_gemstone_dark_necro('test_decks/Manamorphose_Wind_Lose.txt', 19, expect_win=False)
    
    def test_wind_valakut_win(self):
        self._run_deck_test_with_gemstone_dark_necro('test_decks/Wind_Valakut_Win.txt', 19, expect_win=True)
    
    def test_wind_valakut_lose(self):
        self._run_deck_test_with_gemstone_dark_necro('test_decks/Wind_Valakut_Lose.txt', 19, expect_win=False)
    
    def test_wind_valakut_cantor_win(self):
        #print('test_wind_valakut_cantor_win')
        self._run_deck_test_with_gemstone_dark_necro('test_decks/Wind_Valakut_Cantor_Win.txt', 19, expect_win=True)
    
if __name__ == '__main__':
    unittest.main()
