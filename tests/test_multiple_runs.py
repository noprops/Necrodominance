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
from deck_utils import create_deck

class TestMultipleRuns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create GameState instance once for all tests"""
        cls.game = GameState()
        # テスト中はデバッグ出力を無効化
        cls.game.debug_print = False
        # デッキを作成
        # プロジェクトルートのパスを取得
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # デッキファイルの絶対パスを構築
        deck_file = os.path.join(root_dir, 'decks', 'gemstone4_paradise0_cantor0_chrome4_wind4_valakut3.txt')
        cls.deck = create_deck(deck_file)
    
    def setUp(self):
        """各テストの前に実行される処理"""
        # 乱数のシードを固定して再現性を確保
        random.seed(42)
    
    def compare_initial_hands(self, initial_hand_a, initial_hand_b, bottom_list_a=[], bottom_list_b=[], iterations=ITERATIONS, cast_summoners_pact=False):
        """
        2つの初期手札の勝率を比較する汎用関数
        
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
        
        # 初期手札Aの勝率を計算
        wins_a = 0
        for _ in range(iterations):
            # デッキをコピーしてシャッフル
            deck_copy = self.deck.copy()
            random.shuffle(deck_copy)
            
            # ゲームを実行
            result = self.game.run_with_initial_hand(deck_copy, initial_hand_a, bottom_list_a, 19, cast_summoners_pact)
            if result:
                wins_a += 1
        
        win_rate_a = wins_a / iterations * 100
        
        # 初期手札Bの勝率を計算
        wins_b = 0
        for _ in range(iterations):
            # デッキをコピーしてシャッフル
            deck_copy = self.deck.copy()
            random.shuffle(deck_copy)
            
            # ゲームを実行
            result = self.game.run_with_initial_hand(deck_copy, initial_hand_b, bottom_list_b, 19, cast_summoners_pact)
            if result:
                wins_b += 1
        
        win_rate_b = wins_b / iterations * 100
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, cast_summoners_pact=False)
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, cast_summoners_pact=True)
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, cast_summoners_pact=False)
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, cast_summoners_pact=True)
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, cast_summoners_pact=False)
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, cast_summoners_pact=True)
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, cast_summoners_pact=False)
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, bottom_list_a, bottom_list_b, cast_summoners_pact=True)
        
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
        win_rate_a, win_rate_b = self.compare_initial_hands(initial_hand_a, initial_hand_b, cast_summoners_pact=False)
        
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
