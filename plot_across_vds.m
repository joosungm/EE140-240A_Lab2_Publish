% MATLAB
VGS = 0.1:0.3:max(nch.VGS);
plot(nch.VDS, look_up(nch, 'ID', 'VGS', VGS, 'VDS', nch.VDS))
