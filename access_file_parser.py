import argparse

# Set up argument parser
parser = argparse.ArgumentParser(
    prog='submission_parser',
    description='Parses access_file to generate submission files for GISAID and ENA'
)

# Add filename argument
parser.add_argument('access_file', help="Input file in 'dd-mm-yy.tsv' format")

# Parse arguments
args = parser.parse_args()
access_file_name = args.access_file

# Extract the submission date from the filename (before '.tsv')
submission_date = access_file_name.rsplit('.tsv', 1)[0]

# Define output filenames based on the extracted date
gisaid_fasta_filename = f"GISAID_{submission_date}.fasta"
gisaid_tsv_filename = f"gisaid_{submission_date}.tsv"
symlink_script_filename = f"makeLinks_{submission_date}.sh"

# Initialize counters
total_samples = 0
samples_for_submission = 0

with open (access_file_name, "r") as access_file_in, \
    open(gisaid_tsv_filename,"w") as gisaid_tsv_file_out, \
    open(gisaid_fasta_filename,"w") as gisaid_fasta_out, \
    open(symlink_script_filename,"w") as symlinks_file_out:
    for line in access_file_in:
        line=line.strip()
        words =line.split("\t")

        if line.startswith("Sample"):
            continue

        total_samples +=1

        if len(words) != 66:
            print("check input access_file at line number " + str(total_samples-1))
            continue

        # THIS IS FOR THE FIELD "ToRIVM"
        if words[11] != "TRUE":
            print("skipping line " +str(total_samples))
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
            print("sampling date and alias date inconsistent: check line " + str(total_samples-1))

        if len(dates)==3:
            # format the date as per GISAID/ENA requirements
            yyyy=dates[2]
            mm=dates[1]
            dd=dates[0]

            # check if date is in double digit format
            if len(dd) != 2:
                # app
                dd="0"+dd

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
        ruzzz_bcyy="Run"+words[14].split("_")[2]+"_"+words[15]

        alias="hCoV-19/"+seq_alias+"/"+str(yyyy)

        #print(format_date+"\t"+ruzzz_bcyy+"\t"+alias+"\t"+sampletype+"\t"+words[64])
        #gisaid_tsv_file_out.write(format_date+"\t"+ruzzz_bcyy+"\t"+alias+"\t"+sampletype+"\t"+words[64]+"\t"+"Europe / Netherlands / "+words[64]+"\n")

        if words[64]=="":
            if words[61]=="ZH":
                words[64]="Zuid-Holland"
            elif words[61]=="ZE":
                words[64]="Zeeland"
            elif words[61]=="NH":
                words[64]="Noord-Holland"
            elif words[61]=="UT":
                words[64]="Utrecht"
            elif words[61]=="GE":
                words[64]="Gelderland"
            elif words[61]=="NB":
                words[64]="Noord-Brabant"
            elif words[61]=="LI":
                words[64]="Limburg"
            elif words[61]=="OV":
                words[64]="Overijssel"
            elif words[61]=="GR":
                words[64]="Groningen"
            elif words[61]=="DR":
                words[64]="Drenthe"
            elif words[61]=="FL":
                words[64]="Flevoland"

        if words[64]=="":
            print("Province has problem: check line " + str(total_samples-1))

        # create file that can be directly used in the GISAID.xls file
        gisaid_tsv_file_out.write("GISAID_"+submission_date+".fasta\t"+alias+"\tbetacoronavirus\tOriginal\t"+format_date+"\t"+"Europe / Netherlands / "+words[64]+"\t"+ruzzz_bcyy+"\t"+sampletype+"\t"+words[64]+"\n")

        # create fasta file to submit to GISAID
        gisaid_fasta_out.write(">"+alias+"\n")
        gisaid_fasta_out.write(words[18]+"\n")

        # create file to make symlinks to the raw reads
        symlinks_file_out.write("ln -s /mnt/viro0002/sequencedata/processed/SARS-CoV-2/Runs/"+words[14]+"/filtered/barcode"+words[15][2:]+"_filtered.fastq "+ruzzz_bcyy+".fastq"+"\n")

print("total samples in access_file: " + str(total_samples))
print("total samples to submit: " + str(samples_for_submission))

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
