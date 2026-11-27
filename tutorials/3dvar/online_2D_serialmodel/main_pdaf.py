"""Model with data assimilation (translation of 3dvar/online_2D_serialmodel/main_pdaf.F90).

3D-Var variants (filtertype 200), selected by -subtype. Parameterized
3D-Var has a single state (1 process), the ensemble methods use one process
per ensemble member::

    python main_pdaf.py -dim_ens 1 -dim_cvec 9 -filtertype 200 -subtype 0 -type_opt 1
    mpiexec -n 9 python main_pdaf.py -dim_ens 9 -filtertype 200 -subtype 1 -type_opt 2
    mpiexec -n 9 python main_pdaf.py -dim_ens 9 -filtertype 200 -subtype 4 -type_opt 2 -dim_cvec 9
"""
from finalize_pdaf import finalize_pdaf
from init_parallel_pdaf import init_parallel_pdaf
from initialize import initialize
from integrate_pdaf import integrate_pdaf
import mod_parallel_pdaf as par


def main() -> None:
    # *** Initialize parallelization for PDAF ***
    init_parallel_pdaf(1)

    if par.mype_world == 0:
        print('\n' + ' ' * 17 + '+++++ PDAF tutorial - online mode +++++\n')
        print(' ' * 16 + 'Tutorial: 2D model without parallelization')
        print('\n')

    # *** Initialize model and PDAF ***
    initialize()

    # *** Time stepping with data assimilation ***
    integrate_pdaf()

    # *** Finalize PDAF ***
    finalize_pdaf()


if __name__ == '__main__':
    main()
