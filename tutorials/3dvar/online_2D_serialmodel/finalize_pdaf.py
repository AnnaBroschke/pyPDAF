"""Finalise PDAF (translation of finalize_pdaf.F90).

Print timing and memory information and finalise PDAF. PDAF_finalize also
finalises MPI if it was initialised by PDAF.
"""
import pyPDAF.PDAF

import mod_parallel_pdaf as par


def finalize_pdaf() -> None:
    """Print PDAF information and finalise."""
    if par.mype_world == 0:
        pyPDAF.PDAF.print_info(10)   # timing information
        pyPDAF.PDAF.print_info(3)    # memory information
    pyPDAF.PDAF.finalize()
