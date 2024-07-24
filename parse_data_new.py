import pandas as pd
from os.path import join,split
from datetime import time, timedelta
import numpy as np
import os

def parse_technical_data(dataDir,project,plateName):
    df_technical = pd.read_excel(join(dataDir,project,plateName,"combined_metadata.xlsx"),sheet_name="Metadata")
    expID = project + "_" + plateName
    experimenter = df_technical["Experimenter's Name"]
    date = df_technical["Date of Experiment (DD/MM/YY)"]
    device = df_technical["Device Used"]
    temperature = df_technical["Temperature"]
    shaking = df_technical["Shaking (Y/N)"]
    co2 = df_technical["CO2 (Y/N)"]
    return pd.DataFrame({"expID":expID,"Experimenter":experimenter,"Date":date,"Device":device,"Temperature":temperature,"Shaking":shaking,"CO2":co2})

def parse_sheet(meta,dataDir,project,plateName,sheet_name,key_name):
    df = pd.read_excel(join(dataDir,project,plateName,'combined_metadata.xlsx'),sheet_name=sheet_name,index_col=0)
    for sample_name,sample in meta.items():
        well = sample['samples'][0]
        i,c = well[0],int(well[1:])
        value = df.at[i,c]
        meta[sample_name][key_name] = value
    return meta


def parse_meta_data(dataDir,project,plateName):
    #Parses groups.xlsx file
    #Sample IDs must be in form of S00B00.
    #B00 corresponds to the blank name
    df = pd.read_excel(join(dataDir,project,plateName,'combined_metadata.xlsx'),sheet_name="Groups",index_col=0)
    sample_names = []
    for entry in df.to_numpy().flatten():
        if isinstance(entry,str):
            if entry[0] == 'S':
                sample_names.append(entry)
        

    meta = {key:{'samples':[],'blanks':[],'linegroup':None,'species':None,
                 'carbon_source':None,'cs_conc':None,'base_media':None,'inhibitor':None,'inhibitor_conc':None,'comments':None} 
            for key in set(sample_names)}
    #Storing well names of corresponding samples
    for c in df.columns:
        for i in df.index:
            well = i + str(c)
            entry = df.at[i,c]
            if isinstance(entry,str):
                if entry[0] == 'S':
                    meta[df.at[i,c]]['samples'].append(well)
                    meta[df.at[i,c]]['linegroup'] = '_'.join([project,plateName,well])

    #Stroring corresponding blank wells
    for sample in meta.keys():
        blank = sample[sample.find('B'):]
        for c in df.columns:
            for i in df.index:
                well = i + str(c)
                entry = df.at[i,c]
                if entry == blank:
                    meta[sample]['blanks'].append(well)

    meta = parse_sheet(meta,dataDir,project,plateName,"Species","species")
    meta = parse_sheet(meta,dataDir,project,plateName,"Carbon Source","carbon_source")
    meta = parse_sheet(meta,dataDir,project,plateName,"CS Concentration","cs_conc")
    meta = parse_sheet(meta,dataDir,project,plateName,"Base Media","base_media")
    meta = parse_sheet(meta,dataDir,project,plateName,"Inhibitor","inhibitor")
    meta = parse_sheet(meta,dataDir,project,plateName,"Inhibitor Conc","inhibitor_conc")
    meta = parse_sheet(meta,dataDir,project,plateName,"Comments","comments")
    
    return meta

def parse_raw_data(dir):
    """This parses an excel file where the wells are in the column names."""
    df = pd.read_excel(join(dir,'data.xlsx'), skiprows=40)
    df = df[df.columns[1:]]
    for i, row in df.iterrows():
        if pd.isna(row["Time"]):
            break
    df = df.loc[0 : i - 1]
    ts = []
    for i in df["Time"]:
        """I have this bug that pandas converts strings up to 23:59:59 
        into datetime.time and strings >= 24:00:00 into time.timedelta.
        Conversion into string doesn't work (I tired a lot)."""
        if type(i) is time:
            ts.append(i.hour * 60 * 60 + i.minute * 60 + i.second)
        elif type(i) is timedelta:
            ts.append(i.total_seconds())
        elif type(i) is str:
            hour,minute,second = i.split(':')
            ts.append(int(hour) * 60 * 60 + int(minute) * 60 + int(second))
        else:
            print("Time is note in datetime.time or datetime.timedelat format.")
    df["Time"] = np.array(ts) / 60 / 60 
    return df

