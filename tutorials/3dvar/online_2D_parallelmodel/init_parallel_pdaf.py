"""Initialise communicators for PDAF (translation of online_2D_parallelmodel/init_parallel_pdaf.F90).

The model communicator (here MPI_COMM_WORLD) is split into ``n_modeltasks =
dim_ens`` model tasks. Each task runs the parallel model on its own
communicator, which is returned to the model.
"""
import pyPDAF.PDAF3

import mod_parallel_pdaf as par
from init_pdaf_parse import pdaf_parse


class _Opt:
    """Small container so that pdaf_parse can be used for a local variable."""
    dim_ens: int = 9   # default if -dim_ens is not given on the command line


def init_parallel_pdaf(screen: int, model_comm: int, model_comm_rank: int,
                       model_comm_size: int) -> tuple[int, int, int]:
    """Split the model processes into model tasks.

    Parameters
    ----------
    model_comm : int
        Fortran handle of the communicator containing all model processes
    model_comm_rank, model_comm_size : int
        Rank and size in model_comm

    Returns
    -------
    model_comm, model_comm_rank, model_comm_size
        Communicator of the own model task, rank and size in it
        (INTENT(inout) in Fortran).
    """
    pdaf_parse(_Opt, 'dim_ens')
    dim_ens = _Opt.dim_ens
    par.n_modeltasks = dim_ens

    # Rank and size in the original model communicator
    par.mype_world = model_comm_rank
    par.npes_world = model_comm_size

    (par.n_modeltasks, model_comm, model_comm_rank, model_comm_size,
     par.COMM_filter, par.mype_filter, par.npes_filter,
     par.task_id) = pyPDAF.PDAF3.init_parallel(screen, 0, 1, dim_ens,
                                                par.n_modeltasks, model_comm)

    par.COMM_model = model_comm
    par.mype_model = model_comm_rank
    par.npes_model = model_comm_size

    return model_comm, model_comm_rank, model_comm_size
