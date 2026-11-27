"""Setup of the state vector with several fields (translation of mod_statevector_pdaf.F90).

The state vector contains two model fields A and B, stored one after the
other::

    state_p = [ field A (nx*ny values) | field B (nx*ny values) ]

For each field we store its dimension ``dim`` and its offset ``off`` in the
state vector. Field ``i`` occupies the (0-based) slice ``off : off + dim``.
Adding a further field only requires changes in this file (and in
collect/distribute_state and init_ens).
"""
from dataclasses import dataclass

from mpi4py import MPI

import mod_model as model
import mod_parallel_pdaf as par


@dataclass
class StateField:
    """Information on one field in the state vector (Fortran TYPE state_field)."""
    name: str
    dim: int = 0
    off: int = 0

    @property
    def slice(self) -> slice:
        """0-based slice of this field in the state vector."""
        return slice(self.off, self.off + self.dim)


class _FieldIds:
    """Indices of the fields (Fortran TYPE field_ids). 0-based in Python."""
    fieldA: int = 0
    fieldB: int = 1


id = _FieldIds()                  # noqa: A001  (same name as in Fortran)
n_fields: int = 0                 # Number of fields in state vector
sfields: list[StateField] = []    # Information on each field


def init_id() -> int:
    """Set the number of fields and their ids."""
    id.fieldA = 0
    id.fieldB = 1
    return 2


def init_sfields() -> None:
    """Set names, dimensions and offsets of the fields."""
    # Fill the list in place, so that 'from mod_statevector_pdaf import sfields'
    # in other modules refers to the same (filled) list
    sfields.clear()
    sfields.extend(StateField('') for _ in range(n_fields))
    sfields[id.fieldA] = StateField('A', model.nx * model.ny)
    sfields[id.fieldB] = StateField('B', model.nx * model.ny)

    # Offsets: fields are stored one after the other
    sfields[0].off = 0
    for i in range(1, n_fields):
        sfields[i].off = sfields[i - 1].off + sfields[i - 1].dim


def setup_statevector(screen: int) -> tuple[int, int]:
    """Set up the state vector. Returns (dim_state, dim_state_p)."""
    global n_fields
    n_fields = init_id()
    init_sfields()

    dim_state_p = sum(f.dim for f in sfields)

    # Global state dimension (sum over the processes of one model task)
    comm_model = MPI.Comm.f2py(par.COMM_model)
    dim_state = comm_model.reduce(dim_state_p, op=MPI.SUM, root=0)

    if par.task_id == 1:
        if par.mype_model == 0:
            print('\nmodel-PDAF  *** Setup of state vector ***')
            print(f'model-PDAF   --- Number of fields in state vector:{n_fields:5d}')
            print('model-PDAF  proc.   ID    variable     dimension      offset')
        if (par.mype_model == 0 and screen <= 2) or screen > 2:
            for i, f in enumerate(sfields):
                print(f'model-PDAF{par.mype_model:6d}  {i + 1:4d}    {f.name:>10s}  '
                      f'{f.dim:10d}  {f.off:10d}')
        if par.npes_model > 1 and (screen > 2 or par.mype_model == 0):
            print(f'model-PDAF  PE {par.mype_model:4d}  process-local full state '
                  f'dimension:  {dim_state_p:10d}')
        if par.mype_model == 0:
            print(f'model-PDAF  Global state dimension:  {dim_state:10d}')

    MPI.COMM_WORLD.Barrier()
    return dim_state, dim_state_p
