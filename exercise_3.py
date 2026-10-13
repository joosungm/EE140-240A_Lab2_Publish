# python
L = nch['L']
fu = 5e8
CL = 1e-12
vds = 0.55
gm_id_range = np.linspace(5, 30, 50)
gm_id = []
av = []
for i, l in enumerate(L):
    # your code to obtain ft
    m = ft >= 10*fu
    if(any(m)):
        gm_id.append(gm_id_range[max(np.where(m==1)[0])])
    else:
        gm_id.append(float('nan'))
    # your code to obtain av[i] = gm/gds

fig, ax = plt.subplots(1)
ax.plot(L, av)
ax.plot(L, gm_id)
plt.show()

gm_id_opt = x # replace x based on the results above
l_opt = y     # replace y based on the results above
# your code to find jd = id/w
cdd_w = look_up(nch, 'CDD_W', gm_id=gm_id_opt, l=l_opt)
cdd = 0
for i in range(1, 10):
    gm_opt = 2 * np.pi * fu*(CL + cdd)
    # your code to calculate id
    w = id / jd
    cdd = w * cdd_w
