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

The combined_metadata contains multiple sheets which need to be filled out.

#### Metadata

The Metadata sheet contains mandatory information about the experiment.  

<table><thead>
  <tr>
    <th>Experimenter's Name</th>
    <th>Date of Experiment (DD/MM/YY)</th>
    <th>Device Used</th>
    <th>Temperature</th>
    <th>Shaking (Y/N)</th>
    <th>CO2 (Y/N)</th>
    <th></th>
  </tr></thead>
<tbody>
  <tr>
    <td>Snorre Sulheim</td>
    <td>26.6.2024</td>
    <td>Biotek Synergy 2408</td>
    <td>28</td>
    <td>Y</td>
    <td>N</td>
    <td></td>
  </tr>
</tbody>
</table>

#### Groups

In this mandatory groups sheet, one specifies in which well the samples are located and which blanks corresponds to the samples. One sample can have multiple replicates.  
Samples start with a sample ID which has to start with `S`, followed by the blank ID which has to start with `B`, for example `S1B1`. Wells that are not used must be left empty.

In the example below, Sample 1 has three replicates in A1-A3, with corresponding blanks in H1-H3.  

<<table><thead>
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

The Species sheet is used to parse which species was grown in which well. So far `curves` only works with monoculture data. For every well specified in `Group` one must define the full name of the grown bacteria. In the example below, all samples filled out before in `Groups` are Agrobacterium tumefaciens.  

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

## Local data parsing and plotting


