## Overview

This repository is specific for SARS-CoV-2 submission to the European Nucleotide Archive (ENA). It includes scripts and dummy data for converting TSV metadata into the required XML format and submitting sample, experiment, and run metadata objects all in one go.

The wrapper script `make-submit-xml.sh` automates the entire process, including XML generation, submission, and modification of existing ENA metadata objects, using [programmatic ENA submission](https://ena-docs.readthedocs.io/en/latest/submit/reads/programmatic.html).


---

### Installation

Install dependencies:
```
pip install lxml
```


Set environment variables for secure credential handling:
```
export U_NAME="your_username"
export PASS_WORD="your_password"
```

---

**Usage:**

#### Automated submission

```
./make-submit-xml.sh -t  # Run in test mode (default)
./make-submit-xml.sh -s  # Run in submission mode
./make-submit-xml.sh -h  # Display help message
```

`make-submit-xml.sh` integrates all the three subparts of the metadata generation (`create_sam_xml.py`, `create_exp_xml.py` , `create_run_xml.py`) and submits to testing/production service.



**Generate individual XML files:**
```
python3 create_sam_xml.py #converts sam.tsv → sam.xml
python3 create_exp_xml.py #converts exp.tsv → exp.xml
python3 create_run_xml.py #converts run.tsv → run.xml
```

### Repository Structure

After cloning the repo and executing the wrapper `make-submit-xml.sh`, you get this directory structure

```
this_repo
├── make-submit-xml.sh
├── access_file_parser.py       # Parser for access_file
├── exp/                        # Experiment metadata
│   ├── create_exp_xml.py
│   ├── exp.tsv
│   └── exp.xml
├── run/                        # Run metadata
│   ├── create_run_xml.py
│   ├── run.tsv
│   └── run.xml
├── runExpSubmit/               # Combined submission
│   ├── add_submission.xml
│   ├── modify_submission.xml
│   ├── exp.xml
│   └── run.xml
└── samSubmit/                  # Sample metadata
    ├── create_sam_xml.py
    ├── add_submission.xml
    ├── modify_submission.xml
    ├── sam.tsv
    └── sam.xml
```


### Notes  

- Ensure that the sample metadata objects are submitted before submitting the experiment and run metadata objects.
- Ensure that the TSV files include all required fields for metadata XML generation.
