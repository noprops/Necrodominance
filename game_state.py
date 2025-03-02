import random
from copy import copy
import os
from deck_utils import create_deck

# Card name constants
GEMSTONE_MINE = "Gemstone Mine"
UNDISCOVERED_PARADISE = "Undiscovered Paradise"
VAULT_OF_WHISPERS = "Vault of Whispers"
CHROME_MOX = "Chrome Mox"
LOTUS_PETAL = "Lotus Petal"
SUMMONERS_PACT = "Summoner's Pact"
ELVISH_SPIRIT_GUIDE = "Elvish Spirit Guide"
SIMIAN_SPIRIT_GUIDE = "Simian Spirit Guide"
WILD_CANTOR = "Wild Cantor"
MANAMORPHOSE = "Manamorphose"
VALAKUT_AWAKENING = "Valakut Awakening"
BORNE_UPON_WIND = "Borne Upon a Wind"
DARK_RITUAL = "Dark Ritual"
CABAL_RITUAL = "Cabal Ritual"
NECRODOMINANCE = "Necrodominance"
BESEECH_MIRROR = "Beseech the Mirror"
TENDRILS_OF_AGONY = "Tendrils of Agony"
PACT_OF_NEGATION = "Pact of Negation"
DURESS = "DURESS"

# Loss Reason
FALIED_NECRO = "Failed to cast Necrodominance"
FAILED_VALAKUT_AND_WIND = "Failed to cast both Valakut and Borne Upon a Wind"
FAILED_WIND_AFTER_VALAKUT = "Cast Valakut but failed to cast Borne Upon a Wind"
FAILED_TENDRILS_AFTER_WIND = "Cast Borne Upon a Wind but failed to cast Tendrils"

class ManaPool:
    def __init__(self):
        self.W = 0  # White mana
        self.U = 0  # Blue mana
        self.B = 0  # Black mana
        self.R = 0  # Red mana
        self.G = 0  # Green mana
    
    def __copy__(self):
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

