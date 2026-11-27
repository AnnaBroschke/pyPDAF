"""Adjoint control variable transformation (translation of cvt_adj_pdaf.F90).

Call-back routine for parameterized and hybrid 3D-Var:
``v_p = Vmat_p^T Vv_p`` (Fortran: DGEMV 't').
"""
import numpy as np

import mod_assimilation as assim


def cvt_adj_pdaf(iter: int, dim_p: int, dim_cvec: int,
                 vv_p: np.ndarray, v_p: np.ndarray) -> np.ndarray:
    """Return Vmat_p.T @ vv_p."""
    v_p[:] = assim.Vmat_p.T @ vv_p
    return v_p
