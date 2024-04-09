import random
import math

Rooms = ['Ball', 'Billiard', 'Conservatory', 'Dining', 'Hall', 'Kitchen', 'Lounge', 'Library', 'Study']
Weapons = ['Knife', 'Pistol', 'Rope', 'Candlestick', 'Wrench', 'Lead_Pipe']
People = ['White', 'Green', 'Scarlet', 'Mustard', 'Peacock', 'Plum']
Cards = Rooms + Weapons + People;
Hand = []
Answer = []

# Use the following constants to affect simulator behavior
SIMULATED = True
NUM_PLAYERS = 4

# Create Player Hand
random.seed()

if (SIMULATED):
    tempRooms = Rooms;
    tempWeapons = Weapons;
    tempPeople = People;
    Answer = (tempRooms.pop(random.randrange(len(tempRooms)))
        + tempWeapons.pop(random.randrange(len(tempWeapons))) 
        + tempPeople.pop(random.randrange(len(tempPeople))))
    remainingCards = tempRooms + tempWeapons + tempPeople

    extra_cards = len(remainingCards) % NUM_PLAYERS
    hand_len = math.floor(len(remainingCards) / NUM_PLAYERS)
    if (random.randrange(NUM_PLAYERS) <= extra_cards): 
        hand_len = hand_len + 1

    indices = random.sample(range(len(remainingCards)), hand_len)
    for idx in indices:
        Hand.append(Cards[idx])
else:
    try:
        NUM_PLAYERS = int(input('Number of Players: '))
    except ValueError:
        print('Improperly Formatted Input')

    hand = input('Input Cards in Hand as Space Deliminated List of Integers:\n' +
        '1: Ballroom\t\t2: Billiard Room\t3: Conservatory\t\t4: Dining Room\n' +
        '5: Hall\t\t\t6: Kitchen\t\t7: Lounge\t\t8: Library\n' +
        '9: Study\t\t10: Knife\t\t11: Pistol\t\t12: Rope\n' +
        '13: Candlestick\t\t14: Wrench\t\t15: Lead Pipe\t\t16: Mrs. White\n' +
        '17: Mr. Green\t\t18: Ms. Scarlet\t\t19: Col. Mustard\t20: Mrs. Peacock\n' +
        '21: Prof. Plum\nCards in Hand: ');
    hand = hand.split();
    if (len(hand) != math.ceil((len(Cards) - 3)/NUM_PLAYERS) 
        and len(hand) != math.floor((len(Cards) - 3)/NUM_PLAYERS)):
        print('Hand length not appropriate for given number of players.')
        exit(1)

    for i in range(0,len(hand)):
        try:
            if (int(hand[i]) < 1 or int(hand[i]) >= len(Cards)):
                print('Improper Hand')
                exit(1)
            Hand.append(Cards[int(hand[i]) - 1]);
        except ValueError:
            print('Improperly Formatted Input.')

print(Hand)
