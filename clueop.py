import random
import math

Rooms = ['Ball', 'Billiard', 'Conservatory', 'Dining', 'Hall', 'Kitchen', 'Lounge', 'Library', 'Study']
Weapons = ['Knife', 'Pistol', 'Rope', 'Candlestick', 'Wrench', 'Lead_Pipe']
People = ['White', 'Green', 'Scarlet', 'Mustard', 'Peacock', 'Plum']
Cards = Rooms + Weapons + People;
Hands = []
Answer = []

# Distance Matrix between rooms in the same order as listed above
# TODO: Add correct distances
Distances = [
    [0, 3, 6, 4, 3, 4, 3, 5, 6],
    [3, 0, 3, 3, 3, 4, 2, 4, 5],
    [6, 3, 0, 4, 5, 4, 5, 4, 3],
    [4, 3, 4, 0, 4, 2, 4, 2, 3],
    [3, 3, 5, 4, 0, 3, 2, 3, 5],
    [4, 4, 4, 2, 3, 0, 3, 3, 4],
    [3, 2, 5, 4, 2, 3, 0, 3, 4],
    [5, 4, 4, 2, 3, 3, 3, 0, 4],
    [6, 5, 3, 3, 5, 4, 4, 4, 0]
]

# Use the following constants to affect simulator behavior
SIMULATED = True # Set to True to simulate a game
global NUM_PLAYERS 
NUM_PLAYERS = 4 # Number of players in the game
PLAYER = 1  # Index of the player in the list of players (0-indexed)
DEALER = 1  # Index of the dealer in the list of players (0-indexed)
PLAYER_STRATEGIES = ['random', 'random', 'random', 'random'] # Strategies for each player
assert(len(PLAYER_STRATEGIES) == NUM_PLAYERS), 'Number of strategies does not match number of players'
assert(PLAYER <= NUM_PLAYERS and DEALER <= NUM_PLAYERS), 'Player or Dealer index out of bounds'

# Calculate Distance between two rooms
def distance_to_room(room1, room2):
    return Distances[Rooms.index(room1)][Rooms.index(room2)]

# Enable User Round Input
def user_round():
    try:
        print('Enter the room, weapon, and suspect of the suggestion.' +
            '1: Ballroom\t\t2: Billiard Room\t3: Conservatory\t\t4: Dining Room\n' +
            '5: Hall\t\t\t6: Kitchen\t\t7: Lounge\t\t8: Library\n' +
            '9: Study\t\t10: Knife\t\t11: Pistol\t\t12: Rope\n' +
            '13: Candlestick\t\t14: Wrench\t\t15: Lead Pipe\t\t16: Mrs. White\n' +
            '17: Mr. Green\t\t18: Ms. Scarlet\t\t19: Col. Mustard\t20: Mrs. Peacock\n' +
            '21: Prof. Plum\nCards in Hand: ');
        room = input('Room: ')
        weapon = input('Weapon: ')
        person = input('Person: ')
        player = input('Player that showed a card: ')
        return room, weapon, person, player
    except ValueError:
        print('Improperly Formatted Input.')

# Run Simulated Round
# TODO: Implement Logic and stuff
def simulated_round(player):
    # Get the suggestion from the current player
    if (PLAYER_STRATEGIES[player] == 'random'):
        room, weapon, person = random_guess()
    elif (PLAYER_STRATEGIES[player] == 'simplex'):
        room, weapon, person = simplex_guess(player)
    else:
        room, weapon, person = random_guess()
    print('Player ' + str(player) + ' suggested ' + room + ', ' + weapon + ', ' + person)
    # Process the Suggestion
    for i in range(1, NUM_PLAYERS):
        responder = (player + i) % NUM_PLAYERS
        response = show_card(responder, room, weapon, person)
        # Check if the player showed a card
        if (response != 'None'):
            print('Player ' + str(responder) + ' responded ' + response)
            break
    # Process the response
    # TODO: Implement Logic

