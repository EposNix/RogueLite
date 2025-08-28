"""Enemy templates for different acts and encounter types."""

import random
from card import Card, CardType
from deck import Deck
from enemy import Enemy

# Each act has 5 basic enemies plus optional elite and boss templates
ENEMY_TEMPLATES = {
    1: {
        "basic": [
            {
                "name": "Brawler Pup",
                "hp": 25,
                "archetype": "Bruiser",
                "deck": [
                    ("Quick Maul", CardType.ATTACK, 5, 2, 1, "Deal 2", "", ""),
                    ("Heavy Chomp", CardType.ATTACK, 2, 4, 3, "Deal 4", "", ""),
                    ("Guard", CardType.GUARD, 1, 0, 4, "Prevent 3", "", ""),
                    ("Howl", CardType.PREP, 3, 0, 2, "Charge", "", ""),
                ],
            },
            {
                "name": "Sneaky Rat",
                "hp": 20,
                "archetype": "Skirmisher",
                "deck": [
                    ("Scratch", CardType.ATTACK, 5, 1, 1, "Deal 1", "", ""),
                    ("Bite", CardType.ATTACK, 3, 2, 2, "Deal 2", "", ""),
                    ("Evade", CardType.DODGE, 6, 0, 1, "Dodge", "", ""),
                    ("Poison Dart", CardType.TRICK, 4, 1, 1, "Bleed 1", "", ""),
                ],
            },
            {
                "name": "Shield Bug",
                "hp": 30,
                "archetype": "Guardian",
                "deck": [
                    ("Pincer Jab", CardType.ATTACK, 4, 2, 2, "Deal 2", "", ""),
                    ("Shell Guard", CardType.GUARD, 1, 0, 4, "Prevent 3", "", ""),
                    ("Harden", CardType.PREP, 2, 0, 3, "Guard 2 next beat", "", ""),
                    ("Heavy Slam", CardType.ATTACK, 2, 4, 3, "Deal 4", "", ""),
                ],
            },
            {
                "name": "Fire Imp",
                "hp": 22,
                "archetype": "Pyromancer",
                "deck": [
                    ("Flame Flicker", CardType.ATTACK, 5, 1, 1, "Deal 1", "", ""),
                    ("Fireball", CardType.ATTACK, 2, 4, 2, "Deal 4", "", ""),
                    ("Smoke Veil", CardType.DODGE, 6, 0, 1, "Dodge", "", ""),
                    ("Scorch", CardType.SKILL, 3, 1, 2, "Bleed 1", "", ""),
                ],
            },
            {
                "name": "Stone Golem",
                "hp": 35,
                "archetype": "Bulwark",
                "deck": [
                    ("Rock Punch", CardType.ATTACK, 3, 3, 3, "Deal 3", "", ""),
                    ("Boulder Toss", CardType.ATTACK, 1, 5, 4, "Deal 5", "", ""),
                    ("Guard Stance", CardType.GUARD, 2, 0, 4, "Prevent 3", "", ""),
                    ("Slow Step", CardType.GRAPPLE, 1, 2, 4, "Stun", "", ""),
                ],
            },
        ],
        "elite": [
            {
                "name": "Wolf Pack Leader",
                "hp": 45,
                "archetype": "Bruiser",
                "deck": [
                    ("Rending Bite", CardType.ATTACK, 4, 3, 2, "Deal 3", "", ""),
                    ("Alpha Pounce", CardType.ATTACK, 3, 5, 3, "Deal 5", "", ""),
                    ("Pack Tactics", CardType.TRICK, 5, 0, 1, "Bleed 1", "", ""),
                    ("Guard", CardType.GUARD, 1, 0, 4, "Prevent 3", "", ""),
                ],
            },
        ],
        "boss": [
            {
                "name": "Act 1 Boss",
                "hp": 80,
                "archetype": "Boss",
                "deck": [
                    ("Crushing Blow", CardType.ATTACK, 3, 5, 3, "Deal 5", "", ""),
                    ("Guard Wall", CardType.GUARD, 1, 0, 5, "Prevent 4", "", ""),
                    ("Roar", CardType.PREP, 2, 0, 3, "Charge", "", ""),
                    ("Smash", CardType.ATTACK, 2, 4, 3, "Deal 4", "", ""),
                ],
            },
        ],
    },
    2: {
        "basic": [
            {
                "name": "Frost Mage",
                "hp": 30,
                "archetype": "Caster",
                "deck": [
                    ("Ice Shard", CardType.ATTACK, 4, 2, 1, "Deal 2", "", ""),
                    ("Frostbolt", CardType.ATTACK, 3, 2, 2, "Slow 1", "", ""),
                    ("Barrier", CardType.GUARD, 2, 0, 3, "Prevent 3", "", ""),
                    ("Chill Winds", CardType.TRICK, 5, 0, 1, "Slow 2", "", ""),
                ],
            },
            {
                "name": "Berserker",
                "hp": 40,
                "archetype": "Bruiser",
                "deck": [
                    ("Frenzy Slash", CardType.ATTACK, 5, 3, 1, "Deal 3", "", ""),
                    ("Rage Smash", CardType.ATTACK, 2, 5, 3, "Deal 5", "", ""),
                    ("Reckless Guard", CardType.GUARD, 1, 0, 2, "Prevent 3", "", ""),
                    ("War Cry", CardType.PREP, 3, 0, 2, "Charge", "", ""),
                ],
            },
            {
                "name": "Poison Serpent",
                "hp": 28,
                "archetype": "Skirmisher",
                "deck": [
                    ("Fang Strike", CardType.GRAPPLE, 4, 2, 2, "Stun", "", ""),
                    ("Venom Spit", CardType.ATTACK, 3, 1, 1, "Bleed 2", "", ""),
                    ("Shed Skin", CardType.DODGE, 6, 0, 1, "Dodge", "", ""),
                    ("Coil", CardType.PREP, 2, 0, 2, "Charge", "", ""),
                ],
            },
            {
                "name": "Scout Archer",
                "hp": 25,
                "archetype": "Trickster",
                "deck": [
                    ("Quick Shot", CardType.ATTACK, 5, 2, 1, "Deal 2", "", ""),
                    ("Aimed Shot", CardType.ATTACK, 3, 4, 2, "Deal 4", "", ""),
                    ("Roll", CardType.DODGE, 6, 0, 1, "Dodge", "", ""),
                    ("Smoke Bomb", CardType.TRICK, 4, 0, 1, "Dodge", "", ""),
                ],
            },
            {
                "name": "Ironclad Soldier",
                "hp": 45,
                "archetype": "Guardian",
                "deck": [
                    ("Shield Bash", CardType.ATTACK, 3, 3, 3, "Deal 3", "", ""),
                    ("Fortify", CardType.GUARD, 1, 0, 4, "Prevent 3", "", ""),
                    ("Spear Thrust", CardType.ATTACK, 4, 2, 2, "Deal 2", "", ""),
                    ("Rally", CardType.PREP, 2, 0, 3, "Guard 2", "", ""),
                ],
            },
        ],
        "elite": [
            {
                "name": "Orc Warlord",
                "hp": 60,
                "archetype": "Bruiser",
                "deck": [
                    ("Cleave", CardType.ATTACK, 4, 4, 2, "Deal 4", "", ""),
                    ("Skull Crusher", CardType.ATTACK, 2, 6, 3, "Deal 6", "", ""),
                    ("Battle Cry", CardType.PREP, 3, 0, 2, "Charge", "", ""),
                    ("Guard", CardType.GUARD, 1, 0, 4, "Prevent 3", "", ""),
                ],
            },
        ],
        "boss": [
            {
                "name": "Act 2 Boss",
                "hp": 110,
                "archetype": "Boss",
                "deck": [
                    ("Devastate", CardType.ATTACK, 3, 6, 3, "Deal 6", "", ""),
                    ("Guard Wall", CardType.GUARD, 1, 0, 5, "Prevent 4", "", ""),
                    ("Enrage", CardType.PREP, 2, 0, 3, "Charge", "", ""),
                    ("Overrun", CardType.ATTACK, 2, 5, 3, "Deal 5", "", ""),
                ],
            },
        ],
    },
    3: {
        "basic": [
            {
                "name": "Void Reaver",
                "hp": 50,
                "archetype": "Striker",
                "deck": [
                    ("Void Slash", CardType.ATTACK, 5, 4, 2, "Deal 4", "", ""),
                    ("Rift Tear", CardType.ATTACK, 3, 6, 3, "Deal 6", "", ""),
                    ("Phase Shift", CardType.DODGE, 6, 0, 1, "Dodge", "", ""),
                    ("Void Shield", CardType.GUARD, 2, 0, 3, "Prevent 3", "", ""),
                ],
            },
            {
                "name": "Storm Caller",
                "hp": 45,
                "archetype": "Caster",
                "deck": [
                    ("Lightning Bolt", CardType.ATTACK, 5, 3, 1, "Deal 3", "", ""),
                    ("Thunder Crash", CardType.ATTACK, 2, 5, 3, "Deal 5", "", ""),
                    ("Tempest Barrier", CardType.GUARD, 3, 0, 3, "Prevent 3", "", ""),
                    ("Static Charge", CardType.PREP, 4, 0, 2, "Charge", "", ""),
                ],
            },
            {
                "name": "Plague Doctor",
                "hp": 40,
                "archetype": "Debuffer",
                "deck": [
                    ("Scalpel Cut", CardType.ATTACK, 4, 2, 1, "Deal 2", "", ""),
                    ("Toxic Vial", CardType.SKILL, 3, 1, 2, "Bleed 2", "", ""),
                    ("Plague Shield", CardType.GUARD, 2, 0, 3, "Prevent 3", "", ""),
                    ("Virulent Cloud", CardType.TRICK, 5, 0, 1, "Slow 1", "", ""),
                ],
            },
            {
                "name": "Shadow Assassin",
                "hp": 35,
                "archetype": "Assassin",
                "deck": [
                    ("Backstab", CardType.ATTACK, 6, 3, 1, "Deal 3", "", ""),
                    ("Shadow Strike", CardType.ATTACK, 4, 2, 1, "Stun if hits", "", ""),
                    ("Cloak", CardType.DODGE, 5, 0, 1, "Dodge", "", ""),
                    ("Fade", CardType.PREP, 3, 0, 1, "Charge", "", ""),
                ],
            },
            {
                "name": "Titan's Fist",
                "hp": 60,
                "archetype": "Bruiser",
                "deck": [
                    ("Titan Smash", CardType.ATTACK, 2, 7, 4, "Deal 7", "", ""),
                    ("Earthquake", CardType.ATTACK, 1, 5, 4, "Deal 5", "", ""),
                    ("Stone Guard", CardType.GUARD, 3, 0, 4, "Prevent 3", "", ""),
                    ("Seismic Step", CardType.GRAPPLE, 2, 3, 3, "Stun", "", ""),
                ],
            },
        ],
        "elite": [
            {
                "name": "Dragon Champion",
                "hp": 80,
                "archetype": "Bruiser",
                "deck": [
                    ("Claw Sweep", CardType.ATTACK, 4, 5, 3, "Deal 5", "", ""),
                    ("Tail Slam", CardType.ATTACK, 2, 6, 4, "Deal 6", "", ""),
                    ("Wing Buffet", CardType.TRICK, 5, 0, 1, "Slow 1", "", ""),
                    ("Scale Guard", CardType.GUARD, 1, 0, 5, "Prevent 3", "", ""),
                ],
            },
        ],
        "boss": [
            {
                "name": "Act 3 Boss",
                "hp": 150,
                "archetype": "Boss",
                "deck": [
                    ("Obliterate", CardType.ATTACK, 3, 7, 4, "Deal 7", "", ""),
                    ("Guard Wall", CardType.GUARD, 1, 0, 5, "Prevent 4", "", ""),
                    ("Cataclysm", CardType.ATTACK, 2, 6, 4, "Deal 6", "", ""),
                    ("Rallying Cry", CardType.PREP, 2, 0, 3, "Charge", "", ""),
                ],
            },
        ],
    },
}

def create_enemy(act, elite=False, boss=False):
    """Create an enemy instance for the given act and encounter type."""
    act_templates = ENEMY_TEMPLATES.get(act, ENEMY_TEMPLATES[1])
    if boss:
        template = random.choice(act_templates["boss"])
    elif elite:
        template = random.choice(act_templates["elite"])
    else:
        template = random.choice(act_templates["basic"])

    enemy_cards = []
    for name, card_type, speed, damage, stability, effect, read, clash in template["deck"]:
        for _ in range(3):
            enemy_cards.append(Card(name, card_type, speed, damage, stability, effect, read, clash))

    enemy_deck = Deck(enemy_cards)
    return Enemy(template["name"], template["hp"], enemy_deck, template.get("archetype", "Neutral"))
