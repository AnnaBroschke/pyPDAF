"""Common helper functions for the plotting scripts of the pyPDAF tutorials.

The scripts are based on PDAF/tutorial/plotting. Fields are shown in grid
coordinates x = 1..nx, y = 1..ny (1-based, as in PDAF and in the observation
files).
"""
import os
import re

import matplotlib
if not os.environ.get('DISPLAY'):
    matplotlib.use('Agg')          # no display: only saving figures is possible
import matplotlib.pyplot as plt
import numpy as np

NX, NY = 36, 18                    # Grid size of the tutorial model
MISSING = -999.0                   # Missing value in observation files

# Diverging colour map for fields with values around zero
CMAP_FIELD = 'RdBu_r'
CMAP_DIFF = 'PiYG'

_PATTERN = re.compile(
    r'^(?P<kind>ens|state|true|obs|iobs_field)(?P<field>[AB]?)'
    r'(?:_(?P<member>\d+))?(?:_step(?P<step>\d+))?(?:_(?P<phase>ini|for|ana))?\.txt$')
_PHASE = {'for': 'forecast', 'ana': 'analysis', 'ini': 'initial'}


def read_field(filename: str) -> np.ndarray:
    """Read a 2D field (ny rows, nx columns)."""
    field = np.loadtxt(filename)
    if field.ndim == 1:
        field = field.reshape(NY, NX)
    return field


def describe(filename: str) -> str:
    """Readable description derived from the file name of a tutorial output.

    e.g. 'state_step18_ana.txt' -> 'Analysis state, step 18'
         'ensB_03_step04_for.txt' -> 'Forecast ensemble member 3, field B, step 4'
    Unknown names are returned unchanged.
    """
    name = os.path.basename(filename)
    m = _PATTERN.match(name)
    if not m:
        return name
    kind, field, member, step, phase = m.group('kind', 'field', 'member', 'step', 'phase')
    text = {'ens': f'ensemble member {int(member)}' if member else 'ensemble',
            'state': 'state', 'true': 'true state', 'obs': 'observations',
            'iobs_field': 'interpolated observations'}[kind]
    if phase:
        text = f'{_PHASE[phase]} {text}'
    if field and kind == 'obs':
        text += f' {field}'              # observation type, e.g. obsB
    elif field:
        text += f', field {field}'
    if step:
        text += f', step {int(step)}'
    return text[0].upper() + text[1:]


def show_field(ax, field: np.ndarray, cmap: str, vmax: float):
    """Show a 2D field in grid coordinates with symmetric colour limits."""
    ny, nx = field.shape
    img = ax.imshow(field, origin='lower', interpolation='none', cmap=cmap,
                    vmin=-vmax, vmax=vmax, extent=(0.5, nx + 0.5, 0.5, ny + 0.5))
    ax.set_xlabel('x (grid point)')
    ax.set_ylabel('y (grid point)')
    ax.set_xticks([1] + list(range(5, nx + 1, 5)))
    ax.set_yticks([1] + list(range(5, ny + 1, 5)))
    return img


def sym_limit(*arrays: np.ndarray) -> float:
    """Symmetric colour limit: maximum absolute (finite, unmasked) value."""
    vals = [np.max(np.abs(a.compressed() if np.ma.isMaskedArray(a) else a))
            for a in arrays]
    return float(max(vals)) or 1.0


def show_or_save(save, default_name: str) -> None:
    """Show the figure, or save it as PNG if --save is given or no display is available."""
    if save is None and not os.environ.get('DISPLAY'):
        save = default_name
    if save:
        plt.savefig(save, dpi=150, bbox_inches='tight')
        print('Figure saved to', save)
    else:
        plt.show()
