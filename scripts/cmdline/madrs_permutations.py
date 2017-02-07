import os, sys
import numpy as np
from pandas import DataFrame, read_csv
from scipy.stats import pearsonr
from scipy.ndimage import measurements

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

args = sys.argv[1:]        # Extract arguments
space = args[0]            # Extract space
analysis = args[1]         # Extract analysis
label = args[2]            # Extract label
freq = args[3]             # Extract frequency information
domain = args[4]

alpha = 0.05

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare information.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
root_dir = '/space/sophia/2/users/EMOTE-DBS/afMSIT/%s' %space
info = read_csv(os.path.join(root_dir, 'afMSIT_%s_info.csv' %space))

## Prepare MADRS scores.
ratings = read_csv('/space/sophia/2/users/EMOTE-DBS/afMSIT/behavior/Subject_Rating_Scales.csv')
ratings = ratings.set_index('Subject')
madrs = ratings.loc[info.Subject.unique(), 'MADRS_Now'] - ratings.loc[info.Subject.unique(), 'MADRS_Base']

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

npz = np.load(os.path.join(root_dir, 'afMSIT_%s_%s_%s_%s.npz' %(space,analysis,label,freq)))
data = npz['data']
times = npz['times']

## Average within subjects and DBS. Subtract.
contrast = []
for subject in info.Subject.unique():

    ts = []
    for dbs in [0,1]:

        ix, = np.where((info.Subject==subject)&(info.DBS==dbs))
        if domain == 'timedomain': 
            ts.append( np.mean(data[ix], axis=0) )
        elif domain == 'frequency': 
            ts.append( np.log10( np.median( 10 ** (data[ix] / 10), axis=0 ) ) * 10 )

    contrast.append( ts[-1] - ts[0] ) # DBSon - DBSoff

contrast = np.array(contrast)
del data, ts

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Perform correlations.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Compute true correlations.
r_vals, p_vals = np.apply_along_axis(pearsonr, axis=0, arr=contrast, y=madrs)

## Find real clusters.
masked = p_vals < alpha
clusters, n_clusters = measurements.label(masked)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Perform permutation testing (if possible).
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

if n_clusters > 0:

    ## Compute cluster sums. 
    cluster_sums = measurements.sum(r_vals, clusters, index=np.arange(n_clusters)+1)

     ## Compute cluster bounds.
    tmin = np.array([times[clusters==i].min() for i in np.arange(n_clusters)+1])
    tmax = np.array([times[clusters==i].max() for i in np.arange(n_clusters)+1])

    ## Find null clusters.
    null_sums = []
    shuffles = np.load('/space/sophia/2/users/EMOTE-DBS/afMSIT/scripts/cmdline/madrs_permutations.npy')
    
    for s in shuffles:
        r, p = np.apply_along_axis(pearsonr, axis=0, arr=contrast, y=madrs[s]) 
        null, nn = measurements.label(p<alpha)
        if nn < 1: null_sums.append(0)
        else: null_sums.append( np.abs( measurements.sum(r, null, index=np.arange(nn)+1) ).max() )
    null_sums = np.array(null_sums)

    ## Compute p-values.
    p_vals = [((np.abs(cs) < null_sums).sum() + 1.) / (null_sums.shape[0] + 1.) for cs in cluster_sums]
    
    ## Assemble results.
    results = DataFrame(dict(Score = cluster_sums, Pval=p_vals, Tmin=tmin, Tmax=tmax))
    results['Contrast'] = 'DBS'
    results['Label'] = label
    results['Freq'] = freq
    results['Tdiff'] = results['Tmax'] - results['Tmin']
    results = results[['Contrast','Label','Freq','Tmin','Tmax','Tdiff','Score','Pval']]
    
    ## Save.
    f = '/space/sophia/2/users/EMOTE-DBS/afMSIT/%s/madrs/afMSIT_%s_%s_%s_%s_dbs.csv' %(space, space, analysis, label, freq)
    results.to_csv(f, index=False)
    
    f = '/space/sophia/2/users/EMOTE-DBS/afMSIT/%s/madrs/afMSIT_%s_%s_%s_%s_dbs' %(space, space, analysis, label, freq)
    np.save(f, r_vals)
    
print 'Done.'