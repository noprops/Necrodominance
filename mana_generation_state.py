from mana_pool import ManaPool
from card_constants import *

class ManaGenerationState:
    def __init__(
            self, mana_pool=None, any_mana_source=0,
            hand=None, deck=None, cards_to_imprint=None, can_cast_sorcery=False,
            cards_used_from_hand=None, cards_imprinted=None, cards_searched=None):
        self.mana_pool = mana_pool if mana_pool is not None else ManaPool()
        self.any_mana_source = any_mana_source
        self.hand = hand if hand is not None else []
        self.deck = deck if deck is not None else []
        self.cards_to_imprint = cards_to_imprint if cards_to_imprint is not None else []
        self.can_cast_sorcery = can_cast_sorcery
        self.cards_used_from_hand = cards_used_from_hand if cards_used_from_hand is not None else []
        self.cards_imprinted = cards_imprinted if cards_imprinted is not None else []
        self.cards_searched = cards_searched if cards_searched is not None else []
    
    def copy(self):
        new_instance = ManaGenerationState()
        new_instance.copy_from(self)
        return new_instance
    
    def copy_from(self, other):
        self.mana_pool = other.mana_pool.copy()
        self.any_mana_source = other.any_mana_source
        self.hand = other.hand.copy()
        self.deck = other.deck.copy()
        self.cards_to_imprint = other.cards_to_imprint.copy()
        self.can_cast_sorcery = other.can_cast_sorcery
        self.cards_used_from_hand = other.cards_used_from_hand.copy()
        self.cards_imprinted = other.cards_imprinted.copy()
        self.cards_searched = other.cards_searched.copy()
    
    def can_generate_mana_pattern(self, required: dict[str, int], generic: int) -> tuple[bool, list[str], list[str], list[str]]:
        if self.mana_pool.can_pay_pattern(required, generic):
            return [True, self.cards_used_from_hand, self.cards_imprinted, self.cards_searched]
        
        initial_elvish_count = self.hand.count(ELVISH_SPIRIT_GUIDE)
        
        # Summoners PactでElvishをサーチ
        while SUMMONERS_PACT in self.hand and ELVISH_SPIRIT_GUIDE in self.deck:
            self.cast_card_from_hand(SUMMONERS_PACT)
            self.deck.remove(ELVISH_SPIRIT_GUIDE)
            self.hand.append(ELVISH_SPIRIT_GUIDE)
            self.cards_searched.append(ELVISH_SPIRIT_GUIDE)
        
        # Spirit Guideをすべてマナに変える
        while ELVISH_SPIRIT_GUIDE in self.hand:
            self.cast_card_from_hand(ELVISH_SPIRIT_GUIDE)
            self.mana_pool.add_mana('G')
        
        while SIMIAN_SPIRIT_GUIDE in self.hand:
            self.cast_card_from_hand(SIMIAN_SPIRIT_GUIDE)
            self.mana_pool.add_mana('R')
        
        # Spirit Guideでマナを払えるか確認
        if self.mana_pool.can_pay_pattern(required, generic):
            self.mana_pool.pay_pattern(required, generic)
            self.revert_remaining_mana(initial_elvish_count)
            return [True, self.cards_used_from_hand, self.cards_imprinted, self.cards_searched]
        
        if self.can_cast_sorcery:
            while LOTUS_PETAL in self.hand:
                self.cast_card_from_hand(LOTUS_PETAL)
                self.any_mana_source += 1
        
        total_available_mana = self.mana_pool.get_total() + self.any_mana_source + self.hand.count(CHROME_MOX) + self.hand.count(DARK_RITUAL) * 2 + self.hand.count(CABAL_RITUAL)
        total_required_mana = sum(required.values()) + generic
        if total_available_mana < total_required_mana:
            #print(f'total available_mana {total_available_mana} < total required mana {total_required_mana}')
            return [False, [], [], []]
        
        if self.try_generate_mana_recursively(required, generic):
            self.revert_remaining_mana(initial_elvish_count)
            return [True, self.cards_used_from_hand, self.cards_imprinted, self.cards_searched]
        else:
            return [False, [], [], []]
    
    def can_generate_mana(self, mana_cost: str) -> tuple[bool, list[str], list[str], list[str]]:
        required, generic = self.mana_pool.analyze_mana_pattern(mana_cost)
        return self.can_generate_mana_pattern(required, generic)

    # 余ったマナを手札のSpirit GuideとLotus Petalに戻す
    # Gは手札のESGに優先して戻す
    # つまり、手札のESGよりもSummoner's Pactを優先して使用したことになる
    def revert_remaining_mana(self, initial_elvish_count: int):
        while self.mana_pool.G > 0 and ELVISH_SPIRIT_GUIDE in self.cards_used_from_hand:
            self.mana_pool.G -= 1
            self.cards_used_from_hand.remove(ELVISH_SPIRIT_GUIDE)
            if initial_elvish_count > 0:
                # 手札のElvishに戻す
                initial_elvish_count -= 1
                self.hand.append(ELVISH_SPIRIT_GUIDE)
            elif ELVISH_SPIRIT_GUIDE in self.cards_searched:
                # 手札のSummoner's Pactに戻す
                self.cards_searched.remove(ELVISH_SPIRIT_GUIDE)
                self.cards_used_from_hand.remove(SUMMONERS_PACT)
                self.hand.append(SUMMONERS_PACT)
                self.deck.append(ELVISH_SPIRIT_GUIDE)
        
        while self.mana_pool.R > 0 and SIMIAN_SPIRIT_GUIDE in self.cards_used_from_hand:
            self.mana_pool.R -= 1
            self.cards_used_from_hand.remove(SIMIAN_SPIRIT_GUIDE)
            self.hand.append(SIMIAN_SPIRIT_GUIDE)
        
        while self.any_mana_source > 0 and LOTUS_PETAL in self.cards_used_from_hand:
            self.any_mana_source -= 1
            self.cards_used_from_hand.remove(LOTUS_PETAL)
            self.hand.append(LOTUS_PETAL)
    
    def cast_card_from_hand(self, card):
        self.hand.remove(card)
        self.cards_used_from_hand.append(card)
        if card in self.cards_to_imprint:
            self.cards_to_imprint.remove(card)
    
    def try_search_cantor(self) -> bool:
        if WILD_CANTOR not in self.deck:
            return False
        
        if SUMMONERS_PACT in self.hand:
            self.cast_card_from_hand(SUMMONERS_PACT)
            self.deck.remove(WILD_CANTOR)
            self.hand.append(WILD_CANTOR)
            self.cards_searched.append(WILD_CANTOR)
            return True
        elif ELVISH_SPIRIT_GUIDE in self.cards_searched and self.mana_pool.G > 0:
            self.mana_pool.G -= 1
            # Elvishをデッキに戻す
            self.deck.append(ELVISH_SPIRIT_GUIDE)
            self.cards_used_from_hand.remove(ELVISH_SPIRIT_GUIDE)
            self.cards_searched.remove(ELVISH_SPIRIT_GUIDE)
            # 代わりにCantorを手札に加える
            self.deck.remove(WILD_CANTOR)
            self.hand.append(WILD_CANTOR)
            self.cards_searched.append(WILD_CANTOR)
            return True
        
        return False
    
    def try_imprint(self, card: str) -> bool:
        if card in self.cards_to_imprint and card in self.hand:
            self.cards_to_imprint.remove(card)
            self.hand.remove(card)
            self.cards_imprinted.append(card)
            return True
        return False

    def try_cast_chrome_mox(self, color: str) -> bool:
        if color == 'W':
            if self.try_imprint(CHANCELLOR_OF_ANNEX):
                self.hand.remove(CHROME_MOX)
                self.cards_used_from_hand.append(CHROME_MOX)
                return True
        elif color == 'U':
            if self.try_imprint(PACT_OF_NEGATION) or self.try_imprint(BORNE_UPON_WIND):
                self.hand.remove(CHROME_MOX)
                self.cards_used_from_hand.append(CHROME_MOX)
                return True
        elif color == 'R':
            if self.try_imprint(VALAKUT_AWAKENING) or self.try_imprint(WILD_CANTOR) or self.try_imprint(MANAMORPHOSE):
                self.hand.remove(CHROME_MOX)
                self.cards_used_from_hand.append(CHROME_MOX)
                return True
        elif color == 'G':
            if self.try_imprint(SUMMONERS_PACT):
                self.hand.remove(CHROME_MOX)
                self.cards_used_from_hand.append(CHROME_MOX)
                return True
        elif color == 'B':
            if self.try_imprint(DURESS) or self.try_imprint(NECRODOMINANCE) or self.try_imprint(BESEECH_MIRROR) or self.try_imprint(CABAL_RITUAL) or self.try_imprint(DARK_RITUAL):
                self.hand.remove(CHROME_MOX)
                self.cards_used_from_hand.append(CHROME_MOX)
                return True
        
        return False

    def try_generate_mana_recursively(self, required: dict[str, int], generic: int) -> bool:
        return self.try_generate_colored_mana('R', required, generic)
    
    def try_generate_colored_mana(self, color: str, required: dict[str, int], generic: int) -> bool:
        required_count = required[color]
        if required_count <= self.mana_pool.get_colored_mana_count(color):
            # 色マナを支払う
            self.mana_pool.remove_mana(color, required_count)

            if color == 'R':
                return self.try_generate_colored_mana('G', required, generic)
            elif color == 'G':
                return self.try_generate_colored_mana('W', required, generic)
            elif color == 'W':
                return self.try_generate_colored_mana('U', required, generic)
            elif color == 'U':
                return self.try_generate_B(required, generic)
            else:
                # Invalid Color
                return False
        
        initial_state = self.copy()
        
        # Use any color mana source
        if self.any_mana_source > 0:
            self.any_mana_source -= 1
            self.mana_pool.add_mana(color)
            if self.try_generate_colored_mana(color, required, generic):
                return True
            # 失敗したら元の状態に戻す
            self.copy_from(initial_state)
        
        if self.can_cast_sorcery:
            # Cast Chrome Mox
            if CHROME_MOX in self.hand and self.try_cast_chrome_mox(color):
                self.mana_pool.add_mana(color)
                if self.try_generate_colored_mana(color, required, generic):
                    return True
                self.copy_from(initial_state)
            
            # Cast Wild Cantor
            if WILD_CANTOR in self.hand:
                if color != 'G' and self.mana_pool.G > 0:
                    self.mana_pool.G -= 1
                    self.cast_card_from_hand(WILD_CANTOR)
                    self.any_mana_source += 1
                    if self.try_generate_colored_mana(color, required, generic):
                        return True
                    self.copy_from(initial_state)

                if color != 'R' and self.mana_pool.R > 0:
                    self.mana_pool.R -= 1
                    self.cast_card_from_hand(WILD_CANTOR)
                    self.any_mana_source += 1
                    if self.try_generate_colored_mana(color, required, generic):
                        return True
                    self.copy_from(initial_state)
                
            elif color != 'G' and (self.mana_pool.G > 0 or self.mana_pool.R > 0) and\
                SUMMONERS_PACT in self.hand and WILD_CANTOR in self.deck:
                if self.try_search_cantor():
                    if self.try_generate_colored_mana(color, required, generic):
                        return True
                    self.copy_from(initial_state)
        
        return False
    
    def try_generate_B(self, required: dict[str, int], generic: int) -> bool:
        requiredB = required['B']
        if requiredB <= self.mana_pool.B:
            # 黒マナはマナプールから支払わない
            return self.try_generate_generic(required, generic)
        
        initial_state = self.copy()
        
        if DARK_RITUAL in self.hand and self.mana_pool.B > 0:
            self.cast_card_from_hand(DARK_RITUAL)
            self.mana_pool.B += 2
            if self.try_generate_B(required, generic):
                return True
            self.copy_from(initial_state)
        
        if CABAL_RITUAL in self.hand and self.mana_pool.can_pay_mana('1B'):
            self.cast_card_from_hand(CABAL_RITUAL)
            self.mana_pool.pay_mana('1B')
            self.mana_pool.add_mana('B', 3)
            if self.try_generate_B(required, generic):
                return True
            self.copy_from(initial_state)
        
        # Use any color mana source
        if self.any_mana_source > 0:
            self.any_mana_source -= 1
            self.mana_pool.add_mana('B')
            if self.try_generate_B(required, generic):
                return True
            self.copy_from(initial_state)
        
        if self.can_cast_sorcery:
            # Cast Chrome Mox
            if CHROME_MOX in self.hand:
                if self.try_cast_chrome_mox('B'):
                    self.mana_pool.add_mana('B')
                    if self.try_generate_B(required, generic):
                        return True
                    self.copy_from(initial_state)
            
            # Cast Wild Cantor
            if WILD_CANTOR in self.hand:
                cantor_costs = ['G', 'R']
                for cost in cantor_costs:
                    if self.mana_pool.can_pay_mana(cost):
                        self.mana_pool.pay_mana(cost)
                        self.cast_card_from_hand(WILD_CANTOR)
                        self.any_mana_source += 1
                        if self.try_generate_B(required, generic):
                            return True
                        self.copy_from(initial_state)
            elif (self.mana_pool.G > 0 or self.mana_pool.R > 0) and SUMMONERS_PACT in self.hand and WILD_CANTOR in self.deck:
                if self.try_search_cantor():
                    if self.try_generate_B(required, generic):
                        return True
                    self.copy_from(initial_state)
        
        return False
    
    def try_generate_generic(self, required: dict[str, int], generic: int) -> bool:
        requiredB = required['B']
        if requiredB + generic <= self.mana_pool.get_total():
            # 黒マナとgenericマナを支払う
            self.mana_pool.pay_pattern({'B': requiredB}, generic)
            return True
        
        initial_state = self.copy()
        
        if DARK_RITUAL in self.hand and self.mana_pool.B > 0:
            self.cast_card_from_hand(DARK_RITUAL)
            self.mana_pool.B += 2
            if self.try_generate_generic(required, generic):
                return True
            self.copy_from(initial_state)
        
        if CABAL_RITUAL in self.hand and self.mana_pool.can_pay_mana('1B'):
            self.cast_card_from_hand(CABAL_RITUAL)
            self.mana_pool.pay_mana('1B')
            self.mana_pool.add_mana('B', 3)
            if self.try_generate_generic(required, generic):
                return True
            self.copy_from(initial_state)
        
        # Use any color mana source
        if self.any_mana_source > 0:
            self.any_mana_source -= 1
            self.mana_pool.add_mana('B')
            if self.try_generate_generic(required, generic):
                return True
            self.copy_from(initial_state)
        
        if self.can_cast_sorcery:
            # Cast Chrome Mox
            if CHROME_MOX in self.hand:
                for color in ['W', 'G', 'B', 'R', 'U']:
                    if self.try_cast_chrome_mox(color):
                        self.mana_pool.add_mana(color)
                        if self.try_generate_generic(required, generic):
                            return True
                        self.copy_from(initial_state)
        
        return False
    
