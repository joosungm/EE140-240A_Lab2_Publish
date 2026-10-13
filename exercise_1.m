% MATLAB
gm_ID = 15;
L = 0.1;
fu = 1e9;
CL = 1e-12;
vds = 0.55;
fT = look_up(nch, 'GM_CGG', 'GM_ID', gm_ID, 'L', L)/2/pi;
%% Your code to obtain the intrinsic gain
%% Your code to obtain the current density JD = ID/W
%% Your code to calculate 'gm' from 'fu' and 'CL'
ID = gm/gm_ID;
W = ID/JD;
VGS = look_upVGS(nch, 'GM_ID', gm_ID, 'L', L);
