"""
Python based Gm/Id lookup
Aviral Pandey, 2023; Built from look_up function by Boris Murmuann
Joosung Moon, 2026; Made some changes to make the function efficient, and works similarly to the Matlab code (With AI tools)

Changes:
- Unified direct, arbitrary-ratio, and VGS queries in look_up().
- Added VGB/VDB-based VGS lookup for an unknown source voltage.
- Added MATLAB-style name/value arguments and case-insensitive keywords.
- Added selectable 1-D interpolation with MATLAB's PCHIP default.
- Interpolate table ratios as in MATLAB; cache ratio interpolators.
- Detect multiple solutions; return NaN for targets outside the search range.
- Vectorized coordinates and reused grids; retained existing function names.

Usage:
    nch = importdata('nch_1v.mat')                    # Load data and build interpolators.
    id_val = look_up(nch, 'ID', vgs=0.6, l=0.1)       # Find drain current at the given bias.
    wt = look_up(nch, 'GM_CGG', gm_id=15, l=0.1)      # Find GM/CGG at GM/ID=15.
    wt = look_up(nch, 'GM_CGG', gm_gds=20, l=0.1)     # Query using any table-parameter ratio.
    vgs = look_up(nch, 'VGS', gm_id=15, l=0.1)        # Find VGS with known VDS/VSB (defaults).
    vgs = look_up(nch, 'VGS', gm_id=15, vgb=1, vdb=0.6, l=0.1)  # Unknown source voltage.
    wt = look_up(nch, 'GM_CGG', 'GM_ID', 15, 'METHOD', 'linear')  # MATLAB-style arguments.

Notes:
- Multidimensional table interpolation remains linear, as in MATLAB.
- Direct axes: (L, VGS, VDS, VSB); ratio axes: (L, VDS, VSB, targets).
- Singleton axes are squeezed by default; use squeeze=False to retain them.
- Ratio searches use all VGS by default. Specify vgs or branch='left'/'right'
  to select a solution when a curve has multiple intersections.
- paired=True evaluates corresponding bias points rather than all combinations.
- Unknown-source queries use VGS=VGB-VSB and VDS=VDB-VSB in the table's
  voltage convention.
- Methods: pchip, linear, nearest, next, previous, spline, makima; cubic is
  a PCHIP alias matching the original MATLAB starter kit.
References: https://github.com/bmurmann/Book-on-gm-ID-design / https://github.com/jarvis94/Gm-ID-starter-kit
"""

from scipy.io import loadmat
import scipy.interpolate as interp
import numpy as np

_out_vars = ['W', 'ID', 'VT', 'IGD', 'IGS', 'GM', 'GMB', 'GDS',
             'CGG', 'CGS', 'CGD', 'CDG', 'CGB', 'CDD', 'CSS', 'STH', 'SFL']
_in_vars = ['L', 'VGS', 'VDS', 'VSB']
_info_vars = ['INFO', 'CORNER', 'TEMP', 'NFING']
_ignore_keys = ['__version__', '__header__', '__globals__']


def _build_interpolator(var, l, vgs, vds, vsb):
    return interp.RegularGridInterpolator(
        (l, vgs, vds, vsb), var, bounds_error=False, fill_value=np.nan)


def importdata(filename):
    """Load MATLAB device data into a dictionary of grids and interpolators."""
    loaded = loadmat(filename, simplify_cells=True)
    data = next((value for key, value in loaded.items()
                 if key not in _ignore_keys and isinstance(value, dict)
                 and all(axis in value for axis in _in_vars)), None)
    if data is None:
        raise ValueError('No device data structure found in the MAT file.')
    for axis in _in_vars:
        data[axis] = _correct_arr(data[axis], None)
    grid = tuple(data[axis] for axis in _in_vars)
    shape = tuple(len(axis) for axis in grid)
    for name in _out_vars:
        if name in data:
            values = np.asarray(data[name], dtype=float)
            if name == 'W':
                values = np.broadcast_to(values, shape)
            else:
                values = values.reshape(shape)
            data[name] = _build_interpolator(values, *grid)
    data['_RATIO_CACHE'] = {}
    return data


def _correct_arr(var, default):
    var = default if var is None else var
    if var is None:
        raise ValueError('A numeric value is required.')
    arr = np.atleast_1d(np.asarray(var, dtype=float))
    if arr.ndim != 1 or arr.size == 0 or not np.all(np.isfinite(arr)):
        raise ValueError('Expected a finite scalar or nonempty 1-D numeric sequence.')
    return arr


