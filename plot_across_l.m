% MATLAB
L = 0.1:0.2:1;   % Lengths of interest
semilogy(nch.VGS, look_up(nch, 'ID', 'VGS', nch.VGS, 'L', L));
