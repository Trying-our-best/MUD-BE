import random as rnd

rooms = ["Chamber",
"Quarter",
"Room",
"Passage",
"Atrium",
"Court",
"Dungeon",
"Antechamber",
"Hall",
"Catacomb",
"Mausoleum",
"Vault",
"Tomb",
"Grave",
"Cell",
"Crypt",
"Compartment"]

adjectives=["Wicked",
"Gloomy",
"Diabolical",
"Fiendish",
"Heinous",
"Nefarious",
"Evil",
"Vile",
"Monstrous",
"Malevolent",
"Malignant",
"Sinister",
"Hellish",
"Demonic",
"Horrendous",
"Spooky",
"Creepy",
"Vile"]

descriptions =[
    "You walk into room and fear for what awaits ahead.",
    "You gait and now find your self in room,  concerned if you have made the correct decision.",
    "You stumble upon the room, uneased about the current situation at hand.",
    "You shuffle past hallways and arrive at the room, you start to feel a cold sweat behind your back",
    "Questioning your decision of being a knight, you hesitate into the room.",
    "Panic starts to settle in, upon the sight of the room.",
    "You continue moving and now find yourself at the room, perhaps a slight sign of hope",
    "Foolishly entering the room, you know have dun goofed now."
]


def generate_desc_title():
    titleName = rnd.choice(rooms)
    titleAdj = rnd.choice(adjectives)

    def generate_title():
        return f"{titleAdj} {titleName}"
    
    def generate_desc():
        return rnd.choice(descriptions).replace("room", f"{titleAdj} {titleName}")
    
    return {'title': generate_title(), 'desc': generate_desc()}