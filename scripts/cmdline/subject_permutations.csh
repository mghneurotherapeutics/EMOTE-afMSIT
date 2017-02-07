set SUBJECTS = (BRTU CHDR CRDA JADE JASE M5 MEWA S2)
set SPACES = (source)
set ANALYSES = (stim resp)
set LABELS = (dlpfc_5-lh)
set FREQS = (theta)
set NP = 100
set SEEDS = (`cat seeds.txt`)

foreach SUBJECT ($SUBJECTS)

  foreach SPACE ($SPACES)

    foreach ANALYSIS ($ANALYSES)

      foreach LABEL ($LABELS)

        foreach FREQ ($FREQS)

          pbsubmit -m szoro -c "python subject_permutations.py $SUBJECT $SPACE $ANALYSIS $LABEL $FREQ 1 0"

          foreach SEED ($SEEDS)
 
            pbsubmit -m szoro -c "python subject_permutations.py $SUBJECT $SPACE $ANALYSIS $LABEL $FREQ $NP $SEED"

          end

        end

      end

    end

  end

end
