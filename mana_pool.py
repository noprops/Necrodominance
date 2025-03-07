class ManaPool:
    def __init__(self):
        self.W = 0  # White mana
        self.U = 0  # Blue mana
        self.B = 0  # Black mana
        self.R = 0  # Red mana
        self.G = 0  # Green mana
    
    def copy(self):
        new_pool = ManaPool()
        new_pool.W = self.W
        new_pool.U = self.U
        new_pool.B = self.B
        new_pool.R = self.R
        new_pool.G = self.G
        return new_pool
    
    def add_mana(self, color: str, amount: int = 1) -> None:
        """Add specified color mana"""
        if hasattr(self, color):
            setattr(self, color, getattr(self, color) + amount)
    
    def remove_mana(self, color: str, amount: int = 1) -> None:
        """Remove specified color mana"""
        if not hasattr(self, color):
            raise ValueError(f"Invalid mana color: {color}")
        current_mana = getattr(self, color)
        if current_mana < amount:
            raise ValueError(f"Not enough {color} mana in pool. Required: {amount}, Available: {current_mana}")
        setattr(self, color, current_mana - amount)
    
    def get_total(self) -> int:
        """Return total mana in mana pool"""
        return self.W + self.U + self.B + self.R + self.G
    
    def get_colored_mana_count(self, color: str) -> int:
        if hasattr(self, color):
            return getattr(self, color)
        else:
            return 0
    
    def clear(self) -> None:
        """Clear all mana in pool"""
        self.W = 0
        self.U = 0
        self.B = 0
        self.R = 0
        self.G = 0
    
    def __str__(self) -> str:
        """Return mana pool state as string"""
        mana_str = ''
        for color in ['W', 'U', 'B', 'R', 'G']:
            amount = getattr(self, color)
            mana_str += color * amount
        
        if not mana_str:
            return ''
        return mana_str
    
    def analyze_mana_pattern(self, pattern: str) -> tuple[dict[str, int], int]:
        """Analyze mana pattern and calculate required mana"""
        required = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0}
        generic = 0  # Generic mana count
        
        # Split into number and non-number parts
        number_str = ''
        for c in pattern:
            if c.isdigit():
                number_str += c
            elif c in ['W', 'U', 'B', 'R', 'G']:
                required[c] += 1
        
        # Process remaining number if any
        if number_str:
            generic += int(number_str)
        
        return required, generic
    
    def can_pay_pattern(self, required: dict[str, int], generic: int) -> bool:
        """Check if can pay specific mana pattern"""
        if (self.W < required['W'] or
            self.U < required['U'] or
            self.B < required['B'] or
            self.R < required['R'] or
            self.G < required['G']):
            return False
        total_required = sum(required.values()) + generic
        return self.get_total() >= total_required
    
    def can_pay_mana(self, pattern: str) -> bool:
        """Check if can pay mana.
        pattern: String in format like '1G'"""
        required, generic = self.analyze_mana_pattern(pattern)
        if self.can_pay_pattern(required, generic):
            return True
        return False
    
    def pay_pattern(self, required: dict[str, int], generic: int, priority: str = 'WGRBU') -> None:
        # First pay colored mana
        for color, amount in required.items():
            if amount > 0:
                self.remove_mana(color, amount)
        
        # Then pay generic mana according to priority
        for color in priority:
            while generic > 0:
                if color == 'W' and self.W > 0:
                    self.remove_mana('W')
                    generic -= 1
                elif color == 'U' and self.U > 0:
                    self.remove_mana('U')
                    generic -= 1
                elif color == 'B' and self.B > 0:
                    self.remove_mana('B')
                    generic -= 1
                elif color == 'R' and self.R > 0:
                    self.remove_mana('R')
                    generic -= 1
                elif color == 'G' and self.G > 0:
                    self.remove_mana('G')
                    generic -= 1
                else:
                    break
    
    def pay_mana(self, pattern: str, priority: str = 'WGRBU') -> None:
        """Pay mana.
        pattern: String in format like '1G'
        priority: Color priority for generic mana (e.g., 'WGRBU')"""
        required, generic = self.analyze_mana_pattern(pattern)
        self.pay_pattern(required, generic, priority)
    
    def transfer_from(self, other_pool: 'ManaPool') -> None:
        """Transfer all mana from another mana pool to this mana pool."""
        for color in ['W', 'U', 'B', 'R', 'G']:
            mana_to_transfer = other_pool.get_colored_mana_count(color)
            if mana_to_transfer > 0:
                self.add_mana(color, mana_to_transfer)
                other_pool.remove_mana(color, mana_to_transfer)
