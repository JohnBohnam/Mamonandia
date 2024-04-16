
# Timesteps used in training files
TIME_DELTA = 100
old = False
# Please put all! the price and log files into
# the same directory or adjust the code accordingly
# TRAINING_DATA_PREFIX = "./training"
TRAINING_DATA_PREFIX = "./new_data"
if old:
    current_limits = {
        'PEARLS': 20,
        'BANANAS': 20,
        'COCONUTS': 600,
        'PINA_COLADAS': 300,
        'DIVING_GEAR': 50,
        'BERRIES': 250,
        'BAGUETTE': 150,
        'DIP': 300,
        'UKULELE': 70,
        'PICNIC_BASKET': 70,
    }

    ALL_SYMBOLS = [
        'PEARLS',
        'BANANAS',
        'COCONUTS',
        'PINA_COLADAS',
        'DIVING_GEAR',
        'BERRIES',
        'DOLPHIN_SIGHTINGS',
        'BAGUETTE',
        'DIP',
        'UKULELE',
        'PICNIC_BASKET'
    ]
    POSITIONABLE_SYMBOLS = [
        'PEARLS',
        'BANANAS',
        'COCONUTS',
        'PINA_COLADAS',
        'DIVING_GEAR',
        'BERRIES',
        'BAGUETTE',
        'DIP',
        'UKULELE',
        'PICNIC_BASKET'
    ]
    first_round = ['PEARLS', 'BANANAS']
    snd_round = first_round + ['COCONUTS', 'PINA_COLADAS']
    third_round = snd_round + ['DIVING_GEAR', 'DOLPHIN_SIGHTINGS', 'BERRIES']
    fourth_round = third_round + ['BAGUETTE', 'DIP', 'UKULELE', 'PICNIC_BASKET']
    fifth_round = fourth_round  # + secret, maybe pirate gold?

    SYMBOLS_BY_ROUND = {
        1: first_round,
        2: snd_round,
        3: third_round,
        4: fourth_round,
        5: fifth_round,
    }

    first_round_pst = ['PEARLS', 'BANANAS']
    snd_round_pst = first_round_pst + ['COCONUTS', 'PINA_COLADAS']
    third_round_pst = snd_round_pst + ['DIVING_GEAR', 'BERRIES']
    fourth_round_pst = third_round_pst + ['BAGUETTE', 'DIP', 'UKULELE', 'PICNIC_BASKET']
    fifth_round_pst = fourth_round_pst  # + secret, maybe pirate gold?

    SYMBOLS_BY_ROUND_POSITIONABLE = {
        1: first_round_pst,
        2: snd_round_pst,
        3: third_round_pst,
        4: fourth_round_pst,
        5: fifth_round_pst,
    }
else:
    current_limits = {
        'AMETHYSTS': 20,
        'STARFRUIT': 20,
        'ORCHIDS': 100,
        'ROSES': 60,
        'GIFT_BASKET': 60,
        'CHOCOLATE': 250,
        'STRAWBERRIES': 350,
    }

    ALL_SYMBOLS = [
        'AMETHYSTS',
        'STARFRUIT',
        'ORCHIDS',
    ]
    POSITIONABLE_SYMBOLS = [
        'AMETHYSTS',
        'STARFRUIT',
        'ORCHIDS',
    ]
    first_round = ['AMETHYSTS', 'STARFRUIT']
    snd_round = first_round + ['ORCHIDS']

    SYMBOLS_BY_ROUND = {
        0: first_round,
        1: first_round,
        2: snd_round,
    }

    first_round_pst = ['AMETHYSTS', 'STARFRUIT']
    snd_round_pst = first_round_pst + ['ORCHIDS']
    third_round_pst = ['ROSES', 'STRAWBERRIES', 'GIFT_BASKET', 'CHOCOLATE']

    SYMBOLS_BY_ROUND_POSITIONABLE = {
        0: first_round_pst,
        1: first_round_pst,
        2: snd_round_pst,
        3: third_round_pst,
    }
