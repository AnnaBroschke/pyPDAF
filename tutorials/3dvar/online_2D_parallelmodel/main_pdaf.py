"""3D-Var with a parallelized model (translation of 3dvar/online_2D_parallelmodel/main_pdaf.F90).

Examples (type_opt 12, 13: optimizers parallelized over the model processes)::

    mpiexec -n 2 python main_pdaf.py -dim_ens 1 -dim_cvec 9 -filtertype 200 -subtype 0 -type_opt 12
    mpiexec -n 18 python main_pdaf.py -dim_ens 9 -filtertype 200 -subtype 1 -type_opt 12
    mpiexec -n 18 python main_pdaf.py -dim_ens 9 -filtertype 200 -subtype 4 -type_opt 13 -dim_cvec 9
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
