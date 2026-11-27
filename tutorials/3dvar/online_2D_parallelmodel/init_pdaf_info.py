"""Print information about the chosen filter (translation of init_pdaf_info.F90).

This is a shortened version of the Fortran routine: it prints the name of
the filter and the most important parameters.
"""
import mod_assimilation as assim

# Filter type numbers as defined in PDAF (PDAF_DA_* constants)
FILTER_NAMES = {
    0: 'SEIK', 1: 'SEEK', 2: 'EnKF', 3: 'LSEIK', 4: 'ETKF', 5: 'LETKF',
    6: 'ESTKF', 7: 'LESTKF', 8: 'LEnKF', 9: 'NETF', 10: 'LNETF',
    11: 'LKNETF', 12: 'PF', 13: '3D-Var', 100: 'GENOBS',
}


def init_pdaf_info() -> None:
    """Print the filter configuration."""
    name = FILTER_NAMES.get(assim.filtertype, f'unknown ({assim.filtertype})')
    print(' ' * 21 + f'Filter: {name}')
    print(' ' * 21 + f'subtype: {assim.subtype}')
    print(' ' * 14 + f'ensemble size:{assim.dim_ens:5d}')
    print(' ' * 10 + f'forgetting factor:{assim.forget:6.2f}')
    if assim.filtertype in (3, 5, 7, 8, 10, 11):
        print(' ' * 10 + f'localization cradius:{assim.cradius:8.2f}')
        print(' ' * 10 + f'support radius sradius:{assim.sradius:6.2f}')
