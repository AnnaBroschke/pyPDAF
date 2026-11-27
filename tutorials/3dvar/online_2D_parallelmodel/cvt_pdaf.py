"""Control variable transformation (translation of 3dvar/online_2D_parallelmodel/cvt_pdaf.F90).

``Vv_p = Vmat_p v`` for the process-local rows of Vmat_p. For the
parallelized optimizers (type_opt 12, 13) the control vector is distributed
over the filter processes; the full vector is first gathered with
MPI_Allgatherv.
"""
from mpi4py import MPI
import numpy as np

import mod_assimilation as assim
import mod_parallel_pdaf as par


def cvt_pdaf(iter: int, dim_p: int, dim_cvec_p: int,
             v_p: np.ndarray, vv_p: np.ndarray) -> np.ndarray:
    """Return Vmat_p @ v (v gathered over the processes for type_opt 12, 13)."""
    if assim.type_opt in (12, 13):
        comm = MPI.Comm.f2py(par.COMM_filter)
        v_g = np.empty(assim.dim_cvec)
        comm.Allgatherv(np.ascontiguousarray(v_p[:dim_cvec_p]),
                        [v_g, assim.dims_cv_p, assim.off_cv_p, MPI.DOUBLE])
        vv_p[:] = assim.Vmat_p @ v_g
    else:
        vv_p[:] = assim.Vmat_p @ v_p
    return vv_p
