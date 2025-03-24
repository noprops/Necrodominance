from game_state import *
from deck_utils import get_filename_without_extension, create_deck, save_results_to_csv, DEFAULT_PRIORITY_FIELDS
from deck_analyzer import DeckAnalyzer
import time
import datetime

# 定数
BEST_DECK_PATH = 'decks/gemstone4_paradise0_cantor0_chrome4_wind4_valakut3.txt'
DEFAULT_ITERATIONS = 1000000

def run_test_patterns(analyzer: DeckAnalyzer, pattern_list: list, filename: str, iterations: int = DEFAULT_ITERATIONS, sort_by_win_rate: bool = False):
    """
    テストパターンのリストに対してシミュレーションを実行する汎用関数
    
    各パターンは以下の形式のディクショナリです：
    {
        'name': str,  # パターン名
        'deck': list[str],  # デッキ
        'initial_hand': list[str],  # 初期手札（空リストの場合はrun_multiple_simulations_without_initial_handを使用）
        'bottom_list': list[str],  # デッキボトムに戻すカードのリスト
        'cast_summoners_pact': bool,  # Summoner's Pactをキャストするかどうか
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
        cast_summoners_pact = pattern.get('cast_summoners_pact', False)
        draw_count = pattern.get('draw_count', 19)
        
        print(f"\nRunning pattern: {name}")
        print(f"Initial hand: {', '.join(initial_hand) if initial_hand else 'None'}")
        print(f"Bottom list: {', '.join(bottom_list) if bottom_list else 'None'}")
        print(f"Cast Summoner's Pact: {cast_summoners_pact}")
        print(f"Draw count: {draw_count}")
        
        # 初期手札が空の場合はrun_multiple_simulations_without_initial_handを使用
        if not initial_hand:
            stats = analyzer.run_multiple_simulations_without_initial_hand(
                deck=deck, 
                draw_count=draw_count, 
                mulligan_until_necro=True, 
                cast_summoners_pact=cast_summoners_pact, 
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
                cast_summoners_pact=cast_summoners_pact, 
                iterations=iterations
            )
        
        # 結果にパターン情報を追加
        result = stats.copy()
        result['pattern_name'] = name
        result['initial_hand'] = ', '.join(initial_hand) if initial_hand else 'None'
        result['bottom_list'] = ', '.join(bottom_list) if bottom_list else 'None'
        result['cast_summoners_pact'] = cast_summoners_pact
        
        results.append(result)
    
    # sort_by_win_rateがTrueの場合のみ結果をソート
    if sort_by_win_rate:
        results.sort(key=lambda x: x['win_rate'], reverse=True)
    
    # 結果を表示
    print("\nTest Pattern Results:")
    for result in results:
        print(f"Pattern: {result['pattern_name']}, Win Rate: {result['win_rate']:.2f}%")
    
    # 結果をCSVに保存
    save_results_to_csv(filename, results, DEFAULT_PRIORITY_FIELDS)
    
    return results

def compare_summoners_pact_strategies(analyzer: DeckAnalyzer, deck_path: str = BEST_DECK_PATH, draw_count: int = 19, iterations: int = DEFAULT_ITERATIONS):
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
            'cast_summoners_pact': False,
            'draw_count': draw_count
        })
        
        # 次に「Cast」を追加
        all_patterns.append({
            'name': f'Case {case_name} - Cast Summoner\'s Pact',
            'deck': deck,
            'initial_hand': initial_hand,
            'bottom_list': bottom_list,
            'cast_summoners_pact': True,
            'draw_count': draw_count
        })
    
    # すべてのパターンを一度に実行
    filename = "compare_summoners_pact_strategies_all_cases"
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
    
    # Summoner's Pactをキャストする方が良いケースとキャストしない方が良いケースを表示
    print("\n=== Summoner's Pactをキャストする方が良いケース ===")
    for case in better_cast:
        print(f"- {case}")
    
    print("\n=== Summoner's Pactをキャストしない方が良いケース ===")
    for case in better_not_cast:
        print(f"- {case}")
    
    # 結果をCSVに保存
    save_results_to_csv('compare_summoners_pact_strategies_summary', all_results, ['case', 'initial_hand', 'bottom_list', 'win_rate_without_cast', 'win_rate_with_cast', 'win_rate_diff', 'better_strategy'])
    
    return all_results

## old methods
def create_custom_deck(card_counts: dict, base_deck_path: str = 'decks/gemstone4_paradise0_cantor1_chrome4_wind3_valakut3.txt') -> list:
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

def compare_decks(analyzer: DeckAnalyzer, iterations: int = 1000000, opponent_has_forces: bool = False):
    """
    様々なデッキバリエーションを比較する関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        iterations: シミュレーション回数
        opponent_has_forces: 相手がForceを持っているかどうか
        
    Returns:
        各デッキの結果のリスト
    """
    # デッキとデッキ名のリスト
    decks = []
    deck_names = []
    
    # デッキパターンのリスト
    # [GEMSTONE_MINE, UNDISCOVERED_PARADISE, WILD_CANTOR, CHROME_MOX, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    deck_patterns = [
        [4, 0, 1, 4, 3, 3],  # ベースデッキ
        [4, 1, 0, 4, 3, 3],
        [4, 0, 1, 4, 4, 2],
        [4, 1, 0, 4, 4, 2],
        [4, 0, 0, 4, 4, 3],
        [4, 0, 0, 4, 4, 4],
        [4, 1, 0, 3, 3, 4],
        [4, 0, 1, 3, 4, 3],
        [4, 1, 0, 3, 4, 3],
        [4, 0, 0, 3, 4, 4],
        [4, 1, 0, 4, 2, 4],
        [4, 1, 1, 2, 4, 3],
        [4, 0, 0, 4, 4, 3],
        [4, 1, 0, 2, 4, 4],
        [4, 0, 1, 2, 4, 4],
        [4, 1, 0, 3, 4, 3],
        [4, 2, 0, 2, 4, 3],
        [4, 0, 1, 2, 4, 4],
        [3, 0, 1, 4, 4, 3],
        [3, 0, 0, 4, 4, 4],
        [3, 0, 1, 3, 4, 4]
    ]
    
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
        deck_name = f"GM{gemstone_count}_UP{paradise_count}_WC{cantor_count}_CM{chrome_count}_BW{wind_count}_VA{valakut_count}"
        
        # デッキとデッキ名を追加
        decks.append(deck)
        deck_names.append(deck_name)
    
    # デッキの枚数とカード構成を確認
    for i, deck in enumerate(decks):
        print(f"Deck {deck_names[i]}: {len(deck)} cards")
        
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
    
    # 比較を実行
    results = analyzer.compare_decks(decks, deck_names, 19, opponent_has_forces, iterations)
    
    # 各結果にカード枚数情報を追加
    for i, result in enumerate(results):
        gemstone_count, paradise_count, cantor_count, chrome_count, wind_count, valakut_count = deck_patterns[i]
        result['GEMSTONE_MINE'] = gemstone_count
        result['UNDISCOVERED_PARADISE'] = paradise_count
        result['WILD_CANTOR'] = cantor_count
        result['CHROME_MOX'] = chrome_count
        result['BORNE_UPON_WIND'] = wind_count
        result['VALAKUT_AWAKENING'] = valakut_count
        
        # deck_nameを削除
        if 'deck_name' in result:
            del result['deck_name']
    
    results.sort(key=lambda x: x['win_rate'], reverse=False)
    
    # ソート後の結果を表示
    print("\nDeck Comparison Results (sorted by win rate):")
    for i, result in enumerate(results):
        gemstone_count = result['GEMSTONE_MINE']
        paradise_count = result['UNDISCOVERED_PARADISE']
        cantor_count = result['WILD_CANTOR']
        chrome_count = result['CHROME_MOX']
        wind_count = result['BORNE_UPON_WIND']
        valakut_count = result['VALAKUT_AWAKENING']
        
        deck_desc = f"GM{gemstone_count}_UP{paradise_count}_WC{cantor_count}_CM{chrome_count}_BW{wind_count}_VA{valakut_count}"
        print(f"Deck {i+1}: {deck_desc}, Win Rate: {result['win_rate']:.1f}%")
        if opponent_has_forces and 'necro_resolve_rate' in result:
            print(f"  Necro Resolve Rate: {result['necro_resolve_rate']:.1f}%")
    
    # 結果をCSVに保存
    save_results_to_csv('compare_deck_variations', results, DEFAULT_PRIORITY_FIELDS)
    
    return results

def analyze_draw_counts(analyzer: DeckAnalyzer, iterations: int = 100000):
    """
    最適なデッキ（BEST_DECK_PATH）に対してドロー数分析を実行する関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        
    Returns:
        各ドロー数ごとの結果のリスト
    """
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
    
    print(f"\nAnalyzing best deck: {BEST_DECK_PATH}")
    deck = create_deck(BEST_DECK_PATH)
    deck_name = get_filename_without_extension(BEST_DECK_PATH)

    results = analyzer.run_draw_count_analysis(deck, initial_hand, min_draw=10, max_draw=19, iterations=iterations)
    
    # 各結果にデッキ名を追加
    for result in results:
        result['deck_name'] = deck_name
    
    save_results_to_csv('analyze_draw_counts', results, DEFAULT_PRIORITY_FIELDS)
    
    return results

def compare_initial_hands(analyzer: DeckAnalyzer, iterations: int = 1000000):
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
    '''
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
    '''
    one_card_additions = [
        DARK_RITUAL,
        CABAL_RITUAL
    ]
    
    for card in one_card_additions:
        hand = base_hand.copy()
        hand.append(card)
        initial_hands.append(hand)
    
    # 2枚加える
    '''
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
    '''
    
    # ベストなデッキを使用
    deck = create_deck(BEST_DECK_PATH)
    results = analyzer.compare_initial_hands(deck, initial_hands, 19, iterations)
    
    save_results_to_csv('compare_initial_hands', results, DEFAULT_PRIORITY_FIELDS)
    
    return results

def compare_chancellor_decks(analyzer: DeckAnalyzer, iterations: int = 1000000):
    """
    Chancellor of the Annexを4枚追加したデッキバリエーションを比較する関数
    
    基本デッキ: decks/wind3_valakut3_cantor0_paradise1.txt
    - Chancellor of the Annexを4枚追加
    - 指定されたパターンに従って4枚のカードを抜いて60枚にする
    - 各パターンに対してcompare_decksを実行
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
    
    # 比較を実行
    results = analyzer.compare_decks(decks, deck_names, 19, iterations)
    
    # win_rateの昇順でソート（最も低いものが先頭に来るように）
    results.sort(key=lambda x: x['win_rate'])
    
    # ソート後の結果を表示
    print("\nDeck Comparison Results (sorted by win rate):")
    for result in results:
        print(f"Deck: {result['deck_name']}, Win Rate: {result['win_rate']:.1f}%")
    
    # 結果をCSVに保存
    save_results_to_csv('compare_chancellor_decks', results, DEFAULT_PRIORITY_FIELDS)
    
    return results

