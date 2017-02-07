import os, sys
import numpy as np

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

space = sys.argv[1]
analysis = sys.argv[2]
label = sys.argv[3]
fmax = sys.argv[4]
model = sys.argv[5]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Compute p-values.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

root_dir = '/space/sophia/2/users/EMOTE-DBS/afMSIT'
results_dir = os.path.join(root_dir, space, model)

## Load and extract data.
obs = np.load(os.path.join(results_dir, 'afMSIT_%s_%s_%s_%s_obs.npz' %(space, analysis, label, fmax)))
tfce = obs['tfce'].squeeze()

## Iteratively perform FWE.
null_files = [f for f in os.listdir(results_dir) if f.startswith('afMSIT_%s_%s_%s_%s' %(space, analysis, label, fmax)) and 'obs' not in f]

n_shuffles = 0.
for n, nf in enumerate(null_files):
    
    npz = np.load(os.path.join(results_dir, nf))
    null = npz['tfce'].squeeze()
    n_shuffles += null.shape[0]

    if not n: p_vals = np.array([nt > tfce.T for nt in null.max(axis=-1)]).sum(axis=0).astype(float).T
    else: p_vals += np.array([nt > tfce.T for nt in null.max(axis=-1)]).sum(axis=0).astype(float).T
    
print 'Total permutations: %s.' %n_shuffles
p_vals /= n_shuffles

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

f = os.path.join(results_dir, 'afMSIT_%s_%s_%s_%s_fwe.npz' %(space, analysis, label, fmax))
np.savez_compressed(f, t_scores = obs['t_scores'], tfce = tfce, p_vals = p_vals, 
                    times = obs['times'], n_shuffles = n_shuffles)
