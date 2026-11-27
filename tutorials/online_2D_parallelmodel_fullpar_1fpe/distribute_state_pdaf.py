"""Initialise the model fields from the state vector
(translation of online_2D_parallelmodel_fullpar_1fpe/distribute_state_pdaf.F90).

Process 0 of each model task receives the full state vector from PDAF and
sends the column blocks to the other processes of its model task.
"""
import numpy as np

import mod_model as model
import mod_parallel_model as pm


def distribute_state_pdaf(dim_p: int, state_p: np.ndarray) -> np.ndarray:
    """Scatter the full state vector from process 0 to the model task."""
    nloc = model.nx_p * model.ny
    shape = (model.ny, model.nx_p)
    if pm.mype_2Dmodel == 0:
        model.field_p[:, :] = state_p[:nloc].reshape(shape, order='F')
        offset = nloc
        for rank in range(1, pm.npes_2Dmodel):
            pm.COMM_2Dmodel.Send(np.ascontiguousarray(state_p[offset:offset + nloc]),
                                 dest=rank, tag=rank)
            offset += nloc
    else:
        state_part = np.empty(nloc)
        pm.COMM_2Dmodel.Recv(state_part, source=0, tag=pm.mype_2Dmodel)
        model.field_p[:, :] = state_part.reshape(shape, order='F')
    return state_p
