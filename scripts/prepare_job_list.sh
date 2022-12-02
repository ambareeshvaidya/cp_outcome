#!/bin/bash

PROJ_DIR="/home/ambareesh.vaidya/repos/cp_outcome"
CUTS="0 1"
RANDOM_SEED="2 4 8 16 32"
TYPE="solved"
if [ ! -z $1 ]; then
  INSTANCE_FILE=$1
else
  INSTANCE_FILE="${PROJ_DIR}/data/${TYPE}.instances"  
fi

DATESTUB=`date +%F`
TASK_ID=4260
NUM_DIGITS=4
while read INST; do
  for CUT_MODE in $CUTS; do 
    for SEED in $RANDOM_SEED; do
      TASK_ID=$((TASK_ID+1))
      CASE_NUM=`printf %0${NUM_DIGITS}d $TASK_ID`

      RESULTS_DIR="/blue/akazachkov/ambareesh.vaidya/cp_outcome/paper/results/${DATESTUB}/cut_${CUT_MODE}/seed_${SEED}/${CASE_NUM}"
      echo -n "mkdir -p ${RESULTS_DIR}; "
  
      FILE="/home/ambareesh.vaidya/miplib2017/${INST}"


      echo "python ${PROJ_DIR}/src/fullrun_new.py --instance ${FILE} --cuts ${CUT_MODE} --seed ${SEED} --results_path=${RESULTS_DIR}"
    done # loop over RANDOM_SEED
  done # loop over CUTS
done < ${INSTANCE_FILE}
