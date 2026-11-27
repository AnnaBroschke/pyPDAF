# 3dvar/offline_2D_serial (pyPDAF)

Python translation of `PDAF/tutorial/3dvar/offline_2D_serial`: offline 3D-Var
for the 2D tutorial model (one analysis step). It is based on
`../../offline_2D_serial`; the folder structure follows PDAF, so inputs are
read from `../../inputs_offline`.

## Methods

All methods use `-filtertype 200`; the variant is selected with `-subtype`:

| subtype | Method | B^1/2 from | Call-backs for B^1/2 |
|---|---|---|---|
| 0 | parameterized 3D-Var | `init_3dvar_offline` (Vmat_p) | `cvt_pdaf`, `cvt_adj_pdaf` |
| 1 | 3D-EnVar, ensemble update with LESTKF | ensemble (Vmat_ens_p) | `cvt_ens_pdaf`, `cvt_adj_ens_pdaf` |
| 2 | 3D-EnVar, ensemble update with ESTKF | ensemble | `cvt_ens_pdaf`, `cvt_adj_ens_pdaf` |
| 3 | hybrid 3D-Var with LESTKF | both | all four |
| 4 | hybrid 3D-Var with ESTKF | both | all four |

Further options: `-type_opt` (1: LBFGS, 2: CG+, 3: plain CG), `-dim_cvec`,
`-mcols_cvec_ens`, `-beta_3dvar` (hybrid weight), `-forget`, `-assim_A/B/C`,
`-cradius`, `-locweight`.

## Run and verify

The same cases as in PDAF's `3dvar/runtests.sh`:

```bash
conda activate pyPDAF
cd tutorials/3dvar/offline_2D_serial
python main_offline.py -dim_ens 1 -dim_cvec 9 -filtertype 200 -subtype 0 -type_opt 1   # -> offline_2D_serial_var_bfgs
python main_offline.py -dim_ens 1 -dim_cvec 9 -filtertype 200 -subtype 0 -type_opt 2   # -> offline_2D_serial_var_cg
python main_offline.py -dim_ens 9 -filtertype 200 -subtype 1 -type_opt 2              # -> offline_2D_serial_lenvar_cg
python main_offline.py -dim_ens 9 -filtertype 200 -subtype 2 -type_opt 2              # -> offline_2D_serial_ESTKF
python main_offline.py -dim_ens 9 -filtertype 200 -subtype 3 -type_opt 2 -dim_cvec 9  # -> offline_2D_serial_lenvar_cg
python main_offline.py -dim_ens 9 -filtertype 200 -subtype 4 -type_opt 2 -dim_cvec 9  # -> offline_2D_serial_ESTKF

# after each run, from the tutorials directory:
python verification/check_offline.py 3dvar/offline_2D_serial <reference>
```

## New compared to offline_2D_serial

* **Control variable transformation**: `cvt_pdaf` / `cvt_adj_pdaf` compute
  `Vmat_p @ v` and `Vmat_p.T @ Vv` (Fortran: `DGEMV`), the ensemble versions
  build `Vmat_ens_p` from the ensemble perturbations in the first iteration.
* **Linearized and adjoint observation operators**: `obs_op_lin_pdafomi` and
  `obs_op_adj_pdafomi` in `callback_obs_pdafomi.py`, using
  `PDAFomi.obs_op_adj_gridpoint` and `PDAFomi.obs_op_adj_interp_lin`.
* `nx`, `ny` are part of `mod_assimilation` (as in the Fortran 3D-Var tutorial).

## Notes on pyPDAF

* `assim_offline_3dvar` and `assim_offline_en3dvar` are not exported in
  `pyPDAF/PDAF3/__init__.py` (pyPDAF 1.1). They are imported from
  `pyPDAF.PDAF3.assim` in `assimilate_pdaf_offline.py`.
* The type stub (`.pyi`) of `cvt_ens_pdaf` lacks the `ens_p` argument; the
  call-back is actually called with `(iter, dim_p, dim_ens, dim_cvec_ens,
  ens_p, v_p, Vv_p)`, as in Fortran.
