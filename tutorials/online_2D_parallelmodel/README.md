# online_2D_parallelmodel (pyPDAF)

Python translation of `PDAF/tutorial/online_2D_parallelmodel`: online data
assimilation with a **parallelized model**. Two levels of parallelization are
combined:

* **Ensemble:** the processes are split into `dim_ens` model tasks (one per
  ensemble member), as in `../online_2D_serialmodel`.
* **Model:** each model task runs the model on several processes with domain
  decomposition in x-direction: each process holds `nx_p = nx / npes` columns.
  The number of processes per task must divide nx = 36 (1, 2, 3, 4, 6, 9, 12, 18).

The processes of model task 1 also compute the analysis (with the same
domain decomposition).

## Run

```bash
conda activate pyPDAF
cd tutorials/online_2D_parallelmodel
mpiexec -n 18 python main_pdaf.py -dim_ens 9 -filtertype 7     # 9 members x 2 processes
mpiexec -n 27 python main_pdaf.py -dim_ens 9 -filtertype 6     # 9 members x 3 processes
mpiexec -n 4 python main.py                                    # model only, 4 processes
```

## Verification

```bash
cd tutorials
python verification/check_online.py online_2D_parallelmodel online_2D_parallelmodel        # after -filtertype 7
python verification/check_online.py online_2D_parallelmodel online_2D_parallelmodel_ESTKF  # after -filtertype 6
```

## Structure

| File | Role |
|---|---|
| `mod_parallel_model.py` | MPI for the model; with PDAF, `COMM_2Dmodel` is replaced by the communicator of the own model task |
| `init_parallel_pdaf.py` | `PDAF3.init_parallel` splits the model communicator into model tasks (Fortran: `INTENT(inout)` arguments, here returned) |
| `initialize.py` | domain decomposition, each process reads its columns |
| `init_ens_pdaf`, `obs_A/B_pdafomi`, `init_dim_l_pdaf` | use only the process-local columns (offset `nx_p * mype_filter`) |
| `init_pdaf.py` | additionally `PDAFomi.set_domain_limits` for the local domain |
| `prepoststep_pdaf.py` | process 0 collects the column blocks with `Send`/`Recv` and writes the files |

## Note for Albedo

With many processes on one node, OpenBLAS would start up to 128 threads per
process and exceed the thread limit (`pthread_create failed`). The `pyPDAF`
conda environment therefore sets `OPENBLAS_NUM_THREADS=1` on activation.
