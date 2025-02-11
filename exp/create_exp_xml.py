#!/usr/bin/env python3
import sys
import argparse
from lxml import etree

"""
Usage: create_exp_lxml.py [-h] -i INPUT

Convert an `exp.tsv` file into an `exp.xml` file with the required structure for submitting an experiment metadata object to ENA.
Note: The sample metadata object must be submitted before running this script.

Options:
  -h, --help            Help message
  -i INPUT, --input INPUT
                        Specify the path to the input TSV file containing experimental data.
                        The file must include all required fields for generating the experiment metadata XML.

# CHECK LIST: fill these fields

    # center_name
    # study_ref.attrib["accession"] = "PRJxxxxxx"
    # (experiment, "TITLE").text = ""
    # "LIBRARY_STRATEGY".text : "AMPLICON"
    # "LIBRARY_SOURCE".text : "VIRAL RNA"
    # "LIBRARY_SELECTION".text : "PCR"
    # "LIBRARY_LAYOUT": "SINGLE"
    # "PLATFORM" : "OXFORD_NANOPORE" / "ILLUMINA"
    # "INSTRUMENT_MODEL" : "MinION" / "GridION"

"""

# Helper function to create an EXPERIMENT_ATTRIBUTE
def create_experiment_attribute(parent, tag, value):
    """
    Create an EXPERIMENT_ATTRIBUTE XML element.
    """
    experiment_attr = etree.SubElement(parent, "EXPERIMENT_ATTRIBUTE")
    etree.SubElement(experiment_attr, "TAG").text = tag
    etree.SubElement(experiment_attr, "VALUE").text = value

def tsv2XML(tsvInFile, xmlOutFile):
    """
    Convert a TSV file into an XML file with the required structure.
    """
    root = etree.Element("EXPERIMENT_SET")
    line_counter = 0  # Total lines processed
    skipped_lines= 0   # Number of skipped lines (header, errors, or incomplete data)

    try:
        with open(tsvInFile, 'r') as f:
            for line in f:
                line_counter += 1
                line = line.strip()

                # skip empty or malformed lines (not exactly 4 tab-separated values)
                if not line or len(line.split('\t')) != 4:
                    print(f"Warning: Skipping malformed or incomplete line {line_counter}.")
                    skipped_lines+= 1
                    continue

                # skip lines containing "alias" (header or irrelevant)
                if "alias" in line:
                    skipped_lines+=1
                    continue

                try:
                    # Extract required values from TSV (expecting exactly 4 tab-separated fields)
                    samAlias, expAlias, _, _, = line.split('\t')

                    # Check if any of the unpacked values is an empty string
                    # Ensure no empty values in required fields
                    if not all([samAlias, expAlias]):
                    #if any(value == "" for value in [samAlias, expAlias, platform_name]):
                        print(f"Warning: Line {line_counter} contains empty values. Skipping.")
                        skipped_lines+= 1
                        continue

                except ValueError:
                    print(f"Warning: Line {line_counter} does not have the expected 4 tab-separated values. Skipping.")
                    skipped_lines+= 1
                    continue

                # Create EXPERIMENT element
                experiment = etree.SubElement(root, "EXPERIMENT", {
                    "alias": expAlias,
                    "center_name": "Dutch COVID-19 response team"})

                # Add TITLE element: short title for each experiment
                etree.SubElement(experiment, "TITLE").text = (f"GridION sequencing")

                # Add STUDY_REF element: accession to the ENA study
                study_ref = etree.SubElement(experiment, "STUDY_REF")
                study_ref.attrib["accession"] = "PRJEB39014"

                # Add DESIGN element: alias to the sample metadata
                design = etree.SubElement(experiment, "DESIGN")
                etree.SubElement(design, "DESIGN_DESCRIPTION").text = ""
                sample_descriptor = etree.SubElement(design, "SAMPLE_DESCRIPTOR")
                sample_descriptor.attrib["refname"] = samAlias

                # Add LIBRARY_DESCRIPTOR element: describe the library
                library_descriptor = etree.SubElement(design, "LIBRARY_DESCRIPTOR")
                etree.SubElement(library_descriptor, "LIBRARY_NAME").text = ""
                etree.SubElement(library_descriptor, "LIBRARY_STRATEGY").text = "AMPLICON"
                etree.SubElement(library_descriptor, "LIBRARY_SOURCE").text = "VIRAL RNA"
                etree.SubElement(library_descriptor, "LIBRARY_SELECTION").text = "PCR"
                library_layout = etree.SubElement(library_descriptor, "LIBRARY_LAYOUT")
                etree.SubElement(library_layout, "SINGLE")

                # Add PLATFORM and INSTRUMENT_MODEL elements
                platform_element = etree.SubElement(experiment, "PLATFORM")
                oxford_nanopore = etree.SubElement(platform_element, "OXFORD_NANOPORE")
                etree.SubElement(oxford_nanopore, "INSTRUMENT_MODEL").text = "GridION"

                # Add other EXPERIMENT_ATTRIBUTES
                experiment_attributes = etree.SubElement(experiment, "EXPERIMENT_ATTRIBUTES")
                create_experiment_attribute(experiment_attributes, "library preparation date", "not collected")


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
        description="Convert a `exp.tsv` file into an `exp.xml` file with the required structure for submitting an experiment metadata object to ENA."
                    "Note: The sample metadata object must be submitted before running this script."
    )
    parser.add_argument(
        "-i", "--input",
        help="Specify the path to the input TSV file containing experiment metadata. "
             "The file must include all required fields for generating the experiment metadata XML.",
        default="exp.tsv"
    )

    # Parse arguments
    args = parser.parse_args()
    inFile = args.input  # Input file name
    outFile = 'exp.xml'  # Output file name

    # Execute the TSV to XML conversion
    try:
        written_lines = tsv2XML(inFile, outFile)
        print(f"\n{written_lines} experiment_objects successfully written to '{outFile}'.")
    except FileNotFoundError:
        print(f"Error: The input file '{inFile}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
