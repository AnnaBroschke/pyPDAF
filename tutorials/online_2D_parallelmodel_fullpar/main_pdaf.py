"""Parallel model with data assimilation and separate filter processes
(translation of online_2D_parallelmodel_fullpar/main_pdaf.F90).

The processes are split into one filter task and ``dim_ens`` model tasks of
equal size. Example: 20 processes = 2 filter processes + 9 tasks x 2::

    mpiexec -n 20 python main_pdaf.py -dim_ens 9 -filtertype 7
"""
import mod_parallel_model as pm
from filtering import filtering
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

    if pm.modelproc:
        # Model processes: model with PDAF calls
        initialize()
        integrate_pdaf()
    else:
        # Filter processes: only analysis
        filtering()
    finalize_pdaf()
    pm.finalize_parallel()


if __name__ == '__main__':
    main()
