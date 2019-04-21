# Minio variables
export MINIO_URL=localhost;
export MINIO_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE;
export MINIO_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY;
export MINIO_OUTPUT_BUCKET_NAME=investigator-rpa-output;
# Google Sheets Document ID
export GSHEET_ID=1pBecz5Db9eK0QDR_oePmamdaFtEiCaO69RaE-Ozduko;

# Instantiate enviornment variables
source env-vars.sh
# Install reqs
python setup.py install
# Get geckodriver
python -c "from pybotlib.utils import get_geckodriver; get_geckodriver()"
# Run the RPA
python ./examples/investigator_RPA.py
# Clean up
rm geckodriver
