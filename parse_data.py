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
        """I have this bug that pandas converts strings 
        up to 23:59:59 into datetime.time strings >= 24:00:00 into time.timedelta.
        Conversion into string doesn't work (I tired a lot)."""
        if type(i) == time:
            ts.append(i.hour * 60 * 60 + i.minute * 60 + i.second)
        elif type(i) == timedelta:
            ts.append(i.total_seconds())
        else:
            print("Time is note in datetime.time or datetime.timedelat format")
    df["Time"] = np.array(ts) / 60 / 60 
    return df

def parse_meta_data(dir):
    #Parses groups.xlsx file

    df = pd.read_excel(join(dir,'groups.xlsx'),index_col=0)
    values = df.to_numpy().flatten()
    samples = []
    for v in values:
        if v[0] == 'S':
            samples.append(v)
    samples = {key:{'samples':[],'blanks':[],'species':None} for key in set(samples)}
    for c in df.columns:
        for i in df.index:
            well = i + str(c)
            value = df.at[i,c]
            if value[0] == 'S':
                samples[df.at[i,c]]['samples'].append(well)
    for sample in samples.keys():
        blank = sample[2:]
        for c in df.columns:
            for i in df.index:
                well = i + str(c)
                value = df.at[i,c]
                if value == blank:
                    samples[sample]['blanks'].append(well)

    #Parses species
    df = pd.read_excel(join(dir,'species.xlsx'),index_col=0)
    for name,sample in samples.items():
        well = sample['samples'][0]
        i,c = well[0],int(well[1])
        species = df.at[i,c]
        samples[name]['species'] = species
    return samples

def annotate_data(dir):
    #Annotates raw data
    raw = parse_raw_data(dir)
    samples = parse_meta_data(dir)
    dfs = []
    for name,sample in samples.items():
        df = pd.DataFrame(columns = ['Time','OD','well','sample','species'])
        blank = raw[sample['blanks']].mean(axis=1)
        for well in sample['samples']:
            df['Time'] = raw['Time']
            df['OD'] = raw[well] - blank
            df['well'] = well
            df['sample'] = name
            df['species'] = samples[name]['species']
            dfs.append(df)
    out = pd.concat(dfs)
    out.to_csv(join('test_data','240619_alisson','data_annotated.csv'))
    return out
    
dir = join('test_data','240619_alisson')
meta = parse_meta_data(dir)
df = annotate_data(dir)