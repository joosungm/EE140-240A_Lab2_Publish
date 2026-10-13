# Python
gm_ID = 5
L = nch['L']
fu = 5e8
CL = 1e-12
vds = 0.55
# Your code to calculate gm from fu and CL
ID = gm/gm_ID
JD = look_up(nch, 'ID_W', gm_id=gm_ID, l=L, vds=vds)
W = ID/JD
# Your code to obtain fT = gm/2picgg
Av = look_up(nch, 'GM_GDS', gm_id=gm_ID, l=L, vds=vds)
plt.semilogy(L, fT/1e9, '-k')
plt.plot(L, Av, ':k')
plt.show()
