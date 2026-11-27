"""Parallel model without data assimilation (translation of main.F90).

Usage: ``mpiexec -n 4 python main.py``
"""
import mod_parallel_model as pm
from initialize import initialize
from integrate import integrate


def main() -> None:
    pm.init_parallel()
    if pm.mype_world == 0:
        print('\n' + ' ' * 17 + '+++++ PDAF tutorial - online mode +++++\n')
        print(' ' * 17 + 'Tutorial: 2D model with parallelization')
        print('\n')
    initialize(use_pdaf=False)
    integrate()
    pm.finalize_parallel()


if __name__ == '__main__':
    main()
