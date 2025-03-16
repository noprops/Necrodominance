from game_state import *
from deck_utils import get_filename_without_extension, create_deck, save_results_to_csv
from deck_analyzer import DeckAnalyzer
import time
import datetime

# デッキパスの定義
DECK_PATHS = [
    'decks/wind4_valakut2_cantor1_paradise0.txt',
    'decks/wind4_valakut2_cantor0_paradise1.txt',
    'decks/wind3_valakut3_cantor1_paradise0.txt',
    'decks/wind3_valakut3_cantor0_paradise1.txt'
]

# フィールドの優先順位リスト（基本とマリガン回数ごとの統計情報を含む）
DEFAULT_PRIORITY_FIELDS = [
    'GEMSTONE_MINE', 'UNDISCOVERED_PARADISE', 'WILD_CANTOR', 'CHROME_MOX', 'BORNE_UPON_WIND', 'VALAKUT_AWAKENING',
    'initial_hand', 'kept_card', 'bottom_cards', 'draw_count', 'total_games', 'win_rate', 
    'cast_necro_rate', 'total_cast_necro', 'necro_resolve_count', 'necro_countered_count', 'necro_resolve_rate', 'win_after_necro_resolve_rate',
    'total_wins', 'total_losses', 'wins', 'losses', 'failed_necro_count', 'loss_reasons',
    # wins_mull0, wins_mull1, ...
    'wins_mull0', 'wins_mull1', 'wins_mull2', 'wins_mull3', 'wins_mull4',
    # losses_mull0, losses_mull1, ...
    'losses_mull0', 'losses_mull1', 'losses_mull2', 'losses_mull3', 'losses_mull4',
    # cast_necro_mull0, cast_necro_mull1, ...
    'cast_necro_mull0', 'cast_necro_mull1', 'cast_necro_mull2', 'cast_necro_mull3', 'cast_necro_mull4',
    # win_rate_mull0, win_rate_mull1, ...
    'win_rate_mull0', 'win_rate_mull1', 'win_rate_mull2', 'win_rate_mull3', 'win_rate_mull4'
]

# 既存のDeckAnalyzerクラスのメソッドを使用するため、これらの関数は不要

def compare_initial_hands(analyzer: DeckAnalyzer, iterations: int = 200000):
    """
    プリセットされた初期手札のリストを比較する関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        
    Returns:
        各初期手札の結果のリスト
    """
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
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CHROME_MOX],
        [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, GEMSTONE_MINE]
    ]

    deck = create_deck('decks/wind3_valakut3_cantor0_paradise1.txt')
    results = analyzer.compare_initial_hands(deck, initial_hands, 19, iterations)
    
    save_results_to_csv('compare_initial_hands', results, DEFAULT_PRIORITY_FIELDS)
    
    return results

