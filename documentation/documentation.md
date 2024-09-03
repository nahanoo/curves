# Documentation

## Introduction

Curves lets you parse 96-well plate OD time series along with relevant metadata. Adding metadata to your growth curves not only simplifies data analysis but also enhances the reproducibility of your experiments. Additionally, Curves makes your data accessible and downloadable online through an interactive dashboard, enabling quick analysis and easy data sharing.  
You can also use the dashboard to browse existing growth curve data for various bacteria and carbon sources, allowing you to streamline your experimental planning and assisting in deciding on conditions to test your hypothesis experimentally.
Future versions will also include the ability to fit various growth models, with the goal of creating a database of experimentally determined growth parameters that can be used for theoretical modeling.

## Adding data within the Mitri lab

![test](documentation/screenshots/test.png)

### Preparing data sumission

The code for `curves` is on [GitHub](https://github.com/nahanoo/curves). This repository is cloned in the `NAS` from where data is submitted. If you want to parse and visualize data yourself without submitting it, clone the repository locally. See the section [Local data parsing and plotting](#local-data-parsing-and-plotting). 

`Curves` treats each 96-well plate as a single experiment. For every experiment, you are required to complete a metadata file called `combined_metadata.xlsx` and a data file called `data.xlsx`. Multiple experiments can be grouped into projects, with data parsed on a per-project basis. This grouping is reflected in the file structure as follows: 

```
data/
├─ project/
│  ├─ experiment/
│  │  ├─ combined_metadata.xlsx
│  │  ├─ data.xlsx
```

To submit data, navigate the curves `data` directory on the `NAS` located in `FAC/FBM/DMF/smitri/default/D2c/curves/data`. Within the data directory, create a new folder for your project.  It is recommended to include the date in YY/MM/DD format along with a short, meaningful name. For example, you might name the folder `240820_at_phenotyping`. Within the project folder create a new folder for your experiment with a meaningful name, for example `acetate_adenosine_cysteine_arabinose`. Within the experiment folder, copy the `combined_metadata.xlsx` and the `data.xlsx` data from the templates located in:
```
data/
├─ TEMPLATE_PROJECT
│  ├─ TEMPLATE_EXPERIMENT
│  │  ├─ combined_metadata.xlsx
│  │  ├─ data.xlsx
``` 

### Filling out the combined_metadata table

The `combined_metadata.xlsx` contains multiple sheets which includes all the metadata of your experiment. Below is explained how each sheet needs to be filled out.

#### Metadata

The Metadata sheet contains mandatory information about the technical aspects of your experiment.

#### Groups

In this sheet, you specify in which wells replicates of a sample and the corresponding blanks are located. Sample IDs must start with `S`, followed by the blank ID, which must start with `B`, for example, S1B1. Replicates of the same sample share the same name. Wells that are not used must be left empty.  
In the example below, Sample 1 has three replicates in A1-A3, with corresponding blanks in H1-H3.  

#### Species

The Species sheet is used to indicate which species was grown in each well. Currently, Curves only supports monoculture data. For every well specified in the `Groups` sheet, you must define the full name of the grown bacteria. In the example below, all samples previously specified in Groups are Agrobacterium tumefaciens. 

#### Base media

If you conduct your experiments in simple media, a base media containing all necessary resources in excess—except for the carbon source—is used. This base media is specified in this sheet. You can provide additional information in the `Comments` sheet. In the example above, the experiment was done in a simple media with M9 and HMB as base media.  
If you did your experiments in rich media such as TSB, enter TSB.

#### Carbon source

This sheet stores the information which carbon source was used in which well. If the experiment was done in rich media, enter the name of the rich media.

#### CS Concnetration

Provide the information about the concentration of the carbon source used in millimolar.
If you used rich media, put the name of the rich media.

#### Inhibitor and Inhibitor Conc

If you used inhibitors for your experiments, such as antibiotics, enter the names of the inhibitors in the according wells and state the concentration in the `Inhibitor Conc` sheet. The concentration in the `Inhibitor Conc` is in µM. If you didn't use any inhibitors, enter None in the `Inhibitor` and 0 in the `Inhibitor Conc` sheets for the wells you used. 

#### Comments 

Here you can provide additional information for the different wells, such as protocols, observations or other useful information. If you have no comments, add None for the used wells.

### Filling out the data table

The `data.xlsx` contains the time series OD data with time and the different wells as columns. You can find the data in this format for most plate readers if you export your data in excel.  
Below you can find an example for three wells for the first 5 hours.  

## Submitting data to the database

For now you can contact [Prajwal Padmanabha](prajwal.padmanabha@unil.ch) or [Eric Ulrich](eric.ulrich@unil.ch) to add the data to the dashboard for visualization and exporting. Shortly after, the data will be available for exploration and exportation udder [https://curves.onrender.com/](https://curves.onrender.com/).

## Local data parsing and plotting

If you want to parse and visualize the data yourself you can do so by cloning the [curves](https://github.com/nahanoo/curves) repository locally.

```bash
git clone https://github.com/nahanoo/curves.git
```

You fill out the `combined_metadata.xlsx` and the `data.xlsx` file as explained in the section [Adding data within the Mitri lab](#adding-data-within-the-mitri-lab) within an experiment folder belonging to a project.  

```
data/
├─ your_project_name/
│  ├─ your_experiment_name/
│  │  ├─ combined_metadata.xlsx
│  │  ├─ data.xlsx
parse_data.py

```

Next, execute the `parse_data.py` script with the project name as an argument.
```python
python parse_data.py your_project_name
```
The logger of the script will provide you with information about the success of the parsing and tell you if you forgot to provide certain information for a well in the `combined_metadata.xlsx` file. 

The exported parsed data is located in several files under the following directory.
```
export/
├─ your_project_name/
│  ├─ carbon_source_data.csv
│  ├─ comment_data.csv
│  ├─ inhibitor_data.csv
│  ├─ measurement_data.csv
│  ├─ species_data.csv
│  ├─ run_data.csv
│  ├─ technical_data.csv
```

This acts as a backbone for the dasbhoard and is for now a little bit clumsy to work with directly. You can join the different tables via the `linegroup` column. For now it's easier to work with the data exported from the dashboard. See also [Working with data exported via the dasboard](#working-with-data-exported-via-the-dasboard).

## Local data visualization

After you parsed your data, you can execute the `dashboard.py` script for data visualization.

```python
python dashboard.py
```
Select your project and start exploring the data in the `View Data` tab. If you switch to the `Export Data` tab, you can export the curves that are interesting for you.

## Working with data exported via the dashboard

After you selected the conditions that are interesting for you in the `Export Data` tab, you can download the data by clicking the Download Data button.
This gives you a zip file containing two files, `measurements.csv` and `metadata.csv`. You can filter the Metadata according to your interests and mask the measurements. Below is a short example how this can be done.

```python
# Load dataframes
meta = pd.read_csv(join(path, "metadata.csv"))
raw = pd.read_csv(join(path, "measurements.csv"))
# Filtering meta data for species and carbon source
mask = (meta["species"] == 'Agrobacterium tumefaciens') & (meta["carbon_source"] == 'Acetate')
# This stores all unique wells across experiment and projects that fulfill your filtering criteria. 
columns = list(set(meta[mask]["linegroup"]))
# Filter measurements data according to the fitler
df_acetate =  raw[["time"] + columns].dropna()

```