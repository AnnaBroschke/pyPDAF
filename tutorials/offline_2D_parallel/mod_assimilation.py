"""Variables for the assimilation (translation of mod_assimilation.F90).

Only the variables that are actually used in the offline_2D_serial tutorial
are included. Default values are set in init_pdaf_offline.py and can be
changed on the command line (see init_pdaf_parse.py).
"""
import numpy as np

# Coordinates of the current local analysis domain (set in init_dim_l_pdaf)
coords_l: np.ndarray = np.zeros(2)

dim_state: int = 0        # Global model state dimension
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

# Use the user-provided search for local observations
# (init_dim_obs_l_pdafomi_user.py) instead of PDAFomi.init_dim_obs_l_iso
obs_l_user: bool = False

# ---- Ensemble transformation ----
type_trans: int = 0       # Type of ensemble transformation
type_sqrt: int = 0        # Type of transform matrix square-root

# ---- Further parameters that can be parsed (kept for compatibility) ----
model_error: bool = False
model_err_amp: float = 0.0
rank_ana_enkf: int = 0
dim_lag: int = 0
