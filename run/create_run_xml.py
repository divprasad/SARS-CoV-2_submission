#!/usr/bin/env python3
import sys
import argparse
from lxml import etree

"""
Usage: create_run_lxml.py [-h] [-i INPUT]

Convert a `run.tsv` file into a `run.xml` file with the required structure for submitting a run metadata object to ENA.
Note: The sample metadata object must be submitted before running this script.

Options:
  -h, --help            Help message.
  -i INPUT, --input INPUT
                        Specify the path to the input TSV file containing experimental data.
                        The file must include all required fields for generating the experiment metadata XML.

# CHECK LIST: fill these fields

    # "center_name"
    # "filetype": "fastq"
    # "checksum_method": "MD5"

"""

# Helper function to create an RUN_ATTRIBUTE
def create_run_attribute(parent, tag, value):
    """
    Create a RUN_ATTRIBUTE XML element.
    """
    run_attr = etree.SubElement(parent, "RUN_ATTRIBUTE")
    etree.SubElement(run_attr, "TAG").text = tag
    etree.SubElement(run_attr, "VALUE").text = value

def tsv2XML(tsvInFile, xmlOutFile):
    """
    Convert a TSV file into an XML file with the required structure.
    """
    root = etree.Element("RUN_SET")
    line_counter = 0  # Total lines processed
    skipped_lines= 0   # Number of skipped lines (header, errors, or incomplete data)

    try:
        with open(tsvInFile, 'r') as f:
            for line in f:
                line_counter += 1
                line = line.strip()

                # skip empty or malformed lines (not exactly 5 tab-separated values)
                if not line or len(line.split('\t')) != 5:
                    print(f"Warning: Skipping malformed or incomplete line {line_counter}.")
                    skipped_lines+= 1
                    continue

                # skip lines containing "alias" (header or irrelevant)
                if "alias" in line:
                    skipped_lines+= 1
                    continue

                try:
                    # Extract required values from TSV (expecting exactly 5 tab-separated fields)
                    samAlias, expAlias, gzFile, md5, _ = line.split('\t')

                    # Ensure no empty values in required fields
                    if not all([samAlias, expAlias, gzFile, md5]):
                        print(f"Warning: Line {line_counter} contains empty values. Skipping.")
                        skipped_lines+= 1
                        continue

                except ValueError:
                    print(f"Warning: Line {line_counter} does not contain exactly 5 tab-separated values. Skipping.")
                    skipped_lines+= 1
                    continue

                # Create RUN element
                run = etree.SubElement(root, "RUN", {
                    "alias": samAlias,
                    "center_name": "Dutch COVID-19 response team"
                })

                # Add EXPERIMENT_REF
                experiment_ref = etree.SubElement(run, "EXPERIMENT_REF")
                experiment_ref.attrib["refname"] = expAlias

                # Add DATA_BLOCK
                data_block = etree.SubElement(run, "DATA_BLOCK")
                files = etree.SubElement(data_block, "FILES")

                file_elem = etree.SubElement(files, "FILE", {
                    "filename": gzFile,
                    "filetype": "fastq",
                    "checksum_method": "MD5",
                    "checksum": md5
                })

                # # Add RUN_ATTRIBUTES
                # run_attributes = etree.SubElement(run, "RUN_ATTRIBUTES")
                # create_run_attribute(run_attributes, "processing center", "Dutch Genomics Institute")
                # create_run_attribute(run_attributes, "sequencing platform", "Oxford Nanopore GridION")


    except FileNotFoundError:
        print(f"Error: The file '{tsvInFile}' does not exist.")
        sys.exit(1)

    # Format and write the XML to file using lxml
    tree = etree.ElementTree(root)
    with open(xmlOutFile, 'wb') as file:
        tree.write(file, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    written = line_counter - skipped_lines
    return written

# Main execution
if __name__ == '__main__':

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Convert a `run.tsv` file into a `run.xml` file with the required structure for submitting a run metadata object to ENA."
                    "Note: The sample metadata object must be submitted before running this script."
    )
    parser.add_argument(
        "-i", "--input",
        help="Specify the path to the input TSV file containing run metadata. "
             "The file must include all required fields for generating the run metadata XML.",
        default="run.tsv"
    )

    # Parse arguments
    args = parser.parse_args()
    inFile = args.input  # Input file name
    outFile = "run.xml"  # Output file name

    # Execute the TSV to XML conversion
    try:
        written_lines = tsv2XML(inFile, outFile)
        print(f"\n{written_lines} run_objects successfully written to '{outFile}'.")
    except FileNotFoundError:
        print(f"Error: The input file '{inFile}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
