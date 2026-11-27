"""Set up the communicators in the user code (translation of
online_2D_parallelmodel_fullpar_1fpe/init_parallel_pdaf.F90).

Instead of PDAF3_init_parallel, the communicators are created here with MPI
and passed to PDAF with PDAF3_set_parallel. The configuration:

* task 1 (one process) computes only the analysis (filter process),
* the other processes are split into ``n_modeltasks`` model tasks,
* COMM_couple connects the filter process with process 0 of each model task.
"""
from mpi4py import MPI
import numpy as np
import pyPDAF.PDAF3

import mod_parallel_model as pm
import mod_parallel_pdaf as par
from init_pdaf_parse import pdaf_parse


class _Opt:
    """Small container so that pdaf_parse can be used for a local variable."""
    dim_ens: int = 9   # default if -dim_ens is not given on the command line


def init_parallel_pdaf(dim_ens: int, screen: int) -> None:
    """Create the communicators and pass them to PDAF."""
    world = MPI.COMM_WORLD
    pm.npes_world = world.Get_size()
    pm.mype_world = world.Get_rank()

    # Number of model tasks = ensemble size (command line -dim_ens)
    pdaf_parse(_Opt, 'dim_ens')
    n_modeltasks = _Opt.dim_ens

    if pm.mype_world == 0:
        print('\n Initialize communicators for assimilation with PDAF')

    # *** Consistency checks ***
    if n_modeltasks > pm.npes_world:
        n_modeltasks = pm.npes_world
        if pm.mype_world == 0:
            print('   !!! Resetting number of parallel ensemble tasks to total number of PEs!')
    if dim_ens > 0 and n_modeltasks > dim_ens:
        n_modeltasks = dim_ens
        if pm.mype_world == 0:
            print('     !!! Resetting number of parallel ensemble tasks to number of ensemble states!')

    # *** Number of processes per task: 1 for the filter, the rest for the models ***
    comm_ensemble = world
    mype_ens, npes_ens = pm.mype_world, pm.npes_world
    local_npes_model = np.full(n_modeltasks + 1, (pm.npes_world - 1) // n_modeltasks)
    local_npes_model[0] = 1
    nrest = pm.npes_world - n_modeltasks * local_npes_model[1] - 1
    local_npes_model[1:1 + nrest] += 1

    # Task of this process (1-based; task 1 = filter)
    task_id = int(np.searchsorted(np.cumsum(local_npes_model), mype_ens, side='right')) + 1

    # *** COMM_model: one communicator per model task (none for the filter) ***
    t_id = MPI.UNDEFINED if task_id == 1 else task_id
    comm_model = comm_ensemble.Split(t_id, mype_ens)

    filterpe = task_id == 1
    pm.modelpe = not filterpe
    task_id = task_id - 1       # model tasks are numbered 1, ..., n_modeltasks

    if pm.modelpe:
        pm.npes_2Dmodel = comm_model.Get_size()
        pm.mype_2Dmodel = comm_model.Get_rank()
        pm.COMM_2Dmodel = comm_model
        if screen > 1:
            print(f' MODEL: mype(w)= {pm.mype_world}; model task: {task_id}; '
                  f'mype(m)= {pm.mype_2Dmodel}; npes(m)= {pm.npes_2Dmodel}')
    else:
        pm.COMM_2Dmodel = comm_model            # MPI.COMM_NULL

    # *** COMM_filter: the filter process(es) ***
    my_color = task_id if filterpe else MPI.UNDEFINED
    comm_filter = world.Split(my_color, pm.mype_world)
    if filterpe:
        par.npes_filter = comm_filter.Get_size()
        par.mype_filter = comm_filter.Get_rank()
        if screen > 1:
            print(f' FILTER: mype(w)= {pm.mype_world}; mype(f)= {par.mype_filter}; '
                  f'npes(f)= {par.npes_filter}')
    else:
        par.mype_filter = -1                     # not a filter process

    # *** COMM_couple: filter process and process 0 of each model task ***
    if pm.modelpe and pm.mype_2Dmodel == 0:
        color_couple = pm.mype_2Dmodel + 1
    elif pm.modelpe:
        color_couple = MPI.UNDEFINED
    else:
        color_couple = par.mype_filter + 1
    comm_couple = world.Split(color_couple, pm.mype_world)
    mype_couple = comm_couple.Get_rank() if comm_couple != MPI.COMM_NULL else None

    # *** Print configuration ***
    if screen > 0:
        if pm.mype_world == 0:
            print('\n' + ' ' * 18 + 'PE configuration:')
            print('   world   filter     model        couple     model/filter')
            print('   rank     rank   task   rank   task   rank     M/F')
            print('  ' + '-' * 58)
        world.Barrier()
        if filterpe:
            print(f'  {pm.mype_world:4d}    {par.mype_filter:4d}'
                  + (f'{" " * 22}{color_couple:3d}    {mype_couple:3d}' if mype_couple is not None else ' ' * 32)
                  + '        F', flush=True)
        if pm.modelpe:
            print(f'  {pm.mype_world:4d}{" " * 12}{task_id:3d}    {pm.mype_2Dmodel:3d}'
                  + (f'    {color_couple:3d}    {mype_couple:3d}' if mype_couple is not None else ' ' * 14)
                  + '        M', flush=True)
        world.Barrier()
        if pm.mype_world == 0:
            print('')

    # *** Store variables for PDAF and the call-back routines ***
    par.n_modeltasks = n_modeltasks
    par.task_id = task_id
    par.COMM_model = comm_model.py2f()
    par.COMM_filter = comm_filter.py2f()
    par.COMM_couple = comm_couple.py2f()
    par.filterpe = filterpe
    par.mype_world = pm.mype_world
    par.npes_world = pm.npes_world

    # *** Provide the communicators to PDAF ***
    flag = pyPDAF.PDAF3.set_parallel(comm_ensemble.py2f(), par.COMM_model,
                                     par.COMM_filter, par.COMM_couple,
                                     task_id, n_modeltasks, filterpe, 0)
