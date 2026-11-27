"""Variables for the assimilation (translation of mod_assimilation.F90).

Only the variables that are actually used in the offline_2D_serial tutorial
are included. Default values are set in init_pdaf_offline.py and can be
changed on the command line (see init_pdaf_parse.py).
"""
import numpy as np

# ---- Model grid (in the 3D-Var tutorial these are part of mod_assimilation) ----
nx: int = 0               # Size of 2D grid in x-direction
ny: int = 0               # Size of 2D grid in y-direction

# ---- Square root of the covariance matrix for 3D-Var ----
Vmat_p: np.ndarray = np.zeros((0, 0))      # B^1/2 for parameterized 3D-Var, (dim_p, dim_cvec)
Vmat_ens_p: np.ndarray = np.zeros((0, 0))  # Ensemble B^1/2 for 3D-EnVar, (dim_p, dim_cvec_ens)

# Coordinates of the current local analysis domain (set in init_dim_l_pdaf)
coords_l: np.ndarray = np.zeros(2)

dim_state_p: int = 0      # Process-local model state dimension

# ---- Settings for observations ----
delt_obs: int = 1         # Time step interval between analysis/assimilation steps
observe_ens: int = 0      # (0) apply H also to ensemble mean; (1) apply H only to ensemble
type_obs_init: int = 1    # Init obs. (0) before or (1) after call to prepostep

# ---- General control of PDAF ----
screen: int = 0           # Control verbosity of PDAF (0, 1, 2)
dim_ens: int = 0          # Size of ensemble
filtertype: int = 0       # Select filter algorithm
subtype: int = 0          # Subtype of filter algorithm
type_forget: int = 0      # Type of forgetting factor
forget: float = 1.0       # Forgetting factor for filter analysis

# ---- Localisation (LSEIK, LETKF, LESTKF, LNETF, LKNETF, LSEIK) ----
cradius: float = 0.0      # Cut-off radius for local observation domain
locweight: int = 0        # Type of localizing weighting of observations
sradius: float = 0.0      # Support radius for 5th-order polynomial

# ---- Ensemble transformation ----
type_trans: int = 0       # Type of ensemble transformation
type_sqrt: int = 0        # Type of transform matrix square-root

# ---- 3D-Var settings ----
type_opt: int = 1         # Optimizer: (1) LBFGS, (2) CG+, (3) plain CG (+ variants, see PDAF docs)
dim_cvec: int = 0         # Size of control vector (parameterized 3D-Var part)
dim_cvec_ens: int = 0     # Size of control vector (ensemble part)
mcols_cvec_ens: int = 1   # Multiplication factor for number of columns of ensemble B^1/2
beta_3dvar: float = 0.5   # Hybrid weight for hybrid 3D-Var

# ---- Further parameters that can be parsed (kept for compatibility) ----
model_error: bool = False
model_err_amp: float = 0.0
rank_ana_enkf: int = 0
dim_lag: int = 0