def parse_meta_to_df(meta,raw,project,plateName):
    
    df_run = pd.DataFrame()
    df_carbon_source = pd.DataFrame()
    df_species = pd.DataFrame()
    df_inhibitor = pd.DataFrame()
    df_measurement = pd.DataFrame()
    df_comments = pd.DataFrame()
    df_measurement = pd.DataFrame()

    measurement_dfs = []

    for sample_name,sample in meta.items():
        blank = raw[sample['blanks']].mean(axis=1)
        for well in sample['samples']:
            df_run = pd.concat([df_run,pd.DataFrame({"project":project,"expID":project + "_" + plateName,"linegroup":sample['linegroup']},index=[0])])
            df_carbon_source = pd.concat([df_carbon_source,pd.DataFrame({"linegroup":sample['linegroup'],"carbon_source":sample['carbon_source'],"cs_conc":sample['cs_conc'],"base_media":sample['base_media']},index=[0])])
            df_species = pd.concat([df_species,pd.DataFrame({"linegroup":sample['linegroup'],"species":sample['species']},index=[0])])
            df_inhibitor = pd.concat([df_inhibitor,pd.DataFrame({"linegroup":sample['linegroup'],"inhibitor":sample['inhibitor'],"inhibitor_conc":sample['inhibitor_conc']},index=[0])])
            df_comments = pd.concat([df_comments,pd.DataFrame({"linegroup":sample['linegroup'],"comments":sample['comments']},index=[0])])

            measurement = raw[well] - blank
            cur_measurement_df = pd.DataFrame({"linegroup":sample['linegroup'],"time":raw["Time"],"measurement":measurement})
            measurement_dfs.append(cur_measurement_df)

    df_measurement = pd.concat(measurement_dfs)
    return df_run,df_carbon_source,df_species,df_inhibitor,df_comments,df_measurement


def parse_data(dataDir,project):
    dir = join(dataDir,project)
    plateNames = next(os.walk(dir))[1]
    technical_data = pd.DataFrame()
    run_data = pd.DataFrame()
    carbon_source_data = pd.DataFrame()
    species_data = pd.DataFrame()
    inhibitor_data = pd.DataFrame()
    measurement_data = pd.DataFrame()
    comment_data = pd.DataFrame()
    for plateName in plateNames:
        technical_data = pd.concat([technical_data,parse_technical_data(dataDir,project,plateName)])
        meta = parse_meta_data(dataDir,project,plateName)
        raw = parse_raw_data(join(dataDir,project,plateName))
        run,carbon_source,species,inhibitor,comment,measurement = parse_meta_to_df(meta,raw,project,plateName)
        run_data = pd.concat([run_data,run])
        carbon_source_data = pd.concat([carbon_source_data,carbon_source])
        species_data = pd.concat([species_data,species])
        inhibitor_data = pd.concat([inhibitor_data,inhibitor])
        comment_data = pd.concat([comment_data,comment])
        measurement_data = pd.concat([measurement_data,measurement])
    return technical_data,run_data,carbon_source_data,species_data,inhibitor_data,comment_data,measurement_data

def save_data(parsed_data,dataDir,project):
    save_folder = "parsed_csvs"
    technical_data,run_data,carbon_source_data,species_data,inhibitor_data,comment_data,measurement_data = parsed_data
    technical_data.to_csv(join(dataDir,save_folder,project+"_technical_data.csv"),index=False)
    run_data.to_csv(join(dataDir,save_folder,project+"_run_data.csv"),index=False)
    carbon_source_data.to_csv(join(dataDir,save_folder,project+"_carbon_source_data.csv"),index=False)
    species_data.to_csv(join(dataDir,save_folder,project+"_species_data.csv"),index=False)
    inhibitor_data.to_csv(join(dataDir,save_folder,project+"_inhibitor_data.csv"),index=False)
    comment_data.to_csv(join(dataDir,save_folder,project+"_comment_data.csv"),index=False)
    measurement_data.to_csv(join(dataDir,save_folder,project+"_measurement_data.csv"),index=False)



dataDir = "data"
project = "240623_growth_phenotyping"

parsed_data = parse_data(dataDir,project)
save_data(parsed_data,dataDir,project)