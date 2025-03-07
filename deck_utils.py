import os
import csv

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

def save_results_to_csv(filename: str, results: list[dict], priority_fields: list[str] = None) -> None:
    """
    結果をCSVファイルに保存する
    
    Args:
        filename: 保存するファイル名（拡張子なし）
        results: 保存する結果のリスト（各要素は辞書）
        priority_fields: フィールドの優先順位リスト（指定されたフィールドが左から順に並ぶ）
    """
    # resultsフォルダが存在しない場合は作成
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # ファイルパスを構築
    filepath = os.path.join(results_dir, f"{filename}.csv")
    
    # 全てのキーを収集
    all_keys = set()
    for result in results:
        all_keys.update(result.keys())
    
    # デフォルトの優先フィールド
    default_priority_fields = [
        'deck_name', 'initial_hand', 'draw_count', 'total_games', 
        'wins', 'win_rate', 'cast_necro_count', 'cast_necro_rate', 'win_after_necro_rate'
    ]
    
    # 優先フィールドが指定されていない場合はデフォルトを使用
    if priority_fields is None:
        priority_fields = default_priority_fields
    
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
