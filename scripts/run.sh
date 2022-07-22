#!/bin/bash

#SBATCH --job-name=cp_outcome
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=ambareesh.vaidya@ufl.edu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --time=22:00:00
#SBATCH --output=/blue/akazachkov/ambareesh.vaidya/cp_outcome/log/output_%A-%a.log
#SBATCH --array=170

pwd; hostname; date

CUTS="1"
if [ "$1" = 0 ]; then
  CUTS="0"
elif [ "$1" = 1 ]; then
  CUTS="1"
elif [ "$1" = 2 ]; then
  CUTS="0 1"
elif [ ! -z $1 ]; then
  echo "First argument must be a 0 (cuts off), a 1 (cuts on), a 2 (both), or empty (default cuts on)."
  exit 1
fi

RANDOM_SEED="2"
if [ "$2" = 1 ]; then
  RANDOM_SEED="2"
elif [ "$2" = 2 ]; then
  RANDOM_SEED="2 4"
elif [ "$2" = 3 ]; then
  RADOM_SEED="2 4 8"
elif [ "$2" = 4 ]; then
  RANDOM_SEED="2 4 8 16"
elif [ "$2" = 5 ]; then
  RADOM_SEED="2 4 8 16 32"
elif [ ! -z $2 ]; then
  echo "Second argument must be a 1 (one random seed), a 2 (two random seeds), a 3 (three random seeds), a 4 (four random seeds), a 5 (five random seeds) or empty (default random seeds equals to 1)."
  exit 1
fi

module load conda
conda activate python38

TYPE="final"
CASE_NUM=`printf %04d $SLURM_ARRAY_TASK_ID`

for i in $CUTS; do 
  CUT_MODE=$i 
  for j in $RANDOM_SEED; do
    SEED=$j 
    
    mkdir -p /blue/akazachkov/ambareesh.vaidya/cp_outcome/results/$(date +"%d-%m-%Y")/cut_${CUT_MODE}/seed_${SEED}/${CASE_NUM}
    INSTANCE_FILE=${TYPE}.instances
    RESULT_DIR="/blue/akazachkov/ambareesh.vaidya/cp_outcome/results/$(date +"%d-%m-%Y")/cut_${CUT_MODE}/seed_${SEED}/${CASE_NUM}"

    echo "Running task ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID} in parallel mode at `date`"
    INST=$(sed -n "${SLURM_ARRAY_TASK_ID}p" /home/ambareesh.vaidya/repos/cp_outcome/data/${INSTANCE_FILE})
    FILE="/home/ambareesh.vaidya/miplib2017/${INST}"
    
    	
    echo ${INST}
    echo ${CASE_NUM}
    echo cut_${CUT_MODE}
    echo seed_${SEED}

    python /home/ambareesh.vaidya/repos/cp_outcome/src/fullrun.py --instance ${FILE} --cuts ${CUT_MODE} --result_path ${RESULT_DIR} --seed ${SEED}

  done
done
