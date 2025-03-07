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
    DURESS
]

def get_card_color(card_name):
    green_cards = [SUMMONERS_PACT, ELVISH_SPIRIT_GUIDE]
    red_cards = [SIMIAN_SPIRIT_GUIDE, WILD_CANTOR, MANAMORPHOSE, VALAKUT_AWAKENING]
    blue_cards = [BORNE_UPON_WIND, PACT_OF_NEGATION]
    black_cards = [DARK_RITUAL, CABAL_RITUAL, NECRODOMINANCE, BESEECH_MIRROR, DURESS]
    
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