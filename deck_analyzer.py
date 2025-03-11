import random
from copy import copy
from collections import defaultdict
from game_state import *
from deck_utils import get_filename_without_extension, create_deck, save_results_to_csv

DECK_PATHS = [
    'decks/wind4_valakut2_cantor1_paradise0.txt',
    'decks/wind4_valakut2_cantor0_paradise1.txt',
    'decks/wind3_valakut3_cantor1_paradise0.txt',
    'decks/wind3_valakut3_cantor0_paradise1.txt'
]

# フィールドの優先順位リスト（基本とマリガン回数ごとの統計情報を含む）
DEFAULT_PRIORITY_FIELDS = [
    'deck_name', 'initial_hand', 'draw_count', 'total_games', 'win_rate', 'cast_necro_rate', 'win_after_necro_rate',
    'total_wins', 'total_losses', 'failed_necro_count', 'total_cast_necro', 'loss_reasons',
    # wins_mull0, wins_mull1, ...
    'wins_mull0', 'wins_mull1', 'wins_mull2', 'wins_mull3', 'wins_mull4',
    # losses_mull0, losses_mull1, ...
    'losses_mull0', 'losses_mull1', 'losses_mull2', 'losses_mull3', 'losses_mull4',
    # cast_necro_mull0, cast_necro_mull1, ...
    'cast_necro_mull0', 'cast_necro_mull1', 'cast_necro_mull2', 'cast_necro_mull3', 'cast_necro_mull4',
    # win_rate_mull0, win_rate_mull1, ...
    'win_rate_mull0', 'win_rate_mull1', 'win_rate_mull2', 'win_rate_mull3', 'win_rate_mull4'
]

class DeckAnalyzer:
    def __init__(self):
        self.game = GameState()
    
    def run_multiple_simulations_without_mulligan(self, deck: list[str], initial_hand: list[str], draw_count: int, iterations: int = 10000) -> dict:
        """
        マリガンなしでシミュレーションを実行する関数
        
        Args:
            deck: デッキ（カード名のリスト）
            initial_hand: 初期手札
            draw_count: ドロー数
            iterations: シミュレーション回数
            
        Returns:
            シミュレーション結果の統計情報を含む辞書（シンプル版）
        """
        # 基本関数を呼び出し
        full_stats = self.run_multiple_simulations(deck, initial_hand, draw_count, False, iterations)
        
        # シンプルな統計情報を作成
        stats = {
            'draw_count': full_stats['draw_count'],
            'total_games': full_stats['total_games'],
            'wins': full_stats['total_wins'],
            'win_rate': full_stats['win_rate'],
            'losses': full_stats['total_losses'],
            'cast_necro_count': full_stats['total_cast_necro'],
            'failed_necro_count': full_stats['failed_necro_count'],
            'cast_necro_rate': full_stats['cast_necro_rate'],
            'win_after_necro_rate': full_stats['win_after_necro_rate'],
            'loss_reasons': full_stats['loss_reasons']
        }
        
        return stats
    
    def run_multiple_simulations(self, deck: list[str], initial_hand: list[str], draw_count: int, mulligan_until_necro: bool, iterations: int = 10000) -> dict:
        # Statistics
        # Necroを唱えて勝った回数
        wins = defaultdict(int)
        # Necroを唱えて負けた回数
        losses = defaultdict(int)
        # Necroを唱えた回数
        cast_necro_count = defaultdict(int)
        # Necroを唱えられず負けた回数
        failed_necro_count = 0
        # 負けた理由
        loss_reasons = defaultdict(int)
        
        self.game.debug_print = False

        for i in range(iterations):
            self.game.reset_game()
            random.shuffle(deck)
            result = self.game.run(deck, initial_hand, draw_count, mulligan_until_necro)
            mulligan_count = self.game.mulligan_count
            
            # Necroを唱えたかどうかをカウント
            if self.game.did_cast_necro:
                cast_necro_count[mulligan_count] += 1
            
            # Collect results
            if result:
                wins[mulligan_count] += 1
            else:
                if self.game.loss_reason == FALIED_NECRO:
                    # Necroを唱えられず負けた
                    failed_necro_count += 1
                else:
                    # Necroを唱えてから負けた
                    losses[mulligan_count] += 1
                
                # 負けた理由を記録
                if self.game.loss_reason:
                    loss_reasons[self.game.loss_reason] += 1
                else:
                    loss_reasons["Unknown"] += 1
        
        # Calculate statistics
        total_wins = sum(wins.values())
        total_losses = sum(losses.values())
        total_cast_necro = sum(cast_necro_count.values())
        
        # 基本的な統計情報
        stats = {
            'draw_count': draw_count,
            'total_games': iterations,
            'total_wins': total_wins,
            'win_rate': total_wins/iterations*100,
            'total_losses': total_losses,
            'failed_necro_count': failed_necro_count,
            'total_cast_necro': total_cast_necro,
            'cast_necro_rate': total_cast_necro/iterations*100,
            'loss_reasons': dict(loss_reasons)
        }
        
        # マリガン回数ごとの統計情報を展開して追加
        for m in range(5):
            stats[f'wins_mull{m}'] = wins[m]
            stats[f'losses_mull{m}'] = losses[m]
            stats[f'cast_necro_mull{m}'] = cast_necro_count[m]
            if cast_necro_count[m] > 0:
                stats[f'win_rate_mull{m}'] = wins[m]/cast_necro_count[m]*100
            else:
                stats[f'win_rate_mull{m}'] = 0.0
        
        # Necroを唱えたあと、勝利する条件付き確率
        if total_cast_necro > 0:
            stats['win_after_necro_rate'] = total_wins/total_cast_necro*100
        else:
            stats['win_after_necro_rate'] = 0.0

        # Print results
        print(f"\nTest Results ({iterations} iterations, draw_count={draw_count}):")
        print(f"Total Wins: {total_wins} ({stats['win_rate']:.1f}%)")
        print(f"Total Losses: {total_losses} ({total_losses/iterations*100:.1f}%)")
        print(f"Failed to Cast Necro: {failed_necro_count} ({failed_necro_count/iterations*100:.1f}%)")
        print(f"Cast Necro: {total_cast_necro} ({stats['cast_necro_rate']:.1f}%)")
        print(f"Win After Cast Necro: {stats['win_after_necro_rate']:.1f}%")
        
        # マリガン回数ごとの統計を表示
        if mulligan_until_necro:
            print("\nMulligan Statistics:")
            for m in range(5):
                if cast_necro_count[m] > 0:
                    win_rate = wins[m]/cast_necro_count[m]*100
                    print(f"  Mulligan {m}:")
                    print(f"    Cast Necro: {cast_necro_count[m]} ({cast_necro_count[m]/iterations*100:.1f}%)")
                    print(f"    Wins: {wins[m]} ({win_rate:.1f}%)")
                    print(f"    Losses: {losses[m]} ({losses[m]/cast_necro_count[m]*100:.1f}%)")
        
        print("\nLoss Reasons:")
        for reason, count in loss_reasons.items():
            if count > 0:
                percent = count/(total_losses + failed_necro_count)*100
                print(f"  {reason}: {count} ({percent:.1f}% of losses)")
        
        return stats
    
    def run_draw_count_analysis(self, deck: list[str], initial_hand: list[str], min_draw: int = 10, max_draw: int = 19, iterations: int = 10000) -> list:
        results = []
        for draw_count in range(max_draw, min_draw - 1, -1):
            print(f"\nAnalyzing draw_count = {draw_count}")
            stats = self.run_multiple_simulations_without_mulligan(deck, initial_hand, draw_count, iterations)
            results.append(stats)
        
        return results
    
    def compare_decks(self, decks: list[list[str]], deck_names: list[str], draw_count: int, mulligan_until_necro: bool, iterations: int = 10000):
        results = []
        
        for i, deck in enumerate(decks):
            deck_name = deck_names[i]
            if mulligan_until_necro:
                stats = self.run_multiple_simulations(deck, [], draw_count, True, iterations)
            else:
                stats = self.run_multiple_simulations_without_mulligan(deck, [], draw_count, iterations)
            
            # デッキ名を追加
            stats['deck_name'] = deck_name
            
            results.append(stats)
        
        # 結果を表示
        print("\nDeck Comparison Results:")
        for result in results:
            print(f"Deck: {result['deck_name']}, Win Rate: {result['win_rate']:.1f}%")
        
        return results
    
    def compare_initial_hands(self, initial_hands: list[list[str]], deck: list[str], draw_count: int = 19, iterations: int = 10000):
        results = []
        
        for initial_hand in initial_hands:
            stats = self.run_multiple_simulations_without_mulligan(deck, initial_hand, draw_count, iterations)
            
            # 初期手札の内容を追加
            stats['initial_hand'] = ', '.join(initial_hand)
            
            results.append(stats)
        
        # win_rateの昇順でソート（最も低いものが先頭に来るように）
        results.sort(key=lambda x: x['win_rate'])
        
        # 結果を表示
        print("\nInitial Hand Comparison Results (sorted by win rate):")
        for result in results:
            print(f"Initial Hand: {result['initial_hand']}, Win Rate: {result['win_rate']:.1f}%")
        
        return results

