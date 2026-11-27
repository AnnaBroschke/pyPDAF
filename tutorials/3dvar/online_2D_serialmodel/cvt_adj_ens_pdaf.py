"""Adjoint ensemble control variable transformation (translation of cvt_adj_ens_pdaf.F90).

Call-back routine for 3D-EnVar and hybrid 3D-Var:
``v_p = Vmat_ens_p^T Vv_p`` (Vmat_ens_p was set up in cvt_ens_pdaf).
"""
import numpy as np

import mod_assimilation as assim


def cvt_adj_ens_pdaf(iter: int, dim_p: int, dim_ens: int, dim_cvec_ens: int,
                     ens_p: np.ndarray, vv_p: np.ndarray, v_p: np.ndarray) -> np.ndarray:
    """Return Vmat_ens_p.T @ vv_p."""
    v_p[:] = assim.Vmat_ens_p.T @ vv_p
    return v_p
