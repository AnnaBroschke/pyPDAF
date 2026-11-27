"""Adjoint control variable transformation (translation of 3dvar/online_2D_parallelmodel/cvt_adj_pdaf.F90).

``v = Vmat_p^T Vv_p``. Since the rows of Vmat_p are distributed over the
filter processes, the partial products are summed with MPI_Allreduce. For
type_opt 12, 13 each process keeps only its part of the control vector.
"""
from mpi4py import MPI
import numpy as np

import mod_assimilation as assim
import mod_parallel_pdaf as par


def cvt_adj_pdaf(iter: int, dim_p: int, dim_cvec_p: int,
                 vv_p: np.ndarray, v_p: np.ndarray) -> np.ndarray:
    """Return the (process-local part of) Vmat_p.T @ Vv summed over the processes."""
    comm = MPI.Comm.f2py(par.COMM_filter)
    v_g_part = assim.Vmat_p.T @ vv_p
    v_g = np.empty(assim.dim_cvec)
    comm.Allreduce(v_g_part, v_g, op=MPI.SUM)
    if assim.type_opt in (12, 13):
        off = assim.off_cv_p[par.mype_filter]
        v_p[:dim_cvec_p] = v_g[off:off + dim_cvec_p]
    else:
        v_p[:] = v_g
    return v_p