def _build_lookup_grid(data_dict, vgs=None, vds=None, vsb=None, l=None, *, paired=False):
    axes = (
        _correct_arr(l, np.min(data_dict['L'])),
        _correct_arr(vgs, data_dict['VGS']),
        _correct_arr(vds, np.max(data_dict['VDS']) / 2),
        _correct_arr(vsb, 0),
    )
    if paired:
        return np.stack(np.broadcast_arrays(*axes), axis=-1)
    return np.stack(np.meshgrid(*axes, indexing='ij', copy=False), axis=-1)


def _evaluate_lookup(data_dict, out_var, x):
    """Reuse coordinates and interpolate ratios computed on the table grid."""
    out_var = out_var.upper()
    if out_var in _in_vars:
        return x[..., _in_vars.index(out_var)]
    if '_' not in out_var:
        if out_var not in data_dict or not callable(data_dict[out_var]):
            raise ValueError(f'Unknown output parameter: {out_var}')
        return data_dict[out_var](x)
    parts = out_var.split('_')
    if len(parts) != 2 or any(name not in data_dict or not callable(data_dict[name])
                              for name in parts):
        raise ValueError(f'Invalid parameter ratio: {out_var}')
    cache = data_dict.setdefault('_RATIO_CACHE', {})
    if out_var not in cache:
        numerator, denominator = (data_dict[name] for name in parts)
        with np.errstate(divide='ignore', invalid='ignore'):
            values = numerator.values / denominator.values
        values[~np.isfinite(values)] = np.nan
        cache[out_var] = interp.RegularGridInterpolator(
            numerator.grid, values, bounds_error=False, fill_value=np.nan)
    return cache[out_var](x)


def _look_up_basic(data_dict, out_var, vgs=None, vds=None, vsb=None, l=None):
    return _evaluate_lookup(data_dict, out_var,
                            _build_lookup_grid(data_dict, vgs, vds, vsb, l))


def look_up_basic(data_dict, out_var, vgs=None, vds=None, vsb=None, l=None):
    return np.squeeze(_look_up_basic(data_dict, out_var, vgs, vds, vsb, l))


def _parse_options(args, kwargs):
    if len(args) % 2:
        raise ValueError('Positional options must be name/value pairs.')
    options = {}
    for key, value in list(zip(args[::2], args[1::2])) + list(kwargs.items()):
        if not isinstance(key, str):
            raise ValueError('Option names must be strings.')
        key = key.lower()
        if key in options:
            raise ValueError(f'Duplicate option: {key}')
        options[key] = value
    return options


def _curve_segments(x, y):
    """Split finite runs into monotonic pieces without crossing data gaps."""
    valid = np.isfinite(x) & np.isfinite(y)
    edges = np.diff(np.r_[False, valid, False].astype(int))
    segments, plateaus = [], []
    for first, stop in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
        start, direction = first, 0
        for i in range(first, stop - 1):
            sign = np.sign(x[i + 1] - x[i])
            if sign == 0:
                segments.append((x[start:i + 1], y[start:i + 1], np.arange(start, i + 1)))
                plateaus.append((x[i], y[i], y[i + 1], i))
                start, direction = i + 1, 0
            else:
                if direction and sign != direction:
                    segments.append((x[start:i + 1], y[start:i + 1], np.arange(start, i + 1)))
                    start = i
                direction = sign
        segments.append((x[start:stop], y[start:stop], np.arange(start, stop)))
    return segments, plateaus


def _interpolate_curve(x, y, targets, *, method='pchip', branch='all'):
    """Invert a sampled curve, rejecting distinct solutions for one target."""
    method, branch = method.lower(), branch.lower()
    if method not in {'pchip', 'linear', 'nearest', 'next', 'previous',
                       'spline', 'cubic', 'makima'}:
        raise ValueError('Unsupported 1-D interpolation method.')
    if branch not in {'all', 'left', 'right'}:
        raise ValueError('branch must be all, left, or right.')
    x, y = np.asarray(x).reshape(-1), np.asarray(y).reshape(-1)
    if branch != 'all' and np.any(np.isfinite(x)):
        peak = np.nanargmax(np.where(np.isfinite(x), x, np.nan))
        selection = slice(None, peak + 1) if branch == 'left' else slice(peak, None)
        x, y = x[selection], y[selection]
    segments, plateaus = _curve_segments(x, y)
    candidates = [[] for _ in targets]
    for xp, yp, positions in segments:
        if not len(xp):
            continue
        if xp[-1] < xp[0]:
            xp, yp, positions = xp[::-1], yp[::-1], positions[::-1]
        inside = (targets >= xp[0]) & (targets <= xp[-1])
        if len(xp) == 1:
            values = np.full(np.count_nonzero(inside), yp[0])
        elif method in {'pchip', 'cubic'}:
            values = interp.PchipInterpolator(xp, yp, extrapolate=False)(targets[inside])
        elif method == 'spline':
            values = interp.CubicSpline(xp, yp, extrapolate=False)(targets[inside])
        elif method == 'makima':
            values = interp.Akima1DInterpolator(
                xp, yp, method='makima', extrapolate=False)(targets[inside])
        else:
            if not np.any(inside):
                continue
            values = interp.interp1d(xp, yp, kind=method, bounds_error=False,
                                    fill_value=np.nan)(targets[inside])
        locations = np.interp(targets[inside], xp, positions)
        for i, value, location in zip(np.flatnonzero(inside), values, locations):
            candidates[i].append((float(value), float(location)))
    result = np.full(len(targets), np.nan)
    for i, target in enumerate(targets):
        for value, left, right, position in plateaus:
            if target == value:
                candidates[i].extend([(float(left), float(position)),
                                      (float(right), float(position + 1))])
        solutions = candidates[i]
        if solutions:
            locations = [location for _, location in solutions]
            if not np.allclose(locations, locations[0], rtol=1e-10, atol=1e-12):
                raise ValueError(f'Multiple curve intersections at target {target:g}; '
                                 'restrict vgs or specify branch="left"/"right".')
            result[i] = solutions[0][0]
    return result


