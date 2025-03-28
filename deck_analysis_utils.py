from game_state import *
from deck_utils import get_filename_without_extension, create_deck, save_results_to_csv, DEFAULT_PRIORITY_FIELDS
from deck_analyzer import DeckAnalyzer
import time
import datetime
import itertools

# 定数
BEST_DECK_PATH = 'decks/gemstone4_paradise0_cantor0_chrome4_wind4_valakut3.txt'
DEFAULT_ITERATIONS = 1000000
DEFAULT_INITIAL_ITERATIONS = 100000

def run_test_patterns(analyzer: DeckAnalyzer, pattern_list: list, filename: str, iterations: int = DEFAULT_ITERATIONS, sort_by_win_rate: bool = False):
    """
    テストパターンのリストに対してシミュレーションを実行する汎用関数
    
    各パターンは以下の形式のディクショナリです：
    {
        'name': str,  # パターン名
        'deck': list[str],  # デッキ
        'initial_hand': list[str],  # 初期手札（空リストの場合はrun_multiple_simulations_without_initial_handを使用）
        'bottom_list': list[str],  # デッキボトムに戻すカードのリスト
        'summoners_pact_strategy': SummonersPactStrategy,  # Summoner's Pactの戦略
        'draw_count': int  # ドロー数
    }
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        pattern_list: テストパターンのリスト
        filename: 結果を保存するCSVファイルの名前（拡張子なし）
        iterations: シミュレーション回数
        sort_by_win_rate: 結果をwin_rateでソートするかどうか（デフォルトはFalse）
        
    Returns:
        各パターンの結果のリスト
    """
    results = []
    
    print(f"\nRunning {len(pattern_list)} test patterns with {iterations} iterations each")
    
    for i, pattern in enumerate(pattern_list):
        name = pattern.get('name', f'Pattern {i+1}')
        deck = pattern.get('deck', [])
        initial_hand = pattern.get('initial_hand', [])
        bottom_list = pattern.get('bottom_list', [])
        summoners_pact_strategy = pattern.get('summoners_pact_strategy', SummonersPactStrategy.NEVER_CAST)
        draw_count = pattern.get('draw_count', 19)
        opponent_has_forces = pattern.get('opponent_has_forces', False)
        
        print(f"\nRunning pattern: {name}")
        print(f"Initial hand: {', '.join(initial_hand) if initial_hand else 'None'}")
        print(f"Bottom list: {', '.join(bottom_list) if bottom_list else 'None'}")
        print(f"Summoner's Pact Strategy: {summoners_pact_strategy}")
        print(f"Draw count: {draw_count}")
        print(f"Opponent has forces: {opponent_has_forces}")
        
        # 初期手札が空の場合はrun_multiple_simulations_without_initial_handを使用
        if not initial_hand:
            stats = analyzer.run_multiple_simulations_without_initial_hand(
                deck=deck, 
                draw_count=draw_count, 
                mulligan_until_necro=True, 
                summoners_pact_strategy=summoners_pact_strategy, 
                opponent_has_forces=opponent_has_forces, 
                iterations=iterations
            )
        else:
            # 初期手札が指定されている場合はrun_multiple_simulations_with_initial_handを使用
            stats = analyzer.run_multiple_simulations_with_initial_hand(
                deck=deck, 
                initial_hand=initial_hand, 
                bottom_list=bottom_list, 
                draw_count=draw_count, 
                summoners_pact_strategy=summoners_pact_strategy, 
                iterations=iterations
            )
        
        # 結果にパターン情報を追加（statsを直接変更）
        stats['pattern_name'] = name
        if initial_hand:  # 初期手札が空でない場合のみ追加
            stats['initial_hand'] = ', '.join(initial_hand)
        if bottom_list:  # ボトムリストが空でない場合のみ追加
            stats['bottom_list'] = ', '.join(bottom_list)
        stats['summoners_pact_strategy'] = summoners_pact_strategy
        
        # statsを使用
        result = stats
        
        results.append(result)
    
    # sort_by_win_rateがTrueの場合のみ結果を勝率の昇順でソート
    if sort_by_win_rate:
        results.sort(key=lambda x: x['win_rate'], reverse=False)
    
    # 結果を表示
    print("\nTest Pattern Results:")
    for result in results:
        print(f"Pattern: {result['pattern_name']}, Win Rate: {result['win_rate']:.2f}%")
    
    # 結果をCSVに保存
    save_results_to_csv(filename, results, DEFAULT_PRIORITY_FIELDS)
    
    return results

def create_custom_deck(card_counts: dict, base_deck_path: str = BEST_DECK_PATH) -> list:
    """
    指定されたカード枚数でデッキを作成する関数
    
    Args:
        card_counts: カードと枚数の辞書 (例: {GEMSTONE_MINE: 4, CHROME_MOX: 4})
        base_deck_path: ベースデッキのファイルパス
        
    Returns:
        作成されたデッキ（カード名のリスト）
    """
    # ベースデッキを読み込む
    base_deck = create_deck(base_deck_path)
    
    # 辞書のキーに含まれるカードをベースデッキから削除
    remove_cards = list(card_counts.keys())
    new_deck = [card for card in base_deck if card not in remove_cards]
    
    # 指定されたカードを追加
    for card, count in card_counts.items():
        new_deck.extend([card] * count)
    
    # デッキの枚数を確認
    if len(new_deck) != 60:
        print(f"Warning: Deck has {len(new_deck)} cards, not 60.")
    
    return new_deck