def compare_keep_cards_for_hand(analyzer: DeckAnalyzer, initial_hand: list[str], deck_path: str = 'decks/wind3_valakut3_cantor0_paradise1.txt', draw_count: int = 19, iterations: int = 100000):
    """
    特定の初期手札に対してキープするカードを比較する関数
    
    初期手札からGemstone Mine, Dark Ritual, Necrodominanceの3枚を除いた残りのカードについて、
    各カードを1枚だけ手札に残し、他をデッキボトムに送る戦略を比較します。
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        initial_hand: 初期手札
        deck_path: デッキファイルのパス
        draw_count: ドロー数
        iterations: シミュレーション回数
        
    Returns:
        各戦略の結果のリスト
    """
    # デッキを読み込む
    deck = create_deck(deck_path)
    
    # 結果を格納するリスト
    results = []
    
    # 必須の3枚を取り除いたカードリストを作成
    core_cards = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
    remaining_cards = initial_hand.copy()
    for card in core_cards:
        remaining_cards.remove(card)
    
    # ユニークなカードのセットを作成
    unique_cards = set(remaining_cards)
    
    # 初期手札の内容を文字列化してファイル名に使用
    hand_str = '_'.join([card.split(' ')[0] for card in initial_hand if card not in core_cards])
    if len(hand_str) > 50:  # ファイル名が長すぎる場合は短くする
        hand_str = hand_str[:50]
    
    print(f"\nAnalyzing initial hand: {', '.join(initial_hand)}")
    
    # 各カードを1枚だけ手札に残す戦略をループ
    for keep_card in unique_cards:
        # デッキボトムに送るカードリストを作成
        bottom_list = remaining_cards.copy()
        bottom_list.remove(keep_card)
        
        print(f"Testing strategy: Keep {keep_card}, Bottom: {', '.join(bottom_list)}")
        
        # シミュレーション実行
        stats = analyzer.run_multiple_simulations_with_initial_hand(
            deck=deck, 
            initial_hand=initial_hand, 
            bottom_list=bottom_list, 
            draw_count=draw_count, 
            cast_summoners_pact=True, 
            iterations=iterations
        )
        
        # 手札に残したカードをラベル付け
        stats['kept_card'] = keep_card
        stats['bottom_cards'] = ', '.join(bottom_list)
        stats['initial_hand'] = ', '.join(initial_hand)
        
        results.append(stats)
    
    # すべてのカードをデッキボトムに送る戦略も追加
    bottom_list = remaining_cards.copy()
    print(f"Testing strategy: Keep None, Bottom: {', '.join(bottom_list)}")
    stats = analyzer.run_multiple_simulations_with_initial_hand(deck, initial_hand, bottom_list, draw_count, iterations)
    stats['kept_card'] = 'None'
    stats['bottom_cards'] = ', '.join(bottom_list)
    stats['initial_hand'] = ', '.join(initial_hand)
    results.append(stats)
    
    results.sort(key=lambda x: x['win_rate'], reverse=False)
    
    # 結果を表示
    print("\nMulligan Strategy Comparison Results (sorted by win rate):")
    for result in results:
        print(f"Kept Card: {result['kept_card']}, Bottom Cards: {result['bottom_cards']}, Win Rate: {result['win_rate']:.1f}%")
    
    # 結果をCSVに保存
    filename = f"compare_keep_cards_{hand_str}"
    save_results_to_csv(filename, results, DEFAULT_PRIORITY_FIELDS)
    
    return results

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


