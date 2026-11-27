# 3dvar/online_2D_serialmodel (pyPDAF)

Python translation of `PDAF/tutorial/3dvar/online_2D_serialmodel`: the 3D-Var
methods of `../offline_2D_serial` applied in the online mode of
`../../online_2D_serialmodel` (18 time steps, analysis every `delt_obs` = 2 steps).
Inputs are read from `../../inputs_online`.

## Methods

All methods use `-filtertype 200`; the variant is selected with `-subtype`:

| subtype | Method | Processes |
|---|---|---|
| 0 | parameterized 3D-Var (`-dim_ens 1 -dim_cvec 9`) | 1 |
| 1 | 3D-EnVar, ensemble update with LESTKF | 9 (`-dim_ens 9`) |
| 2 | 3D-EnVar, ensemble update with ESTKF | 9 |
| 3 | hybrid 3D-Var with LESTKF (`-dim_cvec 9`) | 9 |
| 4 | hybrid 3D-Var with ESTKF (`-dim_cvec 9`) | 9 |

Further options: `-type_opt` (1: LBFGS, 2: CG+, 3: plain CG), `-mcols_cvec_ens`,
`-beta_3dvar`, `-forget`, `-delt_obs`, `-assim_A/B/C`, `-cradius`, `-locweight`.
(As in the Fortran version, `-ensgroup` is not available in this tutorial.)

## Run and verify

The cases of PDAF's `3dvar/runtests.sh`:

```bash
conda activate pyPDAF
cd tutorials/3dvar/online_2D_serialmodel
V="-dim_ens 1 -dim_cvec 9 -filtertype 200 -subtype 0"
E="-dim_ens 9 -filtertype 200"
python main_pdaf.py $V -type_opt 1                              # -> online_2D_serialmodel_var_bfgs
python main_pdaf.py $V -type_opt 2                              # -> online_2D_serialmodel_var_cg
mpiexec -n 9 python main_pdaf.py $E -subtype 1 -type_opt 2      # -> online_2D_serialmodel_lenvar_cg
mpiexec -n 9 python main_pdaf.py $E -subtype 2 -type_opt 2      # -> online_2D_serialmodel_envar_cg_ESTKF
mpiexec -n 9 python main_pdaf.py $E -subtype 3 -type_opt 2 -dim_cvec 9   # -> online_2D_serialmodel_lhybvar_cg
mpiexec -n 9 python main_pdaf.py $E -subtype 4 -type_opt 2 -dim_cvec 9   # -> online_2D_serialmodel_hybvar_cg_ESTKF
mpiexec -n 9 python main_pdaf.py $E -subtype 2 -type_opt 3      # -> online_2D_serialmodel_envar_plaincg_ESTKF

# after each run, from the tutorials directory:
python verification/check_online.py 3dvar/online_2D_serialmodel <reference>
```

## Differences to the other tutorials

* Compared to `../../online_2D_serialmodel`: control variable transformations
  (`cvt_*.py`, identical to `../offline_2D_serial`), linearized/adjoint
  observation operators, `init_3dvar_pdaf.py`, and two pre/poststep routines
  (`prepoststep_ens_pdaf.py`, `prepoststep_3dvar_pdaf.py`).
* `PDAF_init_forecast` gets `prepoststep_3dvar_pdaf` for subtype 0 and
  `prepoststep_ens_pdaf` otherwise.

## Notes on pyPDAF 1.1

* `assimilate_3dvar` and `assimilate_en3dvar` are not exported in
  `pyPDAF/PDAF3/__init__.py`; they are imported from `pyPDAF.PDAF3.assim`.
* `assimilate_3dvar` has no status argument, while `assimilate_en3dvar` and
  `assimilate_3dvar_all` have one. All three return the status.