def simulate_summoners_pact_strategies(analyzer: DeckAnalyzer, deck_path: str = BEST_DECK_PATH, draw_count: int = 19, iterations: int = DEFAULT_ITERATIONS):
    """
    複数の初期手札と底札の組み合わせについて、Summoner's Pactをキャストするかどうかを比較する関数
    
    様々なカードの組み合わせについて、cast_summoners_pactがTrueとFalseの両方のケースをテストします。
    基本的な初期手札は [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT] で、
    マリガンの場合は [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, X] となり、
    底札は [GEMSTONE_MINE, GEMSTONE_MINE, X] となります。
    Xには様々なカードが入ります。
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        deck_path: デッキファイルのパス
        draw_count: ドロー数
        iterations: シミュレーション回数
        
    Returns:
        各組み合わせの結果のリスト
    """
    # デッキを読み込む
    deck = create_deck(deck_path)
    
    # 初期手札と底札の組み合わせを定義
    test_cases = [
        {
            'name': 'basic_hand',
            'initial_hand': [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT],
            'bottom_list': []
        },
        {
            'name': 'bottom_necessary_cards',
            'initial_hand': [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING],
            'bottom_list': [MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING]
        }
    ]
    
    # 様々なカードをXとして追加
    cards_to_test = [
        CHROME_MOX,
        LOTUS_PETAL,
        SUMMONERS_PACT,
        ELVISH_SPIRIT_GUIDE,
        SIMIAN_SPIRIT_GUIDE,
        WILD_CANTOR,
        MANAMORPHOSE,
        VALAKUT_AWAKENING,
        BORNE_UPON_WIND,
        DARK_RITUAL,
        CABAL_RITUAL,
        NECRODOMINANCE,
        BESEECH_MIRROR,
        TENDRILS_OF_AGONY,
        PACT_OF_NEGATION,
        DURESS,
        CHANCELLOR_OF_ANNEX
    ]
    
    for card in cards_to_test:
        card_name = card.split(' ')[0].lower()
        test_cases.append({
            'name': f'bottom_{card_name}',
            'initial_hand': [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, card],
            'bottom_list': [card]  # Xの1枚のみをボトムに戻す
        })
    
    # テストケースごとにパターンを作成し、「Do not cast」と「Cast」のペアで追加
    all_patterns = []
    
    for test_case in test_cases:
        case_name = test_case['name']
        initial_hand = test_case['initial_hand']
        bottom_list = test_case['bottom_list']
        
        print(f"\nTesting case {case_name}:")
        print(f"Initial hand: {', '.join(initial_hand)}")
        print(f"Bottom list: {', '.join(bottom_list)}")
        
        # このテストケースの「Do not cast」と「Cast」のパターンをペアで追加
        # 「Do not cast」を先に追加
        all_patterns.append({
            'name': f'Case {case_name} - Do not cast Summoner\'s Pact',
            'deck': deck,
            'initial_hand': initial_hand,
            'bottom_list': bottom_list,
            'summoners_pact_strategy': SummonersPactStrategy.NEVER_CAST,
            'draw_count': draw_count
        })
        
        # 次に「Cast」を追加
        all_patterns.append({
            'name': f'Case {case_name} - Cast Summoner\'s Pact',
            'deck': deck,
            'initial_hand': initial_hand,
            'bottom_list': bottom_list,
            'summoners_pact_strategy': SummonersPactStrategy.ALWAYS_CAST,
            'draw_count': draw_count
        })
    
    # すべてのパターンを一度に実行
    filename = "simulate_summoners_pact_strategies"
    results = run_test_patterns(analyzer, all_patterns, filename, iterations)
    
    # 結果を整理
    all_results = []
    better_cast = []
    better_not_cast = []
    
    for test_case in test_cases:
        case_name = test_case['name']
        initial_hand = test_case['initial_hand']
        bottom_list = test_case['bottom_list']
        
        # 結果を取得
        result_without_cast = next(r for r in results if f'Case {case_name} - Do not cast' in r['pattern_name'])
        result_with_cast = next(r for r in results if f'Case {case_name} - Cast Summoner' in r['pattern_name'])
        
        win_rate_without_cast = result_without_cast['win_rate']
        win_rate_with_cast = result_with_cast['win_rate']
        win_rate_diff = win_rate_with_cast - win_rate_without_cast
        
        # 結果を表示
        print(f"\nCase {case_name} - Summoner's Pact Casting Strategy Comparison Results:")
        print(f"Do not cast Summoner's Pact: Win Rate = {win_rate_without_cast:.2f}%")
        print(f"Cast Summoner's Pact: Win Rate = {win_rate_with_cast:.2f}%")
        print(f"Difference (Cast - Do not cast): {win_rate_diff:.2f}%")
        
        # 勝率が高い方の戦略を表示
        if win_rate_with_cast > win_rate_without_cast:
            print(f"Conclusion for Case {case_name}: Casting Summoner's Pact is better")
            better_cast.append(case_name)
        else:
            print(f"Conclusion for Case {case_name}: Not casting Summoner's Pact is better")
            better_not_cast.append(case_name)
        
        # 結果をリストに追加
        all_results.append({
            'case': case_name,
            'initial_hand': ', '.join(initial_hand),
            'bottom_list': ', '.join(bottom_list),
            'win_rate_without_cast': win_rate_without_cast,
            'win_rate_with_cast': win_rate_with_cast,
            'win_rate_diff': win_rate_diff,
            'better_strategy': 'Cast Summoner\'s Pact' if win_rate_with_cast > win_rate_without_cast else 'Do not cast Summoner\'s Pact'
        })
    
    # win_rate_diffでソート（降順）
    all_results.sort(key=lambda x: x['win_rate_diff'], reverse=True)
    
    # Summoner's Pactをキャストする方が良いケースとキャストしない方が良いケースを表示
    print("\n=== Summoner's Pactをキャストする方が良いケース ===")
    for case in better_cast:
        print(f"- {case}")
    
    print("\n=== Summoner's Pactをキャストしない方が良いケース ===")
    for case in better_not_cast:
        print(f"- {case}")
    
    # 結果をCSVに保存
    save_results_to_csv('simulate_summoners_pact_strategies_summary', all_results, ['case', 'initial_hand', 'bottom_list', 'win_rate_without_cast', 'win_rate_with_cast', 'win_rate_diff', 'better_strategy'])
    
    return all_results

