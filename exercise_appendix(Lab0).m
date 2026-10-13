% MATLAB
fu = 1e9;
fT = fu*10;
CL = 1e-12;
VDD = 1.1;
VDS_range = 0.1:0.05:1.1;
L_range = 0.05:0.01:0.15;
for k = 1:length(VDS_range)
  gm_ID(:,k) = look_up(nch,'GM_ID','GM_CGG',2*pi*fT,'VDS',VDS_range(k),'L',L_range);
  % Your code to find gds_ID(:, k)''
  % Your code to find Av(:, k);
end
gain_opt = max(max(Av));
[L_idx, VDS_idx] = find(Av == gain_opt);
VDS_opt = VDS_range(VDS_idx);
L_opt = L_range(L_idx);
% Your code to find gm_ID at the optimal design point
% Your code to find current density (JD) at the optimal design point
Cdd_W = look_up(nch,'CDD_W','GM_ID',gm_ID_opt,'VDS',VDS_opt,'L',L_opt);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Cdd(1) = 0;
for i = 1:10
  % Your code to obtain gm(i) 
  % Your code to obtain I(i) 
  % Your code to obtain W(i)
  Cdd(i+1) = W(i)*Cdd_W;
end
% Your code to find RD
% Your code to find VGS