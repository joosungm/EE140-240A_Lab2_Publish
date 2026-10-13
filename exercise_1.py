# Python
import numpy as np
import matplotlib.pyplot as plt 
from look_up import *
nch = importdata("nch_1v.mat") 
pch = importdata("pch_1v.mat")

gm_ID = 15
L = 0.1
fu = 1e9
CL =1e-12
vds = 0.55
fT = look_up(nch, 'GM_CGG', gm_id=gm_ID, l=L, vds=vds)/2/np.pi
# Your code to calculate intrinsic gain 
# Your code to calculate current density JD = ID/W
# Your code to calculate gm from fu and CL
ID = gm / gm_ID
W = ID/JD
VGS = look_up(nch, 'VGS', gm_id=gm_ID, l=L, vds=vds)
