% MATLAB
L = [0.05 0.2 0.5 1];
gm_ID = 5:0.1:30
fT = look_up(nch, 'GM_CGG', 'GM_ID', gm_ID, 'L', L)/2/pi;
Av = look_up(nch, 'GM_GDS', 'GM_ID', gm_ID, 'L', L);
semilogy(gm_ID, fT, '-')
hold on
yyaxis right
plot(gm_ID, Av, ':')
