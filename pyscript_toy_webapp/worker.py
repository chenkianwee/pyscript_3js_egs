import io
from pyscript import sync
import numpy as np

def heavy_compute():
    res = np.array([1234, 5678, 91011])
    return res

sync.heavy_compute = heavy_compute