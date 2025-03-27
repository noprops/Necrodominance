from game_state import *
from deck_utils import get_filename_without_extension, create_deck, save_results_to_csv, DEFAULT_PRIORITY_FIELDS
from deck_analyzer import DeckAnalyzer
import time
import datetime
import itertools
import csv
import os

# 定数
BEST_DECK_PATH = 'decks/gemstone4_paradise0_cantor0_chrome4_wind4_valakut3.txt'
DEFAULT_ITERATIONS = 10000

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
        
        print(f"\nRunning pattern: {name}")
        print(f"Initial hand: {', '.join(initial_hand) if initial_hand else 'None'}")
        print(f"Bottom list: {', '.join(bottom_list) if bottom_list else 'None'}")
        print(f"Summoner's Pact Strategy: {summoners_pact_strategy}")
        print(f"Draw count: {draw_count}")
        
        # 初期手札が空の場合はrun_multiple_simulations_without_initial_handを使用
        if not initial_hand:
            stats = analyzer.run_multiple_simulations_without_initial_hand(
                deck=deck, 
                draw_count=draw_count, 
                mulligan_until_necro=True, 
                summoners_pact_strategy=summoners_pact_strategy, 
                opponent_has_forces=False, 
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
        stats['initial_hand'] = None if not initial_hand else ', '.join(initial_hand)
        stats['bottom_list'] = None if not bottom_list else ', '.join(bottom_list)
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

def simulate_deck_variations(analyzer: DeckAnalyzer, opponent_has_forces: bool = False, iterations: int = DEFAULT_ITERATIONS):
    """
    様々なデッキバリエーションを比較する関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        iterations: シミュレーション回数
        opponent_has_forces: 相手がForceを持っているかどうか
        
    Returns:
        各デッキの結果のリスト
    """
    # デッキパターンのリスト
    # [GEMSTONE_MINE, UNDISCOVERED_PARADISE, WILD_CANTOR, CHROME_MOX, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    deck_patterns = [
        [4, 2, 0, 3, 4, 2],
        [4, 2, 0, 3, 3, 3],
        [4, 2, 0, 2, 4, 3],
        [4, 1, 1, 2, 4, 3],
        [4, 1, 0, 4, 4, 2],
        [4, 1, 0, 4, 3, 3],
        [4, 1, 0, 3, 4, 3],
        [4, 1, 0, 3, 3, 4],
        [4, 1, 0, 2, 4, 4],
        [4, 0, 1, 4, 4, 2],
        [4, 0, 1, 4, 3, 3],
        [4, 0, 1, 3, 4, 3],
        [4, 0, 1, 2, 4, 4],
        [4, 0, 0, 4, 4, 3],
        [4, 0, 0, 3, 4, 4],
        [3, 0, 1, 4, 4, 3],
        [3, 0, 1, 3, 4, 4],
        [3, 0, 0, 4, 4, 4]
    ]
    
    # テストパターンのリストを作成
    all_patterns = []
    
    # 各パターンに対してデッキを作成
    for pattern in deck_patterns:
        gemstone_count, paradise_count, cantor_count, chrome_count, wind_count, valakut_count = pattern
        
        # デッキを作成
        card_counts = {
            GEMSTONE_MINE: gemstone_count,
            UNDISCOVERED_PARADISE: paradise_count,
            WILD_CANTOR: cantor_count,
            CHROME_MOX: chrome_count,
            BORNE_UPON_WIND: wind_count,
            VALAKUT_AWAKENING: valakut_count
        }
        deck = create_custom_deck(card_counts)
        
        # デッキ名を作成
        deck_name = f"Gemstone{gemstone_count}_Paradise{paradise_count}_Cantor{cantor_count}_Chrome{chrome_count}_Wind{wind_count}_Valakut{valakut_count}"
        
        # パターンを追加
        all_patterns.append({
            'name': deck_name,
            'deck': deck,
            'initial_hand': [],  # 初期手札なし（run_multiple_simulations_without_initial_handを使用）
            'bottom_list': [],
            'summoners_pact_strategy': SummonersPactStrategy.AUTO,
            'draw_count': 19
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
        important_cards = [GEMSTONE_MINE, UNDISCOVERED_PARADISE, WILD_CANTOR, CHROME_MOX, BORNE_UPON_WIND, VALAKUT_AWAKENING]
        for card in important_cards:
            count = card_counts.get(card, 0)
            print(f"  {card}: {count}")
    
    # すべてのパターンを一度に実行
    filename = "simulate_deck_variations"
    results = run_test_patterns(analyzer, all_patterns, filename, iterations, sort_by_win_rate=True)
    
    # 各結果にカード枚数情報を追加
    for i, result in enumerate(results):
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
                
                # 重要なカードの枚数を結果に追加
                important_cards = [GEMSTONE_MINE, UNDISCOVERED_PARADISE, WILD_CANTOR, CHROME_MOX, BORNE_UPON_WIND, VALAKUT_AWAKENING]
                for card in important_cards:
                    count = card_counts.get(card, 0)
                    result[card] = count
                break
    
    # ソート後の結果を表示
    print("\nDeck Comparison Results (sorted by win rate):")
    for i, result in enumerate(results):
        gemstone_count = result.get(GEMSTONE_MINE, 0)
        paradise_count = result.get(UNDISCOVERED_PARADISE, 0)
        cantor_count = result.get(WILD_CANTOR, 0)
        chrome_count = result.get(CHROME_MOX, 0)
        wind_count = result.get(BORNE_UPON_WIND, 0)
        valakut_count = result.get(VALAKUT_AWAKENING, 0)
        
        deck_desc = f"GM{gemstone_count}_UP{paradise_count}_WC{cantor_count}_CM{chrome_count}_BW{wind_count}_VA{valakut_count}"
        print(f"Deck {i+1}: {deck_desc}, Win Rate: {result['win_rate']:.1f}%")
        if opponent_has_forces and 'necro_resolve_rate' in result:
            print(f"  Necro Resolve Rate: {result['necro_resolve_rate']:.1f}%")
    
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

def simulate_chancellor_variations(analyzer: DeckAnalyzer, iterations: int = 10000):
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
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        iterations: シミュレーション回数
        
    Returns:
        各デッキバリエーションの結果のリスト
    """
    import itertools
    
    # カードの枚数範囲を定義
    card_ranges = {
        CHANCELLOR_OF_ANNEX: [4],
        GEMSTONE_MINE: [2, 3, 4],
        CHROME_MOX: [0, 1, 2, 3, 4],
        SUMMONERS_PACT: [0, 1, 2, 3, 4],
        BORNE_UPON_WIND: [3, 4],
        VALAKUT_AWAKENING: [2, 3],
        CABAL_RITUAL: [1, 2, 3, 4],
        BESEECH_MIRROR: [1, 2, 3, 4]
    }
    
    # カードとその範囲のリストを作成
    cards = list(card_ranges.keys())
    ranges = list(card_ranges.values())
    
    # すべての組み合わせを生成
    all_combinations = []
    
    # itertools.productを使用して、すべての組み合わせを生成
    for counts in itertools.product(*ranges):
        # 各カードの枚数を辞書に格納
        card_counts = {card: count for card, count in zip(cards, counts)}
        
        # 合計枚数が27枚になる組み合わせのみを選択
        total_count = sum(counts)
        if total_count == 27:
            all_combinations.append(card_counts)
    
    print(f"Found {len(all_combinations)} valid deck combinations with 27 cards total")
    
    # テストパターンのリストを作成
    all_patterns = []
    
    # 各組み合わせに対してデッキを作成
    for i, combination in enumerate(all_combinations):
        # デッキを作成
        card_counts = combination
        deck = create_custom_deck(card_counts)
        
        # デッキ名を作成（フルネームを使用）
        deck_name = f"Chancellor{combination[CHANCELLOR_OF_ANNEX]}_Gemstone{combination[GEMSTONE_MINE]}_Chrome{combination[CHROME_MOX]}_Summoners{combination[SUMMONERS_PACT]}_Wind{combination[BORNE_UPON_WIND]}_Valakut{combination[VALAKUT_AWAKENING]}_Cabal{combination[CABAL_RITUAL]}_Beseech{combination[BESEECH_MIRROR]}"
        
        # パターンを追加
        all_patterns.append({
            'name': deck_name,
            'deck': deck,
            'initial_hand': [],  # 初期手札なし
            'bottom_list': [],
            'summoners_pact_strategy': SummonersPactStrategy.AUTO,
            'draw_count': 19
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
        important_cards = list(card_ranges.keys())
        for card in important_cards:
            count = card_counts.get(card, 0)
            print(f"  {card}: {count}")
    
    # すべてのパターンを一度に実行
    filename = "simulate_chancellor_variations"
    results = run_test_patterns(analyzer, all_patterns, filename, iterations, sort_by_win_rate=True)
    
    # 各結果にカード枚数情報を追加（直接resultsに追加）
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
                
                # 重要なカードの枚数を結果に追加
                important_cards = list(card_ranges.keys())
                for card in important_cards:
                    count = card_counts.get(card, 0)
                    result[card] = count
                break
    
    # ソート後の結果を表示
    print("\nDeck Comparison Results (sorted by win rate):")
    for i, result in enumerate(results):
        chancellor_count = result.get(CHANCELLOR_OF_ANNEX, 0)
        gemstone_count = result.get(GEMSTONE_MINE, 0)
        chrome_count = result.get(CHROME_MOX, 0)
        summoner_count = result.get(SUMMONERS_PACT, 0)
        wind_count = result.get(BORNE_UPON_WIND, 0)
        valakut_count = result.get(VALAKUT_AWAKENING, 0)
        cabal_count = result.get(CABAL_RITUAL, 0)
        beseech_count = result.get(BESEECH_MIRROR, 0)
        
        # フルネームを使用してデッキ説明を作成
        deck_desc = f"Chancellor{chancellor_count}_Gemstone{gemstone_count}_Chrome{chrome_count}_Summoners{summoner_count}_Wind{wind_count}_Valakut{valakut_count}_Cabal{cabal_count}_Beseech{beseech_count}"
        print(f"Deck {i+1}: {deck_desc}, Win Rate: {result['win_rate']:.1f}%")
    
    return results

def simulate_top_chancellor_variations(analyzer: DeckAnalyzer, iterations: int = 1000000):
    """
    simulate_chancellor_variationsの結果から、win_rateの上位20パターンに絞って、
    より多くのイテレーションでシミュレーションを実行する関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        iterations: シミュレーション回数（デフォルトは1,000,000）
        
    Returns:
        選択された20パターンの結果のリスト
    """
    # 結果ファイルのパスを定義
    results_file = "results/simulate_chancellor_variations.csv"
    
    # 結果ファイルが存在するか確認
    if not os.path.exists(results_file):
        print(f"Error: {results_file} が見つかりません。先にsimulate_chancellor_variationsを実行してください。")
        return None
    
    # CSVファイルから結果を読み込む
    all_results = []
    with open(results_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_results.append(row)
    
    # win_rateでソート（降順）
    all_results.sort(key=lambda x: float(x['win_rate']), reverse=True)
    
    # 上位20パターンを取得
    selected_patterns = all_results[:20]
    
    # 選択されたパターンの名前を表示
    print(f"\n選択された上位20パターン:")
    for i, pattern in enumerate(selected_patterns):
        print(f"{i+1}. {pattern['pattern_name']} - Win Rate: {pattern['win_rate']}%")
    
    # テストパターンのリストを作成
    all_patterns = []
    
    # カードの枚数範囲を定義（simulate_chancellor_variationsと同じ）
    card_ranges = {
        CHANCELLOR_OF_ANNEX: [4],  # 固定
        GEMSTONE_MINE: [3, 4],
        CHROME_MOX: [0, 1, 2, 3, 4],
        SUMMONERS_PACT: [2, 3, 4],
        BORNE_UPON_WIND: [3, 4],
        VALAKUT_AWAKENING: [2, 3],
        CABAL_RITUAL: [2, 3, 4],
        BESEECH_MIRROR: [2, 3, 4]
    }
    
    # 各選択されたパターンに対してデッキを作成
    for pattern in selected_patterns:
        pattern_name = pattern['pattern_name']
        
        # パターン名からカード枚数を抽出
        # 例: "Chancellor4_Gemstone3_Chrome2_Summoners4_Wind3_Valakut3_Cabal4_Beseech4"
        parts = pattern_name.split('_')
        
        # カード枚数の辞書を作成
        card_counts = {}
        
        # Chancellorの枚数を抽出
        chancellor_part = parts[0]  # "Chancellor4"
        chancellor_count = int(chancellor_part[len("Chancellor"):])
        card_counts[CHANCELLOR_OF_ANNEX] = chancellor_count
        
        # Gemstoneの枚数を抽出
        gemstone_part = parts[1]  # "Gemstone3"
        gemstone_count = int(gemstone_part[len("Gemstone"):])
        card_counts[GEMSTONE_MINE] = gemstone_count
        
        # Chromeの枚数を抽出
        chrome_part = parts[2]  # "Chrome2"
        chrome_count = int(chrome_part[len("Chrome"):])
        card_counts[CHROME_MOX] = chrome_count
        
        # Summonersの枚数を抽出
        summoners_part = parts[3]  # "Summoners4"
        summoners_count = int(summoners_part[len("Summoners"):])
        card_counts[SUMMONERS_PACT] = summoners_count
        
        # Windの枚数を抽出
        wind_part = parts[4]  # "Wind3"
        wind_count = int(wind_part[len("Wind"):])
        card_counts[BORNE_UPON_WIND] = wind_count
        
        # Valakutの枚数を抽出
        valakut_part = parts[5]  # "Valakut3"
        valakut_count = int(valakut_part[len("Valakut"):])
        card_counts[VALAKUT_AWAKENING] = valakut_count
        
        # Cabalの枚数を抽出
        cabal_part = parts[6]  # "Cabal4"
        cabal_count = int(cabal_part[len("Cabal"):])
        card_counts[CABAL_RITUAL] = cabal_count
        
        # Beseechの枚数を抽出
        beseech_part = parts[7]  # "Beseech4"
        beseech_count = int(beseech_part[len("Beseech"):])
        card_counts[BESEECH_MIRROR] = beseech_count
        
        # デッキを作成
        deck = create_custom_deck(card_counts)
        
        # パターンを追加
        all_patterns.append({
            'name': pattern_name,
            'deck': deck,
            'initial_hand': [],  # 初期手札なし
            'bottom_list': [],
            'summoners_pact_strategy': SummonersPactStrategy.AUTO,
            'draw_count': 19
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
        important_cards = list(card_ranges.keys())
        for card in important_cards:
            count = card_counts.get(card, 0)
            print(f"  {card}: {count}")
    
    # すべてのパターンを一度に実行
    filename = "simulate_top_chancellor_variations"
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
                
                # 重要なカードの枚数を結果に追加
                important_cards = list(card_ranges.keys())
                for card in important_cards:
                    count = card_counts.get(card, 0)
                    result[card] = count
                break
    
    # ソート後の結果を表示
    print("\nTop Chancellor Variations Results (sorted by win rate):")
    for i, result in enumerate(results):
        chancellor_count = result.get(CHANCELLOR_OF_ANNEX, 0)
        gemstone_count = result.get(GEMSTONE_MINE, 0)
        chrome_count = result.get(CHROME_MOX, 0)
        summoner_count = result.get(SUMMONERS_PACT, 0)
        wind_count = result.get(BORNE_UPON_WIND, 0)
        valakut_count = result.get(VALAKUT_AWAKENING, 0)
        cabal_count = result.get(CABAL_RITUAL, 0)
        beseech_count = result.get(BESEECH_MIRROR, 0)
        
        # フルネームを使用してデッキ説明を作成
        deck_desc = f"Chancellor{chancellor_count}_Gemstone{gemstone_count}_Chrome{chrome_count}_Summoners{summoner_count}_Wind{wind_count}_Valakut{valakut_count}_Cabal{cabal_count}_Beseech{beseech_count}"
        print(f"Deck {i+1}: {deck_desc}, Win Rate: {result['win_rate']:.2f}%")
    
    return results

## old methods

'''
def compare_chancellor_decks_against_counterspells(analyzer: DeckAnalyzer, iterations: int = 1000000):
    """
    相手のデッキに打ち消し呪文（Counterspell）が入っている場合に、
    Chancellor of the Annexを4枚追加したデッキバリエーションを比較する関数
    
    基本デッキ: decks/wind3_valakut3_cantor0_paradise1.txt
    - 元のデッキリストもそのまま比較対象に含める
    - Chancellor of the Annexを4枚追加
    - 指定されたパターンに従って4枚のカードを抜いて60枚にする
    - 各パターンに対してcompare_decksを実行（opponent_has_forces=Trueで実行）
    """
    # 基本デッキを読み込む
    base_deck_path = 'decks/wind3_valakut3_cantor0_paradise1.txt'
    base_deck = create_deck(base_deck_path)
    
    # Chancellor of the Annexを4枚追加
    base_deck_with_chancellor = base_deck + [CHANCELLOR_OF_ANNEX] * 4
    
    # 抜くカードのパターンを定義
    removal_patterns = [
        [CHROME_MOX] * 4,
        [CHROME_MOX] * 3 + [SUMMONERS_PACT] * 1,
        [CHROME_MOX] * 2 + [SUMMONERS_PACT] * 2,
        [CHROME_MOX] * 1 + [SUMMONERS_PACT] * 1 + [BESEECH_MIRROR] * 2,
        [CHROME_MOX] * 1 + [SUMMONERS_PACT] * 1 + [VALAKUT_AWAKENING] * 2,
        [CHROME_MOX] * 1 + [SUMMONERS_PACT] * 1 + [VALAKUT_AWAKENING] * 1 + [BESEECH_MIRROR] * 1,
        [CHROME_MOX] * 1 + [SUMMONERS_PACT] * 1 + [VALAKUT_AWAKENING] * 1 + [BORNE_UPON_WIND] * 1,
        
        [UNDISCOVERED_PARADISE] * 1 + [CHROME_MOX] * 3,
        [UNDISCOVERED_PARADISE] * 1 + [CHROME_MOX] * 2 + [SUMMONERS_PACT] * 1,
        [UNDISCOVERED_PARADISE] * 1 + [CHROME_MOX] * 1 + [SUMMONERS_PACT] * 1 + [BESEECH_MIRROR] * 1,
        [UNDISCOVERED_PARADISE] * 1 + [CHROME_MOX] * 1 + [SUMMONERS_PACT] * 1 + [VALAKUT_AWAKENING] * 1,
        
        [UNDISCOVERED_PARADISE] * 1 + [GEMSTONE_MINE] * 3,
        [UNDISCOVERED_PARADISE] * 1 + [GEMSTONE_MINE] * 1 + [CHROME_MOX] * 2,
    ]
    
    # 各パターンに対してデッキを作成
    decks = []
    deck_names = []
    
    # 元のデッキリストも追加
    decks.append(base_deck)
    deck_names.append("original_deck_no_chancellor")
    
    for i, pattern in enumerate(removal_patterns):
        # パターン名を作成
        pattern_name = f"chancellor_pattern_{i+1}"
        
        # デッキをコピー
        new_deck = base_deck_with_chancellor.copy()
        
        # カードを抜く
        for card in pattern:
            if card in new_deck:
                new_deck.remove(card)
            else:
                print(f"Warning: Card {card} not found in deck for pattern {pattern_name}")
        
        # パターン名にカード情報を追加
        card_counts = {}
        for card in pattern:
            if card in card_counts:
                card_counts[card] += 1
            else:
                card_counts[card] = 1
        
        pattern_desc = "_".join([f"{count}{card.replace(' ', '_')}" for card, count in card_counts.items()])
        pattern_name = f"chancellor_minus_{pattern_desc}"
        
        # デッキとデッキ名を追加
        decks.append(new_deck)
        deck_names.append(pattern_name)
    
    # デッキの枚数を確認
    for i, deck in enumerate(decks):
        print(f"Deck {deck_names[i]}: {len(deck)} cards")
    
    # 比較を実行（opponent_has_forces=Trueで実行）
    results = analyzer.compare_decks(decks, deck_names, 19, opponent_has_forces=True, iterations=iterations)
    
    # win_rateの昇順でソート（最も低いものが先頭に来るように）
    results.sort(key=lambda x: x['win_rate'])
    
    # ソート後の結果を表示
    print("\nDeck Comparison Results (sorted by win rate):")
    for result in results:
        print(f"Deck: {result['deck_name']}, Win Rate: {result['win_rate']:.1f}%")
        if 'necro_resolve_rate' in result:
            print(f"  Necro Resolve Rate: {result['necro_resolve_rate']:.1f}%")
    
    # 結果をCSVに保存
    save_results_to_csv('compare_chancellor_decks_against_counterspells', results, DEFAULT_PRIORITY_FIELDS)
    
    return results
'''


if __name__ == "__main__":
    analyzer = DeckAnalyzer()
    
    print("シミュレーション開始: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    start_time = time.time()
    
    # シミュレーション関数を実行
    print("\n=== シミュレーション実行 ===")
    #simulate_summoners_pact_strategies(analyzer)
    #simulate_auto_summoners_pact_strategy(analyzer)
    #simulate_deck_variations(analyzer)
    #simulate_draw_counts(analyzer)
    #simulate_initial_hands(analyzer)
    #simulate_mulligan_strategies(analyzer)
    #simulate_chancellor_variations(analyzer)
    simulate_top_chancellor_variations(analyzer)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 経過時間を時間、分、秒に変換
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print("\n実行時間:")
    print(f"合計: {elapsed_time:.2f}秒")
    print(f"時間表示: {int(hours)}時間 {int(minutes)}分 {seconds:.2f}秒")
    print("シミュレーション終了: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
