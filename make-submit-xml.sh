#!/bin/bash

# make-submit-xml.sh - Script to generate and submit ENA XML files
#
# Usage:
#   make-submit-xml.sh -t  (Run in test mode, default)
#   make-submit-xml.sh -s  (Run in submission mode)
#   make-submit-xml.sh -h  (Display this help message)

# READ THE DOCS!
# https://ena-docs.readthedocs.io/en/latest/submit/reads/programmatic.html
# https://ena-docs.readthedocs.io/en/latest/update/metadata.html

# Exit immediately if a command fails
set -e


# Check if U_NAME and PASS_WORD are set as environment variables, if not, prompt the user
if [ -z "$U_NAME" ]; then
    read -p "Enter Username: " U_NAME
fi

if [ -z "$PASS_WORD" ]; then
    read -s -p "Enter Password: " PASS_WORD
    echo ""  # Move to a new line after password input
fi

# Define URLs for submission
test_url="https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/"
submit_url="https://www.ebi.ac.uk/ena/submit/drop-box/submit/"

# Function to display usage message
usage() {
  echo "Usage: $0 [-t | -s | -h]"
  echo "  -t    Run in test mode (default)"
  echo "  -s    Run in submission mode"
  echo "  -h    Display this help message"
}

# Display usage message first
echo ""
read -p "Do you want to continue with the default TEST mode? (Y/n): " user_choice
user_choice=${user_choice:-Y}  # Default to "Y" if the user presses Enter

# Determine mode based on user input
if [[ "$user_choice" =~ ^[Nn]$ ]]; then
  mode="submit"
  echo "Running in SUBMISSION mode"
else
  mode="test"
  echo "Running in TEST mode (default)"
fi

# Set appropriate URL
url="$test_url"
[[ "$mode" == "submit" ]] && url="$submit_url"

# Process SAMPLE submission
cd samSubmit
echo "Generating sample XML..."
python3 create_sam_lxml.py
echo "Created sam.xml"
date

echo "Submitting sample XML..."
rm -f *samLog.txt

# For submiting new metadata objects
# curl -u "$U_NAME:$PASS_WORD" -F "SUBMISSION=@add_submission.xml" -F "SAMPLE=@sam.xml" "$url" >> submit_samLog.txt 2>&1

# For updating existing metadata objects
# curl -u "$U_NAME:$PASS_WORD" -F "SUBMISSION=@modify_submission.xml" -F "SAMPLE=@sam.xml" "$url" >> modify_samLog.txt 2>&1
echo "Submitted sam.xml"
date

# Process EXPERIMENT submission
cd ../exp
echo "Generating experiment XML..."
python3 create_exp_lxml.py
cp exp.xml ../runExpSubmit/
echo "Created exp.xml"
date

# Process RUN submission
cd ../run
echo "Generating run XML..."
python3 create_run_lxml.py
cp run.xml ../runExpSubmit/
echo "Created run.xml"
date

# Submit RUN and EXPERIMENT data
cd ../runExpSubmit/
echo "Submitting experiment and run XML..."
rm -f *runExpLog.txt

# For submiting new metadata objects
# curl -u "$U_NAME:$PASS_WORD" -F "SUBMISSION=@add_submission.xml" -F "RUN=@run.xml" -F "EXPERIMENT=@exp.xml" "$url" >> submit_runExpLog.txt 2>&1

# For updating existing metadata objects
# curl -u "$U_NAME:$PASS_WORD" -F "SUBMISSION=@modify_submission.xml" -F "RUN=@run.xml" -F "EXPERIMENT=@exp.xml" "$url" >> modify_runExpLog.txt 2>&1

echo "Submitted run.xml and exp.xml"
date

echo "Process completed successfully!"
