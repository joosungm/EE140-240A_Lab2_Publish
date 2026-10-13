# python
VGS = np.arange(0.1, max(nch['VGS']), 0.3)
plt.plot(nch['VDS'], look_up(nch, 'ID', vgs=VGS, vds=nch['VDS']).T)
