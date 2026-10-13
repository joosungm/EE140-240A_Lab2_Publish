# python
import numpy as np
import matplotlib.pyplot as plt 
from look_up import *
nch = importdata("nch_1v.mat") 
pch = importdata("pch_1v.mat")

L = np.arange(0.1, 1, 0.2)
plt.semilogy(nch['VGS'], look_up(
    nch, 'ID', vgs=nch['VGS'], l=L).T)
plt.show()
