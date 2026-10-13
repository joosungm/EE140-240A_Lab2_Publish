% MATLAB
L = nch.L;
fu = 5e8;
CL = 1e-12;
gm_ID_range = linspace(5, 30, 50);
gm_ID = [];
for i = 1:length(L)
	% Your code to obtain fT
	M = fT >= 10*fu;
	if(any(M))
		gm_ID(i) = gm_ID_range(max(find(M==1)));
	else
		gm_ID(i) = NaN;
	end
	%% Your code to obtain Av(i) = gm/gds
end
plot(L, Av, L, gm_ID);
%%%%%%%%%%%%%%%%%%%%%%
gm_ID_opt = X; % replace X based on the results obtained above
L_opt = Y;     % replace Y based on the results obtained above
%% your code to obtain JD = ID/W;
Cdd_W = look_up(nch, 'CDD_W', 'GM_ID', gm_ID_opt, 'L', L_opt);
Cdd(1) = 0;
for m = 1:10
	gm_opt = 2 * pi * fu*(CL+Cdd(m));
	%% Your code to obtain ID(m) %%
	W(m) = ID(m)./JD;
	Cdd(m+1) = W(m)*Cdd_W;
end

