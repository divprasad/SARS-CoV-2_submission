from lxml import etree
import sys
import argparse


"""
Usage: create_sam_lxml.py [-h] -i INPUT

Convert a `sam.tsv` file into a `sam.xml` file with the required structure for submitting a sample metadata object to ENA.

Options:
  -h, --help            Help message.
  -i INPUT, --input INPUT
                        Specify the path to the input TSV file containing sample metadata.
                        The file must include all required fields for generating the sample metadata XML.

# CHECK LIST


"""






# Helper function to create a SAMPLE_ATTRIBUTE
def create_sample_attribute(parent, tag, value, units=None):
    """
    Create a SAMPLE_ATTRIBUTE XML element.
    """
    sample_attr = etree.SubElement(parent, "SAMPLE_ATTRIBUTE")
    etree.SubElement(sample_attr, "TAG").text = tag
    etree.SubElement(sample_attr, "VALUE").text = value
    if units:
        etree.SubElement(sample_attr, "UNITS").text = units

def tsv2XML(tsvInFile, xmlOutFile):
    """
    Convert a TSV file into an XML file with the required structure.
    """
    root = etree.Element("SAMPLE_SET")
    line_counter = 0  # Total lines processed
    skipped_lines= 0   # Number of skipped lines (header, errors, or incomplete data)

    try:
        with open(tsvInFile, 'r') as f:
            for line in f:
                line_counter += 1
                line = line.strip()

                # skip empty or malformed lines (not exactly 16 tab-separated values)
                if not line or len(line.split('\t')) != 16:
                    print(f"Warning: Skipping malformed or incomplete line {line_counter}.")
                    skipped_lines+= 1
                    continue

                # skip lines containing "alias" (header or irrelevant)
                if "alias" in line:
                    skipped_lines+= 1
                    print("Skipping header")
                    continue

                try:
                    # Extract required values from TSV (expecting exactly 16 tab-separated fields)
                    (
                        insdc_acc, sam_title, isolate, date,
                        alias, region, host_sex, host_sc,
                        host_comm, iso_host, lat, long,
                        host_disease_out, host_health_stat, host_sub_id, pub
                    ) = line.split('\t')

                    # Ensure required fields are not empty
                    required_fields = [
                        insdc_acc, sam_title, isolate, date, alias, region, host_sex, host_sc,
                        host_comm, iso_host, lat, long, host_disease_out, host_health_stat, host_sub_id, pub
                    ]
                    if not all(required_fields):
                        print(f"Warning: Line {line_counter} contains empty values. Skipping.")
                        skipped_lines += 1
                        continue

                except ValueError:
                    print(f"Warning: Line {line_counter} does not have the expected 16 tab-separated values. Skipping.")
                    skipped_lines +=1
                    continue

                # Create SAMPLE element
                sample = etree.SubElement(root, "SAMPLE", {"alias": alias, "center_name": "Dutch COVID-19 response team"})

                # Add TITLE
                etree.SubElement(sample, "TITLE").text = sam_title

                # Add SAMPLE_NAME
                sample_name = etree.SubElement(sample, "SAMPLE_NAME")
                etree.SubElement(sample_name, "TAXON_ID").text = "2697049"
                etree.SubElement(sample_name, "SCIENTIFIC_NAME").text = "Severe acute respiratory syndrome coronavirus 2"
                etree.SubElement(sample_name, "COMMON_NAME").text = "Human coronavirus 2019"

                # Add DESCRIPTION
                etree.SubElement(sample, "DESCRIPTION").text = "A SARS-CoV-2 specfic multiplex PCR for Nanopore sequencing was performed, similar to amplicon-based approaches as previously described. In short, primers for 86 overlapping amplicons spanning the entire genome were designed using primal. The amplicon length was set to 500bp with 75bp overlap between the different amplicons. The libraries were generated using the native barcode kits from Nanopore (EXP-NBD104 and EXP-NBD114 and SQK-LSK109) and sequenced on a R9.4 flow cell multiplexing up to 24 samples per sequence run. Raw data was demultiplexed, amplicon primers were trimmed and human data was removed by mapping against the human reference genome."

                # Add SAMPLE_ATTRIBUTES
                sample_attributes = etree.SubElement(sample, "SAMPLE_ATTRIBUTES")
                create_sample_attribute(sample_attributes, "collecting institution", "not provided")
                create_sample_attribute(sample_attributes, "collection date", date)
                create_sample_attribute(sample_attributes, "collector name", "Dutch COVID-19 response team")
                create_sample_attribute(sample_attributes, "geographic location (country and/or sea)", "Netherlands")
                create_sample_attribute(sample_attributes, "geographic location (region and locality)", province)
                create_sample_attribute(sample_attributes, "sample capture status", "active surveillance in response to outbreak")
                create_sample_attribute(sample_attributes, "isolation source host-associated", iso_host)
                create_sample_attribute(sample_attributes, "host scientific name", "Homo sapiens")
                create_sample_attribute(sample_attributes, "host common name", "Human")
                create_sample_attribute(sample_attributes, "host health state", "not collected")
                create_sample_attribute(sample_attributes, "host sex", "not provided")
                create_sample_attribute(sample_attributes, "host subject id", "restricted access")
                create_sample_attribute(sample_attributes, "isolate", isolate)
                create_sample_attribute(sample_attributes, "GISAID Accession ID", gid)
                # create_sample_attribute(sample_attributes, "host disease outcome", host_disease_out)
                # create_sample_attribute(sample_attributes, "INSDC accession", insdc_acc)
                # create_sample_attribute(sample_attributes, "geographic location (latitude)", lat, "DD")
                # create_sample_attribute(sample_attributes, "geographic location (longitude)", long, "DD")
                create_sample_attribute(sample_attributes, "ENA-CHECKLIST", "ERC000033")

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
        description="Convert a `sam.tsv` file into a `sam.xml` file with the required structure for submitting a sample metadata object to ENA."
    )
    parser.add_argument(
        "-i", "--input",
        help="Specify the path to the input TSV file containing sample metadata. "
             "The file must include all required fields for generating the sam metadata XML.",
        default="sam.tsv"
    )

    # Parse arguments
    args = parser.parse_args()
    inFile = args.input  # Input file name
    outFile ="sam.xml"   # Input file name

    # Execute the TSV to XML conversion
    try:
        COUNT=tsv2XML(inFile, outFile)
        print(f"\n{COUNT} sample_objects successfully written to {outFile} XML file")
    except FileNotFoundError:
        print(f"Error: The file '{inFile}' does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
