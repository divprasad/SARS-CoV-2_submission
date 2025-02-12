#!/bin/bash

# make-submit-xml.sh - Script to generate and submit ENA XML files

# READ THE DOCS!
# https://ena-docs.readthedocs.io/en/latest/submit/reads/programmatic.html
# https://ena-docs.readthedocs.io/en/latest/update/metadata.html

# Function to display usage message
usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options:
  -t    Run in test mode (default)
  -s    Run in submission mode
  -h    Display this help message

This script generates and submits XML files to ENA.
Use -t for testing and -s for actual submission.
EOF
}

# Ensure only valid options (-t, -s, -h) are accepted
while getopts ":tsh" opt; do
  case $opt in
    t) mode="test" ;;      # Test mode
    s) mode="submission" ;; # Submission mode
    h) usage; exit 0 ;;     # Help flag
    \?) usage; exit 1 ;;    # Invalid flag
  esac
done

# Exit immediately if a command fails
set -e

# Check if credentials are set, otherwise ask the user
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

# Confirm submission mode with the user
echo ""
read -p "Continue in (default) TEST mode? (Y/n): " user_choice
user_choice=${user_choice:-Y}  # Default to "Y" if the user presses Enter

# Determine mode based on user input
if [[ "$user_choice" =~ ^[Nn]$ ]]; then
  mode="submit"
  #echo "Running in SUBMISSION mode"
else
  mode="test"
  #echo "Running in TEST mode (default)"
fi

# Set URL based on mode
url="$test_url"
[[ "$mode" == "submit" ]] && url="$submit_url"

echo "----------------------------------------------------------------------------------"
echo "  📂 Running in $mode mode"
echo "  📤 Using submission URL: $url"
echo "----------------------------------------------------------------------------------"

### PROCESS SAMPLE SUBMISSION ###
cd samSubmit
echo ""
date
echo "  🔄 Generating sample XML..."
python3 create_sam_xml.py
echo "  ✅ Created sam.xml"
echo ""
date

echo "  🚀 Submitting sample XML..."
rm -f *samLog.txt

# Uncomment based on requirement:
# Submit new metadata objects:
# curl -u "$U_NAME:$PASS_WORD" -F "SUBMISSION=@add_submission.xml" -F "SAMPLE=@sam.xml" "$url" >> submit_samLog.txt 2>&1

# Update existing metadata objects:
# curl -u "$U_NAME:$PASS_WORD" -F "SUBMISSION=@modify_submission.xml" -F "SAMPLE=@sam.xml" "$url" >> modify_samLog.txt 2>&1

echo "  ✅ Submitted sam.xml"
echo ""
date

### PROCESS EXPERIMENT SUBMISSION ###
cd ../exp
echo "  🔄 Generating experiment XML..."
python3 create_exp_xml.py
cp exp.xml ../runExpSubmit/
echo "  ✅ Created exp.xml"
echo ""
date

### PROCESS RUN SUBMISSION ###
cd ../run
echo "  🔄 Generating run XML..."
python3 create_run_xml.py
cp run.xml ../runExpSubmit/
echo "  ✅ Created run.xml"
echo ""
date

### SUBMIT EXPERIMENT AND RUN DATA ###
cd ../runExpSubmit/
echo "  🚀 Submitting experiment and run XML..."
rm -f *runExpLog.txt

# Uncomment based on requirement:
# Submit new metadata objects:
# curl -u "$U_NAME:$PASS_WORD" -F "SUBMISSION=@add_submission.xml" -F "RUN=@run.xml" -F "EXPERIMENT=@exp.xml" "$url" >> submit_runExpLog.txt 2>&1

# Update existing metadata objects:
# curl -u "$U_NAME:$PASS_WORD" -F "SUBMISSION=@modify_submission.xml" -F "RUN=@run.xml" -F "EXPERIMENT=@exp.xml" "$url" >> modify_runExpLog.txt 2>&1

echo "  ✅ Submitted run.xml and exp.xml"
echo ""
date

echo "  🎉 Process completed successfully!"
