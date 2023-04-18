#
import numpy as np
X0 = np.array((1,0,1,0))
A = np.array([(0,1,0,0),(0,0,1,0),(0,0,0,1),(1,1,0,0)])

for i in range(10):
    X1 = A.dot(X0)
    print(X1)
    X0 = X1

