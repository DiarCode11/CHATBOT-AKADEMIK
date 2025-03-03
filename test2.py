import numpy as np

A = np.array([1, 2, 5])
B = np.array([4, 6, 6])

distance = np.linalg.norm(A - B)
print(distance)  # Output: 5.0
