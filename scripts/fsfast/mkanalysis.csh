set FWHM = 6
set TR = 1.75
set FDs = (0.5)
set fsd = msit_001

cd /autofs/space/lilli_004/users/DARPA-MSIT/

foreach FD ($FDs)
foreach SPACE (lh rh)

mkanalysis-sess \
  -surface fsaverage $SPACE \
  -fwhm $FWHM \
  -notask \
  -taskreg afMSIT.Neu.par 1 \
  -taskreg afMSIT.Int.par 1 \
  -nuisreg afMSIT.mc.par -1 \
  -tpexclude afMSIT.censor.$FD.par \
  -hpf 0.01 \
  -nskip 4 \
  -spmhrf 0 \
  -TR $TR \
  -fsd $fsd \
  -per-run \
  -b0dc  \
  -analysis afMSIT.$FWHM.$FD.$SPACE

end

cd /space/sophia/2/users/EMOTE-DBS/afMSIT/scripts/fsfast
