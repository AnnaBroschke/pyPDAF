"""Parallel model with data assimilation (translation of online_2D_parallelmodel/main_pdaf.F90).

The processes are split into ``dim_ens`` model tasks; each task runs the
parallel model. The number of processes per task must divide nx = 36, e.g.
9 members x 2 processes::

    mpiexec -n 18 python main_pdaf.py -dim_ens 9 -filtertype 7
"""
import mod_parallel_model as pm
from finalize_pdaf import finalize_pdaf
from initialize import initialize
from integrate_pdaf import integrate_pdaf


def main() -> None:
    # *** Initialize MPI for the model and the communicators for PDAF ***
    pm.init_parallel(use_pdaf=True)

    if pm.mype_world == 0:
        print('\n' + ' ' * 17 + '+++++ PDAF tutorial - online mode +++++\n')
        print(' ' * 17 + 'Tutorial: 2D model with parallelization')
        print('\n')

    initialize()
    integrate_pdaf()
    finalize_pdaf()
    pm.finalize_parallel()


if __name__ == '__main__':
    main()
