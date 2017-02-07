import os, sys
import numpy as np
from pandas import read_csv
from mne.stats.cluster_level import _find_clusters as find_clusters

'''
USAGE: The following script is designed to be a command-line callable 
permutations script for the EMOTE-DBS afMSIT data. Everything must 
be defined below.
'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define paramters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Modeling parameters.
model = 'revised'
threshold = dict(start=0.1, step=1, h_power=2, e_power=1) # Mensen & Khatami (2013)
tail = 0
max_step = 1 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Parse command line.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

'''Six parameters: space analysis label fmax n_shuffles seed
-- space: sensor / source
-- analysis: stim / resp
-- label: channel or label
-- fmax: max frequency or frequency band
-- n_shuffles: number of permutations
-- seed: seed for random generator
'''

args = sys.argv[1:]        # Extract arguments
space = args[0]            # Extract space
analysis = args[1]         # Extract analysis
label = args[2]            # Extract label
fmax = args[3]             # Extract frequency information
n_shuffles = int(args[4])  # Define number of permutations
seed = int(args[5])        # Define seed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

root_dir = '/space/sophia/2/users/EMOTE-DBS/afMSIT'

## Load behavior data.
df = os.path.join(root_dir, space, 'afMSIT_%s_info.csv' %space)
df = read_csv(df)

## Load neural data.
f = os.path.join(root_dir, space, 'afMSIT_%s_%s_%s_%s.npz' %(space, analysis, label, fmax))
npz = np.load(f)
data = npz['data']
times = npz['times']

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define model.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def normalize(arr): return (arr - arr.min()) / (arr.max() - arr.min())

if model == 'revised':
    
    ## Add intercept.
    df['Intercept'] = 1 
    ## Add DBS x Interference interaction term.
    df['DBSxInt'] = df[['DBS', 'Interference']].product(axis=1)
    ## Normalize trial number.
    df.Trial = normalize(df.Trial)
    ## Specify columns of interest.
    cols = ['Intercept', 'DBS', 'Interference', 'DBSxInt', 'nsArousal', 'nsValence', 'Trial']
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## De-mean within subjects.
for subject in df.Subject.unique():
    ix, = np.where(df.Subject==subject)
    data[ix] -= data[ix].mean(axis=0)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Perform permutations.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
if seed: np.random.seed(seed)

## Setup for regression.
ix = np.arange(df.shape[0])
t_scores, tfce = [], []

for n in xrange(n_shuffles):
    
    if not n % 100: print n + 1,
    
    ## Permute data.
    np.random.shuffle(ix)
    if seed: df = df.ix[ix].sort_values('Subject')
    
    # Use the following link as your guide in computing the standard error for a coefficient.
    # http://stats.stackexchange.com/questions/44838/how-are-the-standard-errors-of-coefficients-calculated-in-a-regression
    
    ## Construct and invert design matrix.
    design_matrix = df[cols].as_matrix()
    inv = np.linalg.inv( np.dot(design_matrix.T, design_matrix) )
    inv = np.diag(inv)
    
    ## Perform least squares regression.
    betas, resid, _, _ = np.linalg.lstsq(design_matrix, data)
    
    ## Compute mean-squared error from residials.
    n_obs, n_pred = design_matrix.shape
    mse = resid / (n_obs - n_pred)

    ## Compute standard errors.
    beta_se = np.sqrt( np.outer(inv,mse) )

    ## Compute t-scores.
    t_scores.append( betas / beta_se )
    
    ## Perform TFCE.
    sums = []
    for t in ( betas / beta_se ):
        _, s = find_clusters(t, threshold, tail=tail, max_step=max_step, show_info=False)
        sums.append(s)
    tfce.append(np.array(sums))
    
## Merge.
t_scores = np.array(t_scores)
tfce = np.array(tfce)
print 'Done.'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save results.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

out_dir = os.path.join(root_dir, space, model)
if not os.path.isdir(out_dir): os.makedirs(out_dir)
    
if not seed: f = os.path.join(out_dir, 'afMSIT_%s_%s_%s_%s_obs.npz' %(space, analysis, label, fmax))
else: f = os.path.join(out_dir, 'afMSIT_%s_%s_%s_%s_%s.npz' %(space, analysis, label, fmax, seed))
np.savez_compressed(f, t_scores=t_scores, tfce=tfce, times=times, threshold=threshold, seed=seed)