if __name__ == "__main__":
    analyzer = DeckAnalyzer()
    
    print("シミュレーション開始: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    start_time = time.time()
    
    # Summoner's Pactをキャストするかどうかの戦略を比較
    print("\n=== compare_summoners_pact_strategies ===")
    compare_summoners_pact_strategies(analyzer)

    #compare_decks(analyzer, DEFAULT_ITERATIONS)
    #analyze_draw_counts(analyzer)
    #compare_initial_hands(analyzer, DEFAULT_ITERATIONS)
    #compare_chancellor_decks(analyzer, DEFAULT_ITERATIONS)
    #compare_chancellor_decks_against_counterspells(analyzer, DEFAULT_ITERATIONS)
    '''
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, BORNE_UPON_WIND, MANAMORPHOSE, VALAKUT_AWAKENING]
    compare_keep_cards_for_hand(analyzer, initial_hand)
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, LOTUS_PETAL, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    compare_keep_cards_for_hand(analyzer, initial_hand)
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, LOTUS_PETAL, BORNE_UPON_WIND, MANAMORPHOSE]
    compare_keep_cards_for_hand(analyzer, initial_hand)
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, LOTUS_PETAL, MANAMORPHOSE, VALAKUT_AWAKENING]
    compare_keep_cards_for_hand(analyzer, initial_hand)
    '''
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 経過時間を時間、分、秒に変換
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print("\n実行時間:")
    print(f"合計: {elapsed_time:.2f}秒")
    print(f"時間表示: {int(hours)}時間 {int(minutes)}分 {seconds:.2f}秒")
    print("シミュレーション終了: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
