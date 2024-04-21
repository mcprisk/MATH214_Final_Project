####################################################################################################
#                                                                                                  #
# MATH 214 FINAL PROJECT | UNIVERSITY OF MICHIGAN - ANN ARBOR                                      #
# AUTHORS: howarch | joshdoc | mcprisk | timqwang | yangco                                         #
#                                                                                                  #
# SUMMARY: This project uses linear programming methods to suggest the next most optimal guess     #
#          for a player in the game of CLUE.  It has support for fully-simulated games as well as  #
#          physical games (which depend upon user input for each round).                           #
#                                                                                                  #
####################################################################################################

import random
import math
import copy
from scipy.optimize import linprog
import numpy as np

####################################################################################################
####################################################################################################
# GLOBAL VARIABLES                                                                                 #
####################################################################################################
####################################################################################################

People = ['White', 'Green', 'Scarlet', 'Mustard', 'Peacock', 'Plum']
Weapons = ['Knife', 'Pistol', 'Rope', 'Candlestick', 'Wrench', 'Lead_Pipe']
Rooms = ['Ball', 'Billiard', 'Conservatory', 'Dining', 'Hall', 'Kitchen', 'Lounge', 'Library', 'Study']
Cards = People + Weapons + Rooms
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

# define the inequality constraints
A_ub = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],  # neg because we need to convert >= to <= for linprog
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1]
]

b_ub = [-1, -1, -1]  # negative for the same reason as A_ub

####################################################################################################
####################################################################################################
# SIMULATION PARAMETERS                                                                            #
####################################################################################################
####################################################################################################

# Use the following constants to affect simulator behavior
SIMULATED = True # Set to True to simulate a game
global NUM_PLAYERS 
NUM_PLAYERS = 4 # Number of players in the game
PLAYER = 1  # Index of the player in the list of players (0-indexed)
DEALER = 1  # Index of the dealer in the list of players (0-indexed)
PLAYER_STRATEGIES = ['random', 'random', 'random', 'random'] # Strategies for each player
assert(len(PLAYER_STRATEGIES) == NUM_PLAYERS), 'Number of strategies does not match number of players'
assert(PLAYER <= NUM_PLAYERS and DEALER <= NUM_PLAYERS), 'Player or Dealer index out of bounds'


####################################################################################################
####################################################################################################
# PLAYER CLASS                                                                                     #
####################################################################################################
####################################################################################################

