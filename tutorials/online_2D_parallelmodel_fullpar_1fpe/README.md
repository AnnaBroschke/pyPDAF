# online_2D_parallelmodel_fullpar_1fpe (pyPDAF)

Python translation of `PDAF/tutorial/online_2D_parallelmodel_fullpar_1fpe`:
like `../online_2D_parallelmodel_fullpar`, but with **one** filter process and
with the communicators set up **in the user code** instead of by PDAF.

`init_parallel_pdaf.py` creates with mpi4py:

* `COMM_model`: one communicator per model task (not on the filter process),
* `COMM_filter`: the filter process,
* `COMM_couple`: the filter process and process 0 of each model task,

and passes them to PDAF with `PDAF3.set_parallel`. `init_pdaf.py` uses the
PDAF-2 style `PDAF.init`, which also gets the communicators.

Since PDAF exchanges the full state vector between the filter process and
process 0 of each model task, `collect_state_pdaf` gathers the column blocks
of the model task on its process 0 (`Send`/`Recv`), and
`distribute_state_pdaf` scatters them.

## Run and verify

```bash
conda activate pyPDAF
cd tutorials/online_2D_parallelmodel_fullpar_1fpe
mpiexec -n 19 python main_pdaf.py -dim_ens 9 -filtertype 7    # 1 filter process + 9 x 2
cd .. && python verification/check_online.py online_2D_parallelmodel_fullpar_1fpe online_2D_parallelmodel_fullpar_1fpe
```

The processes per model task must be 1, 2, 3, 4, 6 or 9 (e.g. 10, 19, 28, 37 processes for 9 members).

## Notes

* Fortran names the model communicator `COMM_model` (and `mype_model`,
  `npes_model`) in this variant; the Python version keeps the names
  `COMM_2Dmodel`, ... of the other parallel-model tutorials.
* On processes that are not filter processes, `mype_filter` is set to -1
  (undefined in Fortran).