def create_custom_deck(gemstone_count: int, paradise_count: int, cantor_count: int, 
                      chrome_count: int, wind_count: int, valakut_count: int) -> list:
    """
    指定されたカード枚数でデッキを作成する関数
    
    Args:
        gemstone_count: GEMSTONE_MINEの枚数
        paradise_count: UNDISCOVERED_PARADISEの枚数
        cantor_count: WILD_CANTORの枚数
        chrome_count: CHROME_MOXの枚数
        wind_count: BORNE_UPON_WINDの枚数
        valakut_count: VALAKUT_AWAKENINGの枚数
        
    Returns:
        作成されたデッキ（カード名のリスト）
    """
    # ベースデッキを読み込む
    base_deck_path = 'decks/wind3_valakut3_cantor1_paradise0.txt'
    base_deck = create_deck(base_deck_path)

    remove_cards = [GEMSTONE_MINE, UNDISCOVERED_PARADISE, WILD_CANTOR, CHROME_MOX, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    new_deck = [card for card in base_deck if card not in remove_cards]
    
    # 指定されたカードを追加
    new_deck.extend([GEMSTONE_MINE] * gemstone_count)
    new_deck.extend([UNDISCOVERED_PARADISE] * paradise_count)
    new_deck.extend([WILD_CANTOR] * cantor_count)
    new_deck.extend([CHROME_MOX] * chrome_count)
    new_deck.extend([BORNE_UPON_WIND] * wind_count)
    new_deck.extend([VALAKUT_AWAKENING] * valakut_count)
    
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
        [4, 0, 1, 3, 4, 3],
        [4, 1, 0, 3, 4, 3],
        [4, 0, 0, 3, 4, 4],
        [4, 1, 1, 2, 4, 3],
        [4, 1, 0, 2, 4, 4],
        [4, 0, 1, 2, 4, 4],
        [4, 2, 0, 2, 4, 3],
        [3, 0, 1, 4, 4, 3],
        [3, 0, 0, 4, 4, 4],
        [3, 0, 1, 3, 4, 4]
    ]
    
    # 各パターンに対してデッキを作成
    for pattern in deck_patterns:
        gemstone_count, paradise_count, cantor_count, chrome_count, wind_count, valakut_count = pattern
        
        # デッキを作成
        deck = create_custom_deck(
            gemstone_count, paradise_count, cantor_count, 
            chrome_count, wind_count, valakut_count
        )
        
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
    プリセットされたデッキのリストに対してドロー数分析を実行する関数
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        
    Returns:
        各デッキ・各ドロー数ごとの結果のリスト
    """
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
    all_results = []
    
    for deck_path in DECK_PATHS:
        print(f"\nAnalyzing deck: {deck_path}")
        deck = create_deck(deck_path)
        deck_name = get_filename_without_extension(deck_path)
        
        # 100,000回のイテレーションで実行
        results = analyzer.run_draw_count_analysis(deck, initial_hand, min_draw=10, max_draw=19, iterations=iterations)
        
        # 各結果にデッキ名を追加
        for result in results:
            result['deck_name'] = deck_name
            all_results.append(result)
    
    save_results_to_csv('analyze_draw_counts', all_results, DEFAULT_PRIORITY_FIELDS)
    
    return all_results

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
        [UNDISCOVERED_PARADISE] * 1 + [CHROME_MOX] * 1 + [SUMMONERS_PACT] * 1 + [UNDISCOVERED_PARADISE] * 0 + [VALAKUT_AWAKENING] * 1,  # 注: UNDISCOVEREDは1枚しかないので2枚は指定できない
        
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
        stats = analyzer.run_multiple_simulations_with_initial_hand(deck, initial_hand, bottom_list, draw_count, iterations)
        
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
    iterations = 10000
    analyzer = DeckAnalyzer()
    
    print("シミュレーション開始: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    start_time = time.time()
    
    compare_decks(analyzer, iterations)
    #analyze_draw_counts(analyzer, iterations=100000)
    #compare_initial_hands(analyzer, iterations)
    #compare_chancellor_decks(analyzer, iterations)
    #compare_chancellor_decks_against_counterspells(analyzer, iterations)
    #compare_chancellor_decks_against_counterspells(analyzer, iterations=10000)
    '''
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, BORNE_UPON_WIND, MANAMORPHOSE, VALAKUT_AWAKENING]
    compare_keep_cards_for_hand(analyzer, initial_hand, iterations=iterations)
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, LOTUS_PETAL, BORNE_UPON_WIND, VALAKUT_AWAKENING]
    compare_keep_cards_for_hand(analyzer, initial_hand, iterations=iterations)
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, LOTUS_PETAL, BORNE_UPON_WIND, MANAMORPHOSE]
    compare_keep_cards_for_hand(analyzer, initial_hand, iterations=iterations)
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, LOTUS_PETAL, LOTUS_PETAL, MANAMORPHOSE, VALAKUT_AWAKENING]
    compare_keep_cards_for_hand(analyzer, initial_hand, iterations=iterations)
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
