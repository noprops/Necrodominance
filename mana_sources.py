class ManaSources:
    def __init__(self, mana_pool):
        self.mana_pool = mana_pool
        self.W = 0
        self.U = 0
        self.B = 0
        self.R = 0
        self.G = 0
        self.ANY = 0
        self.did_generate_any_mana = None
        self.any_mana_colors = []  # any_mana_sourceから出したマナの色を記録するリスト
    
    def copy(self):
        new_sources = ManaSources(self.mana_pool)
        new_sources.W = self.W
        new_sources.U = self.U
        new_sources.B = self.B
        new_sources.R = self.R
        new_sources.G = self.G
        new_sources.ANY = self.ANY
        new_sources.any_mana_colors = self.any_mana_colors.copy()  # リストのコピーを作成
        #new_sources.did_generate_any_mana = None
        return new_sources
    
    def clear(self) -> None:
        self.W = 0
        self.U = 0
        self.B = 0
        self.R = 0
        self.G = 0
        self.ANY = 0
        self.any_mana_colors = []  # 空のリストに初期化
    
    def get_total(self) -> int:
        return self.W + self.U + self.B + self.R + self.G + self.ANY
    
    def get_colored_source_count(self, color: str) -> int:
        if hasattr(self, color):
            return getattr(self, color)
        else:
            return 0
    
    def generate_any_mana(self, count: int, color: str):
        self.ANY -= count
        # 色が指定されていれば、any_mana_colorsに追加
        if color:
            for _ in range(count):
                self.any_mana_colors.append(color)
        
        # コールバックが存在すれば呼ぶ
        if self.did_generate_any_mana:
            for _ in range(count):
                self.did_generate_any_mana()
    
    def add_mana_source(self, color: str, amount: int = 1) -> None:
        if hasattr(self, color):
            setattr(self, color, getattr(self, color) + amount)
    
    def can_generate_mana(self, color: str, amount: int = 1) -> bool:
        source_count = getattr(self, color)
        total_available = source_count + self.ANY
        return amount <= total_available

    def generate_mana(self, color: str, amount: int = 1) -> None:
        if not hasattr(self, color):
            raise ValueError(f"Invalid mana color: {color}")
        
        source_count = getattr(self, color)
        total_available = source_count + self.ANY

        if total_available < amount:
            raise ValueError(f"Not enough {color} mana source. Required: {amount}, Available: {total_available}")
        
        if source_count >= amount:
            setattr(self, color, source_count - amount)
        else:
            setattr(self, color, 0)
            remaining = amount - source_count
            self.generate_any_mana(remaining, color)
        
        self.mana_pool.add_mana(color, amount)
    
    def __str__(self) -> str:
        """Return mana sources state as string"""
        mana_str = ''
        for color in ['W', 'U', 'B', 'R', 'G']:
            amount = getattr(self, color)
            mana_str += color * amount
        
        # Add ANY sources if present
        if self.ANY > 0:
            if mana_str:
                mana_str += f"+ANY{self.ANY}"
            else:
                mana_str = f"ANY{self.ANY}"
        
        # Add any_mana_colors if present
        if self.any_mana_colors:
            # リストを文字列に変換
            colors_str = ''.join(self.any_mana_colors)
            if mana_str:
                mana_str += f" (Used ANY for: {colors_str})"
            else:
                mana_str = f"Used ANY for: {colors_str}"
        
        if not mana_str:
            return ''
        return mana_str
