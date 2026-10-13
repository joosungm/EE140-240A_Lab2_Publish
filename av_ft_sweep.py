# Python
L = np.array([0.05, 0.2, 0.5, 1])
gm_ID = np.arange(4, 30, 0.1)
fT = look_up(nch, 'GM_CGG', gm_id=gm_ID, l=L)/2/np.pi
Av = look_up(nch, 'GM_GDS', gm_id=gm_ID, l=L)
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.semilogy(gm_ID, fT.T, '-')
ax2.plot(gm_ID, Av.T, ':')
plt.show()