class Player:
#                                                                                                  #
# PLAYER CONSTRUCTOR                                                                               #
#                                                                                                  #
    def __init__(self, Hand, player_num, strategy):
        # STATE ORGANIZATION:
        # First Dimension: Card
        # Second Dimension: Players
        # Third Dimension: List of Tuples w/ 
        #   1. Probabilty of Player having card (only a 1 if it is guaranteed that they have it)
        #   2. List of other cards that they could have shown on that hand
        self.State = []
        for i in range(len(Cards)):
            self.State.append([])
            for j in range(NUM_PLAYERS):
                self.State[i].append([])
                self.State[i][j] = [0,[]]

        # Player Hand (List of Cards)
        self.Hand = Hand

        # Coefficient Matricies for Linear Programming
        self.C_People = [0, 0, 0, 0, 0, 0]
        self.C_Weapons = [0, 0, 0, 0, 0, 0]
        self.C_Rooms = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        # set cards in hand to correspond with coeff matrix of 100
        for card in self.Hand:
            if card in People:
                index = People.index(card)
                self.C_People[index] = 100
            elif card in Weapons:
                index = Weapons.index(card)
                self.C_Weapons[index] = 100
            elif card in Rooms:
                index = Rooms.index(card)
                self.C_Rooms[index] = 100

        # for cards that arent in hand, adjust their probability accordingly
        for coefficients in (self.C_People, self.C_Weapons, self.C_Rooms):
            non_set_indices = [i for i in range(len(coefficients)) if coefficients[i] != 100]
            if non_set_indices:
                update_value = 100 - (1 / len(non_set_indices)) * 100
                for index in non_set_indices:
                    coefficients[index] = update_value

        # Configurable Player Characteristics
        self.player_num = player_num
        self.strategy = strategy
        self.room_location = random.choice(Rooms)
        # Create Player Hand (from input argument)
        for i in range(len(People)):
            self.State[i][player_num] = [Hand.count(People[i]),[]]
        for i in range(len(Weapons)):
            self.State[i + len(People)][player_num] = [Hand.count(Weapons[i]),[]]
        for i in range(len(Rooms)):
            self.State[i + len(People) + len(Weapons)][player_num] = [Hand.count(Rooms[i]), []]

        # Build Opponent Hand probabilities (from current state)
        for i in range(len(People)):
            for j in range(NUM_PLAYERS):
                if j == player_num: continue
                if self.State[i][player_num][0] == 1: self.State[i][j] = [0,[]]
                else: self.State[i][j] = [1/(len(People)-self.len_known_people()),[]]
        for i in range(len(People), len(People) + len(Weapons)):
            for j in range(NUM_PLAYERS):
                if j == player_num: continue
                if self.State[i][player_num][0] == 1: self.State[i][j] = [0,[]]
                else: self.State[i][j] = [1/(len(Weapons)-self.len_known_weapons()),[]]
        for i in range(len(People) + len(Weapons), len(People) + len(Weapons) + len(Rooms)):
            for j in range(NUM_PLAYERS):
                if j == player_num: continue
                if self.State[i][player_num][0] == 1: self.State[i][j] = [0,[]]
                else: self.State[i][j] = [1/(len(Rooms)-self.len_known_rooms()), []]

#                                                                                                  #
# CLASS HELPER FUNCTIONS                                                                           #
#                                                                                                  #

# Determine the number of known cards for each category
# A card is considered known if there is a player with a 1 in its probability field
    def len_known_people(self):
        num_known = 0
        for i in range(len(People)):
            for j in range(NUM_PLAYERS):
                if len(self.State[i][j]) and self.State[i][j][0] == 1: num_known += 1
        return num_known

    def len_known_weapons(self):
        num_known = 0
        for i in range(len(People), len(People) + len(Weapons)):
            for j in range(NUM_PLAYERS):
                if len(self.State[i][j]) and self.State[i][j][0] == 1: num_known += 1
        return num_known

    def len_known_rooms(self):
        num_known = 0
        for i in range(len(People) + len(Weapons), len(People) + len(Weapons) + len(Rooms)):
            for j in range(NUM_PLAYERS):
                if len(self.State[i][j]) and self.State[i][j][0] == 1: num_known += 1
        return num_known

#                                                                                                  #
# SUGGEST THE NEXT BEST GUESS                                                                      #
#                                                                                                  #
    def make_guess(self):
        # TODO: Where more linprogging happens

        coefficients = self.C_People + self.C_Rooms + self.C_Weapons

        result = linprog(c=coefficients, A_ub=A_ub, b_ub=b_ub, method='highs')

        # extract person option
        room_index = result.x[:len(Rooms)].argmax()
        room = Rooms[room_index]

        # extract weapon option
        weapon_index = result.x[len(Rooms):len(Rooms) + len(Weapons)].argmax()
        weapon = Weapons[weapon_index]
    
        # extract person option
        person_index = result.x[len(Rooms) + len(Weapons):].argmax()
        person = People[person_index]

        # If this is the player, suggest a guess and take in player input
        if (not SIMULATED and self.player_num == PLAYER):
            print('Reccomended Guess: ' + person + ', ' + weapon + ', ' + room)
            return
        else:
            print('Guess: ' + person + ', ' + weapon + ', ' + room)
            return person, weapon, room

