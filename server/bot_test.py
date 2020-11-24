from bot.genectic.Bot import Bot
import numpy as np

b = Bot("TheBot", 100, [100, 200])
b.forward_propagate([
    [1, 0, 0, 12, 20],
    [0, 1, 0, 12, 25],
    [1, 0, 0, 12, 20],
    [1, 0, 0, 12, 20],
])
print(b.L[-1])
