"""Main program of the offline_2D_serial tutorial (translation of 3dvar/offline_2D_serial/main_offline.F90).

3D-Var variants (filtertype 200) selected by ``-subtype``:

* 0: parameterized 3D-Var        python main_offline.py -dim_ens 1 -dim_cvec 9 -subtype 0
* 1: 3D-EnVar with LESTKF        python main_offline.py -dim_ens 9 -subtype 1 -type_opt 2
* 2: 3D-EnVar with ESTKF         python main_offline.py -dim_ens 9 -subtype 2 -type_opt 2
* 3: hybrid 3D-Var with LESTKF   python main_offline.py -dim_ens 9 -subtype 3 -type_opt 2 -dim_cvec 9
* 4: hybrid 3D-Var with ESTKF    python main_offline.py -dim_ens 9 -subtype 4 -type_opt 2 -dim_cvec 9

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
            print('\n' + ' ' * 21 + f'Running on {par.npes_world:3d} PEs\n')
        else:
            print('\n' + ' ' * 21 + 'Running on 1 PE\n')
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
