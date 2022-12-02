#!/bin/bash

#SBATCH --job-name=cp_outcome
#SBATCH --partition=hpg-milan
#SBATCH --account=akazachkov
#SBATCH --qos=akazachkov-b
#SBATCH --ntasks=1                   # Number of tasks to run
#SBATCH --cpus-per-task=1            # Number of CPU cores per task
#SBATCH --mem=8gb                  # Total memory limit
#SBATCH --time=06:00:00            # Time limit
#SBATCH --array=1-426

##SBATCH --output=/blue/akazachkov/ambareesh.vaidya/cp_outcome/paper_log/output_%a-%A.log
##SBATCH --output=slurm_log/output_%a-%A.log
#SBATCH --output=slurm_%x_%A-%a.log  # standard output log (%x = job name, %A = job id, %a = array index)
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=ambareesh.vaidya@ufl.edu

pwd; hostname; date

#########################
## Arguments
if [ -z $1 ]; then
  #CUTS="0 1"
  CUTS="1"
elif [ "$1" = 0 ]; then
  CUTS="0"
elif [ "$1" = 1 ]; then
  CUTS="1"
elif [ "$1" = 2 ]; then
  CUTS="0 1"
else
  echo "First argument must be a 0 (cuts off), a 1 (cuts on), a 2 (both), or empty (default cuts on)."
  exit 1
fi

if [ -z $2 ]; then
  #RANDOM_SEED="2 4 8 16 32"
  RANDOM_SEED="2"
elif [ "$2" = 1 ]; then
  RANDOM_SEED="2"
elif [ "$2" = 2 ]; then
  RANDOM_SEED="2 4"
elif [ "$2" = 3 ]; then
  RANDOM_SEED="2 4 8"
elif [ "$2" = 4 ]; then
  RANDOM_SEED="2 4 8 16"
elif [ "$2" = 5 ]; then
  RANDOM_SEED="2 4 8 16 32"
else
  echo "Second argument must be a 1 (one random seed), a 2 (two random seeds), a 3 (three random seeds), a 4 (four random seeds), a 5 (five random seeds) or empty (default random seeds equals to 1)."
  exit 1
fi

#########################
## Constants
PROJ_DIR="/home/ambareesh.vaidya/repos/cp_outcome"
TYPE="solved"
INSTANCE_FILE="$PROJ_DIR/data/$TYPE.instances"
INSTANCE_DIR="/home/ambareesh.vaidya/miplib2017"
CASE_NUM=`printf %04d $SLURM_ARRAY_TASK_ID`
DATESTUB=`date +%F`
RESULTS_DIR="/blue/akazachkov/ambareesh.vaidya/cp_outcome/paper/results/$DATESTUB"
EXECUTABLE="${PROJ_DIR}/src/fullrun_new.py"

#########################
## Modules
module load conda
conda activate python38

#########################
## Run code
for CUT_MODE in $CUTS; do 
  for SEED in $RANDOM_SEED; do
    CURR_RESULT_DIR="${RESULTS_DIR}/cut_${CUT_MODE}/seed_${SEED}/${CASE_NUM}"
    mkdir -p $CURR_RESULT_DIR

    INST=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $INSTANCE_FILE)
    FILE="${INSTANCE_DIR}/${INST}"
    	
    echo "`date`"
    echo "Task: ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
    echo "Case: ${CASE_NUM}"
    echo "Instance: ${FILE}"
    echo "Results: ${CURR_RESULT_DIR}"
    echo "Cut mode: ${CUT_MODE}"
    echo "Seed: ${SEED}"

    CMD="python $EXECUTABLE --instance ${FILE} --cuts ${CUT_MODE} --result_path ${RESULT_DIR} --seed ${SEED}"
    echo -e "Calling:\n$CMD"

    echo "=== START JOB `date` ==="
    eval $CMD
    echo "=== END JOB `date` ==="
  done # loop over RANDOM_SEED
done # loop over SEEDS

#########################
## END JOB
echo "End task ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID} at `date`"
