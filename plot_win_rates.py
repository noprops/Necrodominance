# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import os

# CSVファイルを読み込む
csv_path = 'results/compare_decks_with_varying_draw_counts.csv'
df = pd.read_csv(csv_path)

# デッキ名ごとにデータをグループ化
deck1_data = df[df['deck_name'] == 'wind4_valakut2_cantor1'].sort_values('draw_count', ascending=False)
deck2_data = df[df['deck_name'] == 'wind3_valakut3_cantor1'].sort_values('draw_count', ascending=False)

# グラフの設定
plt.figure(figsize=(12, 8))
plt.plot(deck1_data['draw_count'], deck1_data['win_rate'], 'b-o', label='wind4_valakut2_cantor1', linewidth=2)
plt.plot(deck2_data['draw_count'], deck2_data['win_rate'], 'r-o', label='wind3_valakut3_cantor1', linewidth=2)

# グラフのラベルと凡例
plt.title('Win Rate by Draw Count', fontsize=16)
plt.xlabel('Draw Count', fontsize=14)
plt.ylabel('Win Rate (%)', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)

# X軸の設定（19から10まで）
plt.xticks(range(10, 20))

# Y軸の範囲を0-100%に設定
plt.ylim(0, 100)

# 各データポイントに値を表示
for i, row in deck1_data.iterrows():
    plt.text(row['draw_count'], row['win_rate'] + 1, f"{row['win_rate']:.1f}%", 
             ha='center', va='bottom', color='blue', fontweight='bold')

for i, row in deck2_data.iterrows():
    plt.text(row['draw_count'], row['win_rate'] - 1, f"{row['win_rate']:.1f}%", 
             ha='center', va='top', color='red', fontweight='bold')

# 結果ディレクトリが存在しない場合は作成
results_dir = 'results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# グラフを保存
plt.savefig('results/win_rate_comparison.png', dpi=300, bbox_inches='tight')
plt.savefig('results/win_rate_comparison.pdf', bbox_inches='tight')

print("グラフを保存しました: results/win_rate_comparison.png, results/win_rate_comparison.pdf")

# グラフを表示（必要に応じてコメントアウト）
plt.show()
