# Python
fu = 1e8
ft = fu*10
CL = 1e-12
VDD = 1.1
Vout_range = np.arange(0.3, 0.7, 0.05)
L_range = nch['L']
gm_ID_range = np.arange(5, 30, 1)
# Calculated over the sweep
best_p_l = np.zeros(len(Vout_range))
best_Av = np.zeros((len(Vout_range), len(L_range)))
best_n_gm_id = np.zeros((len(Vout_range), len(L_range)))
# Sweep over Vout
for i, vout in enumerate(Vout_range):
    # Find the best PMOS L
    p_gds_id_vs_l = ...  # Your code to look up PMOS gds/ID across l given VGS, VDS
    p_ft_vs_l = ...  # Your code to look up pmos ft across l given VSG, VDS
    M = p_ft_vs_l > ft
    if any(M): 
        # We know gds_id will decrease as L increases, so find the highest L
        best_idx = max(np.where(M==1)[0])
        p_gds_id = p_gds_id_vs_l[best_idx]
        best_p_l[i] = L_range[best_idx]
        # Knowing PMOS GDS and L, optimize NMOS L and gm_ID
        for j, l in enumerate(L_range):
            n_gds_id = ...  # Your code to find the NMOS gds_ID across the gm_ID range 
            n_ft = ...  # Your code to find NMOS ft across the gm_ID range 
            av = ...  # your code to find Av from gm_ID_range, n_gds_id, p_gds_id
            K = n_ft > ft
            if any(K):
                best_idx = np.argmax(np.where(K==1, av, 0))
                best_n_gm_id[i, j] = gm_ID_range[best_idx]
                best_Av[i, j] = av[best_idx]
            else:
                best_n_gm_id[i, j] = float('NaN')
                best_Av[i, j] = float('NaN')
    else:
        best_p_l[i] = float('NaN')
        best_n_gm_id[i, :] = float('NaN')
        best_Av[i, :] = float('NaN')
# Find the Best Av
vout_idx, n_l_idx = np.unravel_index(np.nanargmax(best_Av.flatten()), best_Av.shape)
opt_n_gm_id = best_n_gm_id[vout_idx, n_l_idx]
opt_p_l = best_p_l[vout_idx]
opt_n_l = ...  # Your code to find the optimum nmos L
opt_vout = ...  # Your code to find the optimum Vout
# Find the real widths of the devices
n_cdd_w = ...  # Your code to find the nmos CDD/W at the optimum gm_ID, L, VDS
n_jd = ...  # Your code to find the nmos JD at the optimum gm_ID, L, VDS 
p_cdd_w = ...  # Your code to find the pmos CDD/W at the optimum VGS, VDS, L
p_jd = ...  # Your code to find the pmos JD at the optimum VGS, VDS, L
# Iterate to find W
cdd = 0
for i in range(10):
    gm = 2 * np.pi * fu * (CL + cdd)
    i = gm / opt_n_gm_id
    wn = i / n_jd
    wp = i / p_jd
    cdd = ...  # Your code to update Cdd 
