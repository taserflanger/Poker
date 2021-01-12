# %%
import numpy as np
import tensorflow as tf

from parse_data import games, predictions

model = tf.keras.layers.LSTM(3)

# %%
model(games[0])
