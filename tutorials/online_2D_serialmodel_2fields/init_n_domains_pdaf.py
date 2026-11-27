"""Number of local analysis domains (translation of init_n_domains_pdaf.F90).

Each grid point is one local analysis domain. With two fields this is
nx*ny (not the state dimension, which is 2*nx*ny).
"""
import mod_model as model


def init_n_domains_pdaf(step: int, n_domains_p: int) -> int:
    """Return the number of local analysis domains."""
    return model.nx * model.ny
