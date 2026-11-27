"""Initialise communicators for PDAF (translation of online_2D_parallelmodel_fullpar/init_parallel_pdaf.F90).

PDAF3_init_parallel with ``type_parallel = 1`` creates ``n_modeltasks + 1``
groups of processes: the first group computes only the analysis (filter
processes), the others are the model tasks. On the filter processes the
returned model communicator is MPI_COMM_NULL.
"""
from mpi4py import MPI
import pyPDAF.PDAF3

import mod_parallel_model as pm
import mod_parallel_pdaf as par
from init_pdaf_parse import pdaf_parse


class _Opt:
    """Small container so that pdaf_parse can be used for a local variable."""
    dim_ens: int = 9   # default if -dim_ens is not given on the command line


def init_parallel_pdaf(screen: int) -> None:
    """Split the processes into filter processes and model tasks."""
    pdaf_parse(_Opt, 'dim_ens')
    dim_ens = _Opt.dim_ens
    par.n_modeltasks = dim_ens

    # Arguments: screen=1, type_parallel=1 (separate filter processes),
    # online_coupling=1, dim_ens, n_modeltasks, communicator of all processes
    (par.n_modeltasks, comm_model, mype_model, npes_model,
     par.COMM_filter, par.mype_filter, par.npes_filter,
     par.task_id) = pyPDAF.PDAF3.init_parallel(1, 1, 1, dim_ens, par.n_modeltasks,
                                                pm.COMM_2Dmodel.py2f())

    # Model processes get a valid model communicator, filter processes MPI_COMM_NULL
    pm.modelproc = comm_model != MPI.COMM_NULL.py2f()
    pm.COMM_2Dmodel = MPI.Comm.f2py(comm_model)
    if pm.modelproc:
        # On filter processes, PDAF does not set rank and size of the model
        # communicator; as in Fortran, the old values (world rank/size) are kept
        pm.mype_2Dmodel = mype_model
        pm.npes_2Dmodel = npes_model

    # Variables used by the PDAF call-back routines
    par.mype_world = pm.mype_world
    par.npes_world = pm.npes_world
    par.COMM_model = comm_model
