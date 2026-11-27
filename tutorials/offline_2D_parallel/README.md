# offline_2D_parallel (pyPDAF)

Python translation of `PDAF/tutorial/offline_2D_parallel`: the offline mode
of `../offline_2D_serial` with the model state distributed over several MPI
processes (domain decomposition). There is no observation type C here.

## Domain decomposition

The global state vector (36 x 18 = 648 values, stored column-wise) is split
into contiguous parts of almost equal size (`initialize.py`):

```
local_dims = [162, 162, 162, 162]          # 4 processes
process p holds state[offset(p) : offset(p) + local_dims[p]]
```

`mod_model_pdaf.offset(p)` corresponds to Fortran's `off_p = SUM(local_dims(1:mype_filter))`.
Consequences for the user routines:

| Routine | What changes |
|---|---|
| `init_ens_offline` | each process keeps only its part of the ensemble |
| `obs_A/B_pdafomi` | each process provides only the observations in its part (`id_obs_p` local); `gather_obs` builds the full vector. Processes without observations pass dummy arrays of size 1 |
| `init_dim_l_pdaf` | the coordinates of a local domain include the offset |
| `prepoststep_ens_offline` | spread computed with `COMM_filter`; process 0 collects the parts with `Send`/`Recv` and writes the files |

## Run and verify

```bash
conda activate pyPDAF
cd tutorials/offline_2D_parallel
mpiexec -n 4 python main_offline.py -filtertype 7
cd .. && python verification/check_offline.py offline_2D_parallel offline_2D_parallel
```

Any number of processes works; the result does not depend on it (up to rounding).

## Notes

* `init_dim_obs_l_pdafomi_user.py` (from the Fortran file of the same name) is an
  example of a user-provided search for local observations instead of
  `PDAFomi.init_dim_obs_l_iso`. In Fortran it is not used (not in the Makefile,
  and it lacks the argument `mode` of `PDAFomi_set_dim_obs_l` required by PDAF 3.1).
  In Python it can be activated with `-obs_l_user .true.`; the results are
  identical to the default:

  ```bash
  mpiexec -n 4 python main_offline.py -filtertype 7 -assim_B .true. -cradius 5.0 -obs_l_user .true.
  ```
* As in Fortran, only observation type A sets `domainsize` and `use_global_obs`.
