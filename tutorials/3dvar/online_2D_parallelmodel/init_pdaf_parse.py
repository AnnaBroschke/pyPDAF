"""Parse command line options (translation of init_pdaf_parse.F90).

The Fortran version uses ``PDAF_parse`` to read options of the form
``-handle value`` from the command line, e.g.::

    python main_offline.py -filtertype 7 -screen 1 -assim_B .true.

This file implements the same behaviour in pure Python. The type of the
value is taken from the current (default) value of the variable, so that
integers stay integers, reals stay floats and logicals stay bools.
Fortran-style logicals (``.true.``/``.false.``/``T``/``F``) are accepted.
"""
import sys

import mod_assimilation as assim
import obs_A_pdafomi as obs_A
import obs_B_pdafomi as obs_B


def _to_bool(text: str) -> bool:
    """Convert a Fortran or Python style logical string to bool."""
    t = text.strip().strip('.').lower()
    if t in ('true', 't', '1'):
        return True
    if t in ('false', 'f', '0'):
        return False
    raise ValueError(f'Cannot interpret "{text}" as logical')


def pdaf_parse(module, handle: str) -> None:
    """Python counterpart of PDAF_parse.

    If ``-<handle> <value>`` is found in the command line, the variable
    ``module.<handle>`` is overwritten with ``value``.
    """
    args = sys.argv[1:]
    key = '-' + handle
    if key not in args:
        return
    idx = len(args) - 1 - args[::-1].index(key)   # last occurrence wins
    if idx + 1 >= len(args):
        raise ValueError(f'No value given for command line option {key}')
    text = args[idx + 1]
    old = getattr(module, handle)
    if isinstance(old, bool):
        value = _to_bool(text)
    elif isinstance(old, int):
        value = int(text)
    elif isinstance(old, float):
        value = float(text.replace('d', 'e').replace('D', 'e'))
    else:
        value = text
    setattr(module, handle, value)


def init_pdaf_parse() -> None:
    """Parse all supported command line options."""
    # Observation settings
    pdaf_parse(obs_A, 'assim_A')
    pdaf_parse(obs_B, 'assim_B')
    pdaf_parse(obs_A, 'rms_obs_A')
    pdaf_parse(obs_B, 'rms_obs_B')
    pdaf_parse(assim, 'delt_obs')
    pdaf_parse(assim, 'observe_ens')
    pdaf_parse(assim, 'type_obs_init')

    # General settings for PDAF
    pdaf_parse(assim, 'screen')
    pdaf_parse(assim, 'dim_ens')
    pdaf_parse(assim, 'filtertype')
    pdaf_parse(assim, 'subtype')
    pdaf_parse(assim, 'forget')
    pdaf_parse(assim, 'type_forget')
    pdaf_parse(assim, 'type_trans')
    pdaf_parse(assim, 'type_sqrt')
    pdaf_parse(assim, 'rank_ana_enkf')
    pdaf_parse(assim, 'model_error')
    pdaf_parse(assim, 'model_err_amp')
    pdaf_parse(assim, 'dim_lag')

    # 3D-Var settings
    pdaf_parse(assim, 'type_opt')
    assim.dim_cvec = assim.dim_ens       # default: as many columns as ensemble members
    pdaf_parse(assim, 'dim_cvec')
    pdaf_parse(assim, 'mcols_cvec_ens')
    pdaf_parse(assim, 'beta_3dvar')

    # Localisation
    pdaf_parse(assim, 'cradius')
    pdaf_parse(assim, 'locweight')
    assim.sradius = assim.cradius
    pdaf_parse(assim, 'sradius')
