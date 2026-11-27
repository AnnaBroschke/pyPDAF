"""Main program of the offline_2D_serial tutorial (translation of offline_2D_parallel/main_offline.F90).

The model state is distributed over the processes (domain decomposition).
Run from this directory, e.g.::

    mpiexec -n 4 python main_offline.py -filtertype 7
    mpiexec -n 4 python main_offline.py -filtertype 6 -assim_B .true.

The analysis ensemble is written to ``ens_XX_ana.txt`` and the analysis
state to ``state_ana.txt``.
"""
from mpi4py import MPI

import mod_parallel_pdaf as par
from assimilate_pdaf_offline import assimilate_pdaf_offline
from finalize_pdaf import finalize_pdaf
from init_parallel_pdaf import init_parallel_pdaf
from init_pdaf_offline import init_pdaf
from initialize import initialize


def main() -> None:
    """Offline data assimilation with PDAF."""
    # *** Initialize MPI and communicators ***
    init_parallel_pdaf(0)

    if par.mype_world == 0:
        print('\n' + ' ' * 8 + '+++++ PDAF offline mode +++++')
        print(' ' * 9 + 'Data assimilation with PDAF')
        if par.npes_world > 1:
            print('\n' + ' ' * 21 + f'Running on {par.npes_world:3d} processes\n')
        else:
            print('\n' + ' ' * 21 + 'Running on 1 process\n')
        print('\n')

    # *** Initialize model information ***
    initialize()

    # *** Initialize PDAF (reads the ensemble) ***
    init_pdaf()

    # *** Perform analysis ***
    if par.mype_world == 0:
        print('\n  PDAF offline mode: START ASSIMILATION')

    assimilate_pdaf_offline()

    # Synchronize at barrier for exit
    MPI.COMM_WORLD.Barrier()
    print(f' model PE exited: mype {par.mype_world:4d}', flush=True)

    if par.mype_world == 0:
        print('\n PDAF offline mode: EXITED ASSIMILATION')

    # *** Finalize PDAF (and MPI) ***
    finalize_pdaf()


if __name__ == '__main__':
    main()
