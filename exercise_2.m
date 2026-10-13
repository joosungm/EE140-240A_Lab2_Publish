% MATLAB
gm_ID = 5;
L = nch.L;
fu = 5e8;
CL = 1e-12;
VDS = 0.55;
%% Your code to calculate 'gm' from 'fu' and 'CL'
ID = gm/gm_ID;
JD = look_up(nch, 'ID_W', 'GM_ID', gm_ID, 'L', L, 'VDS', VDS);
W = ID./JD;
%% Your code to obtain fT = gm/2picgg
Av = look_up(nch, 'GM_GDS', 'GM_ID', gm_ID, 'L', L, 'VDS', VDS);
loglog(L, fT/1e9, '-k', L, Av, ':k');
