# Documentation

## Introduction

Curves lets you parse 96-well plate OD time series along with relevant metadata. Adding metadata to your growth curves not only simplifies data analysis but also enhances the reproducibility of your experiments. Additionally, Curves makes your data accessible and downloadable online through an interactive dashboard, enabling quick analysis and easy data sharing.  
You can also use the dashboard to browse existing growth curve data for various bacteria and carbon sources, allowing you to streamline your experimental planning and assisting in deciding on conditions to test your hypothesis experimentally.
Future versions will also include the ability to fit various growth models, with the goal of creating a database of experimentally determined growth parameters that can be used for theoretical modeling.

## Adding data within the Mitri lab

### Preparing data sumission

The code for `curves` is on [GitHub](https://github.com/nahanoo/curves). This repository is cloned in the `NAS` from where data is submitted. If you want to parse and visualize data yourself without submitting it, clone the repository locally. See the section [Local data parsing and plotting](#local-data-parsing-and-plotting). 

Curves treats each 96-well plate as a single experiment. For every experiment, you are required to complete a metadata file called combined_metadata.xlsx and a data file called data.xlsx. Multiple experiments can be grouped into projects, with data parsed on a per-project basis. This grouping is reflected in the file structure as follows: 

```
data/
├─ project/
│  ├─ experiment/
│  │  ├─ combined_metadata.xlsx
│  │  ├─ data.xlsx
```

To submit data, go to the curves `data` directory on the `NAS` located in `FAC/FBM/DMF/smitri/default/D2c/curves/data`. Within the data directory, create a new folder representing the project. It is suggested to include the date in the `YY/MM/DD` format a long with a short meaningful name, for example `240820_ct_oa_acetate`. Within the project folder create a new folder for your experiment with a meaningful name, for example `concentration_gradient`. Within the experiment folder, copy the `combined_metadata.xlsx` and the `data.xlsx` data from the templates located in:
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

<table><thead>
  <tr>
    <th>Experimenter's Name</th>
    <th>Date of Experiment (DD/MM/YY)</th>
    <th>Device Used</th>
    <th>Temperature</th>
    <th>Shaking (Y/N)</th>
    <th>CO2 (Y/N)</th>
  </tr></thead>
<tbody>
  <tr>
    <td>Snorre Sulheim</td>
    <td>26.6.2024</td>
    <td>Biotek Synergy 2408</td>
    <td>28</td>
    <td>Y</td>
    <td>N</td>
  </tr>
</tbody>
</table>

#### Groups

In this sheet, you specify the wells where replicates of a sample and the corresponding blanks are located. Sample IDs must start with `S`, followed by the blank ID, which must start with `B`, for example, S1B1. Replicates of the same sample share the same name. Wells that are not used must be left empty.  
In the example below, Sample 1 has three replicates in A1-A3, with corresponding blanks in H1-H3.  

<table><thead>
  <tr>
    <th></th>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
    <th>6</th>
    <th>7</th>
    <th>8</th>
    <th>9</th>
    <th>10</th>
    <th>11</th>
    <th>12</th>
  </tr></thead>
<tbody>
  <tr>
    <td>A</td>
    <td>S1B1</td>
    <td>S1B1</td>
    <td>S1B1</td>
    <td>S2B2</td>
    <td>S2B2</td>
    <td>S2B2</td>
    <td>S3B3</td>
    <td>S3B3</td>
    <td>S3B3</td>
    <td>S4B4</td>
    <td>S4B4</td>
    <td>S4B4</td>
  </tr>
  <tr>
    <td>B</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>C</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>D</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>E</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>F</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>G</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>H</td>
    <td>B1</td>
    <td>B1</td>
    <td>B1</td>
    <td>B2</td>
    <td>B2</td>
    <td>B2</td>
    <td>B3</td>
    <td>B3</td>
    <td>B3</td>
    <td>B4</td>
    <td>B4</td>
    <td>B4</td>
  </tr>
</tbody></table>

#### Species

The Species sheet is used to indicate which species was grown in each well. Currently, Curves only supports monoculture data. For every well specified in the Groups sheet, you must define the full name of the grown bacteria. In the example below, all samples previously specified in Groups are Agrobacterium tumefaciens. 

<table><thead>
  <tr>
    <th></th>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
    <th>6</th>
    <th>7</th>
    <th>8</th>
    <th>9</th>
    <th>10</th>
    <th>11</th>
    <th>12</th>
  </tr></thead>
<tbody>
  <tr>
    <td>A</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
    <td>Agrobacterium tumefaciens</td>
  </tr>
  <tr>
    <td>B</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>C</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>D</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>E</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>F</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>G</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>H</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</tbody></table>

#### Base media

If you conduct your experiments in simple media, a base media containing all necessary resources in excess—except for the carbon source—is used. This base media is specified in this sheet. You can provide additional information in the `Comments` sheet. In the example above, the experiment was done in a simple media with M9 and HMB as base media.  
If you did your experiments in rich media such as TSB, enter TSB.

<table><thead>
  <tr>
    <th></th>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
    <th>6</th>
    <th>7</th>
    <th>8</th>
    <th>9</th>
    <th>10</th>
    <th>11</th>
    <th>12</th>
  </tr></thead>
<tbody>
  <tr>
    <td>A</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
    <td>M9 + HMB</td>
  </tr>
  <tr>
    <td>B</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>C</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>D</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>E</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>F</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>G</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>H</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</tbody></table>

#### Carbon source

This sheet stores the information which carbon source was used in which well. If the experiment was done in rich media, enter the name of the rich media.

<table><thead>
  <tr>
    <th></th>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
    <th>6</th>
    <th>7</th>
    <th>8</th>
    <th>9</th>
    <th>10</th>
    <th>11</th>
    <th>12</th>
  </tr></thead>
<tbody>
  <tr>
    <td>A</td>
    <td>Acetate</td>
    <td>Acetate</td>
    <td>Acetate</td>
    <td>Adenosine</td>
    <td>Adenosine</td>
    <td>Adenosine</td>
    <td>Cysteine</td>
    <td>Cysteine</td>
    <td>Cysteine</td>
    <td>D-arabinose</td>
    <td>D-arabinose</td>
    <td>D-arabinose</td>
  </tr>
  <tr>
    <td>B</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>C</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>D</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>E</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>F</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>G</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>H</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</tbody></table>

#### CS Concnetration

Provide the information about the concentration of the carbon source used in millimolar.
If you used rich media, put the name of the rich media.

<table><thead>
  <tr>
    <th></th>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
    <th>6</th>
    <th>7</th>
    <th>8</th>
    <th>9</th>
    <th>10</th>
    <th>11</th>
    <th>12</th>
  </tr></thead>
<tbody>
  <tr>
    <td>A</td>
    <td>45</td>
    <td>45</td>
    <td>45</td>
    <td>9</td>
    <td>9</td>
    <td>9</td>
    <td>30</td>
    <td>30</td>
    <td>30</td>
    <td>18</td>
    <td>18</td>
    <td>18</td>
  </tr>
  <tr>
    <td>B</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>C</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>D</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>E</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>F</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>G</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>H</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</tbody></table>

#### Inhibitor and Inhibitor Conc

If you used an inhibitor for your experiments, such as antibiotics, enter the name of the inhibitor in the according wells and state the concentration in the `Inhibitor Conc` sheet. The concentration in the `Inhibitor Conc` is in µM. If you didn't use any inhibitors, enter None in the `Inhibitor` and 0 in the `Inhibitor Conc` sheets for the wells you used. 

#### Comments 

Here you can provide additional information for the different wells, such as protocols, observations or other useful information. 

### Filling out the data table

The `data.xlsx` contains the time series OD data with time and the different wells as columns. You can find the data in this format for most plate readers if you export your data in excel.  
Below you can find an example for three wells for the first 5 hours.  

<table><thead>
  <tr>
    <th>Time</th>
    <th>A1</th>
    <th>A2</th>
    <th>A3</th>
  </tr></thead>
<tbody>
  <tr>
    <td>0:29:10</td>
    <td>0.0983</td>
    <td>0.1039</td>
    <td>0.0987</td>
  </tr>
  <tr>
    <td>0:59:10</td>
    <td>0.0984</td>
    <td>0.1037</td>
    <td>0.099</td>
  </tr>
  <tr>
    <td>1:29:10</td>
    <td>0.098</td>
    <td>0.103</td>
    <td>0.0981</td>
  </tr>
  <tr>
    <td>1:59:10</td>
    <td>0.0978</td>
    <td>0.1022</td>
    <td>0.0976</td>
  </tr>
  <tr>
    <td>2:29:10</td>
    <td>0.0978</td>
    <td>0.1018</td>
    <td>0.0974</td>
  </tr>
  <tr>
    <td>2:59:10</td>
    <td>0.097</td>
    <td>0.1012</td>
    <td>0.0968</td>
  </tr>
  <tr>
    <td>3:29:10</td>
    <td>0.0972</td>
    <td>0.101</td>
    <td>0.0966</td>
  </tr>
  <tr>
    <td>3:59:10</td>
    <td>0.0974</td>
    <td>0.1009</td>
    <td>0.0965</td>
  </tr>
  <tr>
    <td>4:29:10</td>
    <td>0.0969</td>
    <td>0.1007</td>
    <td>0.0962</td>
  </tr>
  <tr>
    <td>4:59:10</td>
    <td>0.0968</td>
    <td>0.1005</td>
    <td>0.096</td>
  </tr>
</tbody></table>

## Submitting data to the database

For now you can contact [Prajwal Padmanabha](prajwal.padmanabha@unil.ch) or [Eric Ulrich](eric.ulrich@unil.ch) to add the data to the dashboard for visualization.

## Local data parsing and plotting

If you want to parse and visualize the data yourself you can do that by cloning the [curves](https://github.com/nahanoo/curves) repository locally.

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

Next execute the `parse_data.py` script with the project name as an argument.
```python
python parse_data.py your_project_name
```

