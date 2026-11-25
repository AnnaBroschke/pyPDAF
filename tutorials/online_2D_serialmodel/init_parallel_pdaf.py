"""Initialise MPI communicators for PDAF (translation of init_parallel_pdaf.F90).

Online mode: the processes are split into ``n_modeltasks`` model tasks.
This tutorial runs one model task per ensemble member, so
``n_modeltasks = dim_ens``. If fewer processes than ensemble members are
available, PDAF reduces n_modeltasks to the number of processes.

Difference to Fortran: importing pyPDAF already initialises MPI (through
mpi4py). PDAF3_init_parallel then does not set COMM_model itself, so we
pass MPI_COMM_WORLD explicitly as Fortran handle (``py2f()``).
"""
from mpi4py import MPI
import pyPDAF.PDAF3

import mod_parallel_pdaf as par
from init_pdaf_parse import pdaf_parse


class _Opt:
    """Small container so that pdaf_parse can be used for a local variable."""
    dim_ens: int = 9   # default if -dim_ens is not given on the command line


def init_parallel_pdaf(screen: int) -> None:
    """Initialise communicators for the online mode."""
    # Ensemble size from command line: number of model tasks
    pdaf_parse(_Opt, 'dim_ens')
    dim_ens = _Opt.dim_ens
    par.n_modeltasks = dim_ens

    # Arguments: screen, type_parallel, online_coupling (1=online), dim_ens,
    # n_modeltasks, COMM_model (input: communicator containing all processes)
    (par.n_modeltasks, par.COMM_model, par.mype_model, par.npes_model,
     par.COMM_filter, par.mype_filter, par.npes_filter,
     par.task_id) = pyPDAF.PDAF3.init_parallel(screen, 0, 1, dim_ens,
                                                par.n_modeltasks,
                                                MPI.COMM_WORLD.py2f())

    par.npes_world = MPI.COMM_WORLD.Get_size()
    par.mype_world = MPI.COMM_WORLD.Get_rank()
