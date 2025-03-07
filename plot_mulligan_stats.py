# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# imgsフォルダが存在しない場合は作成
if not os.path.exists('imgs'):
    os.makedirs('imgs')

# CSVファイルを読み込む
df = pd.read_csv('results/compare_decks.csv')

# wind3_valakut3_cantor1の行のデータを抽出
deck_data = df[df['deck_name'] == 'wind3_valakut3_cantor1']

if deck_data.empty:
    print("Error: No data found for wind3_valakut3_cantor1")
    exit(1)

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

# グラフを表示（オプション）
# plt.show()