def _look_up_vs_ratio(data_dict, yvar, x_name, x_desired,
                      vgs=None, vds=None, vsb=None, l=None, lim_left=False,
                      lim_right=False, *, method='pchip', branch='all'):
    targets = _correct_arr(x_desired, None)
    coordinates = _build_lookup_grid(data_dict, vgs, vds, vsb, l)
    x = _evaluate_lookup(data_dict, x_name, coordinates).reshape(-1)
    y = _evaluate_lookup(data_dict, yvar, coordinates).reshape(-1)
    if lim_left and lim_right:
        raise ValueError('Select only one branch.')
    branch = 'left' if lim_left else 'right' if lim_right else branch
    return _interpolate_curve(x, y, targets, method=method, branch=branch)


def _look_up_vs_ratio_swp(data_dict, yvar, x_name, x_desired,
                          vgs=None, vds=None, vsb=None, l=None,
                          *, squeeze=True, **kwargs):
    l = _correct_arr(l, np.min(data_dict['L']))
    vds = _correct_arr(vds, np.max(data_dict['VDS']) / 2)
    vsb = _correct_arr(vsb, 0)
    targets = _correct_arr(x_desired, None)
    vgs = _correct_arr(vgs, data_dict['VGS'])
    # One grid and two table evaluations for the entire bias sweep.
    coordinates = _build_lookup_grid(data_dict, vgs, vds, vsb, l)
    x = np.moveaxis(_evaluate_lookup(data_dict, x_name, coordinates), 1, -1)
    y = np.moveaxis(_evaluate_lookup(data_dict, yvar, coordinates), 1, -1)
    out = np.empty((len(l), len(vds), len(vsb), len(targets)))
    lim_left, lim_right = kwargs.pop('lim_left', False), kwargs.pop('lim_right', False)
    if lim_left and lim_right:
        raise ValueError('Select only one branch.')
    if lim_left or lim_right:
        kwargs['branch'] = 'left' if lim_left else 'right'
    for index in np.ndindex(out.shape[:-1]):
        out[index] = _interpolate_curve(x[index], y[index], targets, **kwargs)
    return np.squeeze(out) if squeeze else out


def _look_up_unknown_source(data_dict, targets, vgb, vdb, l,
                            *, method='pchip', branch='all', squeeze=True):
    """Search VGS=VGB-VSB and VDS=VDB-VSB with scalar terminal biases."""
    vgb, vdb, l = (_correct_arr(value, default) for value, default in
                  ((vgb, None), (vdb, None), (l, np.min(data_dict['L']))))
    if any(len(value) != 1 for value in (vgb, vdb, l)):
        raise ValueError('Unknown-source lookup requires scalar vgb, vdb, and l.')
    vgb, vdb, length = vgb[0], vdb[0], l[0]
    if not np.min(data_dict['L']) <= length <= np.max(data_dict['L']):
        raise ValueError('l is outside the device table.')
    lower = max(np.min(data_dict['VSB']), vgb - np.max(data_dict['VGS']),
                vdb - np.max(data_dict['VDS']))
    upper = min(np.max(data_dict['VSB']), vgb - np.min(data_dict['VGS']),
                vdb - np.min(data_dict['VDS']))
    if lower >= upper:
        raise ValueError('No source-voltage search interval lies within the device table.')
    spacing = np.min(np.abs(np.diff(data_dict['VGS'])))
    vsb = np.linspace(lower, upper, max(2, int(np.ceil((upper - lower) / spacing)) + 1))
    # Sort by increasing VGS so branch selection has the same meaning as usual.
    coordinates = _build_lookup_grid(data_dict, vgb - vsb[::-1],
                                     vdb - vsb[::-1], vsb[::-1], length, paired=True)
    ratio = _evaluate_lookup(data_dict, 'GM_ID', coordinates)
    result = _interpolate_curve(ratio, coordinates[..., 1], targets,
                                method=method, branch=branch)
    return np.squeeze(result) if squeeze else result.reshape(1, 1, 1, -1)


