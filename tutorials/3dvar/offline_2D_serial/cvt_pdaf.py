"""Control variable transformation (translation of cvt_pdaf.F90).

Call-back routine for parameterized and hybrid 3D-Var. Computes the state
increment from the control vector: ``Vv_p = Vmat_p v_p`` (Fortran: DGEMV 'n').
"""
import numpy as np

import mod_assimilation as assim


def cvt_pdaf(iter: int, dim_p: int, dim_cvec: int,
             v_p: np.ndarray, vv_p: np.ndarray) -> np.ndarray:
    """Return Vmat_p @ v_p."""
    vv_p[:] = assim.Vmat_p @ v_p
    return vv_p