def simulate_auto_summoners_pact_strategy(analyzer: DeckAnalyzer, deck_path: str = BEST_DECK_PATH, draw_count: int = 19, iterations: int = DEFAULT_ITERATIONS):
    """
    複数の初期手札と底札の組み合わせについて、Summoner's Pactの戦略をAUTOに設定してシミュレーションを実行する関数
    
    compare_summoners_pact_strategiesと同じテストケースを使用しますが、すべてのケースでsummoners_pact_strategyをAUTOに設定します。
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        deck_path: デッキファイルのパス
        draw_count: ドロー数
        iterations: シミュレーション回数
        
    Returns:
        各組み合わせの結果のリスト
    """
    # デッキを読み込む
    deck = create_deck(deck_path)
    
    # 初期手札と底札の組み合わせを定義
    test_cases = [
        {
            'name': 'basic_hand',
            'initial_hand': [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT],
            'bottom_list': []
        },
        {
            'name': 'bottom_necessary_cards',
            'initial_hand': [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING],
            'bottom_list': [MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING]
        }
    ]
    
    # 様々なカードをXとして追加
    cards_to_test = [
        CHROME_MOX,
        LOTUS_PETAL,
        SUMMONERS_PACT,
        ELVISH_SPIRIT_GUIDE,
        SIMIAN_SPIRIT_GUIDE,
        WILD_CANTOR,
        MANAMORPHOSE,
        VALAKUT_AWAKENING,
        BORNE_UPON_WIND,
        DARK_RITUAL,
        CABAL_RITUAL,
        NECRODOMINANCE,
        BESEECH_MIRROR,
        TENDRILS_OF_AGONY,
        PACT_OF_NEGATION,
        DURESS,
        CHANCELLOR_OF_ANNEX
    ]
    
    for card in cards_to_test:
        card_name = card.split(' ')[0].lower()
        test_cases.append({
            'name': f'bottom_{card_name}',
            'initial_hand': [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, card],
            'bottom_list': [card]  # Xの1枚のみをボトムに戻す
        })
    
    # テストケースごとにパターンを作成し、すべてAUTOに設定
    all_patterns = []
    
    for test_case in test_cases:
        case_name = test_case['name']
        initial_hand = test_case['initial_hand']
        bottom_list = test_case['bottom_list']
        
        print(f"\nTesting case {case_name}:")
        print(f"Initial hand: {', '.join(initial_hand)}")
        print(f"Bottom list: {', '.join(bottom_list)}")
        
        # このテストケースのパターンを追加
        all_patterns.append({
            'name': f'Case {case_name} - AUTO Summoner\'s Pact',
            'deck': deck,
            'initial_hand': initial_hand,
            'bottom_list': bottom_list,
            'summoners_pact_strategy': SummonersPactStrategy.AUTO,
            'draw_count': draw_count
        })
    
    # すべてのパターンを一度に実行
    filename = "simulate_auto_summoners_pact_strategy"
    results = run_test_patterns(analyzer, all_patterns, filename, iterations)
    
    # 結果を表示
    print("\nAUTO Summoner's Pact Strategy Results:")
    for result in results:
        print(f"Pattern: {result['pattern_name']}, Win Rate: {result['win_rate']:.2f}%")
    
    return results

