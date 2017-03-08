set SCRIPTS_DIR = /space/sophia/2/users/EMOTE-DBS/afMSIT/scripts/fsfast
set SUBJECTS = (`cat $SCRIPTS_DIR/sessid.manual`)
set SPACES = (lh rh)
set FD = (0.5)

cd /space/lilli/4/users/DARPA-MSIT

foreach SUBJECT ($SUBJECTS)
foreach SPACE ($SPACES)
foreach fd ($FD)

selxavg3-sess -s $SUBJECT -analysis afMSIT.6.$fd.$SPACE -no-preproc -overwrite

end
end
end

cd $SCRIPTS_DIR
