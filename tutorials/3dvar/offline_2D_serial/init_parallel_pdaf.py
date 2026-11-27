"""Initialise MPI communicators for PDAF (translation of init_parallel_pdaf.F90).

PDAF3_init_parallel initialises MPI (if not yet done) and splits the
processes into model tasks and filter processes. For the offline mode
there is always exactly one model task.

Difference to Fortran: importing pyPDAF already initialises MPI (through
mpi4py). PDAF3_init_parallel then does not set COMM_model itself, so we
pass MPI_COMM_WORLD explicitly as Fortran handle (``py2f()``).
"""
from mpi4py import MPI
import pyPDAF.PDAF3

import mod_parallel_pdaf as par


def init_parallel_pdaf(screen: int) -> None:
    """Initialise communicators.

    Parameters
    ----------
    screen : int
        Verbosity of output (0: none, 1: some)
    """
    par.n_modeltasks = 1

    # Arguments: screen, type_parallel, online_coupling (0=offline), dim_ens,
    # n_modeltasks, COMM_model (input: communicator containing all processes)
    (par.n_modeltasks, par.COMM_model, par.mype_model, par.npes_model,
     par.COMM_filter, par.mype_filter, par.npes_filter,
     par.task_id) = pyPDAF.PDAF3.init_parallel(screen, 0, 0, 0,
                                                par.n_modeltasks,
                                                MPI.COMM_WORLD.py2f())

    par.mype_world = par.mype_model
    par.npes_world = par.npes_model
