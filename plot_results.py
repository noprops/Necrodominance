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
    """
    csv_path = 'results/compare_decks.csv'
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping mulligan stats plot.")
        return
    
    # CSVファイルを読み込む
    df = pd.read_csv(csv_path)
    
    # wind3_valakut3_cantor1の行のデータを抽出
    deck_data = df[df['deck_name'] == 'wind3_valakut3_cantor1']
    
    if deck_data.empty:
        print("Error: No data found for wind3_valakut3_cantor1")
        return
    
    # 必要なデータを抽出
    mulligan_counts = range(5)  # 0から4までのマリガン回数
    wins_data = [deck_data[f'wins_mull{i}'].values[0] for i in mulligan_counts]
    cast_necro_data = [deck_data[f'cast_necro_mull{i}'].values[0] for i in mulligan_counts]
    win_rate_data = [deck_data[f'win_rate_mull{i}'].values[0] for i in mulligan_counts]
    
    # グラフの設定
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # X軸の位置を設定
    x = np.arange(len(mulligan_counts))
    width = 0.35  # バーの幅
    
    # 棒グラフを作成
    rects1 = ax.bar(x - width/2, wins_data, width, label='Wins')
    rects2 = ax.bar(x + width/2, cast_necro_data, width, label='Cast Necro')
    
    # グラフのタイトルと軸ラベルを設定
    ax.set_title('Mulligan Statistics for wind3_valakut3_cantor1', fontsize=16)
    ax.set_xlabel('Mulligan Count', fontsize=14)
    ax.set_ylabel('Count', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(mulligan_counts)
    ax.legend()
    
    # 勝率を棒グラフの上に表示
    for i, (rect1, rect2) in enumerate(zip(rects1, rects2)):
        # 高い方の棒の上に表示
        height = max(rect1.get_height(), rect2.get_height())
        win_rate = win_rate_data[i]
        ax.annotate(f'{win_rate:.1f}%',
                    xy=(rect1.get_x() + rect1.get_width() / 2, height),
                    xytext=(0, 3),  # 3ポイント上
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12)
    
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
    """
    csv_path = 'results/analyze_draw_counts.csv'
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping draw count analysis plot.")
        return
    
    # CSVファイルを読み込む
    df = pd.read_csv(csv_path)
    
    # ドロー数でソート（降順）- 左から19~10になるように
    df = df.sort_values('draw_count', ascending=False)
    
    # グラフの設定
    plt.figure(figsize=(12, 8))
    
    # 折れ線グラフを作成
    plt.plot(df['draw_count'], df['win_rate'], 'b-o', linewidth=2)
    
    # グラフのタイトルと軸ラベルを設定
    plt.title('Win Rate by Draw Count', fontsize=16)
    plt.xlabel('Draw Count', fontsize=14)
    plt.ylabel('Win Rate (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # X軸の設定（左から19から10まで）
    plt.xticks(range(19, 9, -1))
    
    # Y軸の範囲を0-100%に設定
    plt.ylim(0, 100)
    
    # 各データポイントに値を表示
    for i, row in df.iterrows():
        plt.text(row['draw_count'], row['win_rate'] + 1, f"{row['win_rate']:.1f}%", 
                 ha='center', va='bottom', fontweight='bold')
    
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
