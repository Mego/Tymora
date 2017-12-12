#!/usr/bin/env python3

import random
import atexit
import pickle

decks = {}


def save_decks():
    with open("decks.pickle", 'wb') as f:
        pickle.dump(decks, f)
    print("Decks saved")


def load_decks():
    global decks
    try:
        with open("decks.pickle", 'rb') as f:
            decks = pickle.load(f)
        print("Decks loaded")
    except:
        print("Unable to load decks")


atexit.register(save_decks)

cards13 = """Sun
Moon
Star
Throne
Key
Knight
Void
Flames
Skull
Ruin
Euryale
Rogue
Jester""".split()

cards22 = """Vizier
Comet
Fates
Gem
Talons
Idiot
Donjon
Balance
Fool""".split() + cards13


def init_deck(deck_id, use_22 = False):
    cards = (cards13 if not use_22 else cards22)[:]
    random.shuffle(cards)
    decks[deck_id] = cards


def draw(deck_id):
    if deck_id not in decks:
        init_deck(deck_id, random.choice([False, False, False, True]))  # 75% chance of 13-card deck
    cards = decks[deck_id]
    card = cards[0]
    if card not in ['Fool', 'Jester']:
        cards.append(card)
        random.shuffle(cards)
    return card
