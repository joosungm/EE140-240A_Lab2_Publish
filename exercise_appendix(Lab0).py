# Python
fu = 1e9
fT = fu*10
CL = 1e-12
VDD = 1.1
VDS_range = np.arange(0.1, 1.1, 0.05)
L_range = np.arange(0.05, 0.15, 0.01)
gm_ID = np.zeros((len(L_range), len(VDS_range)))
gds_ID = np.zeros((len(L_range), len(VDS_range)))
Av = np.zeros((len(L_range), len(VDS_range)))
for k, vds in enumerate(VDS_range):
    gm_ID[:, k] = look_up(nch, 'GM_ID', gm_cgg=2*np.pi*fT, vds=vds, l=L_range, branch='left')
    # Your code to calculate gds_ID
    # Your code to calculate Av

gain_opt_idx = np.nanargmax(Av.flatten())
l_idx, vds_idx = np.unravel_index(gain_opt_idx, Av.shape)
vds_opt = VDS_range[vds_idx]
l_opt = L_range[l_idx]
# Your code to calculate gm_ID_opt
# Your code to calculate JD_opt
Cdd_W = look_up(nch, 'CDD_W', gm_id=gm_ID_opt, vds=vds_opt, l=l_opt)
cdd = 0
for i in range(10):
    # Your code to calculate gm
    # Your code to calculate I
    # Your code to calculate W
    cdd = W*Cdd_W

# Your code to calculate RD
# Your code to calculate VGS