def compare_initial_hands(analyzer: DeckAnalyzer):
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
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CABAL_RITUAL],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, VALAKUT_AWAKENING],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, BESEECH_MIRROR],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, TENDRILS_OF_AGONY],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CHROME_MOX]
    ]

    deck = create_deck('decks/wind3_valakut3_cantor1.txt')
    results = analyzer.compare_initial_hands(initial_hands, deck)
    
    save_results_to_csv('compare_initial_hands', results, DEFAULT_PRIORITY_FIELDS)

def compare_decks(analyzer: DeckAnalyzer):
    decks = [create_deck(path) for path in DECK_PATHS]
    deck_names = [get_filename_without_extension(path) for path in DECK_PATHS]
    
    results = analyzer.compare_decks(decks, deck_names, 19, mulligan_until_necro=True, iterations=1000000)
    
    save_results_to_csv('compare_decks', results, DEFAULT_PRIORITY_FIELDS)

def analyze_draw_counts(analyzer: DeckAnalyzer):
    # 複数のデッキリストを分析
    DECK_PATHS = [
        'decks/wind3_valakut3_cantor1.txt',
        'decks/wind4_valakut2_cantor1.txt',
        'decks/wind4_valakut2_cantor0_paradise1.txt'
    ]
    
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
    all_results = []
    
    for deck_path in DECK_PATHS:
        print(f"\nAnalyzing deck: {deck_path}")
        deck = create_deck(deck_path)
        deck_name = get_filename_without_extension(deck_path)
        
        # 100,000回のイテレーションで実行
        results = analyzer.run_draw_count_analysis(deck, initial_hand, min_draw=10, max_draw=19, iterations=100000)
        
        # 各結果にデッキ名を追加
        for result in results:
            result['deck_name'] = deck_name
            all_results.append(result)
    
    save_results_to_csv('analyze_draw_counts', all_results, DEFAULT_PRIORITY_FIELDS)

if __name__ == "__main__":
    analyzer = DeckAnalyzer()
    #compare_decks(analyzer)
    analyze_draw_counts(analyzer)
    #compare_initial_hands(analyzer)
