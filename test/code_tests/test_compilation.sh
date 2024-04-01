#!/usr/bin/bash


function get_free_filename {
  IFS="/" read -r _ filename <<< "$1"
  IFS="." read -r filename_free _ <<< "$filename"
  echo $filename_free
}

function get_result_filename() {
  result_file="result_files/"
  result_file+=$1
  result_file+=".txt"
  echo $result_file
}

function get_executable_command() {
  executable="./"
  executable+=$1
  executable+=" - >&1"
  echo $executable
}

function test_one_case() {
  filename_free=$(get_free_filename $1)
  result_file=$(get_result_filename $filename_free)
  _=$(python ../../main.py "$file" "$filename_free" -d)
  executable=$(get_executable_command $filename_free)
  run_result=$($executable)
  actual_result=$(<$result_file)
  if [[ "$run_result" == "$actual_result" ]]; then
    echo -e "    \033[92mSUCCESS\033[0m"
    return 0
  else
    echo -e "    \033[91m FAILED - missmatch: \033[0m"
    echo "expected - ${actual_result}"
    echo "got - ${run_result}"
    return 1
  fi
}

function cleanup() {
  filename_free=$(get_free_filename $1)
  filename_free+="*"
  rm -rf $filename_free
}

SUCCESS=0
FAILED=0

echo -e "\033[96mStarting testing session...\033[0m"
for file in python_files/*.py; do
  echo -e "    \033[96mchecking file $file...\033[0m"
  test_one_case $file
  cleanup $file
  status=$?
  if [[ $status == 1 ]]; then
      FAILED=$(($FAILED+1))
  elif [[ $status == 0 ]]; then
      SUCCESS=$(($SUCCESS+1))
  fi
done
echo -e "\033[96mTesting session finished\033[0m"
echo -e "    \033[96mSuccessfully finished ${SUCCESS} tests\033[0m"
echo -e "    \033[96mFailed ${FAILED} tests\033[0m"
