% MATLAB
fu = 1e8;
ft = fu*10;
CL = 1e-12;
VDD = 1.1;
Vout_range = 0.3:0.05:0.7;
L_range = nch.L;
gm_ID_range = 2:1:30;
% Sweep over Vout
for i = 1:length(Vout_range)
	% Find the best PMOS L
	p_gds_id_vs_l = % Your code to look up pmos gds/ID across l given VGS, VDS
	p_ft_vs_l = % Your code to look up pmos ft across l given VGS, VDS
	M = p_ft_vs_l > ft;
	if (any(M))
		% We know gds_id will decrease as L increases, so find the highest L 
		best_idx = max(find(M==1));
		p_gds_id = p_gds_id_vs_l(best_idx);
		best_p_l(i) = L_range(best_idx);
		% Knowing PMOS GDS and L, we can optimize the NMOS L and gm_ID
		for j = 1:length(L_range)
			% Find the gm_ID that maximizes overall gain while meeting ft constraint
			n_gds_id = % Your code to find the NMOS gds_id across the gm_ID_range
			n_ft = % Your code to find the NOMS fT across the gm_ID range
			av = % Your code to find Av from gm_ID_range, n_gds_id and p_gds_id
			K = n_ft > ft;
			if (any(K)) 
				max_av = max(av(find(K==1)));
				best_idx = find(av==max_av);
				best_n_gm_ID(i, j) = gm_ID_range(best_idx);
				best_Av(i, j) = av(best_idx);
			else
				best_n_gm_ID(i,j) = NaN;
				best_Av(i,j) = NaN;
			end
		end
	else
		best_n_gm_ID(i, :) = NaN;
		best_Av(i, :) = NaN;
		best_p_l(i) = NaN;
	end
end
% Find the best Av
max_gain = max(max(best_Av));
[Vout_idx, n_L_idx] = find(best_Av == max_gain);
opt_p_L = best_p_l(Vout_idx);
opt_n_gm_ID = best_n_gm_ID(Vout_idx, n_L_idx);
opt_n_L = % Your code to find the optimum nmos L
opt_Vout = % Your code to find the optimal Vout
% Find the real widths of the devices
n_cdd_w = % Your code to find the nmos CDD/W at the optimum gm_ID, L, VDS
n_JD = % Your code to find the nmos JD at the optimum gm_ID, L, VDS
p_cdd_w = % Your code to find the pmos CDD/W at the optimum VGS, VDS, L
p_JD = % Your code to find the pmos JD at the optimum VGS, VDS, L
% Iterate to find W
Cdd(1) = 0;
for i = 1:10
	gm(i) = 2 * pi * fu * (CL + Cdd(i));
	I(i) = gm(i) / opt_n_gm_ID;
	Wn(i) = I(i) / n_JD;
	Wp(i) = I(i) / p_JD;
	Cdd(i+1) = % Your code to find Cdd
end
