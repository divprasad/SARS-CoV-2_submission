import argparse

# Set up argument parser
parser = argparse.ArgumentParser(
    prog='submission_parser',
    description='Extracts and processes sequencing data from an access file to create submission-ready files for GISAID and ENA.'
)

# Add filename argument
parser.add_argument('access_file', help="Input file in 'dd-mm-yy.tsv' format")

# Parse arguments
args = parser.parse_args()
access_file_name = args.access_file

PROVINCE_MAP = {
    "ZH": "Zuid-Holland", "ZE": "Zeeland", "NH": "Noord-Holland",
    "UT": "Utrecht", "GE": "Gelderland", "NB": "Noord-Brabant",
    "LI": "Limburg", "OV": "Overijssel", "GR": "Groningen",
    "DR": "Drenthe", "FL": "Flevoland"
}

# Extract the submission date from the filename (before '.tsv')
submission_date = access_file_name.rsplit('.tsv', 1)[0]

# Define output filenames based on the extracted date
gisaid_fasta_filename = f"GISAID_{submission_date}.fasta"
gisaid_tsv_filename = f"gisaid_{submission_date}.tsv"
symlink_script_filename = f"makeLinks_{submission_date}.sh"

# Initialize counters
total_samples = 0
samples_for_submission = 0

with open(access_file_name, "r") as access_file_in,        \
     open(gisaid_tsv_filename,"w") as gisaid_tsv_file_out, \
     open(gisaid_fasta_filename,"w") as gisaid_fasta_out,  \
     open(symlink_script_filename,"w") as symlinks_file_out:
    for line in access_file_in:
        line=line.strip()
        words =line.split("\t")

        if line.startswith("Sample"):
            continue

        total_samples +=1

        if len(words) != 66:
            print("Check input access_file at line number " + str(total_samples-1))
            continue

        # this is the fields "ToRIVM"
        if words[11] != "TRUE":
            print("Skipping line " +str(total_samples))
            continue

        else:
            samples_for_submission+=1

        sampletype=words[6] #sample type lysis or throat/nasal
        samplequestion=words[8] #sample question surveillance

        # words[13] hCov-19/Netherlands/ZH-EMC-7898/02-03-2023
        seq_alias="/".join(words[13].split("/")[1:-1])

        # words[7] is sampling date
        dates=words[13].split("/")[-1].split("-")

        # something wrong in the sampling date and the alias from the access_file
        if "/".join(dates) != words[7]:
            print("Sampling date and date extracted from sample_alias inconsistent: check line " + str(total_samples-1))

        if len(dates)==3:
            # format the date as per GISAID/ENA requirements
            yyyy, mm, dd=dates[2], dates[1].zfill(2), dates[0].zfill(2)

            # check if the barcode is in BC+ double digit format
            if len(words[15]) != 4:

                print("old barcode " + words[15]+" changed to "+ "BC0"+words[15][-1])
                words[15]="BC0"+words[15][-1]

            format_date=yyyy+"-"+mm+"-"+dd

        else:
            print("alias date (words[13] 'SequenceID_Internal') has problem: check line " + str(total_samples-1) + "; alias hCoV-19/" + seq_alias)
            format_date=str(2024)
            yyyy="2024"

        # words[14] is Viro_run_zzz # words[15] is BByy
        runyy_bczz="Run"+words[14].split("_")[2]+"_"+words[15]

        alias="hCoV-19/"+seq_alias+"/"+str(yyyy)


        province = words[64] or PROVINCE_MAP.get(words[61], "")
        if not province:
            print(f"Province has problem: check line {total_samples}")

        # create file that can be directly used in the GISAID.xls file
        gisaid_tsv_file_out.write(
            f"GISAID_{submission_date}.fasta\t{alias}\t"
            f"betacoronavirus\tOriginal\t{format_date}\t"
            f"Europe / Netherlands / {province}\t"
            f"{runyy_bczz}\t{sampletype}\t"
            f"{province}\n"
        )

        # create fasta file to submit to GISAID
        gisaid_fasta_out.write(f">{alias}\n{words[18]}\n")

        # create file to make symlinks to the raw reads
        symlinks_file_out.write(
            f"ln -s /mnt/viro0002/sequencedata/processed/SARS-CoV-2/Runs/"
            f"{words[14]}/filtered/barcode{words[15][2:]}_filtered.fastq "
            f"{runyy_bczz}.fastq\n"
        )


print(f"Total samples in access_file: {total_samples}")
print(f"Total samples to submit: {samples_for_submission}")

# 0  # SampleID	Supplier	Applicant	SampleEMCCode
# 4  # SampleExtCode	SampleCoronIT	SampleType	SamplingDate
# 8  # SampleQuestion	CtValue	SampleRemarks	SequenceSuccess
# 12 # SampleLocatie	SequenceID_Internal	SequenceRun	Barcode
# 16 # SequenceDate	Sequence_md5sum	Sequence	SequenceReadPaths
# 20 # SequenceRemarks	WHO_label	NextCLADE	Pangolin
# 24 # ToENA	ToGISAID	ToRIVM	AddedDate
# 28 # UserName	DatabaseGISAID	DatabaseRIVM	DatabaseENA
# 32 # flowcell_number	Primerset	LastNr	SequenceID_gisaid
# 36 # Platform	EntryOrder	Host	PatientCode
# 40 # PatientCoronIT	PatientType	PatientDetails	PatientDob
# 44 # PatientZipcode	PatientCity	PatientProvince	PatientCountry
# 48 # VaccinationDate	VaccinationType	TravelHistory_Country	TravelHistory_Dates
# 52 # Setting	SettingDetails	FirstDayOfIllness	HospitalID
# 56 # DepartmentID	WorkedwithComplaints	SymptomOnsetDate	AutoGeneratedPCode
# 60 # Timestamp	PrvAf	SamplingDateRemarks	ContinentCountryProv
# 64 # ProvinceFullName	Coverage	Extra1	Extra2
