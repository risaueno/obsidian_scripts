#!/bin/bash

######
# [Optional]
# This is an example bash script to create all summary notes in one go
# e.g. you can use a scheduler to run bash this_script.sh every day
# ** Before running: ** Set use_external_input to True in the .py scripts and check the settings below it
######

# Optional specify python environment
eval "$(conda shell.bash hook)"
conda activate py36

# Generate summary tables
declare -a header_list=('Habits' 'Mood')  # Summary tables I want generated
for idx in "${!header_list[@]}"; do
  header_name=${header_list[$idx]}
  python generate_habit_table.py "$header_name"
done

# Generate summary pages
declare -a header_list=( 'To do' 'Morning pages' 'Events' 'Grateful' )  # Summaries I want generated
declare -a transclusion_list=( true true false false )  # Display full transclusion or not for corresponding header
declare -a display_list=( 'dates' 'dates' 'dates' 'bullet' )  # Dates or bullet points

for idx in "${!header_list[@]}"; do
  header_name=${header_list[$idx]}
  display_transclusion=${transclusion_list[$idx]}
  display_type=${display_list[$idx]}
  python generate_header_summary.py "$header_name" "$display_transclusion" "$display_type"
done