class GameState:
    def __init__(self):
        self.debug_print = True  # Print control flag

        self.mana_pool = ManaPool()
        # main_phaseに浮いたUをend_stepに渡すためのマナプール
        self.reserved_mana_pool = ManaPool()

        self.reset_game()
    
    def reset_game(self):
        self.mana_pool.clear()
        self.reserved_mana_pool.clear()
        self.deck = []
        self.hand = []
        self.battlefield = []
        self.graveyard = []
        self.bargain = []

        self.storm_count = 0
        self.can_cast_sorcery = False
        self.did_cast_necro = False
        self.did_cast_valakut = False
        self.did_cast_wind = False
        self.did_cast_tendril = False
        self.loss_reason = ''
    
    def __copy__(self):
        new_instance = GameState()
        new_instance.copy_from(self)
        return new_instance
    
    def copy_from(self, other):
        self.debug_print = other.debug_print
        
        self.mana_pool = copy(other.mana_pool)
        self.reserved_mana_pool = copy(other.reserved_mana_pool)
        self.deck = other.deck.copy()
        self.hand = other.hand.copy()
        self.battlefield = other.battlefield.copy()
        self.graveyard = other.graveyard.copy()
        self.bargain = other.bargain.copy()
        
        self.storm_count = other.storm_count
        self.can_cast_sorcery = other.can_cast_sorcery
        self.did_cast_necro = other.did_cast_necro
        self.did_cast_valakut = other.did_cast_valakut
        self.did_cast_wind = other.did_cast_wind
        self.did_cast_tendril = other.did_cast_tendril
        self.loss_reason = other.loss_reason
    
    def debug(self, message: str) -> None:
        """Debug print function"""
        if self.debug_print:
            print(message)
    
    def draw_cards(self, count: int) -> None:
        drawn_cards = self.deck[:count]
        self.hand.extend(drawn_cards)
        self.deck = self.deck[count:]
        card_word = "card" if count == 1 else "cards"
        self.debug(f"Draw {count} {card_word}: {', '.join(drawn_cards)}")
    
    def validate_hand(self):
        """Basic hand validation
        Conditions:
        1. Need 2+ total of Spirit Guides (Elvish/Simian) and Summoner's Pact
        2. If no Manamorphose:
           - Need 1+ Valakut Awakening (to improve hand)
           - Need 3+ total of Spirit Guides and Summoner's Pact (for mana)
           - Need 1+ Simian Spirit Guide (for red mana)
        """
        # Count cards
        simian_count = self.hand.count(SIMIAN_SPIRIT_GUIDE)
        elvish_count = self.hand.count(ELVISH_SPIRIT_GUIDE)
        summoners_count = self.hand.count(SUMMONERS_PACT)
        manamorphose_count = self.hand.count(MANAMORPHOSE)
        valakut_count = self.hand.count(VALAKUT_AWAKENING)
        
        # Need 2+ total of Spirit Guides and Summoner's Pact
        spirit_guide_total = simian_count + elvish_count + summoners_count
        if spirit_guide_total < 2:
            self.debug("Validation Failure: Less than 2 total Spirit Guides and Summoner's Pact")
            self.loss_reason = FAILED_VALAKUT_AND_WIND
            return False
        
        # Additional conditions if no Manamorphose
        if manamorphose_count == 0:
            # Need 1+ Valakut Awakening
            if valakut_count == 0:
                self.debug("Validation Failure: No Manamorphose and no Valakut Awakening")
                self.loss_reason = FAILED_VALAKUT_AND_WIND
                return False
            
            # Need 3+ total of Spirit Guides and Summoner's Pact
            if spirit_guide_total < 3:
                self.debug("Validation Failure: No Manamorphose and less than 3 total Spirit Guides and Summoner's Pact")
                self.loss_reason = FAILED_VALAKUT_AND_WIND
                return False
            
            # Need 1+ Simian Spirit Guide
            if simian_count == 0:
                self.debug("Validation Failure: No Manamorphose and no Simian Spirit Guide")
                self.loss_reason = FAILED_VALAKUT_AND_WIND
                return False
        
        return True
    
    def create_imprint_list(self) -> list:
        imprint_list = []
        if not self.did_cast_necro:
            if self.hand.count(NECRODOMINANCE) >= 2:
                imprint_list.extend([NECRODOMINANCE] * (self.hand.count(NECRODOMINANCE) - 1))
            if DURESS in self.hand:
                imprint_list.extend([DURESS] * self.hand.count(DURESS))
            if BESEECH_MIRROR in self.hand:
                if NECRODOMINANCE in self.hand:
                    imprint_list.extend([BESEECH_MIRROR] * self.hand.count(BESEECH_MIRROR))
                elif self.hand.count(BESEECH_MIRROR) >= 2:
                    imprint_list.extend([BESEECH_MIRROR] * (self.hand.count(BESEECH_MIRROR) - 1))
            if CABAL_RITUAL in self.hand:
                imprint_list.extend([CABAL_RITUAL] * self.hand.count(CABAL_RITUAL))
            if DARK_RITUAL in self.hand:
                imprint_list.extend([DARK_RITUAL] * self.hand.count(DARK_RITUAL))
        else:
            if NECRODOMINANCE in self.hand:
                imprint_list.extend([NECRODOMINANCE] * self.hand.count(NECRODOMINANCE))
            if DURESS in self.hand:
                imprint_list.extend([DURESS] * self.hand.count(DURESS))
            if BESEECH_MIRROR in self.hand:
                if TENDRILS_OF_AGONY in self.hand:
                    imprint_list.extend([BESEECH_MIRROR] * self.hand.count(BESEECH_MIRROR))
                elif self.hand.count(BESEECH_MIRROR) >= 2:
                    imprint_list.extend([BESEECH_MIRROR] * (self.hand.count(BESEECH_MIRROR) - 1))
            if CABAL_RITUAL in self.hand:
                imprint_list.extend([CABAL_RITUAL] * self.hand.count(CABAL_RITUAL))
            if DARK_RITUAL in self.hand:
                imprint_list.extend([DARK_RITUAL] * self.hand.count(DARK_RITUAL))
        return imprint_list
    
    # マナを生成できるか判定する関数
    # Return [マナを生成できるか、手札から使用したカード、Imprintしたカード]
    def can_generate_mana(self, mana_cost: str) -> tuple[bool, dict[str, int], list[str]]:
        # 手札から使用したカードの辞書
        cards_used = {
            ELVISH_SPIRIT_GUIDE: 0,
            SIMIAN_SPIRIT_GUIDE: 0,
            WILD_CANTOR: 0,
            LOTUS_PETAL: 0,
            CHROME_MOX: 0,
            DARK_RITUAL: 0,
            CABAL_RITUAL: 0
        }

        cards_imprinted = []

        if self.mana_pool.can_pay_mana(mana_cost):
            return [True, cards_used, cards_imprinted]
        
        tmp_pool = copy(self.mana_pool)
        required, generic = tmp_pool.analyze_mana_pattern(mana_cost)

        G_source = self.hand.count(ELVISH_SPIRIT_GUIDE)
        R_source = self.hand.count(SIMIAN_SPIRIT_GUIDE)
        B_source = self.battlefield.count(VAULT_OF_WHISPERS) + self.battlefield.count(CHROME_MOX)

        cards_used[ELVISH_SPIRIT_GUIDE] = G_source
        cards_used[SIMIAN_SPIRIT_GUIDE] = R_source

        tmp_pool.add_mana('G', G_source)
        tmp_pool.add_mana('R', R_source)
        tmp_pool.add_mana('B', B_source)
        
        any_mana_source = self.battlefield.count(GEMSTONE_MINE) + self.battlefield.count(UNDISCOVERED_PARADISE) + self.battlefield.count(LOTUS_PETAL) + self.battlefield.count(WILD_CANTOR)

        cards_to_count = [
            SUMMONERS_PACT, DARK_RITUAL, CABAL_RITUAL, WILD_CANTOR, LOTUS_PETAL, CHROME_MOX, NECRODOMINANCE, BESEECH_MIRROR, TENDRILS_OF_AGONY, DURESS
        ]
        hand_card_counts = {card: self.hand.count(card) for card in cards_to_count}

        deck_elvish_count = self.deck.count(ELVISH_SPIRIT_GUIDE)
        deck_cantor_count = self.deck.count(WILD_CANTOR)
        search_elvish_count = 0
        
        while hand_card_counts[SUMMONERS_PACT] > 0 and deck_elvish_count > 0:
            hand_card_counts[SUMMONERS_PACT] -= 1
            deck_elvish_count -= 1
            search_elvish_count += 1
            tmp_pool.add_mana('G', 1)
            cards_used[ELVISH_SPIRIT_GUIDE] += 1
        
        #self.debug(f'can_generate_mana: tmp mana pool {tmp_pool}')
        
        def try_search_cantor(pool: ManaPool) -> bool:
            nonlocal cards_used, deck_elvish_count, deck_cantor_count, search_elvish_count, hand_card_counts

            if deck_cantor_count <= 0:
                return False

            if hand_card_counts[SUMMONERS_PACT] > 0:
                hand_card_counts[SUMMONERS_PACT] -= 1
                deck_cantor_count -= 1
                hand_card_counts[WILD_CANTOR] += 1
                return True
            elif search_elvish_count > 0 and pool.can_pay_mana('G'):
                # Summoners PactでサーチしたElvishを戻してCantorをサーチしたことにする
                deck_elvish_count += 1
                search_elvish_count -= 1
                pool.pay_mana('G')
                cards_used[ELVISH_SPIRIT_GUIDE] -= 1

                deck_cantor_count -= 1
                hand_card_counts[WILD_CANTOR] += 1
                return True
            else:
                return False
        
        # Black以外のrequired manaを処理
        for color in ['R', 'G', 'W', 'U']:
            required_mana = required[color]

            if required_mana == 0:
                continue
            
            # tmp_poolの色マナが足りない場合
            while tmp_pool.get_colored_mana_count(color) < required_mana:
                if any_mana_source > 0:
                    any_mana_source -= 1
                    tmp_pool.add_mana(color, 1)
                    continue

                if self.can_cast_sorcery:
                    if hand_card_counts[LOTUS_PETAL] > 0:
                        hand_card_counts[LOTUS_PETAL] -= 1
                        cards_used[LOTUS_PETAL] += 1
                        any_mana_source += 1
                        continue
                    
                    if hand_card_counts[WILD_CANTOR] > 0:
                        if tmp_pool.can_pay_mana('G'):
                            tmp_pool.pay_mana('G')
                            hand_card_counts[WILD_CANTOR] -= 1
                            cards_used[WILD_CANTOR] += 1
                            any_mana_source += 1
                            continue
                        elif tmp_pool.can_pay_mana('R'):
                            tmp_pool.pay_mana('R')
                            hand_card_counts[WILD_CANTOR] -= 1
                            cards_used[WILD_CANTOR] += 1
                            any_mana_source += 1
                            continue
                    elif color != 'G' and try_search_cantor(tmp_pool):
                        continue
                
                # Failed: Not enough colored mana and can't generate more
                #self.debug(f'Failed: Not enough {color} mana. {tmp_pool}')
                return [False, cards_used, cards_imprinted]
            # その色のマナをtmp_poolから支払う
            tmp_pool.remove_mana(color, required_mana)
        
        # RGWUの必要な色マナはtmp_poolから支払った
        
        imprint_list = self.create_imprint_list() if self.can_cast_sorcery else []
        requiredB = required['B']

        # Black manaを支払う
        while tmp_pool.B < requiredB:
            if tmp_pool.can_pay_mana('B') and hand_card_counts[DARK_RITUAL] > 0:
                tmp_pool.pay_mana('B')
                tmp_pool.add_mana('B', 3)
                hand_card_counts[DARK_RITUAL] -= 1
                cards_used[DARK_RITUAL] += 1
                continue
            
            if tmp_pool.can_pay_mana('1B') and hand_card_counts[CABAL_RITUAL] > 0:
                tmp_pool.pay_mana('1B')
                tmp_pool.add_mana('B', 3)
                hand_card_counts[CABAL_RITUAL] -= 1
                cards_used[CABAL_RITUAL] += 1
                continue
            
            if any_mana_source > 0:
                any_mana_source -= 1
                tmp_pool.add_mana('B', 1)
                continue

            if self.can_cast_sorcery:
                if hand_card_counts[LOTUS_PETAL] > 0:
                    hand_card_counts[LOTUS_PETAL] -= 1
                    cards_used[LOTUS_PETAL] += 1
                    any_mana_source += 1
                    continue

                if hand_card_counts[WILD_CANTOR] > 0:
                    if tmp_pool.can_pay_mana('G'):
                        tmp_pool.pay_mana('G')
                        hand_card_counts[WILD_CANTOR] -= 1
                        cards_used[WILD_CANTOR] += 1
                        tmp_pool.add_mana('B', 1)
                        continue
                    elif tmp_pool.can_pay_mana('R'):
                        tmp_pool.pay_mana('R')
                        hand_card_counts[WILD_CANTOR] -= 1
                        cards_used[WILD_CANTOR] += 1
                        tmp_pool.add_mana('B', 1)
                        continue
                elif try_search_cantor(tmp_pool):
                    continue

                # Cast Chrome Mox
                if hand_card_counts[CHROME_MOX] > 0 and imprint_list:
                    imprint = imprint_list.pop(0)
                    hand_card_counts[imprint] -= 1
                    hand_card_counts[CHROME_MOX] -= 1
                    cards_used[CHROME_MOX] += 1
                    cards_imprinted.append(imprint)
                    tmp_pool.add_mana('B', 1)
                    continue
            
            return [False, cards_used, cards_imprinted]
        
        # 必要な黒マナは生成したがtmp_poolから支払っていない
        
        # genericマナが足りない場合、Dark Ritualなどを唱える
        while tmp_pool.get_total() < requiredB + generic:
            if tmp_pool.can_pay_mana('B') and hand_card_counts[DARK_RITUAL] > 0:
                # cast dark ritual
                tmp_pool.pay_mana('B')
                tmp_pool.add_mana('B', 3)
                hand_card_counts[DARK_RITUAL] -= 1
                cards_used[DARK_RITUAL] += 1
                continue
            
            if tmp_pool.can_pay_mana('1B') and hand_card_counts[CABAL_RITUAL] > 0:
                # cast cabal ritual
                tmp_pool.pay_mana('1B')
                tmp_pool.add_mana('B', 3)
                hand_card_counts[CABAL_RITUAL] -= 1
                cards_used[CABAL_RITUAL] += 1
                continue
            
            # Generate B from any mana source
            if any_mana_source > 0:
                any_mana_source -= 1
                tmp_pool.add_mana('B', 1)
                continue
            
            if self.can_cast_sorcery:
                if hand_card_counts[CHROME_MOX] > 0 and imprint_list:
                    imprint = imprint_list.pop(0)
                    hand_card_counts[imprint] -= 1
                    hand_card_counts[CHROME_MOX] -= 1
                    cards_used[CHROME_MOX] += 1
                    cards_imprinted.append(imprint)
                    tmp_pool.add_mana('B', 1)
                    continue

                if hand_card_counts[LOTUS_PETAL] > 0:
                    hand_card_counts[LOTUS_PETAL] -= 1
                    cards_used[LOTUS_PETAL] += 1
                    any_mana_source += 1
                    continue
            
            #self.debug(f'Failed: not enough generic mana. {tmp_pool}')
            return [False, cards_used, cards_imprinted]
        
        # Blackマナとgenericマナをtmp_poolから支払う
        tmp_pool.pay_pattern({'B': requiredB}, generic)
        # 余ったGとRマナをcards_usedから引く
        cards_used[ELVISH_SPIRIT_GUIDE] -= tmp_pool.G
        cards_used[SIMIAN_SPIRIT_GUIDE] -= tmp_pool.R
        return [True, cards_used, cards_imprinted]
    
    def generate_mana(self, mana_cost: str, cards_to_use: dict[str, int], cards_to_imprint: list[str]) -> bool:
        """Generate mana to pay specified mana cost
        mana_cost: String representing required mana (e.g., '1U')
        """
        # Analyze required mana
        required, generic = self.mana_pool.analyze_mana_pattern(mana_cost)

        if self.mana_pool.can_pay_pattern(required, generic):
            return True
        
        elvish_count = cards_to_use[ELVISH_SPIRIT_GUIDE]
        simian_count = cards_to_use[SIMIAN_SPIRIT_GUIDE]
        petal_count = cards_to_use[LOTUS_PETAL]
        cantor_count = cards_to_use[WILD_CANTOR]
        dark_count = cards_to_use[DARK_RITUAL]
        cabal_count = cards_to_use[CABAL_RITUAL]
        chrome_count = cards_to_use[CHROME_MOX]

        # Elvishが足りない場合Summoner's Pactでサーチ
        while self.hand.count(ELVISH_SPIRIT_GUIDE) < elvish_count and\
        SUMMONERS_PACT in self.hand and ELVISH_SPIRIT_GUIDE in self.deck:
            self.cast_summoners_pact(ELVISH_SPIRIT_GUIDE)
        
        while elvish_count > 0 and ELVISH_SPIRIT_GUIDE in self.hand:
            self.hand.remove(ELVISH_SPIRIT_GUIDE)
            self.graveyard.append(ELVISH_SPIRIT_GUIDE)
            self.mana_pool.add_mana('G')
            elvish_count -= 1
        
        while simian_count > 0 and SIMIAN_SPIRIT_GUIDE in self.hand:
            self.hand.remove(SIMIAN_SPIRIT_GUIDE)
            self.graveyard.append(SIMIAN_SPIRIT_GUIDE)
            self.mana_pool.add_mana('R')
            simian_count -= 1
        
        if self.can_cast_sorcery:
            while petal_count > 0 and LOTUS_PETAL in self.hand:
                self.cast_lotus_petal()
                petal_count -= 1
            
            while chrome_count > 0 and CHROME_MOX in self.hand and cards_to_imprint:
                imprint = cards_to_imprint.pop()
                self.cast_chrome_mox(imprint)
                chrome_count -= 1
            
            # 手札のWild Cantorが足りない場合Summoner's Pactでサーチ
            while self.hand.count(WILD_CANTOR) < cantor_count and\
                  SUMMONERS_PACT in self.hand and WILD_CANTOR in self.deck:
                self.cast_summoners_pact(WILD_CANTOR)
        
        # 支払ったマナを一時的に入れておくマナプール
        paid_mana_pool = ManaPool()

        # 戦場にあるany mana sourceから色マナを生成する関数
        def generate_mana_from_any_source(color: str) -> bool:
            for any_mana_source in [GEMSTONE_MINE, UNDISCOVERED_PARADISE, WILD_CANTOR, LOTUS_PETAL]:
                if any_mana_source in self.battlefield:
                    if any_mana_source == LOTUS_PETAL:
                        self.use_lotus_petal(color)
                    else:
                        self.battlefield.remove(any_mana_source)
                        self.graveyard.append(any_mana_source)
                        self.mana_pool.add_mana(color)
                    return True
            return False
        
        def cast_cantor() -> bool:
            nonlocal cantor_count
            if cantor_count > 0 and WILD_CANTOR in self.hand:
                if self.mana_pool.can_pay_mana('G'):
                    self.mana_pool.pay_mana('G')
                    self.cast_wild_cantor()
                    cantor_count -= 1
                    return True
                elif self.mana_pool.can_pay_mana('R'):
                    self.mana_pool.pay_mana('R')
                    self.cast_wild_cantor()
                    cantor_count -= 1
                    return True
            return False
        
        for color in ['G', 'R', 'W', 'U']:
            required_mana = required[color]

            if required_mana == 0:
                continue
            
            # mana poolの色マナが足りない間ループ
            while self.mana_pool.get_colored_mana_count(color) < required_mana:
                if generate_mana_from_any_source(color):
                    continue
                
                if self.can_cast_sorcery and cast_cantor():
                    continue
                
                return False
            
            self.mana_pool.remove_mana(color, required_mana)
            paid_mana_pool.add_mana(color, required_mana)
        
        # RGWUの必要な色マナは支払い済み
        # Black manaとgeneric manaを生成する
        while self.mana_pool.B < required['B'] or self.mana_pool.get_total() < required['B'] + generic:
            if VAULT_OF_WHISPERS in self.battlefield:
                self.use_vault_of_whispers()
                continue

            if CHROME_MOX in self.battlefield:
                self.use_chrome_mox()
                continue

            if self.mana_pool.B >= 1 and dark_count > 0 and DARK_RITUAL in self.hand:
                self.mana_pool.pay_mana('B')
                self.cast_dark_ritual()
                dark_count -= 1
                continue

            if self.mana_pool.can_pay_mana('1B') and cabal_count > 0 and CABAL_RITUAL in self.hand:
                self.mana_pool.pay_mana('1B')
                self.cast_cabal_ritual()
                cabal_count -= 1
                continue
            
            if generate_mana_from_any_source('B'):
                continue

            if self.can_cast_sorcery and cast_cantor():
                continue

            return False
        
        # 支払ってpaid_mana_poolに入れたマナをself.mana_poolに戻す
        self.mana_pool.transfer_from(paid_mana_pool)
        return True
    
    def try_generate_mana(self, mana_cost: str) -> bool:
        result, cards_to_use, cards_to_imprint = self.can_generate_mana(mana_cost)
        #self.debug(f'try_generate_mana: {mana_cost} result: {result} can_cast_sorcery: {self.can_cast_sorcery}')
        if result:
            return self.generate_mana(mana_cost, cards_to_use, cards_to_imprint)
        else:
            return False
    
    def try_pay_mana(self, mana_cost: str) -> bool:
        if self.try_generate_mana(mana_cost):
            self.mana_pool.pay_mana(mana_cost)
            return True
        else:
            return False
    
    def try_sacrifice_bargain(self) -> bool:
        if not self.bargain:
            return False
        
        if NECRODOMINANCE in self.bargain and NECRODOMINANCE in self.battlefield:
            self.bargain.remove(NECRODOMINANCE)
            self.battlefield.remove(NECRODOMINANCE)
            self.graveyard.append(NECRODOMINANCE)
            return True
        
        if VAULT_OF_WHISPERS in self.bargain:
            if VAULT_OF_WHISPERS in self.graveyard:
                self.bargain.remove(VAULT_OF_WHISPERS)
                self.graveyard.remove(VAULT_OF_WHISPERS)
                return True
            elif VAULT_OF_WHISPERS in self.battlefield:
                self.bargain.remove(VAULT_OF_WHISPERS)
                self.battlefield.remove(VAULT_OF_WHISPERS)
                return True
        
        if CHROME_MOX in self.bargain:
            if CHROME_MOX in self.graveyard:
                self.bargain.remove(CHROME_MOX)
                self.graveyard.remove(CHROME_MOX)
                return True
            elif CHROME_MOX in self.battlefield:
                self.bargain.remove(CHROME_MOX)
                self.battlefield.remove(CHROME_MOX)
                return True
        
        if LOTUS_PETAL in self.bargain and LOTUS_PETAL in self.battlefield:
            self.bargain.remove(LOTUS_PETAL)
            self.battlefield.remove(LOTUS_PETAL)
            self.graveyard.append(LOTUS_PETAL)
            return True
        
        return False
    
    def use_vault_of_whispers(self):
        self.battlefield.remove(VAULT_OF_WHISPERS)
        self.graveyard.append(VAULT_OF_WHISPERS)
        self.mana_pool.add_mana('B')
    
    def cast_summoners_pact(self, target: str):
        self.hand.remove(SUMMONERS_PACT)
        self.graveyard.append(SUMMONERS_PACT)

        if target in self.deck:
            self.deck.remove(target)
            self.hand.append(target)
        
        self.storm_count += 1
        self.debug(f"Cast {SUMMONERS_PACT} (Search {target})")
    
    def cast_wild_cantor(self):
        self.debug(f"Cast {WILD_CANTOR}")
        self.hand.remove(WILD_CANTOR)
        self.battlefield.append(WILD_CANTOR)
        self.storm_count += 1
    
    def cast_manamorphose(self, output_mana):
        """Process Manamorphose mana payment and effects
        output_mana: String representing mana to generate (e.g., 'UB')
        """
        # Move Manamorphose to graveyard
        self.hand.remove(MANAMORPHOSE)
        self.graveyard.append(MANAMORPHOSE)
        self.storm_count += 1
        
        # Add mana
        for color in output_mana:
            self.mana_pool.add_mana(color)
        
        self.debug(f"Cast {MANAMORPHOSE} (Generate: {output_mana} Floating: {self.mana_pool})")
        
        # Draw a card
        self.draw_cards(1)
    
    def cast_borne_upon_a_wind(self):
        self.debug(f"Cast {BORNE_UPON_WIND} (Floating: {self.mana_pool})")
        self.hand.remove(BORNE_UPON_WIND)
        self.graveyard.append(BORNE_UPON_WIND)
        self.storm_count += 1

        self.draw_cards(1)
        self.did_cast_wind = True
        self.can_cast_sorcery = True
    
    def cast_dark_ritual(self):
        self.debug(f"Cast {DARK_RITUAL}")
        self.hand.remove(DARK_RITUAL)
        self.graveyard.append(DARK_RITUAL)
        self.storm_count += 1
        self.mana_pool.add_mana('B', 3)
    
    def cast_cabal_ritual(self):
        self.debug(f"Cast {CABAL_RITUAL}")
        self.hand.remove(CABAL_RITUAL)
        self.graveyard.append(CABAL_RITUAL)
        self.storm_count += 1
        self.mana_pool.add_mana('B', 3)
    
    def cast_lotus_petal(self):
        self.debug(f"Cast {LOTUS_PETAL}")
        self.hand.remove(LOTUS_PETAL)
        self.battlefield.append(LOTUS_PETAL)
        self.bargain.append(LOTUS_PETAL)
        self.storm_count += 1
    
    def use_lotus_petal(self, color: str):
        self.battlefield.remove(LOTUS_PETAL)
        self.graveyard.append(LOTUS_PETAL)
        self.bargain.remove(LOTUS_PETAL)
        self.mana_pool.add_mana(color)
    
    def cast_chrome_mox(self, imprint: str):
        self.debug(f"Cast {CHROME_MOX} (Imprint: {imprint})")
        self.hand.remove(CHROME_MOX)
        if imprint:
            self.hand.remove(imprint)
            self.graveyard.append(imprint)
            self.battlefield.append(CHROME_MOX)
        else:
            # no imprint
            self.graveyard.append(CHROME_MOX)
        
        self.bargain.append(CHROME_MOX)
        self.storm_count += 1
    
    def use_chrome_mox(self):
        self.battlefield.remove(CHROME_MOX)
        self.graveyard.append(CHROME_MOX)
        self.mana_pool.add_mana('B')
    
    def cast_valakut(self, cards_to_remove: list):
        self.hand.remove(VALAKUT_AWAKENING)
        self.graveyard.append(VALAKUT_AWAKENING)
        self.storm_count += 1

        for card in cards_to_remove:
            self.hand.remove(card)
        
        self.debug(f"Cast {VALAKUT_AWAKENING} (Floating: {self.mana_pool}, Keep: {', '.join(self.hand)})")
        count = len(cards_to_remove)
        self.deck.extend(cards_to_remove)
        self.draw_cards(count+1)
        self.did_cast_valakut = True
    
    def cast_beseech(self):
        self.debug(f"Cast {BESEECH_MIRROR}")
        self.hand.remove(BESEECH_MIRROR)
        self.graveyard.append(BESEECH_MIRROR)
        self.storm_count += 1
    
    def cast_tendril(self, cast_from_hand: bool):
        self.debug(f"Cast {TENDRILS_OF_AGONY} (Storm Count: {self.storm_count})")
        if cast_from_hand:
            self.hand.remove(TENDRILS_OF_AGONY)
        else:
            self.deck.remove(TENDRILS_OF_AGONY)
        self.graveyard.append(TENDRILS_OF_AGONY)
        self.storm_count += 1
        self.did_cast_tendril = True
    
    def cast_pact_of_negation(self):
        self.debug(f"Cast {PACT_OF_NEGATION}")
        self.hand.remove(PACT_OF_NEGATION)
        self.graveyard.append(PACT_OF_NEGATION)
        self.storm_count += 1
    
    def cast_necro(self, cast_from_hand: bool):
        self.debug(f"Cast {NECRODOMINANCE}")
        if cast_from_hand:
            self.hand.remove(NECRODOMINANCE)
        else:
            self.deck.remove(NECRODOMINANCE)
        self.battlefield.append(NECRODOMINANCE)
        self.bargain.append(NECRODOMINANCE)
        self.storm_count += 1
        self.did_cast_necro = True
    
    def main_phase(self) -> bool:
        self.can_cast_sorcery = True

        if NECRODOMINANCE not in self.hand and BESEECH_MIRROR not in self.hand:
            self.loss_reason = FALIED_NECRO
            return False

        copy_state = copy(self)

        lands = []
        if GEMSTONE_MINE in self.hand:
            lands.append(GEMSTONE_MINE)
        elif UNDISCOVERED_PARADISE in self.hand:
            lands.append(UNDISCOVERED_PARADISE)
        if VAULT_OF_WHISPERS in self.hand:
            lands.append(VAULT_OF_WHISPERS)
        if not lands:
            lands.append("None")
        
        for land in lands:
            # GameStateをリセット
            self.copy_from(copy_state)
            if land != "None":
                self.hand.remove(land)
                self.battlefield.append(land)
                self.debug(f"set land {land}")
                if land == VAULT_OF_WHISPERS:
                    self.bargain.append(VAULT_OF_WHISPERS)
            
            while not self.is_main_phase_loop_completed():
                continue

            if self.did_cast_necro:
                break
        
        if self.mana_pool.U > 0:
            self.reserved_mana_pool.add_mana('U', self.mana_pool.U)
        
        if self.did_cast_necro:
            while LOTUS_PETAL in self.hand:
                self.cast_lotus_petal()
            return True
        else:
            self.loss_reason = FALIED_NECRO
            return False
    
    # Return true to end loop
    def is_main_phase_loop_completed(self) -> bool:
        if NECRODOMINANCE in self.hand:
            mana_patterns = ['UBBB', 'BBB']
            for pattern in mana_patterns:
                if self.try_generate_mana(pattern):
                    self.mana_pool.pay_mana('BBB')
                    # Cast Necro from hand
                    self.cast_necro(True)
                    return True
        elif BESEECH_MIRROR in self.hand:
            mana_patterns = ['1UBBB', '1BBB']
            for pattern in mana_patterns:
                copy_state = copy(self)
                if self.try_generate_mana(pattern):
                    if self.try_sacrifice_bargain():
                        self.mana_pool.pay_mana('1BBB')
                        self.cast_beseech()
                        # Cast Necro from deck
                        self.cast_necro(False)
                        return True
                    else:
                        if CHROME_MOX in self.hand:
                            self.cast_chrome_mox('')
                            return False
                        elif LOTUS_PETAL in self.hand:
                            self.cast_lotus_petal()
                            return False
                        else:
                            # マナは生成したがbargainがない場合、GameStateをマナ生成前にリセット
                            self.copy_from(copy_state)
            
            mana_patterns = ['1UBBBBBB', '1BBBBBB']
            for pattern in mana_patterns:
                if self.try_generate_mana(pattern):
                    self.mana_pool.pay_mana('1BBBBBB')
                    self.cast_beseech()
                    # Search Necro from deck
                    self.deck.remove(NECRODOMINANCE)
                    self.hand.append(NECRODOMINANCE)
                    self.cast_necro(True)
                    return True
        
        if MANAMORPHOSE in self.hand and\
            (self.try_pay_mana('1G') or self.try_pay_mana('1R')):
            self.cast_manamorphose('BB')
            return False
        
        # Failure
        return True

    def end_step(self, draw_count: int) -> bool:
        self.can_cast_sorcery = False
        self.mana_pool.clear()
        self.mana_pool.transfer_from(self.reserved_mana_pool)

        self.draw_cards(draw_count)
        
        # Show drawn cards
        self.debug("\n=== Initial Hand ===")
        for card in self.hand:
            self.debug(card)
        self.debug("==================\n")
        
        # Basic validation
        result = self.validate_hand()
        if not result:
            return False
        
        # Main loop
        while not self.is_end_step_loop_completed():
            continue
        
        return self.did_cast_tendril
    
    # Return True to end loop
    def is_end_step_loop_completed(self) -> bool:
        # Summoner's Pactが手札にあり、デッキのElvishとCantorの枚数よりも手札のSummoner's Pactの枚数が多い場合
        if SUMMONERS_PACT in self.hand and self.deck.count(ELVISH_SPIRIT_GUIDE) + self.deck.count(WILD_CANTOR) <= self.hand.count(SUMMONERS_PACT):
            did_cast_summoners_pact = False
            while SUMMONERS_PACT in self.hand:
                if ELVISH_SPIRIT_GUIDE in self.deck:
                    self.cast_summoners_pact(ELVISH_SPIRIT_GUIDE)
                    did_cast_summoners_pact = True
                elif WILD_CANTOR in self.deck:
                    self.cast_summoners_pact(WILD_CANTOR)
                    did_cast_summoners_pact = True
                else:
                    break
            if did_cast_summoners_pact:
                return False
        
        self.imprint_priority = [NECRODOMINANCE, BESEECH_MIRROR, DURESS, CABAL_RITUAL, DARK_RITUAL]
        if TENDRILS_OF_AGONY not in self.hand and self.hand.count(BESEECH_MIRROR) == 1:
            # Tendrilが手札になく、Beseechが1枚しかないならBeseechをImprintしない
            self.imprint_priority.remove(BESEECH_MIRROR)
        
        if MANAMORPHOSE in self.hand:
            if self.try_pay_mana('1G') or self.try_pay_mana('1R'):
                output_mana = 'UB'
                if self.did_cast_wind:
                    # Borne upon a Windを唱えた後はUは不要
                    if not self.can_generate_mana('R')[0]:
                        output_mana = 'BR'
                    else:
                        output_mana = 'BB'
                else:
                    # Borne upon a Windをまだ唱えていないのでUが必要
                    if BORNE_UPON_WIND in self.hand:
                        if not self.can_generate_mana('U')[0]:
                            output_mana = 'UB'
                        else:
                            output_mana = 'BR'
                    elif VALAKUT_AWAKENING in self.hand:
                        if not self.can_generate_mana('R')[0]:
                            output_mana = 'BR'
                        else:
                            output_mana = 'UB'
                    else:
                        if not self.can_generate_mana('U')[0]:
                            output_mana = 'UB'
                        else:
                            output_mana = 'BR'
                # Cast Manamorphose
                self.cast_manamorphose(output_mana)
                return False
        
        if self.did_cast_wind:
            # After casting Borne Upon a Wind
            if BESEECH_MIRROR in self.hand or TENDRILS_OF_AGONY in self.hand:
                mana_cost = '2BB' if TENDRILS_OF_AGONY in self.hand else '1BBB'
                required_storm_count = 9 if TENDRILS_OF_AGONY in self.hand else 8

                if self.try_generate_mana(mana_cost):
                    #self.debug(f'did generate {mana_cost} to cast tendril after wind.')
                    did_cast_0 = False
                    while LOTUS_PETAL in self.hand:
                        self.cast_lotus_petal()
                        did_cast_0 = True
                    
                    while CHROME_MOX in self.hand:
                        self.cast_chrome_mox('')
                        did_cast_0 = True
                    
                    while DARK_RITUAL in self.hand and self.mana_pool.can_pay_mana('B'):
                        self.mana_pool.pay_mana('B')
                        self.cast_dark_ritual()
                    
                    while CABAL_RITUAL in self.hand and self.mana_pool.can_pay_mana('1B'):
                        self.mana_pool.pay_mana('1B')
                        self.cast_cabal_ritual()
                    
                    if did_cast_0 or self.hand.count(PACT_OF_NEGATION) >= 2:
                        while PACT_OF_NEGATION in self.hand:
                            self.cast_pact_of_negation()
                    
                    self.debug(f"Floating: {self.mana_pool}")
                    
                    if required_storm_count <= self.storm_count:
                        if TENDRILS_OF_AGONY in self.hand:
                            self.mana_pool.pay_mana('2BB')
                            self.cast_tendril(True)
                            return True
                        elif BESEECH_MIRROR in self.hand and self.try_sacrifice_bargain():
                            self.mana_pool.pay_mana('1BBB')
                            self.cast_beseech()
                            self.cast_tendril(False)
                            return True
            
            if VALAKUT_AWAKENING in self.hand:
                self.debug(f'{VALAKUT_AWAKENING} in hand after wind.')
                mana_patterns = ['2RBBB', '2RBB', '2RB', '2R']
                b_generate_mana = False
                for cost in mana_patterns:
                    if self.try_generate_mana(cost):
                        b_generate_mana = True
                        break
                
                #self.debug(f'b_generate_mana = {b_generate_mana} to cast {VALAKUT_AWAKENING}.')
                
                if b_generate_mana:
                    self.mana_pool.pay_mana('2R')
                    cards_to_remove = self.hand.copy()
                    cards_to_remove.remove(VALAKUT_AWAKENING)
                    if TENDRILS_OF_AGONY in self.hand:
                        cards_to_remove.remove(TENDRILS_OF_AGONY)
                    elif BESEECH_MIRROR in self.hand:
                        cards_to_remove.remove(BESEECH_MIRROR)
                    self.cast_valakut(cards_to_remove)
                    return False
            
            if BORNE_UPON_WIND in self.hand:
                if self.try_pay_mana('1U'):
                    self.cast_borne_upon_a_wind()
                    return False

        else:
            # Haven't cast Borne Upon a Wind
            if BORNE_UPON_WIND in self.hand:
                mana_patterns = ['1UBBB', '1UBB', '1UB', '1U']
                if TENDRILS_OF_AGONY not in self.hand and BESEECH_MIRROR not in self.hand and VALAKUT_AWAKENING in self.hand:
                    # TendrilもBeseechもhandになく、Valakutがある場合はRを浮かせたい
                    mana_patterns = ['3URB', '2URB', '1URB', '3UR', '2UR', '1UR', '1UB','1U']
                b_generate_mana = False
                for mana_cost in mana_patterns:
                    if self.try_generate_mana(mana_cost):
                        b_generate_mana = True
                        break
                
                if b_generate_mana:
                    self.mana_pool.pay_mana('1U')
                    self.cast_borne_upon_a_wind()
                    return False
            
            if VALAKUT_AWAKENING in self.hand:
                # Borne Upon a WindのためにUを浮かせたい
                mana_patterns = ['3UR', '2UR', '3RR', '3RG', '2RR', '2RG', '2R']
                b_generate_mana = False
                for cost in mana_patterns:
                    if self.try_generate_mana(cost):
                        b_generate_mana = True
                        break
                
                if b_generate_mana:
                    self.mana_pool.pay_mana('2R')
                    cards_to_remove = self.hand.copy()
                    cards_to_remove.remove(VALAKUT_AWAKENING)
                    if BORNE_UPON_WIND in self.hand:
                        cards_to_remove.remove(BORNE_UPON_WIND)
                    if TENDRILS_OF_AGONY in self.hand:
                        cards_to_remove.remove(TENDRILS_OF_AGONY)
                    elif BESEECH_MIRROR in self.hand:
                        cards_to_remove.remove(BESEECH_MIRROR)
                    self.cast_valakut(cards_to_remove)
                    return False
        
        # Break and fail if nothing was done
        if not self.did_cast_tendril:
            if not self.did_cast_wind:
                if self.did_cast_valakut:
                    self.loss_reason = FAILED_WIND_AFTER_VALAKUT
                else:
                    self.loss_reason = FAILED_VALAKUT_AND_WIND
            else:
                self.loss_reason = FAILED_TENDRILS_AFTER_WIND
        
        return True

    def run(self, deck: list[str], initial_hand: list[str], draw_count: int) -> bool:
        # デッキが60枚かどうかをチェック
        if len(deck) != 60:
            self.debug(f"Error: Deck must contain exactly 60 cards. Current deck has {len(deck)} cards.")
            self.loss_reason = "Invalid deck size"
            return False
        
        self.reset_game()
        self.deck = deck.copy()
        
        if initial_hand:
            self.hand = initial_hand.copy()
            for card in self.hand:
                self.deck.remove(card)
        else:
            self.draw_cards(7)
        
        if not self.main_phase():
            self.debug("Failed to cast Necrodominance.")
            return False
        
        if self.end_step(draw_count):
            self.debug("You Win.")
            return True
        else:
            self.debug("You Lose.")
            return False

if __name__ == "__main__":
    game = GameState()
    deck = create_deck('decks/wind4_valakut2_cantor1.txt')
    random.shuffle(deck)
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE]
    game.run(deck, initial_hand, 19)
