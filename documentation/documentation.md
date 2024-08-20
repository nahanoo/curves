# Documentation

## Introduction

Curves let's you parse 96 well plate OD data along with relevant meta. Adding the metadata to your growth curves not only makes data analysis easier, but also increases the reproducibility of your experiments. Curves also comes with the option that your data is accessible and downloadable online via an interactive dash board allowing for quick analysis and data sharing.  
You can also use the dashboard to browse existing growth curve data for various bacteria and carbon sources, allowing to streamline you experimental planning or deciding on conditions to test your hypothesis experimentally. 

## Adding data within the Mitri lab

### Preparing data sumission

The code for `curves` is on [GitHub](https://github.com/nahanoo/curves). This repository is cloned in the `NAS` from where data is submitted. If you want to parse and plot data yourself without submitting it, clone the repository locally. See the section [Local data parsing and plotting](#local-data-parsing-and-plotting). 

`Curves` treats each well plate as a single experiment. For every experiment, a metadata file called `combined_metadata.xlsx` and a data file called `data.xlsx` are required to fill out. Multiple experiments are grouped into projects and data is parsed per project. This grouping is reflected in the file structure: 

```data/
├─ project/
│  ├─ experiment/
│  │  ├─ combined_metadata.xlsx
│  │  ├─ data.xlsx
```

To submit data go to the curves `data` directory on the `NAS` located in `FAC/FBM/DMF/smitri/default/D2c/curves/data`. Within the data directory, create a new folder representing the project. It is suggested to include the date in the `YY/MM/DD` format a long with a short meaningful name, for example `240820_ct_oa_acetate`. Within the project folder create a new folder for your experiment with a meaningful name, for example `concentration_gradient`. Within the experiment folder, copy the `combined_metadata.xlsx` and the `data.xlsx` data from the template experiment located in 
```data/
├─ TEMPLATE_PROJECT
│  ├─ TEMPLATE_EXPERIMENT
│  │  ├─ combined_metadata.xlsx
│  │  ├─ data.xlsx
``` 

### Filling out the combined_metadata table



## Local data parsing and plotting