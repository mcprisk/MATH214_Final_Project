from scipy.optimize import linprog
import numpy as np

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


# run the linear programming algorithm to minimize the total cost
result = linprog(c=coefficients, A_ub=A_ub, b_ub=b_ub, method='highs')

# print the results
print(result.x)

