from bot.genectic.GenerationManager import GenerationManager
import numpy as np

SIZES = [50]
# ne pas modifier sans générer de nouveaux paramètres
Params = {"W": [], "b": [], "f": []}

# read params
for s in "W", "b", "f":
    for i in range(len(SIZES) + 2):
        # car on ajoute les layer (il y en a un pour les indices)
        Params[s].append(np.loadtxt(f"bot/genectic/data/{s}{str(i)}.csv"))

engine = GenerationManager(
    sizes=SIZES,
    mutation_factor=1,
    W=Params["W"],
    b=Params["b"],
    f=Params["f"]
)

W, b, f = engine.train(N=100, m=1, nb_players=5, small_blind=5, max_round=1)

# write params
for s, X in zip(("W", "b", "f"), (W, b, f)):
    for i in range(len(X)):
        np.savetxt(f"bot/genectic/data/{s}{str(i)}.csv", X[i])
