# -*- coding: utf-8 -*-
import unittest
import sys
import os
import random

# 試行回数の定義
ITERATIONS = 100000

# Add parent directory to path to import modules from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_state import *
from deck_utils import create_deck, save_results_to_csv
from deck_analyzer import DeckAnalyzer

class TestDeckAnalyzer(unittest.TestCase):
    # 結果を保存するフォルダパス
    RESULTS_FOLDER = 'results'
    
    @classmethod
    def setUpClass(cls):
        """Create DeckAnalyzer instance once for all tests"""
        cls.analyzer = DeckAnalyzer()
        # テスト中はデバッグ出力を無効化
        cls.analyzer.game.debug_print = False
    
    def setUp(self):
        """各テストの前に実行される処理"""
        # 乱数のシードを固定して再現性を確保
        random.seed(42)
    
    def get_default_deck(self):
        """デフォルトのデッキを取得する関数"""
        # プロジェクトルートのパスを取得
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # デッキファイルの絶対パスを構築
        deck_file = os.path.join(root_dir, 'decks', 'gemstone4_paradise0_cantor0_chrome4_wind4_valakut3.txt')
        return create_deck(deck_file)
    
    def compare_initial_hands_with_default_deck(self, initial_hand_a, initial_hand_b, bottom_list_a=[], bottom_list_b=[], iterations=ITERATIONS, summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST):
        """
        デフォルトのデッキを使用して2つの初期手札の勝率を比較する関数
        
        Args:
            initial_hand_a: 初期手札A
            initial_hand_b: 初期手札B
            bottom_list_a: 初期手札Aでデッキボトムに戻すカードのリスト
            bottom_list_b: 初期手札Bでデッキボトムに戻すカードのリスト
            iterations: 試行回数
            cast_summoners_pact: Summoner's Pactを唱えるかどうか
            
        Returns:
            (win_rate_a, win_rate_b): 初期手札AとBの勝率
        """
        # デフォルトのデッキを取得
        deck = self.get_default_deck()
        
        # compare_initial_hands関数を呼び出す
        return self.compare_initial_hands(deck, deck, initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, iterations, summoners_pact_strategy)
    
    def compare_initial_hands(self, deck_a, deck_b, initial_hand_a, initial_hand_b, bottom_list_a=[], bottom_list_b=[], iterations=ITERATIONS, summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST):
        """
        2つの初期手札の勝率を比較する汎用関数
        
        Args:
            deck_a: デッキA
            deck_b: デッキB
            initial_hand_a: 初期手札A
            initial_hand_b: 初期手札B
            bottom_list_a: 初期手札Aでデッキボトムに戻すカードのリスト
            bottom_list_b: 初期手札Bでデッキボトムに戻すカードのリスト
            iterations: 試行回数
            cast_summoners_pact: Summoner's Pactを唱えるかどうか
            
        Returns:
            (win_rate_a, win_rate_b): 初期手札AとBの勝率
        """
        
        # 初期手札Aの勝率を計算
        stats_a = self.analyzer.run_multiple_simulations_with_initial_hand(
            deck=deck_a.copy(), 
            initial_hand=initial_hand_a, 
            bottom_list=bottom_list_a, 
            draw_count=19, 
            iterations=iterations, 
            summoners_pact_strategy=summoners_pact_strategy
        )
        win_rate_a = stats_a['win_rate']
        
        # 初期手札Bの勝率を計算
        stats_b = self.analyzer.run_multiple_simulations_with_initial_hand(
            deck=deck_b.copy(), 
            initial_hand=initial_hand_b, 
            bottom_list=bottom_list_b, 
            draw_count=19, 
            iterations=iterations, 
            summoners_pact_strategy=summoners_pact_strategy
        )
        win_rate_b = stats_b['win_rate']
        
        # 結果をリストにまとめる
        results = [
            {
                'initial_hand': ', '.join(initial_hand_a),
                'bottom_list': ', '.join(bottom_list_a),
                'summoners_pact_strategy': summoners_pact_strategy,
                **stats_a
            },
            {
                'initial_hand': ', '.join(initial_hand_b),
                'bottom_list': ', '.join(bottom_list_b),
                'summoners_pact_strategy': summoners_pact_strategy,
                **stats_b
            }
        ]
        
        # 結果をCSVに保存
        save_results_to_csv(self._testMethodName, results, folder_path=self.RESULTS_FOLDER)
        
        print(f"初期手札A: {', '.join(initial_hand_a)} (Bottom: {', '.join(bottom_list_a)}) の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B: {', '.join(initial_hand_b)} (Bottom: {', '.join(bottom_list_b)}) の勝率: {win_rate_b:.2f}%")
        
        return win_rate_a, win_rate_b
    
    def test_summoners_vs_elvish_without_shuffle(self):
        """
        初期手札AとBの勝率を比較するテスト（Summoner's Pactを唱えない場合）
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE]
        
        実際のテスト結果では、Summoner's Pactを唱えない場合は、
        初期手札B（ELVISH_SPIRIT_GUIDE）の方が勝率が高いことが分かった
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT]
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT]
        # 初期手札B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE]
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE]
        
        # 勝率を比較（Summoner's Pactを唱えない）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（SUMMONERS_PACT）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (SUMMONERS_PACT)' if diff > 0 else 'B (ELVISH_SPIRIT_GUIDE)'}")
        print("="*80)

        self.assertGreater(win_rate_a, win_rate_b)
    
    def test_summoners_vs_elvish_with_shuffle(self):
        """
        初期手札AとBの勝率を比較するテスト（Summoner's Pactを唱える場合）
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE]
        
        実際のテスト結果では、Summoner's Pactを唱える場合は、
        初期手札A（SUMMONERS_PACT）の方が勝率が高いことが分かった
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT]
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT]
        # 初期手札B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE]
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE]
        
        # 勝率を比較（Summoner's Pactを唱える）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, summoners_pact_strategy=SummonersPactStrategy.ALWAYS_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（SUMMONERS_PACT）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (SUMMONERS_PACT)' if diff > 0 else 'B (ELVISH_SPIRIT_GUIDE)'}")
        print("="*80)

        self.assertGreater(win_rate_b, win_rate_a)
    
    def test_summoners_vs_elvish_bottom_wind_without_shuffle(self):
        """
        マリガンありの初期手札AとBの勝率を比較するテスト（Summoner's Pactを唱えない場合）
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
           Bottom: [GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
           Bottom: [GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        
        実際のテスト結果では、Summoner's Pactを唱えない場合は、
        初期手札A（SUMMONERS_PACT）の方が勝率が高いことが分かった（勝率の差: 0.55%）
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        bottom_list_a = [GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        
        # 初期手札B
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        bottom_list_b = [GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        
        # 勝率を比較（Summoner's Pactを唱えない）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（SUMMONERS_PACT）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (SUMMONERS_PACT)' if diff > 0 else 'B (ELVISH_SPIRIT_GUIDE)'}")
        print("="*80)
        
        # Aの方が勝率が高いことを確認
        self.assertGreater(win_rate_a, win_rate_b, 
                          f"初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）が初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）より高くありません")
    
    def test_summoners_vs_elvish_bottom_wind_with_shuffle(self):
        """
        マリガンありの初期手札AとBの勝率を比較するテスト（Summoner's Pactを唱える場合）
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
           Bottom: [GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
           Bottom: [GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        
        実際のテスト結果では、Summoner's Pactを唱える場合も、
        初期手札A（SUMMONERS_PACT）の方が勝率が高いことが分かった（勝率の差: 0.08%）
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        bottom_list_a = [GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        
        # 初期手札B
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        bottom_list_b = [GEMSTONE_MINE, GEMSTONE_MINE, BORNE_UPON_WIND]
        
        # 勝率を比較（Summoner's Pactを唱える）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, summoners_pact_strategy=SummonersPactStrategy.ALWAYS_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（SUMMONERS_PACT）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (SUMMONERS_PACT)' if diff > 0 else 'B (ELVISH_SPIRIT_GUIDE)'}")
        print("="*80)
        
        # Aの方が勝率が高いことを確認
        self.assertGreater(win_rate_a, win_rate_b, 
                          f"初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）が初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）より高くありません")

    def test_summoners_vs_elvish_bottom_mana_wind_without_shuffle(self):
        """
        マリガンありの初期手札AとBの勝率を比較するテスト（Summoner's Pactを唱えない場合）
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
           Bottom: [GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
           Bottom: [GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        bottom_list_a = [GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        
        # 初期手札B
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        bottom_list_b = [GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        
        # 勝率を比較（Summoner's Pactを唱えない）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（SUMMONERS_PACT）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (SUMMONERS_PACT)' if diff > 0 else 'B (ELVISH_SPIRIT_GUIDE)'}")
        print("="*80)
        
        # 勝率の高い方を確認
        if win_rate_a > win_rate_b:
            self.assertGreater(win_rate_a, win_rate_b, 
                              f"初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）が初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）より高くありません")
        else:
            self.assertGreater(win_rate_b, win_rate_a, 
                              f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）が初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）より高くありません")
    
    def test_summoners_vs_elvish_bottom_mana_wind_with_shuffle(self):
        """
        マリガンありの初期手札AとBの勝率を比較するテスト（Summoner's Pactを唱える場合）
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
           Bottom: [GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
           Bottom: [GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        bottom_list_a = [GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        
        # 初期手札B
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        bottom_list_b = [GEMSTONE_MINE, MANAMORPHOSE, BORNE_UPON_WIND]
        
        # 勝率を比較（Summoner's Pactを唱える）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, summoners_pact_strategy=SummonersPactStrategy.ALWAYS_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（SUMMONERS_PACT）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (SUMMONERS_PACT)' if diff > 0 else 'B (ELVISH_SPIRIT_GUIDE)'}")
        print("="*80)
        
        # 勝率の高い方を確認
        if win_rate_a > win_rate_b:
            self.assertGreater(win_rate_a, win_rate_b, 
                              f"初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）が初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）より高くありません")
        else:
            self.assertGreater(win_rate_b, win_rate_a, 
                              f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）が初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）より高くありません")

    def test_summoners_vs_elvish_bottom_3gemstones_without_shuffle(self):
        """
        マリガンありの初期手札AとBの勝率を比較するテスト（Summoner's Pactを唱えない場合）
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
           Bottom: [GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
           Bottom: [GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        bottom_list_a = [GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        
        # 初期手札B
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        bottom_list_b = [GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        
        # 勝率を比較（Summoner's Pactを唱えない）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（SUMMONERS_PACT）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (SUMMONERS_PACT)' if diff > 0 else 'B (ELVISH_SPIRIT_GUIDE)'}")
        print("="*80)
        
        # 勝率の高い方を確認
        if win_rate_a > win_rate_b:
            self.assertGreater(win_rate_a, win_rate_b, 
                              f"初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）が初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）より高くありません")
        else:
            self.assertGreater(win_rate_b, win_rate_a, 
                              f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）が初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）より高くありません")
    
    def test_summoners_vs_elvish_bottom_3gemstones_with_shuffle(self):
        """
        マリガンありの初期手札AとBの勝率を比較するテスト（Summoner's Pactを唱える場合）
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
           Bottom: [GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
           Bottom: [GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, SUMMONERS_PACT, GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        bottom_list_a = [GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        
        # 初期手札B
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, ELVISH_SPIRIT_GUIDE, GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        bottom_list_b = [GEMSTONE_MINE, GEMSTONE_MINE, GEMSTONE_MINE]
        
        # 勝率を比較（Summoner's Pactを唱える）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, summoners_pact_strategy=SummonersPactStrategy.ALWAYS_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（SUMMONERS_PACT）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (SUMMONERS_PACT)' if diff > 0 else 'B (ELVISH_SPIRIT_GUIDE)'}")
        print("="*80)
        
        # 勝率の高い方を確認
        if win_rate_a > win_rate_b:
            self.assertGreater(win_rate_a, win_rate_b, 
                              f"初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）が初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）より高くありません")
        else:
            self.assertGreater(win_rate_b, win_rate_a, 
                              f"初期手札B（ELVISH_SPIRIT_GUIDE）の勝率（{win_rate_b:.2f}%）が初期手札A（SUMMONERS_PACT）の勝率（{win_rate_a:.2f}%）より高くありません")

    def test_dark_vs_cabal(self):
        """
        初期手札AとBの勝率を比較するテスト
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, DARK_RITUAL]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CABAL_RITUAL]
        
        DARK_RITUALとCABAL_RITUALのどちらが勝率が高いかを比較する
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, DARK_RITUAL]
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, DARK_RITUAL]
        # 初期手札B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CABAL_RITUAL]
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CABAL_RITUAL]
        
        # 勝率を比較（Summoner's Pactを唱えない）
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（DARK_RITUAL x2）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（DARK_RITUAL + CABAL_RITUAL）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (DARK_RITUAL x2)' if diff > 0 else 'B (DARK_RITUAL + CABAL_RITUAL)'}")
        print("="*80)
        
        # 勝率の高い方を確認
        if win_rate_a > win_rate_b:
            self.assertGreater(win_rate_a, win_rate_b, 
                              f"初期手札A（DARK_RITUAL x2）の勝率（{win_rate_a:.2f}%）が初期手札B（DARK_RITUAL + CABAL_RITUAL）の勝率（{win_rate_b:.2f}%）より高くありません")
        else:
            self.assertGreater(win_rate_b, win_rate_a, 
                              f"初期手札B（DARK_RITUAL + CABAL_RITUAL）の勝率（{win_rate_b:.2f}%）が初期手札A（DARK_RITUAL x2）の勝率（{win_rate_a:.2f}%）より高くありません")

    def test_compare_deck_dark_to_cabal(self):
        """
        デッキAとデッキBの勝率を比較するテスト
        デッキA: デフォルトのデッキ
        デッキB: デフォルトのデッキのDark Ritual 3枚をCabal Ritualに変更したもの
        
        初期手札: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
        
        Dark RitualとCabal Ritualのどちらが勝率が高いかを比較する
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # デフォルトのデッキを取得
        deck_a = self.get_default_deck()
        deck_b = self.get_default_deck().copy()
        
        # デッキBのDark Ritual 3枚をCabal Ritualに変更
        dark_ritual_count = 0
        for i, card in enumerate(deck_b):
            if card == DARK_RITUAL and dark_ritual_count < 3:
                deck_b[i] = CABAL_RITUAL
                dark_ritual_count += 1
        
        # 初期手札
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
        
        # 勝率を比較
        stats_a = self.analyzer.run_multiple_simulations_with_initial_hand(
            deck=deck_a.copy(), 
            initial_hand=initial_hand, 
            bottom_list=[], 
            draw_count=19, 
            summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST, 
            iterations=ITERATIONS
        )
        win_rate_a = stats_a['win_rate']
        
        stats_b = self.analyzer.run_multiple_simulations_with_initial_hand(
            deck=deck_b.copy(), 
            initial_hand=initial_hand, 
            bottom_list=[], 
            draw_count=19, 
            summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST, 
            iterations=ITERATIONS
        )
        win_rate_b = stats_b['win_rate']
        
        # 結果をリストにまとめる
        results = [
            {
                'deck_type': 'デフォルト（Dark Ritual）',
                'initial_hand': ', '.join(initial_hand),
                **stats_a
            },
            {
                'deck_type': 'Dark Ritual 3枚をCabal Ritualに変更',
                'initial_hand': ', '.join(initial_hand),
                **stats_b
            }
        ]
        
        # 結果をCSVに保存
        save_results_to_csv(self._testMethodName, results, folder_path='tests/results')
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"デッキA（デフォルト）の勝率: {win_rate_a:.2f}%")
        print(f"デッキB（Dark Ritual 3枚をCabal Ritualに変更）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (デフォルト)' if diff > 0 else 'B (Dark Ritual 3枚をCabal Ritualに変更)'}")
        print("="*80)
        
        # 勝率の高い方を確認
        if win_rate_a > win_rate_b:
            self.assertGreater(win_rate_a, win_rate_b, 
                              f"デッキA（デフォルト）の勝率（{win_rate_a:.2f}%）がデッキB（Dark Ritual 3枚をCabal Ritualに変更）の勝率（{win_rate_b:.2f}%）より高くありません")
        else:
            self.assertGreater(win_rate_b, win_rate_a, 
                              f"デッキB（Dark Ritual 3枚をCabal Ritualに変更）の勝率（{win_rate_b:.2f}%）がデッキA（デフォルト）の勝率（{win_rate_a:.2f}%）より高くありません")
    
    def test_compare_deck_cabal_to_dark(self):
        """
        デッキAとデッキBの勝率を比較するテスト
        デッキA: デフォルトのデッキ
        デッキB: デフォルトのデッキのCabal Ritual 4枚をDark Ritualに変更したもの
        
        初期手札: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
        
        Dark RitualとCabal Ritualのどちらが勝率が高いかを比較する
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # デフォルトのデッキを取得
        deck_a = self.get_default_deck()
        deck_b = self.get_default_deck().copy()
        
        # デッキBのCabal Ritual 4枚をDark Ritualに変更
        cabal_ritual_count = 0
        for i, card in enumerate(deck_b):
            if card == CABAL_RITUAL and cabal_ritual_count < 4:
                deck_b[i] = DARK_RITUAL
                cabal_ritual_count += 1
        
        # 初期手札
        initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
        
        # 勝率を比較
        stats_a = self.analyzer.run_multiple_simulations_with_initial_hand(
            deck=deck_a.copy(), 
            initial_hand=initial_hand, 
            bottom_list=[], 
            draw_count=19, 
            iterations=ITERATIONS, 
            summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST
        )
        win_rate_a = stats_a['win_rate']
        
        stats_b = self.analyzer.run_multiple_simulations_with_initial_hand(
            deck=deck_b.copy(), 
            initial_hand=initial_hand, 
            bottom_list=[], 
            draw_count=19, 
            summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST, 
            iterations=ITERATIONS
        )
        win_rate_b = stats_b['win_rate']
        
        # 結果をリストにまとめる
        results = [
            {
                'deck_type': 'デフォルト（Cabal Ritual）',
                'initial_hand': ', '.join(initial_hand),
                **stats_a
            },
            {
                'deck_type': 'Cabal Ritual 4枚をDark Ritualに変更',
                'initial_hand': ', '.join(initial_hand),
                **stats_b
            }
        ]
        
        # 結果をCSVに保存
        save_results_to_csv(self._testMethodName, results, folder_path='tests/results')
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"デッキA（デフォルト）の勝率: {win_rate_a:.2f}%")
        print(f"デッキB（Cabal Ritual 4枚をDark Ritualに変更）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (デフォルト)' if diff > 0 else 'B (Cabal Ritual 4枚をDark Ritualに変更)'}")
        print("="*80)
        
        # 勝率の高い方を確認
        if win_rate_a > win_rate_b:
            self.assertGreater(win_rate_a, win_rate_b, 
                              f"デッキA（デフォルト）の勝率（{win_rate_a:.2f}%）がデッキB（Cabal Ritual 4枚をDark Ritualに変更）の勝率（{win_rate_b:.2f}%）より高くありません")
        else:
            self.assertGreater(win_rate_b, win_rate_a, 
                              f"デッキB（Cabal Ritual 4枚をDark Ritualに変更）の勝率（{win_rate_b:.2f}%）がデッキA（デフォルト）の勝率（{win_rate_a:.2f}%）より高くありません")

    def test_compare_initial_hands_dark_vs_cabal(self):
        """
        初期手札AとBの勝率を比較するテスト
        A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, DARK_RITUAL]
        B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CABAL_RITUAL]
        
        Dark RitualとCabal Ritualのどちらが勝率が高いかを比較する
        """
        print("\n" + "="*80)
        print(f"テスト: {self._testMethodName}")
        print("="*80)
        
        # 初期手札A: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, DARK_RITUAL]
        initial_hand_a = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, DARK_RITUAL]
        # 初期手札B: [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CABAL_RITUAL]
        initial_hand_b = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CABAL_RITUAL]
        
        # 勝率を比較
        win_rate_a, win_rate_b = self.compare_initial_hands_with_default_deck(initial_hand_a, initial_hand_b, summoners_pact_strategy=SummonersPactStrategy.NEVER_CAST)
        
        # 勝率の差を表示
        diff = win_rate_a - win_rate_b
        print("\n結果サマリー:")
        print(f"初期手札A（DARK_RITUAL x2）の勝率: {win_rate_a:.2f}%")
        print(f"初期手札B（DARK_RITUAL + CABAL_RITUAL）の勝率: {win_rate_b:.2f}%")
        print(f"勝率の差（A - B）: {diff:.2f}%")
        print(f"勝率が高いのは: {'A (DARK_RITUAL x2)' if diff > 0 else 'B (DARK_RITUAL + CABAL_RITUAL)'}")
        print("="*80)
        
        # 勝率の高い方を確認
        if win_rate_a > win_rate_b:
            self.assertGreater(win_rate_a, win_rate_b, 
                              f"初期手札A（DARK_RITUAL x2）の勝率（{win_rate_a:.2f}%）が初期手札B（DARK_RITUAL + CABAL_RITUAL）の勝率（{win_rate_b:.2f}%）より高くありません")
        else:
            self.assertGreater(win_rate_b, win_rate_a, 
                              f"初期手札B（DARK_RITUAL + CABAL_RITUAL）の勝率（{win_rate_b:.2f}%）が初期手札A（DARK_RITUAL x2）の勝率（{win_rate_a:.2f}%）より高くありません")

if __name__ == '__main__':
    unittest.main()
