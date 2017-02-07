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
subject = args[0]          # Extract subject
space = args[1]            # Extract space
analysis = args[2]         # Extract analysis
label = args[3]            # Extract label
fmax = args[4]             # Extract frequency information
n_shuffles = int(args[5])  # Define number of permutations
seed = int(args[6])        # Define seed

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

## Reduce data to subject.
ix, = np.where(df.Subject==subject)
df = df.ix[ix].reset_index()
data = data[ix]

print data.shape

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
    
    
## Merge.
t_scores = np.array(t_scores)
print 'Done.'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save results.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

out_dir = os.path.join(root_dir, space, model)
if not os.path.isdir(out_dir): os.makedirs(out_dir)
    
if not seed: f = os.path.join(out_dir, '%s_%s_%s_%s_%s_obs.npz' %(subject, space, analysis, label, fmax))
else: f = os.path.join(out_dir, '%s_%s_%s_%s_%s_%s.npz' %(subject, space, analysis, label, fmax, seed))
np.savez_compressed(f, t_scores=t_scores, times=times,  seed=seed)
