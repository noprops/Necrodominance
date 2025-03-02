import random
from copy import copy
from collections import defaultdict
from game_state import *
from deck_utils import get_filename_without_extension, create_deck, save_results_to_csv

class DeckAnalyzer:
    def __init__(self):
        self.game = GameState()
    
    def run_multiple_simulations(self, deck: list[str], initial_hand: list[str], iterations: int = 10000, draw_count: int = 19) -> dict:
        # デッキが60枚かどうかをチェック
        if len(deck) != 60:
            print(f"Error: Deck must contain exactly 60 cards. Current deck has {len(deck)} cards.")
            return {
                'draw_count': draw_count,
                'total_games': 0,
                'wins': 0,
                'win_rate': 0.0,
                'losses': 0,
                'loss_rate': 0.0,
                'loss_reasons': {'Invalid deck size': 1}
            }
        
        # Statistics
        wins = 0
        losses = 0
        loss_reasons = defaultdict(int)
        cast_necro_count = 0
        
        self.game.debug_print = False

        for i in range(iterations):
            self.game.reset_game()
            random.shuffle(deck)
            result = self.game.run(deck, initial_hand, draw_count)
            
            # Necroを唱えたかどうかをカウント
            if self.game.did_cast_necro:
                cast_necro_count += 1
            
            # Collect results
            if result:
                wins += 1
            else:
                losses += 1
                if self.game.loss_reason:
                    loss_reasons[self.game.loss_reason] += 1
                else:
                    loss_reasons["Unknown"] += 1
        
        # Calculate statistics
        stats = {
            'draw_count': draw_count,
            'total_games': iterations,
            'wins': wins,
            'win_rate': wins/iterations*100,
            'losses': losses,
            'loss_rate': losses/iterations*100,
            'loss_reasons': dict(loss_reasons)
        }
        
        # initial_handが空の場合のみ、追加の統計情報を含める
        if not initial_hand:
            # Necroを唱えた確率
            cast_necro_rate = cast_necro_count/iterations*100
            stats['cast_necro_count'] = cast_necro_count
            stats['cast_necro_rate'] = cast_necro_rate
            
            # Necroを唱えたあと、勝利する条件付き確率
            if cast_necro_count > 0:
                win_after_necro_rate = wins/cast_necro_count*100
                stats['win_after_necro_rate'] = win_after_necro_rate
            else:
                stats['win_after_necro_rate'] = 0.0

        # Print results
        print(f"\nTest Results ({iterations} iterations, draw_count={draw_count}):")
        print(f"Wins: {wins} ({stats['win_rate']:.1f}%)")
        print(f"Losses: {losses} ({stats['loss_rate']:.1f}%)")
        
        if not initial_hand:
            print(f"Cast Necro: {cast_necro_count} ({stats['cast_necro_rate']:.1f}%)")
            print(f"Win After Cast Necro: {stats['win_after_necro_rate']:.1f}%")
        
        print("\nLoss Reasons:")
        for reason, count in loss_reasons.items():
            if count > 0:
                percent = count/losses*100
                print(f"  {reason}: {count} ({percent:.1f}% of losses)")
        
        return stats
    
    def run_draw_count_analysis(self, deck: list[str], initial_hand: list[str], min_draw: int = 10, max_draw: int = 19, iterations: int = 10000) -> list:
        results = []
        for draw_count in range(max_draw, min_draw - 1, -1):
            print(f"\nAnalyzing draw_count = {draw_count}")
            stats = self.run_multiple_simulations(deck, initial_hand, iterations=iterations, draw_count=draw_count)
            results.append(stats)
        
        return results
    
    def compare_decks_with_varying_draw_counts(self, decks: list[list[str]], deck_names: list[str], initial_hand: list[str], min_draw: int = 10, max_draw: int = 19, iterations: int = 10000):
        """
        複数のデッキに対して、各デッキについてdraw_countを変えながら分析を行う
        
        Args:
            decks: デッキのリスト（各デッキはカード名のリスト）
            deck_names: デッキ名のリスト
            initial_hand: 初期手札
            min_draw: 最小ドロー数
            max_draw: 最大ドロー数
            iterations: 各ドロー数でのシミュレーション回数
            
        Returns:
            全デッキの全draw_countの分析結果を含むリスト。各要素は辞書で、デッキ名とdraw_countごとの統計情報を含む
        """
        all_results = []
        
        for i, deck in enumerate(decks):
            deck_name = deck_names[i]
            results = self.run_draw_count_analysis(deck, initial_hand, min_draw, max_draw, iterations)
            
            # 各結果にデッキ名を追加
            for result in results:
                result['deck_name'] = deck_name
                all_results.append(result)
            
            # 結果を表示
            print(f"\nDraw Count Analysis Results for {deck_name}:")
            for result in results:
                print(f"Draw Count: {result['draw_count']}, Win Rate: {result['win_rate']:.1f}%")
        
        return all_results
    
    def compare_decks(self, decks: list[list[str]], deck_names: list[str], initial_hand: list[str], draw_count: int = 19, iterations: int = 10000):
        """
        複数のデッキに対して、固定のdraw_countでrun_multiple_simulationsを実行する
        
        Args:
            decks: デッキのリスト（各デッキはカード名のリスト）
            deck_names: デッキ名のリスト
            initial_hand: 初期手札
            draw_count: ドロー数
            iterations: シミュレーション回数
        """
        results = []
        
        for i, deck in enumerate(decks):
            deck_name = deck_names[i]
            stats = self.run_multiple_simulations(deck, initial_hand, iterations, draw_count)
            
            # デッキ名を追加
            stats['deck_name'] = deck_name
            
            results.append(stats)
        
        # 結果を表示
        print("\nDeck Comparison Results:")
        for result in results:
            print(f"Deck: {result['deck_name']}, Win Rate: {result['win_rate']:.1f}%")
        
        return results
    
    def compare_initial_hands(self, initial_hands: list[list[str]], deck: list[str], draw_count: int = 19, iterations: int = 10000):
        """
        複数の初期手札に対して、固定のデッキでrun_multiple_simulationsを実行する
        
        Args:
            initial_hands: 初期手札のリスト（各初期手札はカード名のリスト）
            deck: デッキ（カード名のリスト）
            draw_count: ドロー数
            iterations: シミュレーション回数
            
        Returns:
            各初期手札の分析結果のリスト。各要素は辞書で、初期手札の内容と統計情報を含む
        """
        results = []
        
        for initial_hand in initial_hands:
            stats = self.run_multiple_simulations(deck, initial_hand, iterations, draw_count)
            
            # 初期手札の内容を追加
            stats['initial_hand'] = ', '.join(initial_hand)
            
            results.append(stats)
        
        # 結果を表示
        print("\nInitial Hand Comparison Results:")
        for result in results:
            print(f"Initial Hand: {result['initial_hand']}, Win Rate: {result['win_rate']:.1f}%")
        
        return results

