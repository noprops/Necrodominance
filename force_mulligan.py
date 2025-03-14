import random
import datetime

# カードの種類を定義
FORCE_OF_WILL = "Force of Will"
FORCE_OF_NEGATION = "Force of Negation"
BLUE_CARD = "Blue Card"
OTHER_CARD = "Other Card"

# 青いカードのリスト
BLUE_CARDS = [FORCE_OF_WILL, FORCE_OF_NEGATION, BLUE_CARD]

class ForceMulliganSimulator:
    """Force of WillとForce of Negationのマリガン戦略をシミュレーションするクラス"""
    
    def __init__(self):
        """初期化"""
        self.deck = []
        self.hand = []
        self.create_deck()
    
    def create_deck(self):
        """60枚のデッキを作成する"""
        self.deck = []
        self.deck.extend([FORCE_OF_WILL] * 4)
        self.deck.extend([FORCE_OF_NEGATION] * 2)
        self.deck.extend([BLUE_CARD] * 26)
        self.deck.extend([OTHER_CARD] * 28)
        # デッキが60枚であることを確認
        assert len(self.deck) == 60, f"デッキは60枚である必要があります。現在: {len(self.deck)}枚"
    
    def shuffle_deck(self):
        """デッキをシャッフルする"""
        random.shuffle(self.deck)
    
    def draw_hand(self, count=7):
        """指定した枚数のカードを引く"""
        self.hand = self.deck[:count]
        self.deck = self.deck[count:]
    
    def return_hand_to_deck(self):
        """手札をデッキに戻す"""
        self.deck.extend(self.hand)
        self.hand = []
    
    def is_blue(self, card: str) -> bool:
        return card in BLUE_CARDS
    
    def get_force_count(self) -> int:
        # Forceを唱えられる回数
        # 各カードの枚数をカウント
        force_count = self.hand.count(FORCE_OF_WILL) + self.hand.count(FORCE_OF_NEGATION)
        blue_count = sum(self.hand.count(card) for card in BLUE_CARDS)
        return min(force_count, blue_count // 2)
    
    def get_cards_to_bottom(self, mulligan_count):
        """ボトムに戻すカードを選択する"""
        # ボトムに戻す枚数
        bottom_count = mulligan_count
        
        # 手札をコピー
        remaining_hand = self.hand.copy()
        bottom_cards = []
        
        # ボトムに戻すカードの優先順位: Other Card > Blue Card > Force of Negation > Force of Will
        priority_order = [OTHER_CARD, BLUE_CARD, FORCE_OF_NEGATION, FORCE_OF_WILL]
        
        for card_type in priority_order:
            # 必要な枚数だけボトムに戻す
            while bottom_count > 0 and card_type in remaining_hand:
                remaining_hand.remove(card_type)
                bottom_cards.append(card_type)
                bottom_count -= 1
            
            # 必要な枚数をボトムに戻したら終了
            if bottom_count == 0:
                break
        
        return bottom_cards
    
    def put_cards_to_bottom(self, mulligan_count):
        """マリガン回数に応じて、手札からカードをデッキボトムに送る"""
        if mulligan_count <= 0:
            return []
        
        # ボトムに戻すカードを選択
        bottom_cards = self.get_cards_to_bottom(mulligan_count)
        
        # 手札からボトムに戻すカードを除去
        for card in bottom_cards:
            if card in self.hand:
                self.hand.remove(card)
            else:
                raise ValueError(f"カード {card} は手札にありません")
        
        # ボトムに戻すカードをデッキの一番下に追加
        self.deck.extend(bottom_cards)
        
        return bottom_cards
    
    def format_card_counts(self, cards):
        """カードの枚数を文字列形式でフォーマットする"""
        card_counts = {}
        for card in cards:
            if card in card_counts:
                card_counts[card] += 1
            else:
                card_counts[card] = 1
        
        # カードの枚数を文字列形式で返す
        return ', '.join([f"{card}: {count}" for card, count in card_counts.items()])
    
    def run(self, max_mulligan=5, verbose=True) -> int:
        """マリガン処理を実行し、Forceを唱えられる回数を返す"""
        # マリガン回数
        mulligan_count = 0
        
        while mulligan_count <= max_mulligan:
            self.create_deck()
            self.shuffle_deck()
            self.draw_hand(7)
            
            if verbose:
                # 手札の内容を表示
                print(f"手札 (マリガン{mulligan_count}回目): {self.format_card_counts(self.hand)}")
            
            # 手札からForceを唱えられる回数を取得
            force_count = self.get_force_count()
            
            # Forceを唱えられる場合はキープ
            if force_count > 0:
                if verbose:
                    print(f"キープ可能な手札です！（Force唱えられる回数: {force_count}）")
                
                # マリガン回数に応じてボトムに戻すカードを選択
                if mulligan_count > 0:
                    bottom_cards = self.put_cards_to_bottom(mulligan_count)
                    if verbose and bottom_cards:
                        print(f"ボトムに戻すカード ({mulligan_count}枚): {self.format_card_counts(bottom_cards)}")
                
                # ボトムに戻した後のForceを唱えられる回数を再計算
                force_count = self.get_force_count()
                
                if verbose:
                    # 最終的な手札を表示
                    print(f"最終的な手札 ({len(self.hand)}枚): {self.format_card_counts(self.hand)}")
                    print(f"Forceを唱えられる回数: {force_count}")
                
                return force_count
            
            if verbose:
                print(f"キープできない手札です。マリガンします。")
            
            # 手札をデッキに戻してシャッフル
            self.return_hand_to_deck()
            
            # マリガン回数を増やす
            mulligan_count += 1
        
        # 最大マリガン回数に達した場合
        if verbose:
            print(f"最大マリガン回数 ({max_mulligan}回) に達しました。")
        
        # 最大マリガン回数に達した場合は0を返す
        return 0
    
    def run_simulations(self, iterations=100000, verbose=True):
        """複数回のシミュレーションを実行する"""
        # 結果を格納する辞書
        raw_results = {
            'total_simulations': iterations,
            'force_counts': {i: 0 for i in range(4)},  # 0回から3回までのForce唱えられる回数
        }
        
        if verbose:
            print(f"シミュレーション開始: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # シミュレーション実行
        for i in range(iterations):
            if verbose and i % 10000 == 0 and i > 0:
                print(f"{i}回のシミュレーション完了...")
            
            force_count = self.run(verbose=False)
            # force_countが3を超える場合は3として扱う（物理的に不可能なため）
            force_count = min(force_count, 3)
            raw_results['force_counts'][force_count] += 1
        
        # 結果の集計
        total_force_count = sum(count * force_count for force_count, count in raw_results['force_counts'].items())
        average_force_count = total_force_count / iterations
        
        # CSVに保存するための整形された結果を作成（各force_countごとに1行）
        results_list = []
        
        for force_count, count in raw_results['force_counts'].items():
            percentage = (count / iterations) * 100
            result_dict = {
                'force_count': force_count,
                'total_simulations': iterations,
                'count': count,
                'percentage': percentage
            }
            results_list.append(result_dict)
        
        if verbose:
            # 結果の表示
            print("\n===== シミュレーション結果 =====")
            print(f"合計シミュレーション回数: {iterations}")
            print(f"平均Force唱えられる回数: {average_force_count:.2f}")
            
            print("\nForce唱えられる回数の分布:")
            for force_count, count in raw_results['force_counts'].items():
                percentage = (count / iterations) * 100
                print(f"  {force_count}回: {count}回 ({percentage:.2f}%)")
            
            print(f"シミュレーション終了: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results_list  # CSVに保存するためにリスト形式で返す

if __name__ == "__main__":
    # 乱数のシードを設定（再現性のため）
    random.seed(42)
    
    # シミュレーターのインスタンスを作成
    simulator = ForceMulliganSimulator()
    
    # 単一のシミュレーションを実行（詳細表示）
    print("===== 単一シミュレーション =====")
    force_count = simulator.run(verbose=True)
    print(f"Forceを唱えられる回数: {force_count}")
    
    print("\n")
    
    # 複数のシミュレーションを実行（統計情報）
    iterations = 1000000
    print(f"===== {iterations}回のシミュレーション =====")
    results = simulator.run_simulations(iterations, verbose=True)
    
    # 結果をCSVに保存
    from deck_utils import save_results_to_csv
    
    # ファイル名を設定
    filename = "force_mulligan_results"
    
    # deck_utils.pyのsave_results_to_csv関数を使用
    # CSVの列の順序を指定
    priority_fields = ['force_count', 'total_simulations', 'count', 'percentage']
    save_results_to_csv(filename, results, priority_fields)