#                                                                                                  #
# PROCESS A GUESS                                                                                  #
#                                                                                                  #
    def process_guess(self, guesser, answerer, person, weapon, room):
        person_idx = People.index(person)
        weapon_idx = Weapons.index(weapon) + len(People)
        room_idx = Rooms.index(room) + len(People) + len(Weapons)
        # Zero out entries of players who dont have the cards
        for i in range(1,(answerer-guesser-1)%NUM_PLAYERS):
            player = (i + guesser) % NUM_PLAYERS
            self.State[player][person_idx] = [0,[]]
            self.State[player][weapon_idx] = [0,[]]
            self.State[player][room_idx] = [0,[]]
            for j in range(len(Cards)):
                for tup_list in self.State[player][j][1]:
                    if self.State[player][j][0] == 0 or len(tup_list) == 0: continue
                    if person_idx in tup_list: tup_list.pop(person_idx)
                    if weapon_idx in tup_list: tup_list.pop(weapon_idx)
                    if room_idx in tup_list: tup_list.pop(room_idx)
                    if (len(tup_list) == 0): self.State[player][j] = [0,[0]]
        # Update answerer cards
        # TODO: Process Coefficient Matricies
        # TODO: This (specifically the '.5' part)
        # TODO: Correctly update the probabilities based on whether the other cards are known.
        if answerer == self.player_num - 1: return
        elif answerer == -1:
            # TODO: Case where no one had the cards
            print('hi')
            return

        self.State[person_idx][answerer][1].append([weapon_idx, room_idx]) 
        self.State[weapon_idx][answerer][1].append([person_idx, room_idx])
        self.State[room_idx][answerer][1].append([weapon_idx, person_idx])
        # TODO: some linear algebra-ey conditional probablity calculation
        return

#                                                                                                  #
# MAKE AN ACCUSATION IF ABLE                                                                       #
#                                                                                                  #
    def accuse(self):
        person = weapon = room = None
        if (self.len_known_people() == len(People) - 1 and
                self.len_known_weapons() == len(Weapons) - 1 and
                self.len_known_rooms() == len(Rooms) - 1):
            # Make the accusation based on the known cards
            # If no players have the card, than the card must be in the answer set
            for i in range(len(People)):
                for j in range(NUM_PLAYERS):
                    if self.State[i][j][0] == 1: break 
                    if j == NUM_PLAYERS - 1: person = People[i]
            for i in range(len(People), len(People) + len(Weapons)):
                for j in range(NUM_PLAYERS):
                    if self.State[i][j][0] == 1: break 
                    if j == NUM_PLAYERS - 1: weapon = Weapons[i]
            for i in range(len(People) + len(Weapons), len(People) + len(Weapons) + len(Rooms)):
                for j in range(NUM_PLAYERS):
                    if self.State[i][j][0] == 1: break 
                    if j == NUM_PLAYERS - 1: room = Rooms[i]
            assert(person == Answer[0] and weapon == Answer[1] and room == Answer[2]), 'Accusation Incorrect!'
            print('Accusation: ' + str(person) + ', ' + str(weapon) + ', ' + str(room))
            return True
        else:
            return False

#                                                                                                  #
# DETERMINE WHICH CARD (IF ANY) TO SHOW                                                            #
#                                                                                                  #
    def show_card(self, person, weapon, room):
        # Determine which cards this player have that match the guess
        MatchingCards = []
        if (self.Hand.count(room) > 0):
            MatchingCards.append(room)
        if (self.Hand.count(weapon) > 0):
            MatchingCards.append(weapon)
        if (self.Hand.count(person) > 0):
            MatchingCards.append(person)
        
        # Return the card to show (logic depends on number of cards / strategy)
        if (len(MatchingCards) == 0):
            response = None
        elif (len(MatchingCards) == 1):
            response = MatchingCards[0]
        else:
            #TODO: Possibly more linprog for finding the best card to show
            if (self.strategy == 'random'):
                response = MatchingCards[random.randrange(len(MatchingCards))]
            elif (self.strategy == 'simplex'):
                response = MatchingCards[random.randrange(len(MatchingCards))]
            else:
                response = MatchingCards[random.randrange(len(MatchingCards))]

        if response != None: print('Showing Card: ' + response)
        return response

