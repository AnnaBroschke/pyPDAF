"""Model with data assimilation (translation of main_pdaf.F90).

This tutorial uses one process per ensemble member (fully parallel ensemble
forecast). Run it with as many processes as ensemble members::

    mpiexec -n 9 python main_pdaf.py -dim_ens 9
    mpiexec -n 9 python main_pdaf.py -dim_ens 9 -filtertype 7 -cradius 5.0
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
