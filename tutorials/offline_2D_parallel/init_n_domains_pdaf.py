"""Number of local analysis domains (translation of init_n_domains_pdaf.F90).

Call-back routine for the local filters (LESTKF, LETKF, LSEIK, ...).
Here each grid point is one local analysis domain.
"""
import mod_assimilation as assim


def init_n_domains_pdaf(step: int, n_domains_p: int) -> int:
    """Return the number of local analysis domains."""
    return assim.dim_state_p
