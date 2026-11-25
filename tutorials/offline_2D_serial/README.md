# offline_2D_serial (pyPDAF)

Python translation of `PDAF/tutorial/offline_2D_serial`. The file structure
follows the Fortran tutorial one to one (`xyz.F90` -> `xyz.py`), so both
versions can be read side by side.

## Run

```bash
conda activate pyPDAF
cd tutorials/offline_2D_serial
python main_offline.py                      # ESTKF (default, filtertype 6)
python main_offline.py -filtertype 7        # LESTKF
python main_offline.py -filtertype 7 -assim_B .true. -assim_C .true. -cradius 5.0
```

Options are given as in the Fortran version (`-handle value`, see
`init_pdaf_parse.py`). Inputs are read from `../inputs_offline`, results are
written to `state_ana.txt` and `ens_XX_ana.txt`.

## Verification

```bash
cd tutorials
python verification/check_offline.py offline_2D_serial offline_2D_serial        # after -filtertype 7
python verification/check_offline.py offline_2D_serial offline_2D_serial_ESTKF  # after -filtertype 6
```

The reference files are copied from `PDAF/tutorial/verification`.

## Main differences to Fortran

| Fortran | Python |
|---|---|
| Module variables (`SAVE`) | Module-level variables (`import mod_assimilation as assim`) |
| `INTENT(out)/(inout)` arguments | Returned from the call-back function |
| `TYPE(obs_f) :: thisobs` per obs module | Object inside PDAF, addressed by index `I_OBS` (`pyPDAF.PDAFomi.init(3)`) |
| `thisobs%id_obs_p = ...` | `pyPDAF.PDAFomi.set_id_obs_p(I_OBS, ...)` |
| State vector column-wise: `(j-1)*ny + i` | `field.ravel(order='F')` / `vec.reshape((ny, nx), order='F')` |
| `PDAF_parse` | `pdaf_parse()` in `init_pdaf_parse.py` |
| `PDAF3_init_parallel` initialises MPI | MPI is already initialised by `import pyPDAF`, so `MPI.COMM_WORLD.py2f()` is passed |

`timer.F90` and `mod_memcount.F90` are not translated (not needed in Python).
