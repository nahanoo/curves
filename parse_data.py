import pandas as pd
from os.path import join,split
from datetime import time, timedelta
import numpy as np

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

def parse_meta_data(dir):
    #Parses groups.xlsx file
    #Sample IDs must be in form of S00B00.
    #B00 corresponds to the blank name
    df = pd.read_excel(join(dir,'groups.xlsx'),index_col=0)
    sample_names = []
    for entry in df.to_numpy().flatten():
        if isinstance(entry,str):
            if entry[0] == 'S':
                sample_names.append(entry)
        

    meta = {key:{'samples':[],'blanks':[],'species':None,
                 'carbon_source':None,'concentration':None} 
            for key in set(sample_names)}
    #Storing well names of corresponding samples
    for c in df.columns:
        for i in df.index:
            well = i + str(c)
            entry = df.at[i,c]
            if isinstance(entry,str):
                if entry[0] == 'S':
                    meta[df.at[i,c]]['samples'].append(well)

    #Stroring corresponding blank wells
    for sample in meta.keys():
        blank = sample[sample.find('B'):]
        for c in df.columns:
            for i in df.index:
                well = i + str(c)
                entry = df.at[i,c]
                if entry == blank:
                    meta[sample]['blanks'].append(well)

    #Parses species
    df = pd.read_excel(join(dir,'species.xlsx'),index_col=0)
    for sample_name,sample in meta.items():
        well = sample['samples'][0]
        i,c = well[0],int(well[1:])
        species = df.at[i,c]
        meta[sample_name]['species'] = species

    #Parse carbon sources
    df = pd.read_excel(join(dir,'carbon_sources.xlsx'),index_col=0)
    for sample_name,sample in meta.items():
        well = sample['samples'][0]
        i,c = well[0],int(well[1:])
        carbon_source = df.at[i,c]
        meta[sample_name]['carbon_source'] = carbon_source

    #Parse concentrations
    df = pd.read_excel(join(dir,'concentrations.xlsx'),index_col=0)
    for sample_name,sample in meta.items():
        well = sample['samples'][0]
        i,c = well[0],int(well[1:])
        concentration = df.at[i,c]
        meta[sample_name]['concentration'] = concentration
    return meta

def annotate_data(dir):
    #Annotates raw data
    raw = parse_raw_data(dir)
    meta = parse_meta_data(dir)
    dfs = []
    for sample_name,sample in meta.items():
        df = pd.DataFrame(columns = ['Time','OD','well','sample',
                                     'species','carbon_source','concentration'])
        blank = raw[sample['blanks']].mean(axis=1)
        for well in sample['samples']:
            df['Time'] = raw['Time']
            df['OD'] = raw[well] - blank
            df['well'] = well
            df['sample'] = sample_name
            df['species'] = meta[sample_name]['species']
            df['species'] = meta[sample_name]['species']
            df['carbon_source'] = meta[sample_name]['carbon_source']
            df['concentration'] = meta[sample_name]['concentration']
            dfs.append(df)
    out = pd.concat(dfs)
    out.to_csv(join(dir,'data_annotated.csv'))
    return out
    
dir = join('data','240623_growth_phenotyping','at')
meta = parse_meta_data(dir)
df = annotate_data(dir)

