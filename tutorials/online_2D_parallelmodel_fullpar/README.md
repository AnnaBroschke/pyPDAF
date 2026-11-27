# online_2D_parallelmodel_fullpar (pyPDAF)

Python translation of `PDAF/tutorial/online_2D_parallelmodel_fullpar`. As
`../online_2D_parallelmodel`, but the analysis is computed on **separate filter
processes**. All ensemble members are sent from the model tasks to the filter
processes (and back) by PDAF.

`PDAF3.init_parallel` with `type_parallel = 1` splits the processes into
`dim_ens + 1` groups of (almost) equal size: group 1 are the filter
processes, the others are the model tasks. On the filter processes the
returned model communicator is `MPI_COMM_NULL`, which sets `modelproc = False`.

| Process type | Runs |
|---|---|
| model (`modelproc = True`) | `initialize` (incl. `init_pdaf`) and `integrate_pdaf` |
| filter (`modelproc = False`) | `filtering`: grid setup for the filter, `init_pdaf`, `assimilate_pdaf` in each step |

## Run and verify

```bash
conda activate pyPDAF
cd tutorials/online_2D_parallelmodel_fullpar
mpiexec -n 20 python main_pdaf.py -dim_ens 9 -filtertype 7    # 2 filter processes + 9 x 2
cd .. && python verification/check_online.py online_2D_parallelmodel_fullpar online_2D_parallelmodel_fullpar
```

The processes per group must be 1, 2, 3, 4, 6 or 9 (e.g. 10, 20, 30, 40 processes for 9 members).

## Differences to `../online_2D_parallelmodel`

* `mod_parallel_model.py`, `init_parallel_pdaf.py`: `type_parallel = 1`, `modelproc`
* new `filtering.py`; `main_pdaf.py` calls `filtering` on the filter processes
* `init_ens_pdaf.py`: as in Fortran, the column offset uses `mype_2Dmodel`,
  which on the filter processes still holds the world rank (PDAF does not set
  it there; the filter processes are world ranks 0, ..., npes_filter-1)
