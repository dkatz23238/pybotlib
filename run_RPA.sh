# Instantiate enviornment variables
source env-vars.sh
# Get firefox geckodriver
bash get_geckodriver.sh
# Install reqs
python -m pip install -r requirements.txt
# Run the RPA
python investigator_RPA.py
# Clean up
rm geckodriver
rm *.pyc
