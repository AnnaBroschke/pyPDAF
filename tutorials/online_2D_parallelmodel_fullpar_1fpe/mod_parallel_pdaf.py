"""Parallelisation variables (translation of mod_parallel_pdaf.F90).

In Fortran these are module variables with SAVE. In Python, module-level
variables play the same role: every file that does
``import mod_parallel_pdaf as par`` sees and modifies the same values.
Communicators are stored as Fortran integer handles, because pyPDAF passes
them directly to the Fortran library.
"""
COMM_model: int = 0     # MPI communicator for model tasks
mype_model: int = 0     # Rank in COMM_model
npes_model: int = 1     # Number of processes in COMM_model
mype_world: int = 0     # Rank in MPI_COMM_WORLD
npes_world: int = 1     # Number of processes in MPI_COMM_WORLD
COMM_filter: int = 0    # MPI communicator for filter processes
mype_filter: int = 0    # Rank in COMM_filter
npes_filter: int = 1    # Number of processes in COMM_filter
n_modeltasks: int = 1   # Number of parallel model tasks
task_id: int = 1        # Index of my model task (1, ..., n_modeltasks)
COMM_couple: int = 0    # Communicator for coupling filter and model tasks
filterpe: bool = False  # Whether this process is a filter process
