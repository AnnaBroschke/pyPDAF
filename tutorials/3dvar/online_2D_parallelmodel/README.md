# 3dvar/online_2D_parallelmodel (pyPDAF)

Python translation of `PDAF/tutorial/3dvar/online_2D_parallelmodel`: the 3D-Var
methods of `../online_2D_serialmodel` with the parallelized model of
`../../online_2D_parallelmodel` (domain decomposition in x-direction, one model
task per ensemble member; the processes of task 1 compute the analysis).

## What is new compared to the serial 3D-Var

* **B^1/2 is distributed**: each filter process holds the rows of `Vmat_p`
  (and `Vmat_ens_p`) for its `nx_p` columns. The adjoint transformations
  `cvt_adj_pdaf` / `cvt_adj_ens_pdaf` therefore sum the partial products over
  the filter processes (`MPI_Allreduce`).
* **Parallelized optimizers** `-type_opt 12` (CG+) and `13` (plain CG): also the
  control vector is distributed. `init_pdaf.py` computes the local sizes and
  offsets (`dims_cv_p`, `off_cv_p`, `dims_cv_ens_p`, `off_cv_ens_p`), the local
  sizes are passed to PDAF, and `cvt_pdaf` / `cvt_ens_pdaf` gather the full
  control vector with `MPI_Allgatherv`.

## Run and verify

The cases of PDAF's `3dvar/runtests.sh` (compared with the references of the
serial 3D-Var tutorial):

```bash
conda activate pyPDAF
cd tutorials/3dvar/online_2D_parallelmodel
V="-dim_ens 1 -dim_cvec 9 -filtertype 200 -subtype 0"
E="-dim_ens 9 -filtertype 200"
python main_pdaf.py $V -type_opt 1                                       # -> online_2D_serialmodel_var_bfgs
mpiexec -n 2 python main_pdaf.py $V -type_opt 12                         # -> online_2D_serialmodel_var_cg
mpiexec -n 18 python main_pdaf.py $E -subtype 1 -type_opt 12             # -> online_2D_serialmodel_lenvar_cg
mpiexec -n 18 python main_pdaf.py $E -subtype 2 -type_opt 12             # -> online_2D_serialmodel_envar_cg_ESTKF
mpiexec -n 18 python main_pdaf.py $E -subtype 3 -type_opt 12 -dim_cvec 9 # -> online_2D_serialmodel_lhybvar_cg
mpiexec -n 18 python main_pdaf.py $E -subtype 4 -type_opt 12 -dim_cvec 9 # -> online_2D_serialmodel_hybvar_cg_ESTKF

# after each run, from the tutorials directory:
python verification/check_online.py 3dvar/online_2D_parallelmodel <reference>
```

The processes per model task must divide nx = 36. There is no observation
type C in this tutorial.

## Notes

* The matrix-vector products use `numpy` (`@`) instead of `DGEMV`. With a
  distributed control vector, results can differ from Fortran by rounding
  (up to ~1e-13 in the tests), far below the tolerance of 1e-9.
* As in `../online_2D_serialmodel`, `assimilate_3dvar` and `assimilate_en3dvar`
  are imported from `pyPDAF.PDAF3.assim` (not exported in pyPDAF 1.1).
