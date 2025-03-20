from game_state import *
from deck_utils import get_filename_without_extension, create_deck, save_results_to_csv, DEFAULT_PRIORITY_FIELDS
from deck_analyzer import DeckAnalyzer
from collections import defaultdict
import time
import datetime

BEST_DECK_PATH = 'decks/gemstone4_paradise0_cantor0_chrome4_wind4_valakut3.txt'

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

def analyze_summoners_pact_casting(analyzer: DeckAnalyzer, initial_hand: list[str], bottom_list: list[str] = [], deck_path: str = BEST_DECK_PATH, draw_count: int = 19, iterations: int = 100000):
    """
    Summoner's Pactをキャストするかどうかを分析する関数
    
    指定された初期手札を使用して、Summoner's Pactをキャストする場合としない場合で勝率を比較します。
    DeckAnalyzerクラスを使用してシミュレーションを実行します。
    
    Args:
        analyzer: DeckAnalyzerインスタンス
        initial_hand: 初期手札
        bottom_list: デッキボトムに戻すカードのリスト
        deck_path: デッキファイルのパス
        draw_count: ドロー数
        iterations: シミュレーション回数
        
    Returns:
        比較結果の辞書
    """
    # デッキを読み込む
    deck = create_deck(deck_path)
    deck_name = get_filename_without_extension(deck_path)
    
    # 結果を格納するリスト
    results = []
    
    print(f"\nAnalyzing Summoner's Pact casting strategies for deck: {deck_path}")
    print(f"Initial hand: {', '.join(initial_hand)}")
    
    # Summoner's Pactをキャストしない場合
    print("Testing strategy: Do not cast Summoner's Pact")
    
    # DeckAnalyzerのrun_multiple_simulations_with_initial_hand関数を使用
    stats_without_cast = analyzer.run_multiple_simulations_with_initial_hand(deck, initial_hand, bottom_list, draw_count, iterations)
    
    # 結果を追加
    result_without_cast = stats_without_cast.copy()
    result_without_cast['initial_hand'] = ', '.join(initial_hand)
    result_without_cast['bottom_cards'] = ', '.join(bottom_list) if bottom_list else ''
    result_without_cast['cast_summoners_pact_before_draw'] = False
    
    # 必要なフィールドが空白にならないようにする
    if 'wins' in result_without_cast and 'total_wins' not in result_without_cast:
        result_without_cast['total_wins'] = result_without_cast['wins']
    
    if 'losses' in result_without_cast and 'total_losses' not in result_without_cast:
        result_without_cast['total_losses'] = result_without_cast['losses']
    
    if 'total_cast_necro' not in result_without_cast and 'cast_necro_count' in result_without_cast:
        result_without_cast['total_cast_necro'] = result_without_cast['cast_necro_count']
    elif 'cast_necro_count' not in result_without_cast and 'total_cast_necro' in result_without_cast:
        result_without_cast['cast_necro_count'] = result_without_cast['total_cast_necro']
    
    results.append(result_without_cast)
    
    # Summoner's Pactをキャストする場合
    print("Testing strategy: Cast Summoner's Pact")
    
    # DeckAnalyzerのrun_multiple_simulations_with_initial_hand関数を使用
    # ただし、GameStateのcast_summoners_pact_before_draw=Trueを設定するために
    # 一時的にanalyzer.gameの設定を変更
    
    # 元の設定を保存
    original_debug_print = analyzer.game.debug_print
    
    # デバッグ出力を無効化
    analyzer.game.debug_print = False
    
    # Summoner's Pactをキャストする場合のシミュレーション用の関数を定義
    def run_with_summoners_pact(deck, initial_hand, bottom_list, draw_count):
        # デッキをコピーしてシャッフル
        deck_copy = deck.copy()
        random.shuffle(deck_copy)
        
        # ゲームを実行（cast_summoners_pact_before_draw=True）
        return analyzer.game.run_with_initial_hand(deck_copy, initial_hand, bottom_list, draw_count, cast_summoners_pact_before_draw=True)
    
    # シミュレーション実行
    wins_with_cast = 0
    losses_with_cast = 0
    cast_necro_count = 0
    failed_necro_count = 0
    loss_reasons = defaultdict(int)
    
    for _ in range(iterations):
        # ゲームをリセット
        analyzer.game.reset_game()
        
        # Summoner's Pactをキャストするシミュレーションを実行
        result = run_with_summoners_pact(deck, initial_hand, bottom_list, draw_count)
        
        # 結果を集計
        if result:
            wins_with_cast += 1
        else:
            losses_with_cast += 1
            
            # 負けた理由を記録
            if analyzer.game.loss_reason == FALIED_NECRO:
                failed_necro_count += 1
            
            if analyzer.game.loss_reason:
                loss_reasons[analyzer.game.loss_reason] += 1
            else:
                loss_reasons["Unknown"] += 1
        
        # Necroを唱えたかどうかをカウント
        if analyzer.game.did_cast_necro:
            cast_necro_count += 1
    
    # 元の設定に戻す
    analyzer.game.debug_print = original_debug_print
    
    # 勝率と各種統計情報を計算
    win_rate_with_cast = wins_with_cast / iterations * 100
    cast_necro_rate = cast_necro_count / iterations * 100
    win_after_necro_resolve_rate = wins_with_cast / cast_necro_count * 100 if cast_necro_count > 0 else 0
    
    # 結果を追加
    result_with_cast = {
        'initial_hand': ', '.join(initial_hand),
        'bottom_cards': ', '.join(bottom_list) if bottom_list else '',
        'cast_summoners_pact_before_draw': True,
        'draw_count': draw_count,
        'total_games': iterations,
        'total_wins': wins_with_cast,
        'wins': wins_with_cast,
        'total_losses': losses_with_cast,
        'losses': losses_with_cast,
        'win_rate': win_rate_with_cast,
        'cast_necro_rate': cast_necro_rate,
        'total_cast_necro': cast_necro_count,
        'cast_necro_count': cast_necro_count,
        'failed_necro_count': failed_necro_count,
        'win_after_necro_resolve_rate': win_after_necro_resolve_rate
    }
    
    # 各loss_reasonごとの欄を追加
    for reason in [
        FALIED_NECRO, FAILED_NECRO_COUNTERED, 
        FAILED_CAST_BOTH_WITH_WIND_AND_VALAKUT, FAILED_CAST_BOTH_WITH_WIND_WITHOUT_VALAKUT, 
        FAILED_CAST_BOTH_WITHOUT_WIND_WITH_VALAKUT, FAILED_CAST_BOTH_WITHOUT_WIND_AND_VALAKUT,
        CAST_VALAKUT_FAILED_WIND_WITH_WIND, CAST_VALAKUT_FAILED_WIND_WITHOUT_WIND,
        CAST_WIND_FAILED_TENDRILS_WITH_BESEECH_OR_TENDRILS, CAST_WIND_FAILED_TENDRILS_WITHOUT_BESEECH_OR_TENDRILS
    ]:
        result_with_cast[reason] = loss_reasons[reason]
    results.append(result_with_cast)
    
    # 勝率の差を計算
    win_rate_without_cast = stats_without_cast['win_rate']
    win_rate_diff = win_rate_with_cast - win_rate_without_cast
    
    # 結果を表示
    print("\nSummoner's Pact Casting Strategy Comparison Results:")
    print(f"Do not cast Summoner's Pact: Win Rate = {win_rate_without_cast:.2f}%")
    print(f"Cast Summoner's Pact: Win Rate = {win_rate_with_cast:.2f}%")
    print(f"Difference (Cast - Do not cast): {win_rate_diff:.2f}%")
    
    # 勝率が高い方の戦略を表示
    if win_rate_with_cast > win_rate_without_cast:
        print("Conclusion: Casting Summoner's Pact is better")
    else:
        print("Conclusion: Not casting Summoner's Pact is better")
    
    # 初期手札と底札からファイル名を生成
    hand_str = '_'.join([card.split(' ')[0] for card in initial_hand])
    bottom_str = '_bottom_' + '_'.join([card.split(' ')[0] for card in bottom_list]) if bottom_list else ''
    filename = f"analyze_summoners_pact_{hand_str}{bottom_str}"
    
    # 結果をCSVに保存
    save_results_to_csv(filename, results, DEFAULT_PRIORITY_FIELDS)
    
    return {
        'win_rate_without_cast': win_rate_without_cast,
        'win_rate_with_cast': win_rate_with_cast,
        'win_rate_diff': win_rate_diff,
        'better_strategy': 'Cast Summoner\'s Pact' if win_rate_with_cast > win_rate_without_cast else 'Do not cast Summoner\'s Pact'
    }

if __name__ == "__main__":
    iterations = 100000
    analyzer = DeckAnalyzer()
    
    print("シミュレーション開始: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    start_time = time.time()
    
    #compare_decks(analyzer, iterations)
    #analyze_draw_counts(analyzer, iterations=100000)
    compare_initial_hands(analyzer, iterations)
    #compare_chancellor_decks(analyzer, iterations)
    #compare_chancellor_decks_against_counterspells(analyzer, iterations)
    #compare_chancellor_decks_against_counterspells(analyzer, iterations=10000)

    #analyze_summoners_pact_casting(analyzer, initial_hand=[GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT], iterations= 10000)
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