def simulate_draw_counts(analyzer: DeckAnalyzer, iterations: int = DEFAULT_ITERATIONS):
    """
    最適なデッキ（BEST_DECK_PATH）に対してドロー数分析を実行する関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        iterations: シミュレーション回数
        
    Returns:
        各ドロー数ごとの結果のリスト
    """
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
    
    print(f"\nAnalyzing best deck: {BEST_DECK_PATH}")
    deck = create_deck(BEST_DECK_PATH)
    deck_name = get_filename_without_extension(BEST_DECK_PATH)
    
    # テストパターンのリストを作成
    patterns = []
    for draw_count in range(19, 9, -1):  # 19から10までのドロー数
        patterns.append({
            'name': f'Draw {draw_count}',
            'deck': deck,
            'initial_hand': initial_hand,
            'bottom_list': [],
            'summoners_pact_strategy': SummonersPactStrategy.AUTO,
            'draw_count': draw_count
        })
    
    # run_test_patternsを使用してシミュレーションを実行
    results = run_test_patterns(analyzer, patterns, 'simulate_draw_counts', iterations)
    
    # 各結果にデッキ名を追加
    for result in results:
        result['deck_name'] = deck_name
    
    return results

def simulate_initial_hands(analyzer: DeckAnalyzer, iterations: int = DEFAULT_ITERATIONS):
    """
    プリセットされた初期手札のリストを比較する関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        iterations: シミュレーション回数
        
    Returns:
        各初期手札の結果のリスト
    """
    # 基本の初期手札
    base_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
    
    # 初期手札のリストを作成
    initial_hands = []
    
    # 0枚加える
    initial_hands.append(base_hand.copy())
    
    # 1枚加える
    one_card_additions = [
        GEMSTONE_MINE,
        ELVISH_SPIRIT_GUIDE,
        SIMIAN_SPIRIT_GUIDE,
        SUMMONERS_PACT,
        DARK_RITUAL,
        CABAL_RITUAL,
        CHROME_MOX,
        LOTUS_PETAL,
        MANAMORPHOSE,
        BORNE_UPON_WIND,
        VALAKUT_AWAKENING,
        BESEECH_MIRROR,
        TENDRILS_OF_AGONY
    ]
    
    for card in one_card_additions:
        hand = base_hand.copy()
        hand.append(card)
        initial_hands.append(hand)
    
    # 2枚加える
    two_card_additions = [
        [ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE],
        [LOTUS_PETAL, LOTUS_PETAL],
        [MANAMORPHOSE, BORNE_UPON_WIND],
        [LOTUS_PETAL, BORNE_UPON_WIND]
    ]
    
    for cards in two_card_additions:
        hand = base_hand.copy()
        hand.extend(cards)
        initial_hands.append(hand)
    
    # ベストなデッキを使用
    deck = create_deck(BEST_DECK_PATH)
    
    # テストパターンのリストを作成
    all_patterns = []
    
    # 各初期手札に対してパターンを作成
    for i, hand in enumerate(initial_hands):
        # パターン名を作成
        hand_str = ', '.join(hand)
        pattern_name = f"Hand {i+1}: {hand_str}"
        
        # パターンを追加
        all_patterns.append({
            'name': pattern_name,
            'deck': deck,
            'initial_hand': hand,
            'bottom_list': [],
            'summoners_pact_strategy': SummonersPactStrategy.AUTO,
            'draw_count': 19
        })
    
    # すべてのパターンを一度に実行
    filename = "simulate_initial_hands"
    results = run_test_patterns(analyzer, all_patterns, filename, iterations, sort_by_win_rate=True)
    
    return results

def simulate_bottom_strategies(analyzer: DeckAnalyzer, initial_hand: list, bottom_candidates: list, pattern_name: str = "", deck_path: str = BEST_DECK_PATH, draw_count: int = 19, iterations: int = DEFAULT_ITERATIONS):
    """
    指定された初期手札とボトム候補カードに対して、様々なボトム戦略をシミュレーションする汎用関数
    
    0枚から len(bottom_candidates) 枚までのすべての組み合わせについてシミュレーションを実行します。
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        initial_hand: 初期手札のリスト
        bottom_candidates: ボトム候補カードのリスト
        pattern_name: CSVファイル名の一部に使用する名前
        deck_path: デッキファイルのパス
        draw_count: ドロー数
        iterations: シミュレーション回数
        
    Returns:
        各戦略の結果のリスト
    """
    # デッキを読み込む
    deck = create_deck(deck_path)
    
    # テストパターンのリストを作成
    all_patterns = []
    
    # ケース1: 0枚ボトムに戻す（すべてキープ）
    all_patterns.append({
        'name': 'Keep all 7 cards',
        'deck': deck,
        'initial_hand': initial_hand,
        'bottom_list': [],
        'summoners_pact_strategy': SummonersPactStrategy.AUTO,
        'draw_count': draw_count
    })
    
    # 1枚以上ボトムに戻す場合
    from itertools import combinations
    for n in range(1, len(bottom_candidates) + 1):
        for combo in combinations(bottom_candidates, n):
            bottom_list = list(combo)
            pattern_name_with_details = f"Bottom {n}: {', '.join(bottom_list)}"
            
            all_patterns.append({
                'name': pattern_name_with_details,
                'deck': deck,
                'initial_hand': initial_hand,
                'bottom_list': bottom_list,
                'summoners_pact_strategy': SummonersPactStrategy.AUTO,
                'draw_count': draw_count
            })
    
    # CSVファイル名を生成
    filename = f"simulate_bottom_strategies_{pattern_name}" if pattern_name else "simulate_bottom_strategies"
    
    # すべてのパターンを一度に実行
    results = run_test_patterns(analyzer, all_patterns, filename, iterations, sort_by_win_rate=False)
    
    return results

