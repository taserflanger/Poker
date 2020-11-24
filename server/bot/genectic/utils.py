import numpy as np


def relu(x):
    """
    fonction d’activation
    :param x:
    :return:
    """
    return np.maximum(x, 0, x)
