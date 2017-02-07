import os, sys
import numpy as np
from pandas import DataFrame, read_csv
from scipy.stats import spearmanr
from scipy.ndimage import measurements

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

args = sys.argv[1:]        # Extract arguments
space = args[0]            # Extract space
analysis = args[1]         # Extract analysis
label = args[2]            # Extract label
freq = args[3]             # Extract frequency information

## Permutation parameters.
alpha = 0.05
n_shuffles = 1000
seed = 47404

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
root_dir = '/space/sophia/2/users/EMOTE-DBS/afMSIT/%s' %space

## Load data.
npz = np.load(os.path.join(root_dir, 'afMSIT_%s_%s_%s_%s.npz' %(space,analysis,label,freq)))
data = npz['data']
times = npz['times']

## Load trial info.
info = read_csv(os.path.join(root_dir, 'afMSIT_%s_info.csv' %space))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Perform correlations.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Compute true correlations.
r_vals, p_vals = np.apply_along_axis(spearmanr, axis=0, arr=data, b=info.RT)

## Find real clusters.
masked = p_vals < alpha
clusters, n_clusters = measurements.label(masked)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Perform permutation testing (if possible).
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
np.random.seed(seed)

if n_clusters > 0:

    ## Compute cluster sums. 
    cluster_sums = measurements.sum(r_vals, clusters, index=np.arange(n_clusters)+1)

     ## Compute cluster bounds.
    tmin = np.array([times[clusters==i].min() for i in np.arange(n_clusters)+1])
    tmax = np.array([times[clusters==i].max() for i in np.arange(n_clusters)+1])

    ## Find null clusters.
    null_sums = []
    ix = np.arange(info.shape[0])
    
    for _ in xrange(n_shuffles):
        np.random.shuffle(ix)
        info = info.ix[ix].sort_values('Subject')
        r, p = np.apply_along_axis(spearmanr, axis=0, arr=data, b=info.RT) 
        null, nn = measurements.label(p<alpha)
        if nn < 1: null_sums.append(0)
        else: null_sums.append( np.abs( measurements.sum(r, null, index=np.arange(nn)+1) ).max() )
    null_sums = np.array(null_sums)

    ## Compute p-values.
    p_vals = [((np.abs(cs) < null_sums).sum() + 1.) / (null_sums.shape[0] + 1.) for cs in cluster_sums]
    
    ## Assemble results.
    results = DataFrame(dict(Score = cluster_sums, Pval=p_vals, Tmin=tmin, Tmax=tmax))
    results['Contrast'] = 'RT'
    results['Label'] = label
    results['Freq'] = freq
    results['Tdiff'] = results['Tmax'] - results['Tmin']
    results = results[['Contrast','Label','Freq','Tmin','Tmax','Tdiff','Score','Pval']]
    
    ## Save.
    f = '/space/sophia/2/users/EMOTE-DBS/afMSIT/%s/rt/afMSIT_%s_%s_%s_%s_rt.csv' %(space, space, analysis, label, freq)
    results.to_csv(f, index=False)
    
    f = '/space/sophia/2/users/EMOTE-DBS/afMSIT/%s/rt/afMSIT_%s_%s_%s_%s_rt' %(space, space, analysis, label, freq)
    np.savez_compressed(f, r_vals=r_vals, times=times)
    
print 'Done.'
