import random
import csv
import os
from deck_utils import create_deck
from mana_pool import ManaPool
from mana_sources import ManaSources
from mana_generation_state import ManaGenerationState
from card_constants import *

class GameState:
    def __init__(self):
        self.debug_print = True  # Print control flag
        self.shuffle_enabled = True

        self.mana_pool = ManaPool()
        self.mana_source = ManaSources(self.mana_pool)
        self.mana_source.did_generate_any_mana = self.did_generate_any_mana

        self.reset_game()
    
    def reset_game(self):
        self.mana_pool.clear()
        self.mana_source.clear()

        self.deck = []
        self.hand = []
        self.battlefield = []
        self.graveyard = []
        self.any_mana_sources = []
        self.used_any_mana_sources = [] # 使用済みのAny Mana Source

        self.mulligan_count = 0 # マリガンした回数
        self.return_count = 0 # マリガンで戻すカードの枚数
        self.storm_count = 0
        self.did_shuffle = False
        self.can_cast_sorcery = False
        self.did_cast_necro = False
        self.did_cast_valakut = False
        self.did_cast_wind = False
        self.did_cast_tendril = False
        self.loss_reason = ''

        self.mana_patterns_valakut_before_wind = ['3UR', '2UR', '2R']
        self.mana_patterns_valakut_after_wind = ['2RBB', '3RB', '2RB', '2R']
        # wind唱えた後はpetalなどを使えるので無理に色マナを浮かせなくて良い
        self.mana_patterns_wind_with_beseech = ['1UBB', '1UB', '3U', '2U', '1U']
        self.mana_patterns_wind_with_valakut = ['3URB', '2URB', '3UR', '2UR', '1UR', '3U', '2U', '1U']
        self.mana_patterns_wind_without_beseech_and_valakut = ['1UBR', '1UB', '1UR', '3U', '2U', '1U']
    
    def copy(self):
        new_instance = GameState()
        new_instance.copy_from(self)
        return new_instance
    
    def copy_from(self, other):
        self.debug_print = other.debug_print
        self.shuffle_enabled = other.shuffle_enabled
        
        self.mana_pool = other.mana_pool.copy()
        self.mana_source = other.mana_source.copy()
        self.mana_source.mana_pool = self.mana_pool
        self.mana_source.did_generate_any_mana = self.did_generate_any_mana

        self.deck = other.deck.copy()
        self.hand = other.hand.copy()
        self.battlefield = other.battlefield.copy()
        self.graveyard = other.graveyard.copy()
        self.any_mana_sources = other.any_mana_sources.copy()
        self.used_any_mana_sources = other.used_any_mana_sources.copy()
        
        self.mulligan_count = other.mulligan_count
        self.return_count = other.return_count
        self.storm_count = other.storm_count
        self.did_shuffle = other.did_shuffle
        self.can_cast_sorcery = other.can_cast_sorcery
        self.did_cast_necro = other.did_cast_necro
        self.did_cast_valakut = other.did_cast_valakut
        self.did_cast_wind = other.did_cast_wind
        self.did_cast_tendril = other.did_cast_tendril
        self.loss_reason = other.loss_reason

        self.mana_patterns_valakut_before_wind = other.mana_patterns_valakut_before_wind
        self.mana_patterns_valakut_after_wind = other.mana_patterns_valakut_after_wind
        self.mana_patterns_wind_with_beseech = other.mana_patterns_wind_with_beseech
        self.mana_patterns_wind_with_valakut = other.mana_patterns_wind_with_valakut
        self.mana_patterns_wind_without_beseech_and_valakut = other.mana_patterns_wind_without_beseech_and_valakut
    
    def shuffle_deck(self):
        if self.shuffle_enabled:
            random.shuffle(self.deck)
            self.did_shuffle = True
    
    # Any Mana Sourceを追加する
    def add_any_mana_source(self, mana_source: str):
        self.mana_source.ANY += 1
        self.any_mana_sources.append(mana_source)
    
    # Any Manaを生成したコールバック
    def did_generate_any_mana(self):
        if GEMSTONE_MINE in self.any_mana_sources:
            self.any_mana_sources.remove(GEMSTONE_MINE)
            self.used_any_mana_sources.append(GEMSTONE_MINE)
        elif UNDISCOVERED_PARADISE in self.any_mana_sources:
            self.any_mana_sources.remove(UNDISCOVERED_PARADISE)
            self.used_any_mana_sources.append(UNDISCOVERED_PARADISE)
        elif WILD_CANTOR in self.any_mana_sources:
            self.any_mana_sources.remove(WILD_CANTOR)
            self.used_any_mana_sources.append(WILD_CANTOR)
            self.battlefield.remove(WILD_CANTOR)
            self.graveyard.append(WILD_CANTOR)
        elif LOTUS_PETAL in self.any_mana_sources:
            self.any_mana_sources.remove(LOTUS_PETAL)
            self.used_any_mana_sources.append(LOTUS_PETAL)
            self.battlefield.remove(LOTUS_PETAL)
            self.graveyard.append(LOTUS_PETAL)
    
    # colorを出すために使用したAny Mana Sourceを元に戻す
    def revert_used_any_mana_source(self, color: str):
        self.mana_source.ANY += 1
        # any_mana_colorsから指定された色を1つだけ削除
        if color in self.mana_source.any_mana_colors:
            self.mana_source.any_mana_colors.remove(color)
        card = self.used_any_mana_sources.pop()
        self.any_mana_sources.append(card)
        if card == WILD_CANTOR or card == LOTUS_PETAL:
            self.graveyard.remove(card)
            self.battlefield.append(card)
    
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
    
    def get_cards_to_imprint(self, casting_cards: list[str]) -> list:
        if not self.can_cast_sorcery or CHROME_MOX not in self.hand:
            return []
        
        unimprintables = [GEMSTONE_MINE, UNDISCOVERED_PARADISE, VAULT_OF_WHISPERS, CHROME_MOX, LOTUS_PETAL, ELVISH_SPIRIT_GUIDE, SIMIAN_SPIRIT_GUIDE, TENDRILS_OF_AGONY]
        cards = [card for card in self.hand if card not in unimprintables]
        cards_removed = []

        if not self.did_cast_necro:
            # Necro設置前
            if NECRODOMINANCE in cards:
                cards.remove(NECRODOMINANCE)
                cards_removed.append(NECRODOMINANCE)
            elif BESEECH_MIRROR in cards:
                cards.remove(BESEECH_MIRROR)
                cards_removed.append(BESEECH_MIRROR)
        else:
            # Necro設置後
            if TENDRILS_OF_AGONY not in self.hand and BESEECH_MIRROR in cards:
                cards.remove(BESEECH_MIRROR)
                cards_removed.append(BESEECH_MIRROR)
        
        for card in casting_cards:
            if card in cards and card not in cards_removed:
                cards.remove(card)
                cards_removed.append(card)
        
        return cards
    
    def create_mana_generation_state(self, cards_to_imprint: list[str]) -> ManaGenerationState:
        state = ManaGenerationState(
            mana_pool=self.mana_pool.copy(),
            any_mana_source=self.mana_source.ANY,
            hand=self.hand.copy(),
            deck=self.deck.copy(),
            cards_to_imprint=cards_to_imprint,
            can_cast_sorcery=self.can_cast_sorcery,
            cards_used_from_hand=None, cards_imprinted=None, cards_searched=None)
        
        # ManaSourcesからstate.poolにマナを移動
        state.mana_pool.W += self.mana_source.W
        state.mana_pool.U += self.mana_source.U
        state.mana_pool.B += self.mana_source.B
        state.mana_pool.R += self.mana_source.R
        state.mana_pool.G += self.mana_source.G
        
        return state
    
    def generate_mana_pattern(self, required: dict[str, int], generic: int, cards_to_use: list[str], cards_to_imprint: list[str], cards_to_search: list[str]) -> tuple[bool, str]:
        while cards_to_search and SUMMONERS_PACT in self.hand:
            card = cards_to_search.pop()
            self.cast_summoners_pact(card)
            cards_to_use.remove(SUMMONERS_PACT)
        
        while cards_to_imprint and CHROME_MOX in self.hand:
            imprint = cards_to_imprint.pop()
            self.cast_chrome_mox(imprint)
            color = get_card_color(imprint)
            self.mana_source.generate_mana(color)
            cards_to_use.remove(CHROME_MOX)
        
        while ELVISH_SPIRIT_GUIDE in cards_to_use and ELVISH_SPIRIT_GUIDE in self.hand:
            self.hand.remove(ELVISH_SPIRIT_GUIDE)
            self.graveyard.append(ELVISH_SPIRIT_GUIDE)
            self.mana_pool.add_mana('G')
            cards_to_use.remove(ELVISH_SPIRIT_GUIDE)
        
        while SIMIAN_SPIRIT_GUIDE in cards_to_use and SIMIAN_SPIRIT_GUIDE in self.hand:
            self.hand.remove(SIMIAN_SPIRIT_GUIDE)
            self.graveyard.append(SIMIAN_SPIRIT_GUIDE)
            self.mana_pool.add_mana('R')
            cards_to_use.remove(SIMIAN_SPIRIT_GUIDE)
        
        while LOTUS_PETAL in cards_to_use and LOTUS_PETAL in self.hand:
            self.cast_lotus_petal()
            cards_to_use.remove(LOTUS_PETAL)
        
        if self.mana_pool.can_pay_pattern(required, generic):
            return (True, "")
        
        tmp_pool = ManaPool()

        for color in ['R', 'G', 'W', 'U']:
            required_count = required[color]
            if required_count == 0:
                continue

            while self.mana_pool.get_colored_mana_count(color) < required_count:
                if self.mana_source.can_generate_mana(color):
                    self.mana_source.generate_mana(color)
                    continue
                elif WILD_CANTOR in cards_to_use and WILD_CANTOR in self.hand:
                    if self.mana_pool.can_pay_mana('G'):
                        self.mana_pool.pay_mana('G')
                        self.cast_wild_cantor()
                        cards_to_use.remove(WILD_CANTOR)
                        continue
                    if self.mana_pool.can_pay_mana('R'):
                        self.mana_pool.pay_mana('R')
                        self.cast_wild_cantor()
                        cards_to_use.remove(WILD_CANTOR)
                        continue
                '''
                error_msg = f"ERROR in generate_mana_pattern: Failed to generate enough {color} mana\n"
                error_msg += f"required: {required_count}, current: {self.mana_pool.get_colored_mana_count(color)}\n"
                error_msg += f"mana_pool: {self.mana_pool}, mana_source: {self.mana_source}\n"
                error_msg += f"cards_to_use: {cards_to_use}, hand: {self.hand}"
                print(error_msg)
                raise RuntimeError(error_msg)'''
                # Failed to generate enough {color} mana
                return (False, f"Failed to generate enough {color} mana")
            
            # その色の必要な点数のマナをいったんtmp_poolに移す
            self.mana_pool.remove_mana(color, required_count)
            tmp_pool.add_mana(color, required_count)
        
        # RGWUを生成してtmp_poolに移した

        while WILD_CANTOR in cards_to_use and WILD_CANTOR in self.hand:
            if self.mana_pool.can_pay_mana('G'):
                self.mana_pool.pay_mana('G')
                self.cast_wild_cantor()
                cards_to_use.remove(WILD_CANTOR)
            elif self.mana_pool.can_pay_mana('R'):
                self.mana_pool.pay_mana('R')
                self.cast_wild_cantor()
                cards_to_use.remove(WILD_CANTOR)
            else:
                # wild cantor in cards_to_use but failed to cast it
                return (False, "Failed to cast Wild Cantor")
        
        # Cast Dark Ritual
        while DARK_RITUAL in cards_to_use and DARK_RITUAL in self.hand:
            if self.mana_pool.B > 0:
                self.mana_pool.pay_mana('B')
                self.cast_dark_ritual()
                cards_to_use.remove(DARK_RITUAL)
            elif self.mana_source.can_generate_mana('B'):
                self.mana_source.generate_mana('B')
            else:
                # dark ritual in cards_to_use but failed to cast it
                return (False, "Failed to cast Dark Ritual")
        
        # Cast Cabal Ritual
        while CABAL_RITUAL in cards_to_use and CABAL_RITUAL in self.hand:
            if self.mana_pool.can_pay_mana('1B'):
                self.mana_pool.pay_mana('1B')
                self.cast_cabal_ritual()
                cards_to_use.remove(CABAL_RITUAL)
            elif self.mana_source.can_generate_mana('B'):
                self.mana_source.generate_mana('B')
            else:
                # cabal in cards_to_use but failed to cast it
                return (False, "Failed to cast Cabal Ritual")
        
        requiredB = required['B']
        while self.mana_pool.B < requiredB and self.mana_source.can_generate_mana('B'):
            self.mana_source.generate_mana('B')
        
        while self.mana_pool.get_total() < requiredB + generic:
            did_generate_mana = False
            for color in ['B', 'W', 'U', 'R', 'G']:
                if self.mana_source.can_generate_mana(color):
                    self.mana_source.generate_mana(color)
                    did_generate_mana = True
                    break
            if not did_generate_mana:
                #error_msg = f"ERROR in generate_mana_pattern: Failed to generate enough mana for generic cost\n"
                #error_msg += f"required: {requiredB} black + {generic} generic, current total: {self.mana_pool.get_total()}\n"
                #error_msg += f"mana_pool: {self.mana_pool}, mana_source: {self.mana_source}\n"
                #error_msg += f"cards_to_use: {cards_to_use}, hand: {self.hand}"
                #print(error_msg)
                #raise RuntimeError(error_msg)
                return (False, "Failed to generate enough mana for generic cost")
        
        if cards_to_use:
            # cards_to_useのすべてのカードをつかわなかった。
            return (False, "Not all cards in cards_to_use were used")
        
        if requiredB + generic <= self.mana_pool.get_total():
            # tmp_poolのマナを元に戻す
            self.mana_pool.transfer_from(tmp_pool)
            return (True, "")
        else:
            #error_msg = f"ERROR in generate_mana_pattern: Failed to generate enough mana after all attempts\n"
            #error_msg += f"required: {requiredB} black + {generic} generic, current total: {self.mana_pool.get_total()}\n"
            #error_msg += f"mana_pool: {self.mana_pool}, mana_source: {self.mana_source}\n"
            #error_msg += f"cards_to_use: {cards_to_use}, hand: {self.hand}"
            #print(error_msg)
            #raise RuntimeError(error_msg)
            return (False, "Failed to generate enough mana after all attempts")
        
        '''
        requiredB = required['B']
        while self.mana_pool.B < requiredB:
            if self.mana_source.can_generate_mana('B'):
                self.mana_source.generate_mana('B')
                continue
            elif DARK_RITUAL in cards_to_use and DARK_RITUAL in self.hand and self.mana_pool.B > 0:
                self.mana_pool.pay_mana('B')
                self.cast_dark_ritual()
                cards_to_use.remove(DARK_RITUAL)
                continue
            elif CABAL_RITUAL in cards_to_use and CABAL_RITUAL in self.hand and self.mana_pool.can_pay_mana('1B'):
                self.mana_pool.pay_mana('1B')
                self.cast_cabal_ritual()
                cards_to_use.remove(CABAL_RITUAL)
                continue
            elif WILD_CANTOR in cards_to_use and WILD_CANTOR in self.hand:
                if self.mana_pool.can_pay_mana('G'):
                    self.mana_pool.pay_mana('G')
                    self.cast_wild_cantor()
                    cards_to_use.remove(WILD_CANTOR)
                    continue
                if self.mana_pool.can_pay_mana('R'):
                    self.mana_pool.pay_mana('R')
                    self.cast_wild_cantor()
                    cards_to_use.remove(WILD_CANTOR)
                    continue
            return False
        
        while self.mana_pool.get_total() < requiredB + generic:
            did_generate_mana = False
            for color in ['B', 'W', 'U', 'R', 'G']:
                if self.mana_source.can_generate_mana(color):
                    self.mana_source.generate_mana(color)
                    did_generate_mana = True
                    break
            if did_generate_mana:
                continue

            if DARK_RITUAL in cards_to_use and DARK_RITUAL in self.hand and self.mana_pool.B > 0:
                self.mana_pool.pay_mana('B')
                self.cast_dark_ritual()
                cards_to_use.remove(DARK_RITUAL)
                continue
            elif CABAL_RITUAL in cards_to_use and CABAL_RITUAL in self.hand and self.mana_pool.can_pay_mana('1B'):
                self.mana_pool.pay_mana('1B')
                self.cast_cabal_ritual()
                cards_to_use.remove(CABAL_RITUAL)
                continue
            return False
        
        # tmp_poolのマナを元に戻す
        self.mana_pool.transfer_from(tmp_pool)
        return True
        '''
    
    def try_generate_mana(self, mana_cost: str, casting_cards: list[str]) -> bool:
        required, generic = self.mana_pool.analyze_mana_pattern(mana_cost)
        return self.try_generate_mana_pattern(required, generic, casting_cards)
    
    def try_generate_mana_pattern(self, required: dict[str, int], generic: int, casting_cards: list[str]) -> bool:
        self.debug(f'try_generate_mana_pattern: required: {required} generic: {generic} casting_cards: {casting_cards}')
        cards_to_imprint = self.get_cards_to_imprint(casting_cards)
        state = self.create_mana_generation_state(cards_to_imprint)
        result, cards_used_from_hand, cards_imprinted, cards_searched = state.can_generate_mana_pattern(required, generic)
        self.debug(f'can_generate_mana_pattern: result: {result} cards_used_from_hand: {cards_used_from_hand} cards_imprinted: {cards_imprinted} cards_searched: {cards_searched}')
        if result:
            generate_result, error_message = self.generate_mana_pattern(required, generic, cards_used_from_hand, cards_imprinted, cards_searched)
            if not generate_result:
                error_msg = f"ERROR: state.can_generate_mana_pattern returned True but self.generate_mana_pattern returned False\n"
                error_msg += f"required: {required}, generic: {generic}\n"
                error_msg += f"result: {result}, cards_used_from_hand: {cards_used_from_hand}, cards_imprinted: {cards_imprinted}, cards_searched: {cards_searched}\n"
                error_msg += f"Error message: {error_message}"
                print(error_msg)
                raise RuntimeError(error_msg)
            return generate_result
        else:
            return False
    
    def try_pay_mana(self, mana_cost: str, casting_cards: list[str]) -> bool:
        if self.try_generate_mana(mana_cost, casting_cards):
            self.mana_pool.pay_mana(mana_cost)
            return True
        else:
            return False
    
    def try_sacrifice_bargain(self) -> bool:
        if NECRODOMINANCE in self.battlefield:
            self.battlefield.remove(NECRODOMINANCE)
            self.graveyard.append(NECRODOMINANCE)
            return True
        
        if CHROME_MOX in self.battlefield:
            self.battlefield.remove(CHROME_MOX)
            self.graveyard.append(CHROME_MOX)
            return True
        
        if VAULT_OF_WHISPERS in self.battlefield:
            self.battlefield.remove(VAULT_OF_WHISPERS)
            self.graveyard.append(VAULT_OF_WHISPERS)
            if self.mana_source.B > 0:
                self.mana_source.B -= 1
            return True
        
        if LOTUS_PETAL in self.battlefield:
            self.battlefield.remove(LOTUS_PETAL)
            self.graveyard.append(LOTUS_PETAL)
            self.mana_source.ANY -= 1
            self.any_mana_sources.remove(LOTUS_PETAL)
            return True
        
        return False
    
    def cast_summoners_pact(self, target: str):
        self.hand.remove(SUMMONERS_PACT)
        self.graveyard.append(SUMMONERS_PACT)

        if target and target in self.deck:
            self.deck.remove(target)
            self.hand.append(target)
        
        self.shuffle_deck()
        self.storm_count += 1
        self.debug(f"Cast {SUMMONERS_PACT} (Search {target})")
    
    def cast_wild_cantor(self):
        self.debug(f"Cast {WILD_CANTOR}")
        self.hand.remove(WILD_CANTOR)
        self.battlefield.append(WILD_CANTOR)
        self.add_any_mana_source(WILD_CANTOR)
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
        self.add_any_mana_source(LOTUS_PETAL)
        self.storm_count += 1
    
    def cast_chrome_mox(self, imprint: str):
        self.debug(f"Cast {CHROME_MOX} (Imprint: {imprint})")
        self.hand.remove(CHROME_MOX)
        self.battlefield.append(CHROME_MOX)
        if imprint:
            self.hand.remove(imprint)
            if imprint == CHANCELLOR_OF_ANNEX:
                self.mana_source.add_mana_source('W')
            elif imprint == PACT_OF_NEGATION or imprint == BORNE_UPON_WIND:
                self.mana_source.add_mana_source('U')
            elif imprint == SUMMONERS_PACT:
                self.mana_source.add_mana_source('G')
            elif imprint == WILD_CANTOR or imprint == MANAMORPHOSE or imprint == VALAKUT_AWAKENING:
                self.mana_source.add_mana_source('R')
            elif imprint == NECRODOMINANCE or imprint == BESEECH_MIRROR or imprint == DARK_RITUAL or imprint == CABAL_RITUAL or imprint == DURESS:
                self.mana_source.add_mana_source('B')
        
        self.storm_count += 1
    
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
        self.shuffle_deck()
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
        self.storm_count += 1
        self.did_cast_necro = True
    
    def set_land(self, land: str):
        self.debug(f"set land {land}")
        self.hand.remove(land)
        self.battlefield.append(land)
        if land == GEMSTONE_MINE or land == UNDISCOVERED_PARADISE:
            self.add_any_mana_source(land)
        elif land == VAULT_OF_WHISPERS:
            self.mana_source.add_mana_source('B')
    
    def get_opponent_force_count(self) -> int:
        """
        results/force_mulligan_results.csvからデータを読み込み、
        確率に基づいて相手が持っているForceの枚数を返す
        
        Returns:
            相手が持っているForceの枚数（0-3）
        """ 
        csv_path = os.path.join('results', 'force_mulligan_results.csv')
        
        # CSVファイルが存在しない場合はデフォルト値を返す
        if not os.path.exists(csv_path):
            self.debug(f"Warning: {csv_path} not found. Using default probabilities.")
            # デフォルトの確率: 0枚:1%, 1枚:79%, 2枚:19%, 3枚:1%
            probabilities = {0: 0.01, 1: 0.79, 2: 0.19, 3: 0.01}
        else:
            # CSVファイルからデータを読み込む
            probabilities = {}
            try:
                with open(csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        force_count = int(row['force_count'])
                        percentage = float(row['percentage'])
                        probabilities[force_count] = percentage / 100.0
            except Exception as e:
                self.debug(f"Error reading {csv_path}: {e}. Using default probabilities.")
                # エラーが発生した場合はデフォルト値を使用
                probabilities = {0: 0.01, 1: 0.79, 2: 0.19, 3: 0.01}
        
        # 確率に基づいてForceの枚数を選択
        r = random.random()
        cumulative_prob = 0.0
        for force_count in sorted(probabilities.keys()):
            cumulative_prob += probabilities[force_count]
            if r <= cumulative_prob:
                return force_count
        
        # 念のため、デフォルト値を返す
        return 1

    def main_phase(self, opponent_has_forces: bool = False, opponent_force_count: int = 0) -> bool:
        # main phase中にシャッフルしたか調べるためにdid_shuffleをリセット
        self.did_shuffle = False
        self.can_cast_sorcery = True
        self.return_count = max(0, self.mulligan_count - (7 - len(self.hand)))
        chancellor_in_initial_hand = CHANCELLOR_OF_ANNEX in self.hand

        if NECRODOMINANCE not in self.hand and BESEECH_MIRROR not in self.hand:
            self.loss_reason = FALIED_NECRO
            return False

        initial_state = self.copy()
        initial_hand = self.hand.copy()
        
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
            if land != "None":
                self.set_land(land)
            
            if self.try_cast_necro(initial_hand):
                break
            self.copy_from(initial_state)
        
        # Necroを唱えるのに失敗
        if not self.did_cast_necro:
            self.loss_reason = FALIED_NECRO
            return False
        
        #self.debug(f'mana pool after casting necro: {self.mana_pool}')
        # Mana Poolの浮きUをMana Sourceに移動
        while self.mana_pool.U > 0:
            self.mana_pool.U -= 1
            # Uを出すためにAny Mana Sourceを使った場合
            if 'U' in self.mana_source.any_mana_colors:
                self.revert_used_any_mana_source('U')
            else:
                self.mana_source.add_mana_source('U')
        
        # 初手にChancellorがあって今ない場合、Chrome MoxにImprintしたと判定する
        did_imprint_chancellor = chancellor_in_initial_hand and CHANCELLOR_OF_ANNEX not in self.hand

        # マリガン分の手札をデッキボトムに戻す
        if self.return_count > 0:
            self.return_cards_for_mulligan(opponent_has_forces, did_imprint_chancellor)
            # Summoner's PactやBeseechでシャッフルしていた場合は、ボトムに戻した後にシャッフルする
            if self.did_shuffle:
                self.shuffle_deck()
        
        # 相手の妨害(Force of Will, Force of Negation)の処理
        if opponent_has_forces:
            #opponent_force_count = self.get_opponent_force_count()
            pact_count = self.hand.count(PACT_OF_NEGATION)
            chancellor_count = 1 if did_imprint_chancellor or CHANCELLOR_OF_ANNEX in self.hand else 0
            
            while opponent_force_count > 0:
                opponent_force_count -= 1
                self.storm_count += 1
                if chancellor_count > 0:
                    chancellor_count -= 1
                elif pact_count > 0:
                    pact_count -= 1
                    self.cast_pact_of_negation()
                else:
                    # Necroが相手に打ち消されたので失敗
                    self.loss_reason = FAILED_NECRO_COUNTERED
                    return False
        
        # Necro is resolved
        return True
    
    def try_cast_necro(self, initial_hand: list[str]) -> bool:
        initial_state = self.copy()

        if NECRODOMINANCE in self.hand:
            # 生成するマナとcasting_cardsのパターン
            patterns = [
                ('UBBB', [NECRODOMINANCE, PACT_OF_NEGATION, BORNE_UPON_WIND]),
                ('BBB', [NECRODOMINANCE])
            ]
            for mana_cost, casting_cards in patterns:
                if self.try_generate_mana(mana_cost, casting_cards):
                    self.mana_pool.pay_mana('BBB')
                    # Cast Necro from hand
                    self.cast_necro(True)
                    if self.validate_hand_count_after_necro(initial_hand):
                        return True
                    self.copy_from(initial_state)
            
        elif BESEECH_MIRROR in self.hand:
            patterns = [
                ('1UBBB', [BESEECH_MIRROR, PACT_OF_NEGATION, BORNE_UPON_WIND]),
                ('1BBB', [BESEECH_MIRROR])
            ]
            for mana_cost, casting_cards in patterns:
                if self.try_cast_beseech_into_necro(mana_cost, casting_cards) and self.validate_hand_count_after_necro(initial_hand):
                    return True
                self.copy_from(initial_state)
                #self.debug(f'failed to cast beseech into necro: mana_pool: {self.mana_pool}')
            
            patterns = [
                ('1UBBBBBB', [BESEECH_MIRROR, PACT_OF_NEGATION, BORNE_UPON_WIND]),
                ('1BBBBBB', [BESEECH_MIRROR])
            ]
            for mana_cost, casting_cards in patterns:
                if self.try_generate_mana(mana_cost, casting_cards):
                    self.mana_pool.pay_mana('1BBBBBB')
                    self.cast_beseech()
                    # Search Necro from deck
                    self.deck.remove(NECRODOMINANCE)
                    self.hand.append(NECRODOMINANCE)
                    self.cast_necro(True)
                    if self.validate_hand_count_after_necro(initial_hand):
                        return True
                    self.copy_from(initial_state)
        
        if MANAMORPHOSE in self.hand:
            casting_cards = [MANAMORPHOSE]
            if NECRODOMINANCE in self.hand:
                casting_cards.append(NECRODOMINANCE)
            elif BESEECH_MIRROR in self.hand:
                casting_cards.append(BESEECH_MIRROR)
            if self.try_pay_mana('1G', casting_cards) or self.try_pay_mana('1R', casting_cards):
                self.cast_manamorphose('BB')
                return self.try_cast_necro(initial_hand)
        
        # Failure
        #self.debug('Failed to cast necro.')
        return False
    
    def try_cast_beseech_into_necro(self, mana_cost: str, casting_cards: list[str]) -> bool:
        #self.debug(f'before try generate mana {mana_cost} mana_pool: {self.mana_pool}')
        if self.try_generate_mana(mana_cost, casting_cards):
            if self.try_sacrifice_bargain():
                #self.debug('cast beseech into necro')
                #self.debug(self.mana_pool)
                self.mana_pool.pay_mana('1BBB')
                self.cast_beseech()
                # Cast Necro from deck
                self.cast_necro(False)
                return True
            else:
                # bargainがない場合
                if CHROME_MOX in self.hand:
                    self.cast_chrome_mox('')
                    return self.try_cast_beseech_into_necro(mana_cost, casting_cards)
                elif LOTUS_PETAL in self.hand:
                    #self.debug('cast petal for bargain')
                    self.cast_lotus_petal()
                    return self.try_cast_beseech_into_necro(mana_cost, casting_cards)
                else:
                    # no bargain
                    return False
        return False

    def validate_hand_count_after_necro(self, initial_hand: list[str]) -> bool:
        # 初期手札に含まれていて使わなかったカード
        cards_unused = []
        initial_hand_copy = initial_hand.copy()

        for card in self.hand:
            if card in initial_hand_copy:
                cards_unused.append(card)
                initial_hand_copy.remove(card)
        
        # マリガンで戻す枚数よりも使わなかったカードの枚数が多ければTrue
        return self.return_count <= len(cards_unused)
    
    def return_cards_for_mulligan(self, opponent_has_forces: bool = False, did_imprint_chancellor: bool = False):
        # 1枚だけ残したいカード
        single_copy_cards = [VALAKUT_AWAKENING, MANAMORPHOSE, BORNE_UPON_WIND, DARK_RITUAL, BESEECH_MIRROR]
        # あるだけ残したいカード
        multi_copy_cards = [LOTUS_PETAL, SIMIAN_SPIRIT_GUIDE, ELVISH_SPIRIT_GUIDE, SUMMONERS_PACT]
        # 全体の優先順位
        priority = [VALAKUT_AWAKENING, MANAMORPHOSE, BORNE_UPON_WIND, LOTUS_PETAL, SIMIAN_SPIRIT_GUIDE, ELVISH_SPIRIT_GUIDE, SUMMONERS_PACT, DARK_RITUAL, BESEECH_MIRROR]
        if self.mana_source.U > 0:
            # 青マナソースがある場合はWindを優先する
            priority.remove(BORNE_UPON_WIND)
            priority.insert(0, BORNE_UPON_WIND)
        
        keep_count = len(self.hand) - self.return_count
        cards_to_keep = []
        pact_count = 0
        chanceller_count = 1 if did_imprint_chancellor else 0
        
        # 相手がカウンターを持っている場合はPact of NegationとChancellor of Annexを優先して残す
        if opponent_has_forces:
            # Pactを優先して残す
            while PACT_OF_NEGATION in self.hand and pact_count + chanceller_count < 2 and len(cards_to_keep) < keep_count:
                cards_to_keep.append(PACT_OF_NEGATION)
                self.hand.remove(PACT_OF_NEGATION)
                pact_count += 1
            
            # 次にChancellorを1枚まで残す
            if CHANCELLOR_OF_ANNEX in self.hand and chanceller_count == 0 and pact_count + chanceller_count < 2 and len(cards_to_keep) < keep_count:
                cards_to_keep.append(CHANCELLOR_OF_ANNEX)
                self.hand.remove(CHANCELLOR_OF_ANNEX)
                chanceller_count += 1
        
        # 残りのカードを優先順位に従って残す
        for priority_card in priority:
            if priority_card in single_copy_cards:
                if priority_card in self.hand and len(cards_to_keep) < keep_count:
                    cards_to_keep.append(priority_card)
                    self.hand.remove(priority_card)
            elif priority_card in multi_copy_cards:
                while priority_card in self.hand and len(cards_to_keep) < keep_count:
                    cards_to_keep.append(priority_card)
                    self.hand.remove(priority_card)
        
        if opponent_has_forces:
            while PACT_OF_NEGATION in self.hand and len(cards_to_keep) < keep_count:
                cards_to_keep.append(PACT_OF_NEGATION)
                self.hand.remove(PACT_OF_NEGATION)
                pact_count += 1
            
            if CHANCELLOR_OF_ANNEX in self.hand and chanceller_count == 0 and len(cards_to_keep) < keep_count:
                cards_to_keep.append(CHANCELLOR_OF_ANNEX)
                self.hand.remove(CHANCELLOR_OF_ANNEX)
                chanceller_count += 1
        
        # 残りのカードをランダムに残す
        while self.hand and len(cards_to_keep) < keep_count:
            card = self.hand.pop(0)
            cards_to_keep.append(card)
        
        cards_to_return = self.hand.copy()
        self.hand = cards_to_keep
        self.deck.extend(cards_to_return)
    
    # main phaseにネクロが解決した後、手札の呪文を唱える
    def cast_spells_after_necro_resolved(self, cast_summoners_pact: bool):
        # 手札のBorne Upon a Windを唱えられるなら唱える
        if BORNE_UPON_WIND in self.hand and self.try_generate_mana('1U', [BORNE_UPON_WIND]):
            self.cast_borne_upon_a_wind()
        
        # 手札のLotus Petalを唱える
        while LOTUS_PETAL in self.hand:
            self.cast_lotus_petal()
        
        # 手札のChrome MoxにPactか2枚目以降のWindを刻印
        if CHROME_MOX in self.hand:
            if PACT_OF_NEGATION in self.hand:
                # もうNecroは解決済なのでPactを刻印する
                self.cast_chrome_mox(PACT_OF_NEGATION)
            elif self.hand.count(BORNE_UPON_WIND) >= 2:
                self.cast_chrome_mox(BORNE_UPON_WIND)
        
        # 手札のSummoner's Pactを唱える
        if cast_summoners_pact:
            while SUMMONERS_PACT in self.hand:
                if ELVISH_SPIRIT_GUIDE in self.deck:
                    self.cast_summoners_pact(ELVISH_SPIRIT_GUIDE)
                elif WILD_CANTOR in self.deck:
                    self.cast_summoners_pact(WILD_CANTOR)
                else:
                    break
    
    def end_step(self, draw_count: int) -> bool:
        if not self.did_cast_wind:
            self.can_cast_sorcery = False
        
        self.mana_pool.clear()

        self.draw_cards(draw_count)
        
        # Show drawn cards
        self.debug("\n=== self.hand in end step ===")
        for card in self.hand:
            self.debug(card)
        self.debug("==================\n")
        
        # Basic validation
        if not self.validate_hand_in_end_step():
            return False
        
        return self.try_cast_tendril()
    
    def validate_hand_in_end_step(self):
        if self.did_cast_wind:
            return True
        
        # Count cards
        simian_count = self.hand.count(SIMIAN_SPIRIT_GUIDE)
        elvish_count = self.hand.count(ELVISH_SPIRIT_GUIDE)
        summoners_count = self.hand.count(SUMMONERS_PACT)
        manamorphose_count = self.hand.count(MANAMORPHOSE)
        wind_count = self.hand.count(BORNE_UPON_WIND)
        valakut_count = self.hand.count(VALAKUT_AWAKENING)

        available_mana_total = self.mana_source.get_total() + elvish_count + simian_count + summoners_count

        if available_mana_total <= 1:
            # 2マナ出ない場合
            if wind_count > 0:
                if valakut_count > 0:
                    self.loss_reason = FAILED_CAST_BOTH_WITH_WIND_AND_VALAKUT
                else:
                    self.loss_reason = FAILED_CAST_BOTH_WITH_WIND_WITHOUT_VALAKUT
            else:
                if valakut_count > 0:
                    self.loss_reason = FAILED_CAST_BOTH_WITHOUT_WIND_WITH_VALAKUT
                else:
                    self.loss_reason = FAILED_CAST_BOTH_WITHOUT_WIND_AND_VALAKUT
            return False
        
        if manamorphose_count == 0 and wind_count == 0 and valakut_count == 0:
            # Manamorphose, Borne Upon a Wind, Valakutがすべてない場合
            self.loss_reason = FAILED_CAST_BOTH_WITHOUT_WIND_AND_VALAKUT
            return False
        
        if manamorphose_count == 0 and wind_count > 0 and valakut_count == 0:
            # windだけあって青が出ない場合
            if not self.mana_source.can_generate_mana('U'):
                self.loss_reason = FAILED_CAST_BOTH_WITH_WIND_WITHOUT_VALAKUT
                return False
        
        if manamorphose_count == 0 and wind_count == 0 and valakut_count > 0:
            # Valakutだけあって3マナ出ない場合
            if available_mana_total < 3:
                self.loss_reason = FAILED_CAST_BOTH_WITHOUT_WIND_WITH_VALAKUT
                return False
        
        return True
    
    # end stepに指定した色マナが出せるかどうか
    def can_generate_mana(self, color: str) -> bool:
        if self.mana_pool.get_colored_mana_count(color) > 0:
            return True
        
        if self.mana_source.can_generate_mana(color):
            return True
        
        if color == 'G':
            if ELVISH_SPIRIT_GUIDE in self.hand:
                return True
            if SUMMONERS_PACT in self.hand and ELVISH_SPIRIT_GUIDE in self.deck:
                return True
        elif color == 'R':
            if SIMIAN_SPIRIT_GUIDE in self.hand:
                return True
        
        return False
    
    def get_manamorphose_output_mana(self) -> str:
        if self.did_cast_wind:
            # Borne upon a Windを唱えた後はUは不要
            if self.can_generate_mana('R'):
                return 'BB'
            else:
                return 'BR'
        else:
            # Borne upon a Windをまだ唱えていないのでUが必要
            if BORNE_UPON_WIND in self.hand:
                if self.can_generate_mana('U'):
                    return 'BR'
                else:
                    return 'UB'
            elif VALAKUT_AWAKENING in self.hand:
                # 手札にWindがなくてValakutがある場合
                if self.can_generate_mana('R'):
                    return 'UB'
                else:
                    return 'BR'
            else:
                if self.can_generate_mana('U'):
                    return 'BR'
                else:
                    return 'UB'
    
    def cast_spells_for_storm_count(self):
        did_cast_0 = False
        while LOTUS_PETAL in self.hand:
            self.cast_lotus_petal()
            did_cast_0 = True
        
        while CHROME_MOX in self.hand:
            self.cast_chrome_mox('')
            did_cast_0 = True
        
        while SUMMONERS_PACT in self.hand:
            self.cast_summoners_pact('')
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
    
    def try_cast_tendril(self) -> bool:
        if SUMMONERS_PACT in self.hand:
            if ELVISH_SPIRIT_GUIDE in self.deck:
                self.cast_summoners_pact(ELVISH_SPIRIT_GUIDE)
                return self.try_cast_tendril()
            elif WILD_CANTOR in self.deck:
                self.cast_summoners_pact(WILD_CANTOR)
                return self.try_cast_tendril()
        
        if MANAMORPHOSE in self.hand:
            casting_cards = [MANAMORPHOSE]
            if self.try_pay_mana('1G', casting_cards) or self.try_pay_mana('1R', casting_cards):
                output_mana = self.get_manamorphose_output_mana()
                self.cast_manamorphose(output_mana)
                return self.try_cast_tendril()
        
        if self.did_cast_wind:
            # After casting Borne Upon a Wind
            if TENDRILS_OF_AGONY in self.hand:
                casting_cards = [TENDRILS_OF_AGONY]
                if self.try_generate_mana('2BB', casting_cards):
                    self.cast_spells_for_storm_count()
                    self.debug(f"Floating: {self.mana_pool}")
                    if 9 <= self.storm_count:
                        self.mana_pool.pay_mana('2BB')
                        self.cast_tendril(True)
                        return True
            elif BESEECH_MIRROR in self.hand:
                casting_cards = [BESEECH_MIRROR]
                if self.try_generate_mana('1BBB', casting_cards):
                    self.cast_spells_for_storm_count()
                    self.debug(f"Floating: {self.mana_pool}")
                    if 8 <= self.storm_count:
                        if self.try_sacrifice_bargain():
                            self.mana_pool.pay_mana('1BBB')
                            self.cast_beseech()
                            self.cast_tendril(False)
                            return True
                        elif self.try_generate_mana('3BBBBB', casting_cards):
                            self.mana_pool.pay_mana('3BBBBB')
                            self.cast_beseech()
                            self.deck.remove(TENDRILS_OF_AGONY)
                            self.hand.append(TENDRILS_OF_AGONY)
                            self.cast_tendril(True)
                            return True
            
            if VALAKUT_AWAKENING in self.hand:
                # self.debug(f'{VALAKUT_AWAKENING} in hand after wind.')
                casting_cards = [VALAKUT_AWAKENING]

                for cost in self.mana_patterns_valakut_after_wind:
                    if self.try_generate_mana(cost, casting_cards):
                        self.mana_pool.pay_mana('2R')
                        cards_to_remove = self.hand.copy()
                        cards_to_remove.remove(VALAKUT_AWAKENING)
                        if TENDRILS_OF_AGONY in self.hand:
                            cards_to_remove.remove(TENDRILS_OF_AGONY)
                        elif BESEECH_MIRROR in self.hand:
                            cards_to_remove.remove(BESEECH_MIRROR)
                        self.cast_valakut(cards_to_remove)
                        return self.try_cast_tendril()
            
            if BORNE_UPON_WIND in self.hand:
                if self.try_pay_mana('1U', [BORNE_UPON_WIND]):
                    self.cast_borne_upon_a_wind()
                    return self.try_cast_tendril()

        else:
            # Haven't cast Borne Upon a Wind
            if BORNE_UPON_WIND in self.hand:
                mana_patterns = self.mana_patterns_wind_with_beseech
                casting_cards = [BORNE_UPON_WIND]
                if TENDRILS_OF_AGONY in self.hand:
                    casting_cards.append(TENDRILS_OF_AGONY)
                elif BESEECH_MIRROR in self.hand:
                    casting_cards.append(BESEECH_MIRROR)
                elif VALAKUT_AWAKENING in self.hand:
                    mana_patterns = self.mana_patterns_wind_with_valakut
                    casting_cards.append(VALAKUT_AWAKENING)
                else:
                    # 手札にBeseech, Tendril, Valakutがない場合
                    mana_patterns = self.mana_patterns_wind_without_beseech_and_valakut
                
                for mana_cost in mana_patterns:
                    if self.try_generate_mana(mana_cost, casting_cards):
                        self.mana_pool.pay_mana('1U')
                        self.cast_borne_upon_a_wind()
                        return self.try_cast_tendril()
            
            if VALAKUT_AWAKENING in self.hand:
                casting_cards = [VALAKUT_AWAKENING, BORNE_UPON_WIND]

                for cost in self.mana_patterns_valakut_before_wind:
                    if self.try_generate_mana(cost, casting_cards):
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
                        return self.try_cast_tendril()
        
        if not self.did_cast_tendril:
            if self.did_cast_wind:
                # Windを唱えた場合
                if BESEECH_MIRROR in self.hand or TENDRILS_OF_AGONY in self.hand:
                    self.loss_reason = CAST_WIND_FAILED_TENDRILS_WITH_BESEECH_OR_TENDRILS
                else:
                    self.loss_reason = CAST_WIND_FAILED_TENDRILS_WITHOUT_BESEECH_OR_TENDRILS
            else:
                # Windを唱えられなかった場合
                if self.did_cast_valakut:
                    # Valakutを唱えた場合
                    if BORNE_UPON_WIND in self.hand:
                        self.loss_reason = CAST_VALAKUT_FAILED_WIND_WITH_WIND
                    else:
                        self.loss_reason = CAST_VALAKUT_FAILED_WIND_WITHOUT_WIND
                else:
                    # WindもValakutも唱えていない場合
                    if BORNE_UPON_WIND in self.hand:
                        if VALAKUT_AWAKENING in self.hand:
                            self.loss_reason = FAILED_CAST_BOTH_WITH_WIND_AND_VALAKUT
                        else:
                            self.loss_reason = FAILED_CAST_BOTH_WITH_WIND_WITHOUT_VALAKUT
                    else:
                        if VALAKUT_AWAKENING in self.hand:
                            self.loss_reason = FAILED_CAST_BOTH_WITHOUT_WIND_WITH_VALAKUT
                        else:
                            self.loss_reason = FAILED_CAST_BOTH_WITHOUT_WIND_AND_VALAKUT
            return False
        
        return True

    def run_with_initial_hand(self, deck: list[str], initial_hand: list[str], bottom_list: list[str],
                              draw_count: int = 19, cast_summoners_pact_before_draw: bool = False) -> bool:
        """
        初期手札が指定されている場合のゲーム実行関数
        
        Args:
            deck: デッキ（カード名のリスト）
            initial_hand: 初期手札
            bottom_list: デッキボトムに戻すカードのリスト（マリガン処理をシミュレート）
            draw_count: ドロー数
            
        Returns:
            ゲームの勝敗結果（True: 勝ち, False: 負け）
        """
        # デッキが60枚かどうかをチェック
        if len(deck) != 60:
            self.debug(f"Error: Deck must contain exactly 60 cards. Current deck has {len(deck)} cards.")
            self.loss_reason = "Invalid deck size"
            return False
        
        self.reset_game()
        self.mulligan_count = 0
        self.deck = deck.copy()
        if self.shuffle_enabled:
            self.shuffle_deck()
        
        self.hand = initial_hand.copy()
        for card in self.hand:
            if card in self.deck:
                self.deck.remove(card)
            else:
                self.debug(f"Warning: Card {card} not found in deck")
        
        # bottom_listが空でない場合、指定されたカードを手札からデッキボトムに移動
        if bottom_list:
            for card in bottom_list:
                if card in self.hand:
                    self.hand.remove(card)
                    self.deck.append(card)
                else:
                    self.debug(f"Warning: Card {card} not found in hand for bottom_list")
        
        #print(f"self.hand = {self.hand}")
        #print(f"self.deck = {self.deck}")
        
        if not self.main_phase(False):
            return False
        
        self.cast_spells_after_necro_resolved(cast_summoners_pact_before_draw)

        #print(f"after main phase self.hand = {self.hand}")
        #print(f"after main phase self.battlefield = {self.battlefield}")
        #print(f"after main phase self.mana_source = {self.mana_source}")
        #print(f"len(self.deck) = {len(self.deck)}")
        #print(f"Dark Ritual count in hand {self.hand.count(DARK_RITUAL)}")
        #print(f"Dark Ritual count in deck {self.deck.count(DARK_RITUAL)}")

        #print(f"Cabal Ritual count in hand {self.hand.count(CABAL_RITUAL)}")
        #print(f"Cabal Ritual count in deck {self.deck.count(CABAL_RITUAL)}")
        
        if self.end_step(draw_count):
            self.debug("You Win.")
            return True
        else:
            self.debug("You Lose.")
            return False
    
    def run_without_initial_hand(self, deck: list[str], draw_count: int, mulligan_until_necro: bool, opponent_has_forces: bool = False, cast_summoners_pact_before_draw: bool = False) -> bool:
        """
        初期手札が指定されていない場合のゲーム実行関数（マリガンを行う）
        
        Args:
            deck: デッキ（カード名のリスト）
            draw_count: ドロー数
            mulligan_until_necro: ネクロを唱えられるまでマリガンするかどうか
            
        Returns:
            ゲームの勝敗結果（True: 勝ち, False: 負け）
        """
        # デッキが60枚かどうかをチェック
        if len(deck) != 60:
            self.debug(f"Error: Deck must contain exactly 60 cards. Current deck has {len(deck)} cards.")
            self.loss_reason = "Invalid deck size"
            return False
        
        max_mulligan_count = 4 if mulligan_until_necro else 0
        for mulligan_count in range(max_mulligan_count + 1):
            self.reset_game()
            self.mulligan_count = mulligan_count
            self.deck = deck.copy()
            if self.shuffle_enabled:
                self.shuffle_deck()
            
            self.draw_cards(7)
            
            opponent_force_count = self.get_opponent_force_count() if opponent_has_forces else 0
            if self.main_phase(opponent_has_forces, opponent_force_count, False):
                # Necroキャストに成功した場合
                self.cast_spells_after_necro_resolved(cast_summoners_pact_before_draw)
                # ループを抜ける
                break
            elif self.loss_reason == FAILED_NECRO_COUNTERED:
                # Necroをキャストしたが打ち消された場合は失敗で終了
                return False
        
        # Necroをキャストできなかった場合
        if not self.did_cast_necro:
            self.debug(f"Failed to cast Necrodominance. mulligan count = {self.mulligan_count}")
            return False
        
        if self.end_step(draw_count):
            self.debug("You Win.")
            return True
        else:
            self.debug("You Lose.")
            return False

if __name__ == "__main__":
    game = GameState()
    deck = create_deck('decks/gemstone4_paradise0_cantor0_chrome4_wind4_valakut3.txt')
    random.shuffle(deck)
    initial_hand = [GEMSTONE_MINE, DARK_RITUAL, NECRODOMINANCE, CABAL_RITUAL]
    #initial_hand = []
    if initial_hand:
        game.run_with_initial_hand(deck, initial_hand, [], 19, False)
    else:
        game.run_without_initial_hand(deck, 19, True)
