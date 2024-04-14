import random
import math

Rooms = ['Ball', 'Billiard', 'Conservatory', 'Dining', 'Hall', 'Kitchen', 'Lounge', 'Library', 'Study']
Weapons = ['Knife', 'Pistol', 'Rope', 'Candlestick', 'Wrench', 'Lead_Pipe']
People = ['White', 'Green', 'Scarlet', 'Mustard', 'Peacock', 'Plum']
Cards = Rooms + Weapons + People;
Hands = []
Answer = []

# Distance Matrix between rooms in the same order as listed above
Distances = [
    [0,  6,  4,  7,  13, 7,  15, 12, 17],
    [6,  0,  7,  14, 15, 17, 22, 4,  15],
    [4,  7,  0,  19, 20, 20, 0,  15, 20],
    [7,  14, 19, 0,  8,  11, 4,  14, 17],
    [13, 15, 20, 8,  0,  19, 8,  7,  4 ],
    [7,  17, 20, 11, 19, 0,  19, 23, 0 ],
    [15, 22, 0,  4,  8,  19, 0,  14, 17],
    [12, 4,  15, 14, 7,  23, 14, 0,  7 ],
    [17, 15, 20, 17, 4,  0,  17, 7,  0 ]
]

# Im a Player
class Player:
    def __init__(self, Hand, player_num, strategy):
        self.State = [[[]]]
        self.C_People = []
        self.C_Weapons = []
        self.C_Rooms = []
        self.Hand = Hand
        self.player_num = player_num
        self.strategy = strategy
        for i in range(len(People)):
            self.State[i] = [Hand.count(People[i]),[]]
        for i in range(len(Weapons)):
            self.State[i + len(People)] = [Hand.count(Weapons[i]),[]]
        for i in range(len(Rooms)):
            self.State[i + len(People) + len(Weapons)] = [Hand.count(Rooms[i]), []]
        # Build Opponent Hand probabilities
        for i in range(len(People)):
            self.State[i] = [1/(len(People)-self.len_known_people()),[]]
        for i in range(len(Weapons)):
            self.State[i + len(People)] = [1/(len(Weapons)-self.len_known_weapons()),[]]
        for i in range(len(Rooms)):
            self.State[i + len(People) + len(Weapons)] = [1/(len(Rooms)-self.len_known_rooms()), []]

    def len_known_people(self):
        #TODO: not this
        return 1
    def len_known_weapons(self):
        #TODO: not this
        return 1
    def len_known_rooms(self):
        #TODO: not this
        return 1
    def make_guess(self):
        # TODO: Where more linprogging happens
        person = weapon = room = 1
        if (not SIMULATED and self.player_num == PLAYER):
            input() #TODO: Player input
            return
        else:
            return person, weapon, room
    def process_guess(self, guesser, answerer, person, weapon, room):
        person_idx = People.index(person)
        weapon_idx = Weapons.index(weapon) + len(People)
        room_idx = Rooms.index(room) + len(People) + len(Weapons)
        # Zero out entries of players who dont have the cards
        for i in range(1,(answerer-guesser-1)%NUM_PLAYERS):
            player = (i + guesser) % NUM_PLAYERS
            self.State[player][person_idx] = [0,[0]]
            self.State[player][weapon_idx] = [0,[0]]
            self.State[player][room_idx] = [0,[0]]
            for j in range(len(Cards)):
                for tup_list in self.State[player][j][1]:
                    if self.State[player][j][0] == 0 or len(tup_list) == 0: continue
                    if person_idx in tup_list: tup_list.pop(person_idx)
                    if weapon_idx in tup_list: tup_list.pop(weapon_idx)
                    if room_idx in tup_list: tup_list.pop(room_idx)
                    if (len(tup_list) == 0): self.State[player][j] = [0,[0]]
        # Update answerer cards
        # TODO: Process Coefficient Matricies
        #TODO: This (specifically the '1' part)
        if answerer == self.player_num - 1: return
        self.State[answerer][person_idx] = [1, self.State[answerer][person_idx][1] + [weapon_idx, room_idx]] 
        self.State[answerer][weapon_idx] = [1, self.State[answerer][weapon_idx][1] + [person_idx, room_idx]]
        self.State[answerer][room_idx] = [1, self.State[answerer][room_idx][1] + [weapon_idx, person_idx]]
        # TODO: some linear algebra-ey conditional probablity calculation
        return

    def accuse(self):
        # assert(its right)
        return 0

    def show_card(self, person, weapon, room):
        MatchingCards = []
        if (self.Hand.count(room) > 0):
            MatchingCards.append(room)
        if (self.Hand.count(weapon) > 0):
            MatchingCards.append(weapon)
        if (self.Hand.count(person) > 0):
            MatchingCards.append(person)
        
        if (len(MatchingCards) == 0):
            response = 'None'
        elif (len(MatchingCards) == 1):
            response = MatchingCards[0]
        else:
            #TODO: Possibly more linprog
            if (self.strategy == 'random'):
                response = MatchingCards[random.randrange(len(MatchingCards))]
            elif (self.strategy == 'simplex'):
                response = MatchingCards[random.randrange(len(MatchingCards))]
            else:
                response = MatchingCards[random.randrange(len(MatchingCards))]
        return response

    def receive_guess(self, card):
    #TODO: Process the received guess.

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
        exit(1)

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
Players = []
for i in range(NUM_PLAYERS):
    Players.append(Player(Hands[i], i + 1, PLAYER_STRATEGIES[i]))
# RUN THE SIMULATORINATOR
first = True
player = int(DEALER) + 1
while(True):
    if (SIMULATED):
        player = (int(player) + 1) % NUM_PLAYERS
        # Player makes a guess
        person, weapon, room = Players[player].make_guess()
        # Players answer the guess
        card = None
        for i in range(1, NUM_PLAYERS):
            card = Players[player + i].show_card(person, weapon, room)
            if card != None: break
        Players[player].receive_guess(card)
        # Players process the guess
        for i in range(NUM_PLAYERS):
            Players[i].process_guess(person, weapon, room)
        # Player makes an accusation if able
        if Players[player].accuse(): break
    else:
        recommend = input('Recommend a Guess?')
        if recommend: print(Players[PLAYER].make_guess())
        person, weapon, room, player = user_round()

print("Player", player, "won the game!")
