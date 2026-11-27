"""Ensemble control variable transformation (translation of 3dvar/online_2D_parallelmodel/cvt_ens_pdaf.F90).

In the first iteration the process-local rows of the ensemble square root
``Vmat_ens_p`` are computed from the ensemble perturbations. Then
``Vv_p = Vmat_ens_p v``; for type_opt 12, 13 the control vector is first
gathered over the filter processes.
"""
from mpi4py import MPI
import numpy as np

import mod_assimilation as assim
import mod_parallel_pdaf as par


def cvt_ens_pdaf(iter: int, dim_p: int, dim_ens: int, dim_cvec_ens_p: int,
                 ens_p: np.ndarray, v_p: np.ndarray, vv_p: np.ndarray) -> np.ndarray:
    """Return Vmat_ens_p @ v (Vmat_ens_p is set up at iter == 1)."""
    if iter == 1:
        # Uses the global size dim_cvec_ens (module variable), as in Fortran
        fact = 1.0 / np.sqrt(assim.dim_cvec_ens - 1)
        assim.Vmat_ens_p = np.zeros((dim_p, assim.dim_cvec_ens), order='F')
        vv_p[:] = 0.0
        invdimens = 1.0 / dim_ens
        for member in range(dim_ens):             # same summation order as Fortran
            vv_p[:] += invdimens * ens_p[:, member]
        for member in range(dim_ens):
            assim.Vmat_ens_p[:, member] = fact * (ens_p[:, member] - vv_p)
        for i in range(2, assim.mcols_cvec_ens + 1):
            for member in range((i - 1) * dim_ens, i * dim_ens):
                assim.Vmat_ens_p[:, member] = assim.Vmat_ens_p[:, member - (i - 1) * dim_ens]

    if assim.type_opt in (12, 13):
        comm = MPI.Comm.f2py(par.COMM_filter)
        cv_g = np.empty(assim.dim_cvec_ens)
        comm.Allgatherv(np.ascontiguousarray(v_p[:dim_cvec_ens_p]),
                        [cv_g, assim.dims_cv_ens_p, assim.off_cv_ens_p, MPI.DOUBLE])
        vv_p[:] = assim.Vmat_ens_p @ cv_g
    else:
        vv_p[:] = assim.Vmat_ens_p @ v_p
    return vv_p