def look_up(data_dict, out_var, *args, **kwargs):
    """Unified lookup; accepts Python keywords or MATLAB name/value pairs.

    Any parameter ratio can be a condition, e.g. gm_gds=20. Use method to
    choose the final 1-D interpolation; table interpolation is always linear.
    For unknown-source VGS queries, supply gm_id, vgb and vdb. Do not mix
    vgb/vdb with vgs/vds/vsb. Missing/out-of-range intersections return NaN.
    """
    options = _parse_options(args, kwargs)
    out_var = out_var.upper()
    known = {'vgs', 'vds', 'vsb', 'l', 'vgb', 'vdb', 'method', 'branch', 'paired', 'squeeze'}
    ratios = [(key.upper(), value) for key, value in options.items()
              if key not in known and '_' in key and value is not None]
    unknown = [key for key in options if key not in known and '_' not in key]
    if unknown:
        raise ValueError(f'Unknown options: {", ".join(unknown)}')
    if len(ratios) > 1:
        raise ValueError('Specify only one input ratio.')
    method = options.get('method', 'pchip')
    branch = options.get('branch', 'all')
    squeeze = options.get('squeeze', True)
    paired = options.get('paired', False)
    bias = {name: options.get(name) for name in ('vgs', 'vds', 'vsb', 'l')}
    if options.get('vgb') is not None or options.get('vdb') is not None:
        if (out_var != 'VGS' or len(ratios) != 1 or ratios[0][0] != 'GM_ID'
                or options.get('vgb') is None or options.get('vdb') is None):
            raise ValueError('vgb/vdb require a VGS query with gm_id and both terminal voltages.')
        if paired or any(bias[name] is not None for name in ('vgs', 'vds', 'vsb')):
            raise ValueError('Do not combine vgb/vdb with vgs/vds/vsb or paired=True.')
        return _look_up_unknown_source(data_dict, _correct_arr(ratios[0][1], None),
                                       options['vgb'], options['vdb'], bias['l'],
                                       method=method, branch=branch, squeeze=squeeze)
    if not ratios:
        coordinates = _build_lookup_grid(data_dict, **bias, paired=paired)
        result = _evaluate_lookup(data_dict, out_var, coordinates)
        return np.squeeze(result) if squeeze else result
    if paired:
        raise ValueError('paired=True is supported only for direct bias queries.')
    name, target = ratios[0]
    return _look_up_vs_ratio_swp(data_dict, out_var, name, target, **bias,
                                 method=method, branch=branch, squeeze=squeeze)


def look_up_vs_gm_id(data_dict, yvar, gm_id, vgs=None, vds=None, vsb=None, l=None,
                     *, method='pchip'):
    return look_up(data_dict, yvar, gm_id=gm_id, vgs=vgs, vds=vds, vsb=vsb,
                   l=l, method=method, branch='right')


def look_up_vs_gm_cgg(data_dict, yvar, gm_cgg, vgs=None, vds=None, vsb=None, l=None,
                      *, method='pchip'):
    return look_up(data_dict, yvar, gm_cgg=gm_cgg, vgs=vgs, vds=vds, vsb=vsb,
                   l=l, method=method, branch='left')


def look_up_vs_id_w(data_dict, yvar, id_w, vgs=None, vds=None, vsb=None, l=None,
                    *, method='pchip'):
    return look_up(data_dict, yvar, id_w=id_w, vgs=vgs, vds=vds, vsb=vsb,
                   l=l, method=method)


def look_upVGS(data_dict, *args, **kwargs):
    """MATLAB-compatible companion name for look_up(data, 'VGS', ...)."""
    options = _parse_options(args, kwargs)
    if options.get('gm_id') is None:
        raise ValueError('look_upVGS requires gm_id.')
    return look_up(data_dict, 'VGS', **options)


def look_up_vgs_vs_gm_id(data_dict, gm_id, vds=None, vsb=None, l=None, *, method='pchip'):
    return look_upVGS(data_dict, gm_id=gm_id, vds=vds, vsb=vsb, l=l, method=method)
