#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
テストランナースクリプト
カレントディレクトリ内のすべてのテストを実行します
"""

import unittest
import sys
import os

def run_all_tests():
    """
    カレントディレクトリ内のすべてのテストを実行する
    """
    # テストディスカバリーを使用してテストを検索・実行
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('.', pattern='test_*.py')
    
    # テスト結果を表示するためのテストランナーを作成
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # テスト結果の概要を表示
    print("\n=== テスト結果の概要 ===")
    print(f"実行したテスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    # 終了コードを設定（失敗またはエラーがあれば1、なければ0）
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    # スクリプトが実行されたディレクトリをカレントディレクトリに設定
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # すべてのテストを実行
    sys.exit(run_all_tests())
