import os
import csv
from card_constants import *

# フィールドの優先順位リスト（基本とマリガン回数ごとの統計情報を含む）
DEFAULT_PRIORITY_FIELDS = [
    'pattern_name', 
    # カード枚数情報（pattern_nameの直後に配置）
    CHANCELLOR_OF_ANNEX, GEMSTONE_MINE, CHROME_MOX, SUMMONERS_PACT, 
    BORNE_UPON_WIND, VALAKUT_AWAKENING, CABAL_RITUAL, BESEECH_MIRROR,
    UNDISCOVERED_PARADISE, WILD_CANTOR,
    # その他の情報
    'initial_hand', 'bottom_list', 'cast_summoners_pact', 'cast_summoners_pact_before_draw',
    'deck_name', 'deck_type', 'kept_card', 'bottom_cards', 
    'draw_count', 'total_games', 'win_rate', 
    'cast_necro_rate', 'total_cast_necro', 'cast_necro_count', 'necro_resolve_count', 
    'necro_countered_count', 'necro_resolve_rate', 'win_after_necro_resolve_rate',
    'total_wins', 'total_losses', 'wins', 'losses', 'failed_necro_count',
    FALIED_NECRO, FAILED_NECRO_COUNTERED, 
    FAILED_CAST_BOTH, CAST_VALAKUT_FAILED_WIND, CAST_WIND_FAILED_TENDRILS,
    FAILED_CAST_BOTH_WITH_WIND_AND_VALAKUT, FAILED_CAST_BOTH_WITH_WIND_WITHOUT_VALAKUT, 
    FAILED_CAST_BOTH_WITHOUT_WIND_WITH_VALAKUT, FAILED_CAST_BOTH_WITHOUT_WIND_AND_VALAKUT,
    CAST_VALAKUT_FAILED_WIND_WITH_WIND, CAST_VALAKUT_FAILED_WIND_WITHOUT_WIND,
    CAST_WIND_FAILED_TENDRILS_WITH_BESEECH_OR_TENDRILS, CAST_WIND_FAILED_TENDRILS_WITHOUT_BESEECH_OR_TENDRILS,
    # wins_mull0, wins_mull1, ...
    'wins_mull0', 'wins_mull1', 'wins_mull2', 'wins_mull3', 'wins_mull4',
    # losses_mull0, losses_mull1, ...
    'losses_mull0', 'losses_mull1', 'losses_mull2', 'losses_mull3', 'losses_mull4',
    # cast_necro_mull0, cast_necro_mull1, ...
    'cast_necro_mull0', 'cast_necro_mull1', 'cast_necro_mull2', 'cast_necro_mull3', 'cast_necro_mull4',
    # win_rate_mull0, win_rate_mull1, ...
    'win_rate_mull0', 'win_rate_mull1', 'win_rate_mull2', 'win_rate_mull3', 'win_rate_mull4'
]

def get_filename_without_extension(file_path: str) -> str:
    """
    パスから拡張子を除いたファイル名を取得する
    
    Args:
        file_path: ファイルパス
    
    Returns:
        拡張子を除いたファイル名
    """
    base_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_name)[0]
    return name_without_ext

def create_deck(deck_path: str) -> list[str]:
    """
    デッキリストからデッキを作成する
    
    Args:
        deck_path: デッキリストのファイルパス
    
    Returns:
        デッキ（カード名のリスト）
    """
    # Load decklist from text file
    deck = []
    with open(deck_path, 'r') as file:
        for line in file:
            # Stop reading at empty line (before sideboard)
            if line.strip() == "":
                break
            # Get count and card name from each line
            count, *card_name = line.strip().split(' ')
            card_name = ' '.join(card_name)
            # カードの枚数が0より大きい場合のみデッキに追加
            count_int = int(count)
            if count_int > 0:
                deck.extend([card_name] * count_int)
    
    return deck

def save_results_to_csv(filename: str, results: list[dict], priority_fields: list[str] = None, folder_path: str = 'results') -> None:
    """
    結果をCSVファイルに保存する
    
    Args:
        filename: 保存するファイル名（拡張子なし）
        results: 保存する結果のリスト（各要素は辞書）
        priority_fields: フィールドの優先順位リスト（指定されたフィールドが左から順に並ぶ）
        folder_path: 保存先のフォルダパス（デフォルトは'results'）
    """
    # 指定したフォルダが存在しない場合は作成
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # ファイルパスを構築
    filepath = os.path.join(folder_path, f"{filename}.csv")
    
    # 全てのキーを収集
    all_keys = set()
    for result in results:
        all_keys.update(result.keys())
    
    # 優先フィールドが指定されていない場合はデフォルトを使用
    if priority_fields is None:
        priority_fields = DEFAULT_PRIORITY_FIELDS
    
    # 優先フィールドを先に追加
    fieldnames = [field for field in priority_fields if field in all_keys]
    
    # 残りのフィールドを追加（優先フィールドに含まれていないもの）
    remaining_fields = sorted(key for key in all_keys if key not in fieldnames)
    fieldnames.extend(remaining_fields)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)
    
    print(f"\nResults saved to {filepath}")
