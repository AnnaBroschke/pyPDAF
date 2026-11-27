"""Parallel model with data assimilation and a single filter process
(translation of online_2D_parallelmodel_fullpar_1fpe/main_pdaf.F90).

The communicators are set up in the user code (init_parallel_pdaf).
Example: 19 processes = 1 filter process + 9 tasks x 2::

    mpiexec -n 19 python main_pdaf.py -dim_ens 9 -filtertype 7
"""
import mod_parallel_model as pm
from filtering import filtering
from finalize_pdaf import finalize_pdaf
from init_parallel_pdaf import init_parallel_pdaf
from init_pdaf import init_pdaf
from initialize import initialize
from integrate_pdaf import integrate_pdaf


def main() -> None:
    # *** Initialize MPI for the model and the communicators for PDAF ***
    pm.init_parallel()
    init_parallel_pdaf(0, 1)

    if pm.mype_world == 0:
        print('\n' + ' ' * 17 + '+++++ PDAF tutorial - online mode +++++\n')
        print(' ' * 17 + 'Tutorial: 2D model with parallelization')
        print('\n')

    if pm.modelpe:
        # Model processes: model with PDAF calls
        initialize()
        init_pdaf()
        integrate_pdaf()
    else:
        # Filter processes: only analysis
        filtering()
    finalize_pdaf()
    pm.finalize_parallel()


if __name__ == '__main__':
    main()
