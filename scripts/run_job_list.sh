#!/bin/bash

#SBATCH --job-name=cp-outcome
#SBATCH --partition=hpg-milan
#SBATCH --account=akazachkov
#SBATCH --qos=akazachkov
#SBATCH --nodes=1                    # Use one node
#SBATCH --exclusive=user             # Nobody else can use this node
#SBATCH --ntasks=1                   # Number of tasks to run
#SBATCH --cpus-per-task=1            # Number of CPU cores per task
#SBATCH --mem=7.8gb                  # Total memory limit
#SBATCH --time=4-00:00:00            # Time limit
#SBATCH --array=1-6420

##SBATCH --output=/blue/akazachkov/ambareesh.vaidya/cp_outcome/paper_log/output_%a-%A.log
##SBATCH --output=slurm_log/output_%a-%A.log
#SBATCH --output=slurm_%x_%A-%a.log  # standard output log (%x = job name, %A = job id, %a = array index)
#SBATCH --mail-type=END,FAIL         # mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=ambareesh.vaidya@ufl.edu

#########################
## To run this script, call (for example)
##     sbatch run_job_list.sh [job list file]
## See arguments below
echo "=== START SLURM SCRIPT MESSAGES ==="
pwd; hostname; date

#########################
## Constants
PROJ_DIR="/home/ambareesh.vaidya/repos/cp_outcome"
CASE_NUM=`printf %04d $SLURM_ARRAY_TASK_ID`
DATESTUB=`date +%F`
RESULTS_DIR="/blue/akazachkov/ambareesh.vaidya/cp_outcome/paper/results/$DATESTUB"

#########################
## Arguments
# Argument 1: JOB_LIST Set command file if given
if [ ! -z $1 ]
then
  JOB_LIST=$1
else
  JOB_LIST="${PROJ_DIR}/data/job_list.txt"
fi

#########################
## Modules
module load conda
conda activate python38

#########################
## Prepare run command
echo ""
echo "Starting ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
CMD=$(sed -n "${SLURM_ARRAY_TASK_ID}p" ${JOB_LIST})

echo ""
echo -e "Calling:\n$CMD"
echo "=== START JOB ==="
echo ""

#########################
## RUN COMMAND HERE
eval $CMD

#########################
## END JOB
echo "=== END JOB ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID} `date` =="