#                                                                                                  #
# RECEIVE A CARD AFTER MAKING A GUESS                                                              #
#                                                                                                  #

    def receive_guess(self, card):
        card_idx = Cards.index(card)
        self.State[card_idx][self.player_num] = [1,[]]
        return

####################################################################################################
####################################################################################################
# HELPER FUNCTIONS                                                                                 #
####################################################################################################
####################################################################################################

#                                                                                                  #
# CALCULATE DISTANCE BETWEEN ROOMS                                                                 #
#                                                                                                  #

def distance_to_room(room1, room2):
    return Distances[Rooms.index(room1)][Rooms.index(room2)]

#                                                                                                  #
# USER ROUND INPUT (NON-SIMULATED CASE)                                                            #
#                                                                                                  #

def user_round():
    try:
        print('Enter the room, weapon, and suspect of the suggestion (or \'n\' if no suggestion is made).' +
            '1: Ballroom\t\t2: Billiard Room\t3: Conservatory\t\t4: Dining Room\n' +
            '5: Hall\t\t\t6: Kitchen\t\t7: Lounge\t\t8: Library\n' +
            '9: Study\t\t10: Knife\t\t11: Pistol\t\t12: Rope\n' +
            '13: Candlestick\t\t14: Wrench\t\t15: Lead Pipe\t\t16: Mrs. White\n' +
            '17: Mr. Green\t\t18: Ms. Scarlet\t\t19: Col. Mustard\t20: Mrs. Peacock\n' +
            '21: Prof. Plum\nCards in Hand: ');
        room = input('Room: ')
        if (room == 'n'): return None, None, None, None, None
        weapon = input('Weapon: ')
        person = input('Person: ')
        receiver = input('Player that received a card: ')
        shower = input('Player that showed a card: ')
        return room, weapon, person, shower, receiver
    except ValueError:
        print('Improperly Formatted Input.')
        exit(1)

#                                                                                                  #
# CREATE PLAYER HANDS                                                                              #
#                                                                                                  #

def createHands():
    random.seed()
    global Answer

    if (SIMULATED):
        tempRooms = copy.deepcopy(Rooms);
        tempWeapons = copy.deepcopy(Weapons);
        tempPeople = copy.deepcopy(People);
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
            hand_len = math.floor((len(Cards) - 3)/NUM_PLAYERS) + ExtraCards[i]
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


####################################################################################################
####################################################################################################
# RUN THE SIMULATOR                                                                                #
####################################################################################################
####################################################################################################

createHands()
Players = []

for i in range(NUM_PLAYERS):
    Players.append(Player(Hands[i], i, PLAYER_STRATEGIES[i]))

player = DEALER

while(True):
    if (SIMULATED):
        # Get next player
        player = (int(player) + 1) % NUM_PLAYERS

        # Player makes a guess
        person, weapon, room = Players[player].make_guess()

        if person == None:
            continue

        # Players answer the guess
        card = None
        answerer = -1
        for i in range(1, NUM_PLAYERS):
            card = Players[(player + i) % NUM_PLAYERS].show_card(person, weapon, room)
            if card != None:
                answerer = (player + i) % NUM_PLAYERS
                break

        # Players process the guess
        for i in range(NUM_PLAYERS):
            print('Guesser: ' + str(player) + '\nAnswerer: ' + str(answerer))
            Players[i].process_guess(player, answerer, person, weapon, room)

        # Guesser processes the received card
        if card != None: Players[player].receive_guess(card)

        # Player makes an accusation if able
        if Players[player].accuse(): break
    else:
        # Get user input for the round and optionally suggest a guess
        recommend = input('Recommend a Guess? (y/n): ')
        if recommend == 'y': print(Players[PLAYER].make_guess())
        person, weapon, room, shower, receiver = user_round()
        Players[PLAYER].process_guess(person, weapon, room)

# Game complete
print("Player", player, "won the game!")

