#!/usr/bin/env bash
# Arguments: results directory
# Example: ./merge.sh ${VPC_DIR}/scripts/results_test

# The first argument is the (full) directory containing the results or batch folders containing results

# Set the RESULTS_DIR
if [ -z $1 ]; then
  echo "First argument must be results directory."
  exit 1
else
  RESULTS_DIR="$1"
fi

TMPNAME="result.csv"

OUTNAME="${RESULTS_DIR}/${TMPNAME}"
ERR_OUTNAME="${RESULTS_DIR}/errors_${TMPNAME}"

i=0
for batchname in `ls -d ${RESULTS_DIR}/*/`; do
  i=$(( $i + 1 ))  # maintain line count
  if [ $i = 1 ]
   then
     head -n 1 ${batchname}${TMPNAME} > ${OUTNAME}
     head -n 1 ${batchname}${TMPNAME} > ${ERR_OUTNAME}
  fi
  
  echo "Copying ${TMPNAME} from ${batchname} to ${OUTNAME}"
  tail -n +2 ${batchname}${TMPNAME} | grep DONE >> ${OUTNAME}

  echo "Copying errors in ${TMPNAME} from ${batchname} to ${ERR_OUTNAME}"
  tail -n +2 ${batchname}${TMPNAME} | grep "ERROR" >> ${ERR_OUTNAME}
done
