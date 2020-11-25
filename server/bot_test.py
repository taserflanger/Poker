from bot.genectic.GenerationManager import GenerationManager
from numpy import array

engine = GenerationManager(sizes=[50, 50], mutation_factor=1)
Params = {"W":None, "b": None, "f": None}

# read params
for s in "W", "b","f":
    with open(f"bot/genectic/{s}.csv") as file:
        Params[s] = eval(file.read())

W, b, f = engine.train(100, 100, 5, 5, 1)

# write params
for s, X in zip(("W", "b", "f"), W, b, f):
    with open(f"bot/genectic/{s}.csv") as file:
        file.write(str(X))

