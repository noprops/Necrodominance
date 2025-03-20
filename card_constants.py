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
CHANCELLOR_OF_ANNEX = "Chancellor of the Annex"

# Loss Reason
FALIED_NECRO = "Failed to cast Necrodominance"
FAILED_NECRO_COUNTERED = "Failed to resolve Necrodominance due to counter spell"

# Wind唱えた後の失敗理由
CAST_WIND_FAILED_TENDRILS_WITH_BESEECH_OR_TENDRILS = "Cast Borne Upon a Wind but failed to cast Tendrils with Beseech or Tendrils in hand"
CAST_WIND_FAILED_TENDRILS_WITHOUT_BESEECH_OR_TENDRILS = "Cast Borne Upon a Wind but failed to cast Tendrils without Beseech or Tendrils in hand"

# Valakut唱えた後の失敗理由
CAST_VALAKUT_FAILED_WIND_WITH_WIND = "Cast Valakut but failed to cast Borne Upon a Wind with Wind in hand"
CAST_VALAKUT_FAILED_WIND_WITHOUT_WIND = "Cast Valakut but failed to cast Borne Upon a Wind without Wind in hand"

# WindもValakutも唱えられなかった場合
FAILED_CAST_BOTH_WITH_WIND_AND_VALAKUT = "Failed to cast both Valakut and Borne Upon a Wind with both in hand"
FAILED_CAST_BOTH_WITH_WIND_WITHOUT_VALAKUT = "Failed to cast both Valakut and Borne Upon a Wind with Wind but without Valakut"
FAILED_CAST_BOTH_WITHOUT_WIND_WITH_VALAKUT = "Failed to cast both Valakut and Borne Upon a Wind without Wind but with Valakut"
FAILED_CAST_BOTH_WITHOUT_WIND_AND_VALAKUT = "Failed to cast both Valakut and Borne Upon a Wind without both"

ALL_CARDS = [
    GEMSTONE_MINE,
    UNDISCOVERED_PARADISE,
    VAULT_OF_WHISPERS,
    CHROME_MOX,
    LOTUS_PETAL,
    SUMMONERS_PACT,
    ELVISH_SPIRIT_GUIDE,
    SIMIAN_SPIRIT_GUIDE,
    WILD_CANTOR,
    MANAMORPHOSE,
    VALAKUT_AWAKENING,
    BORNE_UPON_WIND,
    DARK_RITUAL,
    CABAL_RITUAL,
    NECRODOMINANCE,
    BESEECH_MIRROR,
    TENDRILS_OF_AGONY,
    PACT_OF_NEGATION,
    DURESS,
    CHANCELLOR_OF_ANNEX
]

def get_card_color(card_name):
    white_cards = [CHANCELLOR_OF_ANNEX]
    green_cards = [SUMMONERS_PACT, ELVISH_SPIRIT_GUIDE]
    red_cards = [SIMIAN_SPIRIT_GUIDE, WILD_CANTOR, MANAMORPHOSE, VALAKUT_AWAKENING]
    blue_cards = [BORNE_UPON_WIND, PACT_OF_NEGATION]
    black_cards = [DARK_RITUAL, CABAL_RITUAL, NECRODOMINANCE, BESEECH_MIRROR, DURESS]
    
    if card_name in white_cards:
        return 'W'
    if card_name in green_cards:
        return 'G'
    elif card_name in red_cards:
        return 'R'
    elif card_name in blue_cards:
        return 'U'
    elif card_name in black_cards:
        return 'B'
    else:
        raise ValueError(f"カード '{card_name}' の色は定義されていません")
