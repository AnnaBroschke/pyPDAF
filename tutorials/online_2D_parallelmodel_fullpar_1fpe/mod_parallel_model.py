"""Parallelisation of the model (translation of online_2D_parallelmodel_fullpar_1fpe/mod_parallel_model.F90).

Here, init_parallel only initialises MPI. The communicators for model tasks
and filter are set up afterwards by ``init_parallel_pdaf`` in the user code.
(Fortran names these variables COMM_model, mype_model, npes_model; the Python
tutorials use COMM_2Dmodel, ... in all variants.)
"""
from mpi4py import MPI

COMM_2Dmodel: MPI.Comm = MPI.COMM_WORLD   # Communicator of the (parallel) model
npes_2Dmodel: int = 1                     # Number of processes in COMM_2Dmodel
mype_2Dmodel: int = 0                     # Rank in COMM_2Dmodel
npes_world: int = 1                       # Number of processes in MPI_COMM_WORLD
mype_world: int = 0                       # Rank in MPI_COMM_WORLD
modelpe: bool = True                      # Whether this process runs the model


def init_parallel() -> None:
    """Initialise MPI."""
    global COMM_2Dmodel, npes_2Dmodel, mype_2Dmodel, npes_world, mype_world

    if not MPI.Is_initialized():
        MPI.Init()
    npes_world = MPI.COMM_WORLD.Get_size()
    mype_world = MPI.COMM_WORLD.Get_rank()

    COMM_2Dmodel = MPI.COMM_WORLD
    npes_2Dmodel = npes_world
    mype_2Dmodel = mype_world


def finalize_parallel() -> None:
    """Finalise MPI."""
    MPI.COMM_WORLD.Barrier()
    MPI.Finalize()


def abort_parallel() -> None:
    """Abort all processes."""
    MPI.COMM_WORLD.Abort(1)
