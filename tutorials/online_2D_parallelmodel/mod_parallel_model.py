"""Parallelisation of the model (translation of mod_parallel_model.F90).

The tutorial model is parallelised by domain decomposition. Without PDAF the
model runs on MPI_COMM_WORLD. With PDAF, ``init_parallel_pdaf`` splits the
processes into ``n_modeltasks`` model tasks and returns the communicator of
the own task; the model then runs on this communicator (COMM_2Dmodel).
"""
from mpi4py import MPI

COMM_2Dmodel: MPI.Comm = MPI.COMM_WORLD   # Communicator of the (parallel) model
npes_2Dmodel: int = 1                     # Number of processes in COMM_2Dmodel
mype_2Dmodel: int = 0                     # Rank in COMM_2Dmodel
npes_world: int = 1                       # Number of processes in MPI_COMM_WORLD
mype_world: int = 0                       # Rank in MPI_COMM_WORLD


def init_parallel(use_pdaf: bool = True) -> None:
    """Initialise MPI for the model (and the PDAF communicators if use_pdaf)."""
    global COMM_2Dmodel, npes_2Dmodel, mype_2Dmodel, npes_world, mype_world

    # MPI_Init: done by mpi4py (with PDAF already when pyPDAF is imported)
    if not MPI.Is_initialized():
        MPI.Init()
    npes_world = MPI.COMM_WORLD.Get_size()
    mype_world = MPI.COMM_WORLD.Get_rank()

    COMM_2Dmodel = MPI.COMM_WORLD
    npes_2Dmodel = npes_world
    mype_2Dmodel = mype_world

    if use_pdaf:
        from init_parallel_pdaf import init_parallel_pdaf
        # Fortran: COMM_2Dmodel etc. are INTENT(inout) and replaced by the
        # communicator of the own model task
        comm_f, mype_2Dmodel, npes_2Dmodel = init_parallel_pdaf(
            1, COMM_2Dmodel.py2f(), mype_2Dmodel, npes_2Dmodel)
        COMM_2Dmodel = MPI.Comm.f2py(comm_f)


def finalize_parallel() -> None:
    """Finalise MPI."""
    MPI.COMM_WORLD.Barrier()
    MPI.Finalize()


def abort_parallel() -> None:
    """Abort all processes."""
    MPI.COMM_WORLD.Abort(1)