def simulate_mulligan_strategies(analyzer: DeckAnalyzer, deck_path: str = BEST_DECK_PATH, draw_count: int = 19, iterations: int = DEFAULT_ITERATIONS):
    """
    複数の初期手札パターンについて、様々なボトム戦略をシミュレーションする関数
    
    以下の2つの初期手札パターンについて、様々なボトム戦略を比較します：
    1. [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    2. [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, PACT_OF_NEGATION, MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        deck_path: デッキファイルのパス
        draw_count: ドロー数
        iterations: シミュレーション回数
        
    Returns:
        各戦略の結果のリスト（最後に実行したパターンの結果のみ）
    """
    # パターン1: Lotus Petalを含む初期手札
    initial_hand_1 = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    bottom_candidates_1 = [LOTUS_PETAL, MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    
    # パターン1のシミュレーションを実行
    results_1 = simulate_bottom_strategies(
        analyzer=analyzer,
        initial_hand=initial_hand_1,
        bottom_candidates=bottom_candidates_1,
        pattern_name="Lotus_Petal",
        deck_path=deck_path,
        draw_count=draw_count,
        iterations=iterations
    )
    
    # パターン2: Pact of Negationを含む初期手札
    initial_hand_2 = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, PACT_OF_NEGATION, MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    bottom_candidates_2 = [MANAMORPHOSE, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    
    # パターン2のシミュレーションを実行
    results_2 = simulate_bottom_strategies(
        analyzer=analyzer,
        initial_hand=initial_hand_2,
        bottom_candidates=bottom_candidates_2,
        pattern_name="Pact_of_Negation",
        deck_path=deck_path,
        draw_count=draw_count,
        iterations=iterations
    )
    
    # 最後に実行したパターンの結果を返す
    return results_2

# custom deck simulations
def simulate_custom_deck_variations(analyzer: DeckAnalyzer, card_counts_list: list, filename: str, opponent_has_forces: bool = False, iterations: int = DEFAULT_ITERATIONS):
    """
    カード枚数の辞書のリストからデッキを作成し、シミュレーションを実行する汎用関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        card_counts_list: カード枚数の辞書のリスト
        filename: 結果を保存するCSVファイルの名前（拡張子なし）
        iterations: シミュレーション回数
        opponent_has_forces: 相手がForceを持っているかどうか（デフォルトはFalse）
        
    Returns:
        各デッキバリエーションの結果のリスト
    """
    # テストパターンのリストを作成
    all_patterns = []
    
    # 各組み合わせに対してデッキを作成
    for i, card_counts in enumerate(card_counts_list):
        # デッキを作成
        deck = create_custom_deck(card_counts)
        
        # デッキ名を作成（フルネームを使用）
        deck_name = "_".join([f"{card.split(' ')[0]}{count}" for card, count in card_counts.items()])
        
        # パターンを追加
        all_patterns.append({
            'name': deck_name,
            'deck': deck,
            'initial_hand': [],  # 初期手札なし
            'bottom_list': [],
            'summoners_pact_strategy': SummonersPactStrategy.AUTO,
            'draw_count': 19,
            'opponent_has_forces': opponent_has_forces
        })
    
    # デッキの枚数とカード構成を確認
    for pattern in all_patterns:
        deck = pattern['deck']
        deck_name = pattern['name']
        print(f"Deck {deck_name}: {len(deck)} cards")
        
        # カードの枚数を数える
        card_counts = {}
        for card in deck:
            if card in card_counts:
                card_counts[card] += 1
            else:
                card_counts[card] = 1
        
        # 重要なカードの枚数を表示
        for card, count in card_counts.items():
            print(f"  {card}: {count}")
    
    # すべてのパターンを一度に実行
    results = run_test_patterns(analyzer, all_patterns, filename, iterations, sort_by_win_rate=True)
    
    # 各結果にカード枚数情報を追加
    for result in results:
        pattern_name = result['pattern_name']
        for pattern in all_patterns:
            if pattern['name'] == pattern_name:
                deck = pattern['deck']
                # カードの枚数を数える
                card_counts = {}
                for card in deck:
                    if card in card_counts:
                        card_counts[card] += 1
                    else:
                        card_counts[card] = 1
                
                # カード枚数を結果に追加
                for card, count in card_counts.items():
                    result[card] = count
                break
    
    # ソート後の結果を表示
    print("\nDeck Comparison Results (sorted by win rate):")
    for i, result in enumerate(results):
        # 結果からカード枚数を取得
        card_counts_str = []
        for key, value in result.items():
            if key not in ['pattern_name', 'win_rate', 'initial_hand', 'bottom_list', 'summoners_pact_strategy'] and isinstance(value, (int, float)) and not key.startswith('_'):
                card_name = key.split(' ')[0]
                card_count = value
                card_counts_str.append(f"{card_name}{card_count}")
        
        # デッキ説明を作成
        deck_desc = "_".join(card_counts_str)
        print(f"Deck {i+1}: {deck_desc}, Win Rate: {result['win_rate']:.2f}%")
    
    return results

def simulate_card_combinations(analyzer: DeckAnalyzer, card_ranges: dict, total_cards_count: int, filename: str, opponent_has_forces: bool = False, iterations: int = DEFAULT_ITERATIONS):
    """
    指定されたカードの枚数範囲から、合計枚数が指定された値になるすべての合法な組み合わせを生成し、
    シミュレーションを実行する汎用関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        card_ranges: カードとその枚数範囲の辞書 (例: {GEMSTONE_MINE: [3, 4], CHROME_MOX: [0, 1, 2, 3, 4]})
        total_cards_count: 合計カード枚数
        filename: 結果を保存するCSVファイルの名前（拡張子なし）
        iterations: シミュレーション回数
        
    Returns:
        各デッキバリエーションの結果のリスト
    """
    
    # カードとその範囲のリストを作成
    cards = list(card_ranges.keys())
    ranges = list(card_ranges.values())
    
    # すべての組み合わせを生成
    all_combinations = []
    
    # itertools.productを使用して、すべての組み合わせを生成
    for counts in itertools.product(*ranges):
        # 各カードの枚数を辞書に格納
        card_counts = {card: count for card, count in zip(cards, counts)}
        
        # 合計枚数が指定された値になる組み合わせのみを選択
        total_count = sum(counts)
        if total_count == total_cards_count:
            all_combinations.append(card_counts)
    
    print(f"Found {len(all_combinations)} valid deck combinations with {total_cards_count} cards total")
    
    # 汎用関数を使用してシミュレーションを実行
    return simulate_custom_deck_variations(
        analyzer=analyzer,
        card_counts_list=all_combinations,
        filename=filename,
        opponent_has_forces=opponent_has_forces,
        iterations=iterations
    )

def simulate_two_phase_combinations(analyzer: DeckAnalyzer, card_ranges: dict, total_cards_count: int, filename: str, opponent_has_forces: bool = False, phase2_card_counts: list = None, top_count: int = 20, initial_iterations: int = DEFAULT_INITIAL_ITERATIONS, final_iterations: int = DEFAULT_ITERATIONS):
    """
    2段階のシミュレーションを実行する汎用関数
    
    1. 第1フェーズ：少ないイテレーション数で多くの組み合わせをシミュレーション
    2. 第2フェーズ：第1フェーズの結果から勝率の高い上位パターンを抽出し、より多いイテレーション数で詳細なシミュレーションを実行
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        card_ranges: カードとその枚数範囲の辞書 (例: {GEMSTONE_MINE: [3, 4], CHROME_MOX: [0, 1, 2, 3, 4]})
        total_cards_count: 合計カード枚数
        filename: 結果を保存するCSVファイルの名前（拡張子なし）
        opponent_has_forces: 相手がForceを持っているかどうか（デフォルトはFalse）
        phase2_card_counts: 第2フェーズで追加でシミュレーションを行うベンチマークとなるカードカウントのリスト（デフォルトはNone）
        top_count: 第2フェーズで使用する上位パターンの数（デフォルトは20）
        initial_iterations: 第1フェーズのシミュレーション回数（デフォルトはDEFAULT_INITIAL_ITERATIONS）
        final_iterations: 第2フェーズのシミュレーション回数（デフォルトはDEFAULT_ITERATIONS）
        
    Returns:
        第2フェーズのシミュレーション結果のリスト
    """
    # 第1フェーズ：少ないイテレーション数で多くの組み合わせをシミュレーション
    print(f"\n=== Phase 1: Initial simulation with {initial_iterations} iterations ===")
    phase1_results = simulate_card_combinations(
        analyzer=analyzer,
        card_ranges=card_ranges,
        total_cards_count=total_cards_count,
        filename=f"{filename}_phase1",
        opponent_has_forces=opponent_has_forces,
        iterations=initial_iterations
    )
    
    # 勝率の高い上位パターンを抽出
    phase1_results.sort(key=lambda x: x['win_rate'], reverse=True)
    top_patterns = phase1_results[:top_count]
    
    # 上位パターンのカード構成を取得
    top_card_counts_list = []
    for result in top_patterns:
        pattern_name = result['pattern_name']
        
        # カード枚数を取得
        card_counts = {}
        for card in card_ranges.keys():
            if card in result:
                card_counts[card] = result[card]
        
        top_card_counts_list.append(card_counts)
        
        # 上位パターンの詳細を表示
        print(f"\nTop pattern: {pattern_name}, Win Rate: {result['win_rate']:.2f}%")
        for card, count in card_counts.items():
            print(f"  {card}: {count}")
    
    # phase2_card_countsが存在して空でない場合は、top_card_counts_listに追加（重複は避ける）
    if phase2_card_counts is not None and len(phase2_card_counts) > 0:
        print(f"\nAdding benchmark card counts to Phase 2")
        added_count = 0
        for card_count in phase2_card_counts:
            # すでに同じカード構成がtop_card_counts_listに含まれているかチェック
            if card_count in top_card_counts_list:
                card_counts_str = ", ".join([f"{card}: {count}" for card, count in card_count.items()])
                print(f"Skipping duplicate benchmark: {card_counts_str}")
                continue
                
            # カード構成の詳細を表示
            card_counts_str = ", ".join([f"{card}: {count}" for card, count in card_count.items()])
            print(f"Adding benchmark: {card_counts_str}")
            top_card_counts_list.append(card_count)
            added_count += 1
            
        print(f"Added {added_count} unique benchmark card counts to Phase 2")
    
    # 第2フェーズ：上位パターンに対してより多いイテレーション数でシミュレーション
    print(f"\n=== Phase 2: Detailed simulation with {final_iterations} iterations ===")
    phase2_results = simulate_custom_deck_variations(
        analyzer=analyzer,
        card_counts_list=top_card_counts_list,
        filename=f"{filename}_phase2",
        opponent_has_forces=opponent_has_forces,
        iterations=final_iterations
    )
    
    return phase2_results

def simulate_main_deck_variations(analyzer: DeckAnalyzer, initial_iterations: int = DEFAULT_INITIAL_ITERATIONS, final_iterations: int = DEFAULT_ITERATIONS):
    """
    最適なメインデッキ（サイドボード前のデッキ）の構成を探る関数
    
    2段階のシミュレーションを実行します：
    1. 第1フェーズ：少ないイテレーション数で多くの組み合わせをシミュレーション
    2. 第2フェーズ：第1フェーズの結果から勝率の高い上位パターンを抽出し、より多いイテレーション数で詳細なシミュレーションを実行
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        initial_iterations: 第1フェーズのシミュレーション回数（デフォルトは100,000）
        final_iterations: 第2フェーズのシミュレーション回数（デフォルトは1,000,000）
        
    Returns:
        第2フェーズのシミュレーション結果のリスト
    """
    # カードの枚数範囲を定義
    card_ranges = {
        GEMSTONE_MINE: list(range(0, 7)),  # 0~6
        WILD_CANTOR: [0, 1],  # 0~1
        CHROME_MOX: list(range(0, 5)),  # 0~4
        SUMMONERS_PACT: list(range(2, 5)),  # 2~4
        BORNE_UPON_WIND: [3, 4],  # 3~4
        VALAKUT_AWAKENING: list(range(1, 5))  # 1~4
    }
    
    # ベンチマークとなるカード構成を定義
    benchmark_card_counts = [
        {
            GEMSTONE_MINE: 4,
            WILD_CANTOR: 0,
            CHROME_MOX: 4,
            SUMMONERS_PACT: 4,
            BORNE_UPON_WIND: 4,
            VALAKUT_AWAKENING: 3
        }
    ]
    
    # 2段階シミュレーション汎用関数を使用
    return simulate_two_phase_combinations(
        analyzer=analyzer,
        card_ranges=card_ranges,
        total_cards_count=19,
        filename="simulate_main_deck_variations",
        opponent_has_forces=False,
        phase2_card_counts=benchmark_card_counts,
        initial_iterations=initial_iterations,
        final_iterations=final_iterations
    )

def simulate_chancellor_variations(analyzer: DeckAnalyzer, initial_iterations: int = DEFAULT_INITIAL_ITERATIONS, final_iterations: int = DEFAULT_ITERATIONS):
    """
    Chancellorを4枚入れて他のカードを4枚抜く場合の様々な組み合わせを比較する関数
    
    以下の枚数範囲で、合計27枚になるすべての組み合わせをテストします：
    - chancellor: 4（固定）
    - gemstone: 3~4
    - chrome: 0~4
    - summoner: 2~4
    - wind: 3~4
    - valakut: 2~3
    - cabal: 2~4
    - beseech: 2~4
    
    2段階のシミュレーションを実行します：
    1. 第1フェーズ：少ないイテレーション数で多くの組み合わせをシミュレーション
    2. 第2フェーズ：第1フェーズの結果から勝率の高い上位パターンを抽出し、より多いイテレーション数で詳細なシミュレーションを実行
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        opponent_has_forces: 相手がForceを持っているかどうか（デフォルトはFalse）
        initial_iterations: 第1フェーズのシミュレーション回数（デフォルトは100,000）
        final_iterations: 第2フェーズのシミュレーション回数（デフォルトは1,000,000）
        
    Returns:
        第2フェーズのシミュレーション結果のリスト
    """
    # カードの枚数範囲を定義
    card_ranges = {
        CHANCELLOR_OF_ANNEX: [4],
        GEMSTONE_MINE: [0, 1, 2, 3, 4],
        CHROME_MOX: [0, 1, 2, 3, 4],
        SUMMONERS_PACT: [0, 1, 2, 3, 4],
        BORNE_UPON_WIND: [3, 4],
        VALAKUT_AWAKENING: [0, 1, 2, 3],
        CABAL_RITUAL: [0, 1, 2, 3, 4],
        BESEECH_MIRROR: [0, 1, 2, 3, 4]
    }
    
    # ベンチマークとなるカード構成を定義
    benchmark_card_counts = [
        {
            CHANCELLOR_OF_ANNEX: 0,
            GEMSTONE_MINE: 4,
            CHROME_MOX: 4,
            SUMMONERS_PACT: 4,
            BORNE_UPON_WIND: 4,
            VALAKUT_AWAKENING: 3,
            CABAL_RITUAL: 4,
            BESEECH_MIRROR: 4
        }
    ]
    
    # 2段階シミュレーション汎用関数を使用
    return simulate_two_phase_combinations(
        analyzer=analyzer,
        card_ranges=card_ranges,
        total_cards_count=27,
        filename="simulate_chancellor_variations",
        opponent_has_forces=False,
        phase2_card_counts=benchmark_card_counts,
        initial_iterations=initial_iterations,
        final_iterations=final_iterations
    )

def simulate_chancellor_variations_against_forces(analyzer: DeckAnalyzer, initial_iterations: int = DEFAULT_INITIAL_ITERATIONS, final_iterations: int = DEFAULT_ITERATIONS):
    """
    Forceを持つ相手に対して、Chancellorの枚数を変えた場合の様々な組み合わせを比較する関数
    
    以下の枚数範囲で、合計27枚になるすべての組み合わせをテストします：
    - chancellor: 0~4
    - gemstone: 0~4
    - chrome: 0~4
    - summoner: 0~4
    - wind: 3~4
    - valakut: 0~3
    - cabal: 0~4
    - beseech: 0~4
    
    2段階のシミュレーションを実行します：
    1. 第1フェーズ：少ないイテレーション数で多くの組み合わせをシミュレーション
    2. 第2フェーズ：第1フェーズの結果から勝率の高い上位パターンを抽出し、より多いイテレーション数で詳細なシミュレーションを実行
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        initial_iterations: 第1フェーズのシミュレーション回数（デフォルトは100,000）
        final_iterations: 第2フェーズのシミュレーション回数（デフォルトは1,000,000）
        
    Returns:
        第2フェーズのシミュレーション結果のリスト
    """
    # カードの枚数範囲を定義
    card_ranges = {
        CHANCELLOR_OF_ANNEX: [0,1,2,3,4],
        GEMSTONE_MINE: [0, 1, 2, 3, 4],
        CHROME_MOX: [0, 1, 2, 3, 4],
        SUMMONERS_PACT: [0, 1, 2, 3, 4],
        BORNE_UPON_WIND: [3, 4],
        VALAKUT_AWAKENING: [0, 1, 2, 3],
        CABAL_RITUAL: [0, 1, 2, 3, 4],
        BESEECH_MIRROR: [0, 1, 2, 3, 4]
    }
    
    # ベンチマークとなるカード構成を定義
    benchmark_card_counts = [
        {
            CHANCELLOR_OF_ANNEX: 0,
            GEMSTONE_MINE: 4,
            CHROME_MOX: 4,
            SUMMONERS_PACT: 4,
            BORNE_UPON_WIND: 4,
            VALAKUT_AWAKENING: 3,
            CABAL_RITUAL: 4,
            BESEECH_MIRROR: 4
        }
    ]
    
    # 2段階シミュレーション汎用関数を使用
    return simulate_two_phase_combinations(
        analyzer=analyzer,
        card_ranges=card_ranges,
        total_cards_count=27,
        filename="simulate_chancellor_variations_against_forces",
        opponent_has_forces=True,
        phase2_card_counts=benchmark_card_counts,
        initial_iterations=initial_iterations,
        final_iterations=final_iterations
    )

if __name__ == "__main__":
    analyzer = DeckAnalyzer()
    
    print("シミュレーション開始: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    start_time = time.time()
    
    # シミュレーション関数を実行
    print("\n=== シミュレーション実行 ===")
    #simulate_summoners_pact_strategies(analyzer)
    #simulate_auto_summoners_pact_strategy(analyzer)
    #simulate_main_deck_variations(analyzer)
    #simulate_draw_counts(analyzer)
    #simulate_initial_hands(analyzer)
    #simulate_mulligan_strategies(analyzer)
    simulate_chancellor_variations(analyzer)
    simulate_chancellor_variations_against_forces(analyzer)

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 経過時間を時間、分、秒に変換
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print(f"\nシミュレーション終了: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1時間以上かかった場合は時間も表示
    if hours > 0:
        print(f"経過時間: {int(hours)}時間{int(minutes)}分{seconds:.2f}秒")
    else:
        print(f"経過時間: {elapsed_time:.2f}秒 ({elapsed_time/60:.2f}分)")
