set SPACES = (source)
set ANALYSES = (stim resp)
set LABELS = (dacc-lh dacc-rh dmpfc-lh dmpfc-rh dlpfc_1-lh dlpfc_1-rh dlpfc_2-lh dlpfc_2-rh) 
set LABELS = (dlpfc_3-lh dlpfc_3-rh dlpfc_4-lh dlpfc_4-rh dlpfc_5-lh dlpfc_5-rh)
set LABELS = (dlpfc_6-lh dlpfc_6-rh pcc-lh pcc-rh racc-lh racc-rh)
#set LABELS = (FCZ)
set FREQS = (15 theta alpha beta)

foreach SPACE ($SPACES)

  foreach ANALYSIS ($ANALYSES)

    foreach LABEL ($LABELS)

      foreach FREQ ($FREQS)

        pbsubmit -m szoro -c "python rt_permutations.py $SPACE $ANALYSIS $LABEL $FREQ"

      end

    end

  end

end
