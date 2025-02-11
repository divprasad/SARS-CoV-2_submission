import argparse

parser = argparse.ArgumentParser(
                    prog='submission parser',
                    description='GISAID/ENA submission parser from access_file')

parser.add_argument('filename', help="'dd-mm-yy' of the access_file")

args = parser.parse_args()

submission_date=args.filename #"20-03-23"

afile_in=submission_date+".tsv"
gfasta_out="GISAID_"+submission_date+".fasta"
gfiletsv_out="gisaid_"+submission_date+".tsv"
linksf_out="makeLinks_"+submission_date+".sh"

seqs_in_access_file=0
seqs_to_submit=0
seq_alias=[]
dates=[]
with open (afile_in, "r") as fin, open(gfiletsv_out,"w") as fout1, open(gfasta_out,"w") as fout2, open(linksf_out,"w") as fout3:
    for line in fin:
        line=line.strip()
        words =line.split("\t")

        if line.startswith("Sample"):
            continue

        seqs_in_access_file +=1

        if len(words) != 66:
            print("check input access_file at line number " + str(seqs_in_access_file-1))
            continue

        # THIS IS FOR THE FIELD "ToRIVM"
        if words[11] != "TRUE":
            print("skipping line " +str(seqs_in_access_file))
            continue

        else:
            seqs_to_submit+=1

        sampletype=words[6] #sample type lysis or throat/nasal
        samplequestion=words[8] #sample question surveillance

        # words[13] hCov-19/Netherlands/ZH-EMC-7898/02-03-2023
        seq_alias="/".join(words[13].split("/")[1:-1])

        # words[7] is sampling date
        dates=words[13].split("/")[-1].split("-")

        # something wrong in the sampling date and the alias from the access_file
        if "/".join(dates) != words[7]:
            print("sampling date and alias date inconsistent: check line " + str(seqs_in_access_file-1))

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
            print("alias date (words[13] 'SequenceID_Internal') has problem: check line " + str(seqs_in_access_file-1) + "; alias hCoV-19/" + seq_alias)
            format_date=str(2024)
            yyyy="2024"

        # words[14] is Viro_run_zzz # words[15] is BByy
        ruzzz_bcyy="Run"+words[14].split("_")[2]+"_"+words[15]

        alias="hCoV-19/"+seq_alias+"/"+str(yyyy)

        #print(format_date+"\t"+ruzzz_bcyy+"\t"+alias+"\t"+sampletype+"\t"+words[64])
        #fout1.write(format_date+"\t"+ruzzz_bcyy+"\t"+alias+"\t"+sampletype+"\t"+words[64]+"\t"+"Europe / Netherlands / "+words[64]+"\n")

        if words[64]=="":
            if words[61]=="ZH":
                words[64]="Zuid-Holland"
            if words[61]=="ZE":
                words[64]="Zeeland"
            if words[61]=="NH":
                words[64]="Noord-Holland"
            if words[61]=="UT":
                words[64]="Utrecht"
            if words[61]=="GE":
                words[64]="Gelderland"
            if words[61]=="NB":
                words[64]="Noord-Brabant"
            if words[61]=="LI":
                words[64]="Limburg"
            if words[61]=="OV":
                words[64]="Overijssel"
            if words[61]=="GR":
                words[64]="Groningen"
            if words[61]=="DR":
                words[64]="Drenthe"
            if words[61]=="FL":
                words[64]="Flevoland"

        if words[64]=="":
            print("Province has problem: check line " + str(seqs_in_access_file-1))

        # create file that can be directly used in the GISAID.xls file
        fout1.write("GISAID_"+submission_date+".fasta\t"+alias+"\tbetacoronavirus\tOriginal\t"+format_date+"\t"+"Europe / Netherlands / "+words[64]+"\t"+ruzzz_bcyy+"\t"+sampletype+"\t"+words[64]+"\n")

        # create fasta file to submit to GISAID
        fout2.write(">"+alias+"\n")
        fout2.write(words[18]+"\n")

        # create file to make symlinks to the raw reads
        fout3.write("ln -s /mnt/viro0002/sequencedata/processed/SARS-CoV-2/Runs/"+words[14]+"/filtered/barcode"+words[15][2:]+"_filtered.fastq "+ruzzz_bcyy+".fastq"+"\n")

print("total samples in access_file: " + str(seqs_in_access_file))
print("total samples to submit: " + str(seqs_to_submit))

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
