"""Finalise PDAF (translation of online_2D_parallelmodel/finalize_pdaf.F90).

Timing information is printed by all processes (print_info(11)).
MPI is finalised afterwards by the model (finalize_parallel).
"""
import pyPDAF.PDAF

import mod_parallel_pdaf as par


def finalize_pdaf() -> None:
    """Print PDAF information and finalise PDAF."""
    pyPDAF.PDAF.print_info(11)
    if par.mype_world == 0:
        pyPDAF.PDAF.print_info(3)
    pyPDAF.PDAF.finalize()
