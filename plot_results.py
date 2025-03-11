# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# imgsフォルダが存在しない場合は作成
if not os.path.exists('imgs'):
    os.makedirs('imgs')

def plot_mulligan_stats():
    """
    results/compare_decks.csvからマリガン統計をグラフ化する関数
    縦軸はマリガン回数ごとのネクロを唱えた確率（%）
    """
    csv_path = 'results/compare_decks.csv'
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping mulligan stats plot.")
        return
    
    # CSVファイルを読み込む
    df = pd.read_csv(csv_path)
    
    deck_name = 'wind3_valakut3_cantor0_paradise1'
    # 指定したデッキの行のデータを抽出
    deck_data = df[df['deck_name'] == deck_name]
    
    if deck_data.empty:
        print(f"Error: No data found for {deck_name}")
        return
    
    # 必要なデータを抽出
    mulligan_counts = range(5)  # 0から4までのマリガン回数
    total_games = deck_data['total_games'].values[0]  # 総ゲーム数
    
    # 各マリガン回数ごとのデータを確率に変換
    wins_data = [deck_data[f'wins_mull{i}'].values[0] / total_games * 100 for i in mulligan_counts]
    cast_necro_data = [deck_data[f'cast_necro_mull{i}'].values[0] / total_games * 100 for i in mulligan_counts]
    win_rate_data = [deck_data[f'win_rate_mull{i}'].values[0] for i in mulligan_counts]
    
    # グラフの設定
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # X軸の位置を設定
    x = np.arange(len(mulligan_counts))
    width = 0.35  # バーの幅
    
    # 棒グラフを作成
    rects1 = ax.bar(x - width/2, wins_data, width, label='Wins (%)')
    rects2 = ax.bar(x + width/2, cast_necro_data, width, label='Cast Necro (%)')
    
    # グラフのタイトルと軸ラベルを設定
    ax.set_title(f'Mulligan Statistics for {deck_name}', fontsize=16)
    ax.set_xlabel('Mulligan Count', fontsize=14)
    ax.set_ylabel('Percentage of Total Games (%)', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(mulligan_counts)
    ax.legend()
    
    # Y軸の範囲を0-100%に設定
    ax.set_ylim(0, 100)
    
    # 各棒グラフの上に値を表示
    for i, (rect1, rect2) in enumerate(zip(rects1, rects2)):
        # Wins の値を表示
        height1 = rect1.get_height()
        ax.annotate(f'{height1:.1f}%',
                    xy=(rect1.get_x() + rect1.get_width() / 2, height1),
                    xytext=(0, 3),  # 3ポイント上
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10)
        
        # Cast Necro の値を表示
        height2 = rect2.get_height()
        ax.annotate(f'{height2:.1f}%',
                    xy=(rect2.get_x() + rect2.get_width() / 2, height2),
                    xytext=(0, 3),  # 3ポイント上
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10)
        
        # 条件付き勝率を表示（Cast Necroした場合の勝率）
        win_rate = win_rate_data[i]
        ax.annotate(f'Win Rate After Necro: {win_rate:.1f}%',
                    xy=(x[i], max(height1, height2)),
                    xytext=(0, 20),  # 20ポイント上（より上に表示）
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=8,
                    color='black')  # 黒色に変更
    
    # グリッドを追加
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # グラフを保存
    plt.tight_layout()
    plt.savefig('imgs/mulligan_stats.png')
    print("Graph saved to imgs/mulligan_stats.png")
    
    # グラフを閉じる
    plt.close()

def plot_draw_count_analysis():
    """
    results/analyze_draw_counts.csvからドロー数ごとの勝率をグラフ化する関数
    複数のデッキに対して折れ線グラフを作成する
    """
    csv_path = 'results/analyze_draw_counts.csv'
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping draw count analysis plot.")
        return
    
    # CSVファイルを読み込む
    df = pd.read_csv(csv_path)
    
    # デッキ名でグループ化
    deck_names = df['deck_name'].unique()
    
    # グラフの設定
    plt.figure(figsize=(12, 8))
    
    # 色のリスト
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k']
    markers = ['o', 's', '^', 'D', 'v', '<', '>']
    
    # 各デッキごとに折れ線グラフを作成
    for i, deck_name in enumerate(deck_names):
        # デッキのデータを抽出
        deck_data = df[df['deck_name'] == deck_name]
        
        # ドロー数でソート（降順）- 左から19~10になるように
        deck_data = deck_data.sort_values('draw_count', ascending=False)
        
        # 色とマーカーを選択（リストの範囲を超えないようにインデックスを調整）
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]
        
        # 折れ線グラフを作成
        plt.plot(deck_data['draw_count'].values, deck_data['win_rate'].values, 
                 f'{color}-{marker}', linewidth=2, label=deck_name)
        
        # 各データポイントに値を表示（デッキごとにさらに大きくずらして表示）
        offset = i * 5.0  # デッキごとに表示位置をさらに大きくずらす
        for _, row in deck_data.iterrows():
            plt.text(row['draw_count'], row['win_rate'] + 1 + offset, 
                     f"{row['win_rate']:.1f}%", 
                     ha='center', va='bottom', fontweight='bold', color=color)
    
    # グラフのタイトルと軸ラベルを設定
    plt.title('Win Rate by Draw Count for Multiple Decks', fontsize=16)
    plt.xlabel('Draw Count', fontsize=14)
    plt.ylabel('Win Rate (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # X軸の設定（左から19から10まで）
    plt.gca().invert_xaxis()  # X軸を反転
    
    # Y軸の範囲を0-100%に設定
    plt.ylim(0, 100)
    
    # 凡例を追加
    plt.legend(fontsize=12)
    
    # グラフを保存
    plt.tight_layout()
    plt.savefig('imgs/draw_count_analysis.png')
    print("Graph saved to imgs/draw_count_analysis.png")
    
    # グラフを閉じる
    plt.close()

if __name__ == "__main__":
    # マリガン統計のグラフを作成
    plot_mulligan_stats()
    
    # ドロー数分析のグラフを作成
    plot_draw_count_analysis()
