"""Initialise the state vector from the model fields
(translation of online_2D_parallelmodel_fullpar_1fpe/collect_state_pdaf.F90).

With a single filter process, PDAF exchanges the full state vector with
process 0 of each model task. Process 0 therefore collects the column
blocks of all processes of its model task.
"""
import numpy as np

import mod_model as model
import mod_parallel_model as pm


def collect_state_pdaf(dim_p: int, state_p: np.ndarray) -> np.ndarray:
    """Gather the full state vector on process 0 of the model task."""
    nloc = model.nx_p * model.ny
    if pm.mype_2Dmodel == 0:
        state_p[:nloc] = model.field_p.ravel(order='F')
        offset = nloc
        for rank in range(1, pm.npes_2Dmodel):
            pm.COMM_2Dmodel.Recv(state_p[offset:offset + nloc], source=rank, tag=rank)
            offset += nloc
    else:
        state_part = np.ascontiguousarray(model.field_p.ravel(order='F'))
        pm.COMM_2Dmodel.Send(state_part, dest=0, tag=pm.mype_2Dmodel)
    return state_p
