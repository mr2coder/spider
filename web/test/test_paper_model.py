import numpy as np

a = np.ones((2,3))
a[1,0] = 2
print(a)
print(a[1::2])