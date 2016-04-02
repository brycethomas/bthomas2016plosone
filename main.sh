#!/bin/bash 

# Main script to run all simulations and produce all output figures and data
# used in the paper: "Diffusion in Colocation Contact Networks: the Impact of
# Nodal Spatiotemporal Dynamics".

exit_with_sound() {
    # play sound when script fails anywhere.
    mplayer -msglevel all=-1 trombone.mp3 ; exit 1
}
#trap 'exit_with_sound' ERR # uncomment to reactivate.

# change script's directory to that which this script is in.  Note: won't work
# if the script is a symlink.  See http://goo.gl/34lwT.
DIR="$( cd "$( dirname "$BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

OUT_DIR="./charlie" # base directory to store output artifacts in e.g. figures.

# Make output directories if they don't exist.
mkdir -p tmp ${OUT_DIR} ${OUT_DIR}/figs ${OUT_DIR}/tbls ${OUT_DIR}/vars

# Exit if any command or pipeline returns non-zero status.
set -e

# Change input field separator to newline.
saveIFS="$IFS"
IFS=$'\n'

# Session shuffling flags and their translations.
SESS_SHUFF_FLAGS=("Original" "LNTN" "TLLN" "LN" "TN" "TL" "_")
declare -A SESS_SHUFF_FLAG_LEGEND
# Can change legend to human-intellgible strings (not acronyms) if we desire.
SESS_SHUFF_FLAG_LEGEND=(["Original"]="Original" ["LNTN"]="LN\$-\$TN" ["TLLN"]="TL\$-\$LN" \
["LN"]="LN" ["TN"]="TN" ["TL"]="TL" ["_"]="\$\\\emptyset\$")

# A random seed.
SEED=1000

# Number of trials for any given simulated facet.
TRIALS=250

# If true, prevalence results I(t)/N should use N = |LCC| rather than 
# N = total nodes (LCC: Largest Connected Component).
LCC=true

# compile Go scripts (faster than using "go run ..." each time).
go build session_shuffle.go
go build sessions_to_encounters.go
go build encounter_count.go

# Read in the St Lucia data
DATA=`cat st_lucia.csv`
# Read in all of UQ data
UQ=`cat uq.csv`

pdf_to_eps() {
    if [ -z "$1" ]
   then
     echo "pdf_to_eps needs a base file name!"
     exit
   else
     gs -q -dNOCACHE -dNOPAUSE -dBATCH -dSAFER -sDEVICE=epswrite \
	 -sOutputFile="${1}.eps" "${1}.pdf"
   fi
}

########################################
# Number of active sessions over time. #
########################################
BASE_FILE_NAME="${OUT_DIR}/figs/active_sessions"
(echo -e "Active Sessions"; echo -e "$DATA" | cut -f 2,3 -d , | \
python active_sessions.py) | python lp.py -l 'none' \
-x 'Time' -y 'Number of active sessions' --mark-every 10000 -s \
"${BASE_FILE_NAME}.pdf" --day-of-week --no-color
pdf_to_eps "${BASE_FILE_NAME}"

###############################################################	    
# Bin count number of repeat contacts between pairs of nodes. #
###############################################################
echo -e "Tabulating repeat contacts between node pairs..."
ENCOUNTERS=`echo -e "$DATA" | python sessions_to_encounters.py`
REPEATS=`echo -e "$ENCOUNTERS" | cut -f 1,2 -d , | python repeat_encounters.py`
COUNTS=`echo -e "$REPEATS" | cut -f 3 -d ,`
TBL_DATA=`echo -e "$COUNTS" | python bin_int.py -e 1 -e 2 -g 2 -l`
echo -e "$TBL_DATA" | python latex_tabulator.py -t "repeats" -t "count" \
-c "Number of repeat contacts" -l "tbl:repeat_contacts" > \
${OUT_DIR}/tbls/repeat_contacts.tex

#############################################
# Calculate basic stats on UQ and St Lucia. #
#############################################
echo -e "Calculating basic stats on UQ and St Lucia..."
# UQ stats.
MIN_START=`echo -e "$UQ" | cut -f 2 -d , | awk 'NR == 1 || \\
    $0 < min {min = $0}END{print min}'`
MAX_END=`echo -e "$UQ" | cut -f 3 -d , | awk 'NR == 1 || \\
    $0 > max {max = $0}END{print max}'`
date -d @${MIN_START} > ${OUT_DIR}/vars/uq_trace_first_time_human.tex
date -d @${MAX_END} > ${OUT_DIR}/vars/uq_trace_last_time_human.tex
DAYS=`echo -e "scale=2; (${MAX_END} - ${MIN_START}) / 60 / 60 / 24" | bc`
echo -e "$DAYS" > ${OUT_DIR}/vars/uq_trace_length_days.tex
echo -e "$UQ" | wc -l | tr -d '\n' | xargs -0 printf "%'.f" > \
${OUT_DIR}/vars/uq_trace_session_count.tex
echo -e "$UQ" | cut -f 1 -d , | sort | uniq | wc -l | tr -d '\n' | \
xargs -0 printf "%'.f" > ${OUT_DIR}/vars/uq_trace_mac_count.tex
echo -e "$UQ" | cut -f 4 -d , | sort | uniq | wc -l | tr -d '\n' |
xargs -0 printf "%'.f" > ${OUT_DIR}/vars/uq_trace_ap_count.tex
# St Lucia stats.
echo -e "$DATA" | wc -l | tr -d '\n' | xargs -0 printf "%'.f" > \
${OUT_DIR}/vars/st_lucia_trace_session_count.tex
echo -e "$DATA" | cut -f 1 -d , | sort | uniq | wc -l | tr -d '\n' | \
xargs -0 printf "%'.f" > ${OUT_DIR}/vars/st_lucia_trace_mac_count.tex
echo -e "$DATA" | cut -f 4 -d , | sort | uniq | wc -l | tr -d '\n' | \
xargs -0 printf "%'.f" > ${OUT_DIR}/vars/st_lucia_trace_ap_count.tex

#############################################################################
# Prevalence under inducement-shuffling, versus both time and num contacts. #
#############################################################################
echo -e "Calculating prevalence under session shuffling..."
# 10 days simulation runway, in seconds.
RUNWAY=`echo -e "10 * 24 * 60 * 60" | bc`
PLOT_INPUT=""
E_PLOT_INPUT="" # encounters vs. prevalence plot, non-unique encounters
E_PLOT_INPUT_U="" # encounters vs. prevalence plot, unique encounters
SEM_PLOT_INPUT="" # standard error of mean plot input
ENQ_FREQ_ECDF_PLOT_INPUT="" # encounter frequency ecdf non-unique plot input.
ENQ_FREQ_ECDF_PLOT_INPUT_U="" # encounter frequency ecdf unique plot input.
LOC_ECDF_PER_NODE_PLOT_INPUT="" # unique locations visited per node ecdf input.
INTERSESS_ECDF_PLOT_INPUT="" # intersession times.
ONE_DAY_PREVS_PLOT_INPUT=""
PREV_ONE_DAY="" # prevalence at one day.
for n in ${SESS_SHUFF_FLAGS[@]}; do
    echo -e "Processing prevalence for shuffle ${SESS_SHUFF_FLAG_LEGEND[${n}]}..."
    SEED=1000
    PLOT_INPUT+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    E_PLOT_INPUT+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    E_PLOT_INPUT_U+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    SEM_PLOT_INPUT+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    ONE_DAY_PREVS_PLOT_INPUT+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    
    if [[ $n == "Original" ]]; then
        SESSNS=`echo -e "$DATA"`
    else
        SESSNS=`echo -e "$DATA" | ./session_shuffle $n`
    fi
    ENCOUNTERS=`echo -e "$SESSNS" | ./sessions_to_encounters | \\
    cut -f 1,2,3 -d ,`
    # Total and unique encounters per node.
    TOT_ENC_FREQ_PER_NODE=`echo -e "$ENCOUNTERS" | cut -f 1,2 -d , | \\
    tr ',' '\n' | sort | uniq -c | sed -e 's/ *//' -e 's/ /,/' | cut -f 1 -d ,`
    UNIQ_ENC_FREQ_PER_NODE=`echo -e "$ENCOUNTERS" | cut -f 1,2 -d , | \\
    python sort_csv.py | sort | uniq | tr ',' '\n' | sort | uniq -c | \\
    sed -e 's/ *//' -e 's/ /,/' | cut -f 1 -d ,`
    TOT_ENC_FREQ_PER_NODE_ECDF=`echo -e "$TOT_ENC_FREQ_PER_NODE" | \\
    python ecdf.py`
    UNIQ_ENC_FREQ_PER_NODE_ECDF=`echo -e "$UNIQ_ENC_FREQ_PER_NODE" | \\
    python ecdf.py`
    INTERSESS_ECDF=`echo -e "$SESSNS" | cut -f 1,2,3 -d , | \\
    python intersession_times.py | awk '{print "scale=4;" $0 " / 60.0" }' | \\
    bc | python ecdf.py`
    #INTERSESS_ECDF=`echo -e "$SESSNS" | cut -f 1,2,3 -d , | \\
    #python intersession_times.py | python ecdf.py`

    ENQ_FREQ_ECDF_PLOT_INPUT+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    ENQ_FREQ_ECDF_PLOT_INPUT+="${TOT_ENC_FREQ_PER_NODE_ECDF}\n"
    ENQ_FREQ_ECDF_PLOT_INPUT_U+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    ENQ_FREQ_ECDF_PLOT_INPUT_U+="${UNIQ_ENC_FREQ_PER_NODE_ECDF}\n"
    # Unique locations per node.
    LOC_ECDF_PER_NODE_PLOT_INPUT+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    UNIQ_LOC_PER_NODE=`echo -e "$SESSNS" | cut -f 1,4 -d , | \\
    sort | uniq | cut -f 1 -d , | sort | uniq -c | sed -e 's/ *//' -e 's/ /,/' | \\
    cut -f 1 -d ,`
    LOC_ECDF_PER_NODE_PLOT_INPUT+=`echo -e "$UNIQ_LOC_PER_NODE" | \\
    python ecdf.py`
    LOC_ECDF_PER_NODE_PLOT_INPUT+="\n"
    INTERSESS_ECDF_PLOT_INPUT+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    INTERSESS_ECDF_PLOT_INPUT+="${INTERSESS_ECDF}"
    INTERSESS_ECDF_PLOT_INPUT+="\n"
    FIRST_ENC_TIME=`echo -e "$ENCOUNTERS" | awk -F ',' 'NR == 1 || \\
    $3 < min {min = $3}END{print min}'`
    LAST_ENC_TIME=`echo -e "$ENCOUNTERS" | awk -F ',' 'NR == 1 || \\
    $3 > max {max = $3}END{print max}'`
    # the latest time a source encounter should be selected to ensure
    # $RUNWAY of simulation time.
    SOURCE_CUTOFF=`echo -e "${LAST_ENC_TIME} - ${RUNWAY}" | bc`
    # source encounter event should be prior to the cutoff time
    CAND_SOURCE_ENCS=`echo -e "$ENCOUNTERS" | \\
    awk -v first=$FIRST_ENC_TIME -v last=$SOURCE_CUTOFF -F ',' '$3 >= first && $3 < last'`
    TRI_RES="" # Trial results.
    ONE_DAY_PREVS="" # prevalences at one day
    E_TRI_RES=""
    E_TRI_RES_U=""
    for i in $(seq 0 `expr $TRIALS - 1`); do
        have_source=false
        while [ "$have_source" = false ]; do
            MAC_MAC_TIME=`echo -e "$CAND_SOURCE_ENCS" | \\
            python rand_encounter.py -s $SEED`
            MAC1=`echo -e "$MAC_MAC_TIME" | cut -f 1 -d ,`
            MAC2=`echo -e "$MAC_MAC_TIME" | cut -f 2 -d ,`
            # simulation start and end times
            START_TIME=`echo -e "$MAC_MAC_TIME" | cut -f 3 -d ,`
            END_TIME=`echo -e "${START_TIME} + ${RUNWAY}" | bc` 
            # ENCS should represent the 10-day encounter period starting at the
            # randomly sampled start event.  i.e. encounters prior to start event
            # and after 10 days subsequent should be discarded.
            ENCS=`echo -e "$ENCOUNTERS" | \\
            awk -v start_time=$START_TIME -v end_time=$END_TIME -F ',' \\
            '$3 >= start_time && $3 <= end_time'`
            if [ "$LCC" = true ]; then
                ENCS=`echo -e "$ENCS" | python cc.py`
                # recall 0 = true in a bash if statement like this
                if ! echo -e "$ENCS" | cut -f 1 -d , | \
                awk -v mac=$MAC1 -F ',' '{if ($1 == mac) {found_mac = 1; exit 0;}} \
                END {if (found_mac) exit 0; else exit 1;}'; then
                    echo -e "WARNING: Source MAC not in LCC so resampling."
                    ((SEED++))
                else
                    # all good -- chosen source belongs to LCC
                    have_source=true
                fi
            else
                # if not restricting ourselves to LCC then don't need to
                # verify LCC membership.
                have_source=true
            fi
        done
        THIS_TRI_RES=`echo -e "$ENCS" | python prev.py $START_TIME $MAC1`
        THIS_ENCOUNTER_COUNT=`echo -e "$ENCS" | ./encounter_count`
        THIS_ENCOUNTER_COUNT_U=`echo -e "$ENCS" | ./encounter_count -u`
        # interpolating with -d will has effect of aligning all trials y-results
        # at same value.  Later on avg_y.py can then be used and results should
        # be monotonically non-decreasing.
        THIS_TRI_RES=`echo -e "$THIS_TRI_RES" | \\
        python interp.py -s 336 -d ${RUNWAY}`
        THIS_ENCOUNTER_COUNT=`echo -e "$THIS_ENCOUNTER_COUNT" | \\
        python interp.py -s 336 -d ${RUNWAY}`
        THIS_ENCOUNTER_COUNT_U=`echo -e "$THIS_ENCOUNTER_COUNT_U" | \\
        python interp.py -s 336 -d ${RUNWAY}`
        TRI_RES+=${THIS_TRI_RES}
        TRI_RES+="\n"
        ONE_DAY_PREVS_PLOT_INPUT+=`echo -e "$THIS_TRI_RES" | \\
        python prev_at_time.py 86400 --single-sample`
        ONE_DAY_PREVS_PLOT_INPUT+="\n"
        E_TRI_RES+=${THIS_ENCOUNTER_COUNT}
        E_TRI_RES+="\n"
        E_TRI_RES_U+=${THIS_ENCOUNTER_COUNT_U}
        E_TRI_RES_U+="\n"
        ((SEED++))
    done
    
    # prevalence and encounter count y-values
    P_YS=`echo -e -n "$TRI_RES" | python avg_y.py | cut -f 1,2 -d ,`
    E_YS=`echo -e -n "$E_TRI_RES" | python avg_y.py | cut -f 1,2 -d ,`
    E_V_P=`paste -d , <(echo -e "$E_YS" | cut -f 2 -d ,) \\
    <(echo -e "$P_YS" | cut -f 2 -d ,)`
    E_PLOT_INPUT+=`echo -e "$E_V_P"`
    E_PLOT_INPUT+="\n"

    E_YS_U=`echo -e -n "$E_TRI_RES_U" | python avg_y.py | cut -f 1,2 -d ,`
    E_V_P_U=`paste -d , <(echo -e "$E_YS_U" | cut -f 2 -d ,) \\
    <(echo -e "$P_YS" | cut -f 2 -d ,)`

    E_PLOT_INPUT_U+=`echo -e "$E_V_P_U"`
    E_PLOT_INPUT_U+="\n"

    PREV_ONE_DAY+=`echo -e "${n} "`
    PREV_ONE_DAY+=`echo -e -n "$TRI_RES" | python stat_y.py -s avg -s sem | \\
    python prev_at_time.py 86400`
    PREV_ONE_DAY+="\n"
    
    PLOT_INPUT+=`echo -e -n "$TRI_RES" | python avg_y.py | cut -f 1,2 -d ,`
    PLOT_INPUT+="\n"

    SEM_PLOT_INPUT+=`echo -e -n "$TRI_RES" | python stat_y.py -s avg -s sem`
    SEM_PLOT_INPUT+="\n"
done
# Plot PDF of prevalences at one day.
BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_one_day_prevalences_pdf_lcc_${LCC}"
echo -e -n "$ONE_DAY_PREVS_PLOT_INPUT" | python hp.py \
-x "Prevalence at one day" -y "Number of trials" -s "${BASE_FILE_NAME}.pdf"
pdf_to_eps "${BASE_FILE_NAME}"

# Plot total and unique encounter ECDF.
BASE_FILE_NAME="${OUT_DIR}/figs/contacts_per_node_ecdf_total_lcc_${LCC}"
echo -e -n "$ENQ_FREQ_ECDF_PLOT_INPUT" | python lp.py \
-x "Total contacts per node" -y "\$P(x \le X)\$" -s "${BASE_FILE_NAME}.pdf" \
--log-x --mark-every=500 -a 0.4 --steps
pdf_to_eps "${BASE_FILE_NAME}"

BASE_FILE_NAME="${OUT_DIR}/figs/contacts_per_node_ecdf_uniq_lcc_${LCC}"
echo -e -n "$ENQ_FREQ_ECDF_PLOT_INPUT_U" | python lp.py \
-x "Unique contacts per node" -y "\$P(x \le X)\$" -s "${BASE_FILE_NAME}.pdf" \
--log-x --mark-every=500 -a 0.4 --steps
pdf_to_eps "${BASE_FILE_NAME}"

# Plot unique locations per node ECDF.
BASE_FILE_NAME="${OUT_DIR}/figs/locations_per_node_ecdf_lcc_${LCC}"
echo -e -n "$LOC_ECDF_PER_NODE_PLOT_INPUT" | python lp.py \
--log-x --steps --mark-every=5000 -a 0.4 \
-x "Unique locations visited" -y "\$P(x \le X)\$" -s "${BASE_FILE_NAME}.pdf"
pdf_to_eps "${BASE_FILE_NAME}"

# Plot intersession time ECDF.
BASE_FILE_NAME="${OUT_DIR}/figs/intersession_time_ecdf_lcc_${LCC}"
echo -e -n "$INTERSESS_ECDF_PLOT_INPUT" | python lp.py \
--log-x --steps --mark-every=5000 -a 0.4 -x "Intersession Time (minutes)" \
-y "\$P(x \le X)\$" -s "${BASE_FILE_NAME}.pdf"
pdf_to_eps "${BASE_FILE_NAME}"

# this doesn't get automatically injected into the latex manuscript, but
# rather the values are manually copied over.
echo -e -n "$PREV_ONE_DAY" > ./tmp/${TRIALS}_trials_prev_one_day_lcc_${LCC}.txt


##SSR stands for Session Shuffling and Randomization
BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_SSR_prev_vs_time_lcc_${LCC}"
echo -e -n "$PLOT_INPUT" | python lp.py -x "\$t\$ (in days)" \
-y "\$|I(t)|/N\$" -s "${BASE_FILE_NAME}.pdf" -c
pdf_to_eps "${BASE_FILE_NAME}"

BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_SSR_prev_vs_contacts_total_lcc_${LCC}"
echo -e -n "$E_PLOT_INPUT" | python lp.py -x "Num. Total Contacts" \
-y "\$|I(t)|/N\$" -s "${BASE_FILE_NAME}.pdf"
pdf_to_eps "${BASE_FILE_NAME}"

# 900,000 is hard-coded based on the non-unique max.  could be smarter but isn't.
BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_SSR_prev_vs_contacts_unique_lcc_${LCC}"
echo -e -n "$E_PLOT_INPUT_U" | python lp.py -x "Num. Unique Contacts" \
-y "\$|I(t)|/N\$" -s "${BASE_FILE_NAME}.pdf" --max-x 900000
pdf_to_eps "${BASE_FILE_NAME}"

BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_SSR_prev_delta_sem_pairs_lcc_${LCC}"
echo -e -n "$SEM_PLOT_INPUT" | python delta_and_error_trellis.py \
--x-title "Reference Prevalence (\$R\$)" \
--y-title "Comparison Prevalence (\$C\$) \$- R\$" -s "${BASE_FILE_NAME}.pdf"
pdf_to_eps "${BASE_FILE_NAME}"

# plot with y-zoomed.  0.015 proves a good zoom in practice with many trials.
ABS_LIM=0.015
BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_SSR_prev_delta_sem_pairs_lcc_${LCC}_abs_lim_${ABS_LIM}"
echo -e -n "$SEM_PLOT_INPUT" | python delta_and_error_trellis.py \
--x-title "Reference Prevalence (\$R\$)" \
--y-title "Comparison Prevalence (\$C\$) \$- R\$" -s "${BASE_FILE_NAME}.pdf" \
--y-abs-limit ${ABS_LIM}
pdf_to_eps "${BASE_FILE_NAME}"

##############################################################
# Contact frequency under *session* shuffling/randomization. #
##############################################################
echo -e "Calculating contact frequency for session shuffling/randomization..."
#UNIQUE_FLAGS=("none" "-u")
declare -A UNIQUE_FLAG_LEGEND
# (T)otal, (U)nique
PLOT_INPUT_T=""
PLOT_INPUT_U=""
# 14 days simulation time in seconds.
SIM_TIME=`echo -e "14 * 24 * 60 * 60" | bc`
for n in ${SESS_SHUFF_FLAGS[@]}; do
    echo -e "Processing contact count for shuffle ${SESS_SHUFF_FLAG_LEGEND[${n}]}..."
    SEED=1000
    PLOT_INPUT_U+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    PLOT_INPUT_T+="${SESS_SHUFF_FLAG_LEGEND[${n}]}\n"
    TALLY_U=""
    TALLY_T=""
    for i in $(seq 0 `expr $TRIALS - 1`); do
        if [[ $n == "Original" ]]; then
            SESSNS=`echo -e "$DATA"`
        else
            SESSNS=`echo -e "$DATA" | ./session_shuffle -s $SEED $n`
        fi
        ENCOUNTERS=`echo -e "$SESSNS" | ./sessions_to_encounters \\
        | cut -f 1,2,3 -d ,`
        TALLY_U+=`echo -e "$ENCOUNTERS" | ./encounter_count -u\\
        | python interp.py -s 336 -d ${SIM_TIME}`
        TALLY_U+="\n"
        TALLY_T+=`echo -e "$ENCOUNTERS" | ./encounter_count \\
        | python interp.py -s 336 -d ${SIM_TIME}`
        TALLY_T+="\n"
        ((SEED++))
    done
    PLOT_INPUT_U+=`echo -e -n "$TALLY_U" | python avg_y.py | cut -f 1,2 -d ,`
    PLOT_INPUT_U+="\n"
    PLOT_INPUT_T+=`echo -e -n "$TALLY_T" | python avg_y.py | cut -f 1,2 -d ,`
    PLOT_INPUT_T+="\n"
done
BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_SSR_contact_count_vs_time_total"
echo -e -n "$PLOT_INPUT_T" | python lp.py -x "\$t\$ (days)" \
-y "Total contact pairs" -l "upper left" -c -s "${BASE_FILE_NAME}.pdf"
pdf_to_eps "${BASE_FILE_NAME}"

# hardcoded 1400000 to scale to same as total contacts
BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_SSR_contact_count_vs_time_unique"
echo -e -n "$PLOT_INPUT_U" | python lp.py -x "\$t\$ (days)" \
-y "Unique contact pairs" -l "upper left" --max-y 1400000 \
-c -s "${BASE_FILE_NAME}.pdf"
pdf_to_eps "${BASE_FILE_NAME}"

#####################################################
# St Lucia prevalence under SBSW contact shuffling. #
#####################################################
echo -e "Generating contact-shuffled St Lucia diffusion..."
SHUFFLES=(Original DCWB DCB DCW D)
COLORS=(\#ED2024 \#0B8040 \#15BCBC \#3852A4 \#BCBE32)
MARKERS=(o d \^ s v)
# 10 days simulation runway, in seconds.
RUNWAY=`echo -e "10 * 24 * 60 * 60" | bc`
ENCOUNTERS=`echo -e "$DATA" | ./sessions_to_encounters`
PLOT_INPUT=""
PREVALENCE_THRES=0.5
SHUFF_INDEX=0
for n in ${SHUFFLES[@]}; do
    SEED=1000
    echo -e "Processing prevalence for shuffle ${n}..."
    TRELLIS_INPUT+="${n},,,${COLORS[$SHUFF_INDEX]}\n"
    # shuffle according to one of Small But Slow Worlds methods.  
    SHUF_ENCS=`echo -e "$ENCOUNTERS" | cut -f 1,2,3 -d , | \\
    python SBSW_shuffle.py ${n}`
    FIRST_ENC_TIME=`echo -e "$SHUF_ENCS" | awk -F ',' 'NR == 1 || \\
    $3 < min {min = $3}END{print min}'`
    LAST_ENC_TIME=`echo -e "$SHUF_ENCS" | awk -F ',' 'NR == 1 || \\
    $3 > max {max = $3}END{print max}'`
    # the latest time a source encounter should be selected to ensure
    # $RUNWAY of simulation time.
    SOURCE_CUTOFF=`echo -e "${LAST_ENC_TIME} - ${RUNWAY}" | bc`
    # source encounter event should be prior to the cutoff time
    CAND_SOURCE_ENCS=`echo -e "$SHUF_ENCS" | \\
    awk -v first=$FIRST_ENC_TIME -v last=$SOURCE_CUTOFF -F ',' '$3 >= first && $3 < last'`
    TRI_RES="" # Trial results.
    for i in $(seq 0 `expr $TRIALS - 1`); do
        have_source=false
        while [ "$have_source" = false ];do
            MAC_MAC_TIME=`echo -e "$CAND_SOURCE_ENCS" | \\
            python rand_encounter.py -s $SEED`
            MAC1=`echo -e "$MAC_MAC_TIME" | cut -f 1 -d ,`
            MAC2=`echo -e "$MAC_MAC_TIME" | cut -f 2 -d ,`
            START_TIME=`echo -e "$MAC_MAC_TIME" | cut -f 3 -d ,`
            END_TIME=`echo -e "${START_TIME} + ${RUNWAY}" | bc`
            # ENCS should represent the 10-day encounter period starting at the
            # randomly sampled start event.  i.e. encounters prior to start event
            # and after 10 days subsequent should be discarded.
            ENCS=`echo -e "$SHUF_ENCS" | \\
            awk -v start_time=$START_TIME -v end_time=$END_TIME -F ',' \\
            '$3 >= start_time && $3 <= end_time'`
            if [ "$LCC" = true ]; then
                ENCS=`echo -e "$ENCS" | python cc.py`
                # recall 0 = true in a bash if statement like this
                if ! echo -e "$ENCS" | cut -f 1 -d , | \
                awk -v mac=$MAC1 -F ',' '{if ($1 == mac) {found_mac = 1; exit 0;}} \
                END {if (found_mac) exit 0; else exit 1;}'; then
                    echo -e "WARNING: Source MAC not in LCC so resampling."
                    ((SEED++))
                else
                    # all good -- chosen source belongs to LCC
                    have_source=true
                fi
            else
                # if not restricting ourselves to LCC then don't need to
                # verify LCC membership.
                have_source=true
            fi
        done
        THIS_TRI_RES=`echo -e "$ENCS" | \\
        python prev.py $START_TIME $MAC1`
        # interpolating with -d will has effect of aligning all trials y-results
        # at same value.  Later on avg_y.py can then be used and results should
        # be monotonically non-decreasing.
        THIS_TRI_RES=`echo -e "$THIS_TRI_RES" | \\
        python interp.py -s 336 -d ${RUNWAY}`
        TRI_RES+=${THIS_TRI_RES}
        TRI_RES+="\n"
        ((SEED++))
    done
    # label and color
    PLOT_INPUT+="${n},,,${COLORS[$SHUFF_INDEX]},${MARKERS[$SHUFF_INDEX]}\n"
    PLOT_INPUT+=`echo -e -n "$TRI_RES" | python avg_y.py | cut -f 1,2 -d ,`
    PLOT_INPUT+="\n"
    # MUST pre-increment.  See http://stackoverflow.com/q/7247279/129475
    ((++SHUFF_INDEX))
done
BASE_FILE_NAME="${OUT_DIR}/figs/${TRIALS}_trials_SBSW_prev_vs_time_lcc_${LCC}"
# TODO: come up with a cleaner fix for removing the nans induced by not being
# able to linearly interpolate at time zero point zero.
echo -e -n "$PLOT_INPUT" | awk -F ',' '$2 != "nan"' | \
python lp.py -x "\$t\$ (in days)" -y "\$|I(t)|/N\$" -s "${BASE_FILE_NAME}.pdf" -c
pdf_to_eps "${BASE_FILE_NAME}"

IFS="$saveIFS"