if __name__ == "__main__":
    analyzer = DeckAnalyzer()
    '''
    deck_paths = ['decks/wind4_valakut2_cantor1.txt', 'decks/wind3_valakut3_cantor1.txt']
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]

    decks = [create_deck(path) for path in deck_paths]
    deck_names = [get_filename_without_extension(path) for path in deck_paths]
    
    results = analyzer.compare_decks_with_varying_draw_counts(decks, deck_names, initial_hand)
    save_results_to_csv('compare_decks_with_varying_draw_counts', results)
    
    initial_hands = [
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, MANAMORPHOSE],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, BORNE_UPON_WIND],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, MANAMORPHOSE, BORNE_UPON_WIND],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SIMIAN_SPIRIT_GUIDE],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, LOTUS_PETAL],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, DARK_RITUAL],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, VALAKUT_AWAKENING]
    ]

    deck = create_deck('decks/wind4_valakut2_cantor1.txt')
    results = analyzer.compare_initial_hands(initial_hands, deck)
    save_results_to_csv('compare_initial_hands', results)
    '''

    deck_paths = [
        'decks/wind4_valakut2_cantor1.txt',
        'decks/wind4_valakut2_cantor0_paradise1.txt',
        'decks/duress4_chrome2_summoner2.txt',
        'decks/duress4_chrome3_summoner3_beseech2.txt',
        'decks/duress4_chrome3_summoner3_cantor0_beseech3.txt',
        'decks/duress4_chrome3_summoner3_cantor0_valakut1.txt',
        'decks/duress4_chrome3_summoner3_cantor0_wind3.txt',
        'decks/duress4_chrome3_summoner3_wind3_beseech3.txt',
        'decks/duress4_chrome3_summoner3_wind3_valakut1.txt'    
    ]
    decks = [create_deck(path) for path in deck_paths]
    deck_names = [get_filename_without_extension(path) for path in deck_paths]
    
    results = analyzer.compare_decks(decks, deck_names, [])
    save_results_to_csv('compare_decks', results)
