import os, sys
import numpy as np
import pylab as plt
from mne import read_epochs, read_label, read_source_spaces, set_log_level
from mne.minimum_norm import apply_inverse_epochs, read_inverse_operator
from scipy.io import loadmat
set_log_level(verbose=False)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Subject level parameters.
subject = sys.argv[1]
analysis = sys.argv[2]

task = 'msit'
parc = 'april2016'
fmax = 50

## Source localization parameters.
method = 'dSPM'
snr = 1.0  
lambda2 = 1.0 / snr ** 2
pick_ori = 'normal'

## Labels
rois = ['dacc-lh', 'dacc-rh', 'dmpfc-lh', 'dmpfc-rh', 'dlpfc_1-lh', 'dlpfc_1-rh', 'dlpfc_2-lh', 'dlpfc_2-rh', 
        'dlpfc_3-lh', 'dlpfc_3-rh', 'dlpfc_4-lh', 'dlpfc_4-rh', 'dlpfc_5-lh', 'dlpfc_5-rh', 
        'dlpfc_6-lh', 'dlpfc_6-rh', 'pcc-lh', 'pcc-rh', 'racc-lh', 'racc-rh']

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Iteratively load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

root_dir = '/autofs/space/sophia_002/users/EMOTE-DBS/afMSIT'
fs_dir = '/autofs/space/sophia_002/users/EMOTE-DBS/freesurfs'

## Prepare fsaverage source space.
src = read_source_spaces(os.path.join(fs_dir,'fscopy','bem','fscopy-oct-6p-src.fif'))
vertices_to = [src[n]['vertno'] for n in xrange(2)]
labels = [read_label(os.path.join(fs_dir,'fscopy','label','april2016','%s.label' %roi), subject='fsaverage')
          for roi in rois]

print 'Performing source localization: %s' %subject

## Load in epochs.
epochs = read_epochs(os.path.join(root_dir,'ave','%s_%s_%s_%s-epo.fif' %(subject,task,fmax,analysis)))
times = epochs.times

## Load in secondary files.
inv = read_inverse_operator(os.path.join(root_dir,'cov','%s_%s_%s-inv.fif' %(subject,task,fmax)))
morph_mat = loadmat(os.path.join(root_dir, 'morph_maps', '%s-fsaverage_morph.mat' %subject))['morph_mat']

## Make generator object.
G = apply_inverse_epochs(epochs, inv, method=method, lambda2=lambda2, pick_ori=pick_ori, return_generator=True)
del epochs, inv

## Iteratively compute and store label timecourse. 
ltcs = []
for g in G:
    g = g.morph_precomputed('fsaverage', vertices_to=vertices_to, morph_mat=morph_mat)
    ltcs.append( g.extract_label_time_course(labels, src, mode='pca_flip') )
ltcs = np.array(ltcs)

## Save.
f = os.path.join(root_dir,'source','stcs','%s_%s_%s_%s_%s_epochs' %(subject,task,analysis,method,fmax))
np.savez_compressed(f, ltcs=ltcs, times=times, labels=np.array([l.name for l in labels]))
del ltcs
    
print 'Done.'
