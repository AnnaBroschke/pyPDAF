# online_2D_serialmodel_2fields (pyPDAF)

Python translation of `PDAF/tutorial/online_2D_serialmodel_2fields`. It extends
`online_2D_serialmodel` by a second model field: the state vector contains
the fields A and B one after the other:

```
state_p = [ field A (648 values) | field B (648 values) ]
```

The setup of the state vector (names, dimensions, offsets) is done in
`mod_statevector_pdaf.py`. Observation type A observes field A, observation
type B observes field B (there is no observation type C in this tutorial).

## Run

```bash
conda activate pyPDAF
cd tutorials/online_2D_serialmodel_2fields
mpiexec -n 9 python main_pdaf.py -dim_ens 9                                  # ESTKF, obs A
mpiexec -n 9 python main_pdaf.py -dim_ens 9 -filtertype 7                    # LESTKF
mpiexec -n 9 python main_pdaf.py -dim_ens 9 -filtertype 7 -assim_A .false. -assim_B .true.
python main.py                                                               # model only
```

Output: `ensA_XX_stepYY_{for,ana}.txt`, `ensB_...`, `stateA_stepYY_{for,ana}.txt`, `stateB_...`.

## Verification

The reference files are shared with `online_2D_serialmodel` (as in PDAF's
`runtests.sh`). Field A of this tutorial is compared with the `ens_*` /
`state_*` files of the single-field case:

```bash
cd tutorials
# after -filtertype 7
python verification/check_online.py online_2D_serialmodel_2fields online_2D_serialmodel --fields ensA:ens stateA:state
# after -filtertype 6
python verification/check_online.py online_2D_serialmodel_2fields online_2D_serialmodel_ESTKF --fields ensA:ens stateA:state ensB stateB
# after -filtertype 7 -assim_A .false. -assim_B .true.
python verification/check_online.py online_2D_serialmodel_2fields online_2D_serialmodel_2fields_obsB --fields ensA:ens stateA:state ensB stateB
```

## Plotting

```bash
python ../plotting/plot_file.py stateB_step18_ana.txt
python ../plotting/plot_diff.py stateB_step18_ana.txt ../inputs_online_2fields/trueB_step18.txt
```

`plot_ens.py` expects files named `ens_XX_step...` and therefore works only
for the single-field tutorial.

## Differences to Fortran (in addition to online_2D_serialmodel)

| Fortran | Python |
|---|---|
| `TYPE(state_field) :: sfields(:)` with `%dim`, `%off`, `%name` | `StateField` dataclass, list `sfields`, property `.slice` |
| `state_p(sfields(i)%off+1 : sfields(i)%off+sfields(i)%dim)` | `state_p[sfields[i].slice]` |
| `id%fieldA = 1`, `id%fieldB = 2` (1-based) | `id.fieldA = 0`, `id.fieldB = 1` (0-based list index) |
| `MPI_Reduce` of the state dimension | `comm_model.reduce(...)` with mpi4py |

`localize_covar_A/B` in the Fortran observation modules are not translated:
they are only needed for 3D-Var/ensemble variants and are not called in
this tutorial.
