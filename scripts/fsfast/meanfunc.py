import os
import numpy as np
import nibabel as nib
mri_dir = '/space/lilli/4/users/DARPA-MSIT'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Main loop.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

subjects = np.loadtxt('/space/sophia/2/users/EMOTE-DBS/afMSIT/scripts/fsfast/sessid.manual', dtype='str')

for subject in subjects:
    
    print subject,
    
    for hemi in ['lh','rh']:
        
        ## Load data.
        f = os.path.join(mri_dir, subject, 'msit_001', '001', 'fmcpr.sm6.fsaverage.%s.b0dc.nii.gz' %hemi)
        obj = nib.load(f)
        
        ## Extract data and average over acquisitions.
        data = obj.get_data()
        data = np.apply_over_axes(np.mean, data, -1)
        
        ## Save.
        f = os.path.join(mri_dir, subject, 'msit_001', 'afMSIT.6.0.5.%s' %hemi, 'betaconstant.nii.gz')
        obj = nib.Nifti1Image(data, obj.affine)
        nib.save(obj, f)
        
print 'Done.'
