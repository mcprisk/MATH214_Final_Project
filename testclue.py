from scipy.optimize import linprog
import numpy as np

Rooms = ['Ball', 'Billiard', 'Conservatory', 'Dining', 'Hall', 'Kitchen', 'Lounge', 'Library', 'Study']
Weapons = ['Knife', 'Pistol', 'Rope', 'Candlestick', 'Wrench', 'Lead_Pipe']
People = ['White', 'Green', 'Scarlet', 'Mustard', 'Peacock', 'Plum']

# define the coefficients for 3 suspects, 3 weapons, and 3 rooms
# coefficients would be from 0-100, representing probability we know something ISN'T part of the murder
# e.g. 100 means we def know it isn't part of the murder
C = [100, 75, 50, 100, 100, 100, 100, 100, 100]  # costs for suspects
D = [100, 0, 100, 100, 100, 100]  # costs for weapons
E = [100, 0, 100, 100, 100, 100]  # costs for rooms

# combine all coefficients into one list for the linear program
coefficients = C + D + E

# define the inequality constraints
A_ub = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],  # neg because we need to convert >= to <= for linprog
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1]
]
b_ub = [-1, -1, -1]  # negative for the same reason as A_ub


# results.x will print out a 1d array of options
result = linprog(c=coefficients, A_ub=A_ub, b_ub=b_ub, method='highs')


# extract room option
room_index = result.x[:len(Rooms)].argmax()
room = Rooms[room_index]
    
# extract weapon option
weapon_index = result.x[len(Rooms):len(Rooms) + len(Weapons)].argmax()
weapon = Weapons[weapon_index]
    
# extract person option
person_index = result.x[len(Rooms) + len(Weapons):].argmax()
person = People[person_index]

print(room, weapon, person) # remove later

return room, weapon, person

