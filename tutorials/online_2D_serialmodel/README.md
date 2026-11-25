# online_2D_serialmodel (pyPDAF)

Python translation of `PDAF/tutorial/online_2D_serialmodel`. The file structure
follows the Fortran tutorial one to one (`xyz.F90` -> `xyz.py`).

The model shifts a 2D field (18 x 36) by one grid point in y-direction per
time step, for 18 time steps. Every `delt_obs` (default 2) steps an analysis
is performed, i.e. 9 analysis steps by default.

## Run

Each ensemble member is integrated by its own process (fully parallel
ensemble forecast), so start as many processes as ensemble members:

```bash
conda activate pyPDAF
cd tutorials/online_2D_serialmodel
mpiexec -n 9 python main_pdaf.py -dim_ens 9                    # ESTKF (default, filtertype 6)
mpiexec -n 9 python main_pdaf.py -dim_ens 9 -filtertype 7      # LESTKF
mpiexec -n 9 python main_pdaf.py -dim_ens 9 -filtertype 7 -assim_B .true. -cradius 5.0
python main.py                                                 # model only, without PDAF
```

Further options: `-delt_obs`, `-forget`, `-ensgroup 2` (read `ensB_X.txt`),
`-assim_A/B/C`, `-rms_obs_A/B/C`, `-locweight`, `-cradius`, `-sradius`, `-screen`.

Output: `ens_XX_stepYY_for.txt` / `_ana.txt` and `state_stepYY_for.txt` / `_ana.txt`.

## Verification

```bash
cd tutorials
python verification/check_online.py online_2D_serialmodel online_2D_serialmodel        # after -filtertype 7
python verification/check_online.py online_2D_serialmodel online_2D_serialmodel_ESTKF  # after -filtertype 6
```

All 180 output files (forecast and analysis of all 9 steps) are compared.

## Plotting

```bash
python ../plotting/plot_ens.py 5 20                     # time series at grid point (5, 20)
python ../plotting/plot_file.py state_step18_ana.txt
python ../plotting/plot_diff.py state_step18_ana.txt ../inputs_online/true_step18.txt
```

## Differences to Fortran (in addition to offline_2D_serial)

| Fortran | Python |
|---|---|
| `#ifdef USE_PDAF` in `initialize.F90` | argument `initialize(use_pdaf=True/False)` |
| model step inline in `integrate.F90` and `integrate_pdaf.F90` | shared function in `model_step.py` (`np.roll`) |
| `mod_model_pdaf.F90` re-exports `mod_model` | all files use `import mod_model as model` |
| `next_observation_pdaf(stepnow, nsteps, doexit, time)` | returns `(nsteps, doexit, time)` |
| `distribute_state_pdaf` / `collect_state_pdaf` | `field[:, :] = state_p.reshape(..., order='F')` / `state_p[:] = field.ravel(order='F')` |