# Determine which card to show
def show_card(player, room, weapon, person):
    # Check if the player has any of the cards
    MatchingCards = []
    if (Hands[player].count(room) > 0):
        MatchingCards.append(room)
    if (Hands[player].count(weapon) > 0):
        MatchingCards.append(weapon)
    if (Hands[player].count(person) > 0):
        MatchingCards.append(person)
    
    if (len(MatchingCards) == 0):
        response = 'None'
    elif (len(MatchingCards) == 1):
        response = MatchingCards[0]
    else:
        if (PLAYER_STRATEGIES[player] == 'random'):
            response = MatchingCards[random.randrange(len(MatchingCards))]
        elif (PLAYER_STRATEGIES[player] == 'simplex'):
            response = MatchingCards[random.randrange(len(MatchingCards))]
        else:
            response = MatchingCards[random.randrange(len(MatchingCards))]

    return response

def simplex_guess(player):
    return random_guess()

def random_guess():
    room = Rooms[random.randrange(len(Rooms))]
    weapon = Weapons[random.randrange(len(Weapons))]
    person = People[random.randrange(len(People))]
    return room, weapon, person

# Create Player Hand(s)
def createHands():
    random.seed()

    if (SIMULATED):
        tempRooms = Rooms;
        tempWeapons = Weapons;
        tempPeople = People;
        Answer = (tempRooms.pop(random.randrange(len(tempRooms)))
            + tempWeapons.pop(random.randrange(len(tempWeapons))) 
            + tempPeople.pop(random.randrange(len(tempPeople))))
        remainingCards = tempRooms + tempWeapons + tempPeople

        # Check if the player is near enough to the dealer to receive an extra card
        ExtraCards = [0] * NUM_PLAYERS
        num_extra_cards = len(remainingCards) % (NUM_PLAYERS)
        for i in range(1, num_extra_cards + 1):
            player = DEALER + i
            if (player >= NUM_PLAYERS):
                ExtraCards[DEALER + i - NUM_PLAYERS] = 1
            else:
                ExtraCards[DEALER + i] = 1

        # Deal the cards to the players and opponent hands
        for i in range(0, NUM_PLAYERS):
            Hands.append([])
            extraCards = len(remainingCards) % (NUM_PLAYERS - i)
            hand_len = math.floor(len(remainingCards)/(NUM_PLAYERS-i))
            # Deal Cards
            for j in range(0, hand_len):
                Hands[i].append(remainingCards.pop(random.randrange(len(remainingCards))))

    else:
        try:
            num_players = int(input('Number of Players: '))
        except ValueError:
            print('Improperly Formatted Input.')
            exit(1)

        Hands.append([])
        hand = input('Input Cards in Hand as Space Deliminated List of Integers:\n' +
            '1: Ballroom\t\t2: Billiard Room\t3: Conservatory\t\t4: Dining Room\n' +
            '5: Hall\t\t\t6: Kitchen\t\t7: Lounge\t\t8: Library\n' +
            '9: Study\t\t10: Knife\t\t11: Pistol\t\t12: Rope\n' +
            '13: Candlestick\t\t14: Wrench\t\t15: Lead Pipe\t\t16: Mrs. White\n' +
            '17: Mr. Green\t\t18: Ms. Scarlet\t\t19: Col. Mustard\t20: Mrs. Peacock\n' +
            '21: Prof. Plum\nCards in Hand: ');
        hand = hand.split();
        if (len(hand) != math.ceil((len(Cards) - 3)/num_players) 
            and len(hand) != math.floor((len(Cards) - 3)/num_players)):
            print('Hand length not appropriate for given number of players.')
            exit(1)

        for i in range(0,len(hand)):
            try:
                if (int(hand[i]) < 1 or int(hand[i]) >= len(Cards)):
                    print('Improper Hand.')
                    exit(1)
                Hands[0].append(Cards[int(hand[i]) - 1]);
            except ValueError:
                print('Improperly Formatted Input.')


createHands()
print(Hands)
simulated_round(2)
