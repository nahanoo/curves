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

<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  overflow:hidden;padding:10px 5px;word-break:normal;}
.tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
.tg .tg-0pky{border-color:inherit;text-align:left;vertical-align:top}
</style>
<table class="tg"><thead>
  <tr>
    <th class="tg-0pky">Experimenter's Name</th>
    <th class="tg-0pky">Date of Experiment (DD/MM/YY)</th>
    <th class="tg-0pky">Device Used</th>
    <th class="tg-0pky">Temperature</th>
    <th class="tg-0pky">Shaking (Y/N)</th>
    <th class="tg-0pky">CO2 (Y/N)</th>
  </tr></thead>
<tbody>
  <tr>
    <td class="tg-0pky">Snorre Sulheim</td>
    <td class="tg-0pky">26.6.2024</td>
    <td class="tg-0pky">Biotek Synergy 2408</td>
    <td class="tg-0pky">28</td>
    <td class="tg-0pky">Y</td>
    <td class="tg-0pky">N</td>
  </tr>
</tbody>
</table>

#### Groups

In this mandatory groups sheet, one specifies in which well the samples are located and which blanks corresponds to the samples. One sample can have multiple replicates.  
Samples start with a sample ID which has to start with `S`, followed by the blank ID which has to start with `B`, for example `S1B1`. Wells that are not used must be left empty.

In the example below, Sample 1 has three replicates in A1-A3, with corresponding blanks in H1-H3.

<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  overflow:hidden;padding:10px 5px;word-break:normal;}
.tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
.tg .tg-0pky{border-color:inherit;text-align:left;vertical-align:top}
</style>
<table class="tg"><thead>
  <tr>
    <th class="tg-0pky"></th>
    <th class="tg-0pky">1</th>
    <th class="tg-0pky">2</th>
    <th class="tg-0pky">3</th>
    <th class="tg-0pky">4</th>
    <th class="tg-0pky">5</th>
    <th class="tg-0pky">6</th>
    <th class="tg-0pky">7</th>
    <th class="tg-0pky">8</th>
    <th class="tg-0pky">9</th>
    <th class="tg-0pky">10</th>
    <th class="tg-0pky">11</th>
    <th class="tg-0pky">12</th>
  </tr></thead>
<tbody>
  <tr>
    <td class="tg-0pky">A</td>
    <td class="tg-0pky">S1B1</td>
    <td class="tg-0pky">S1B1</td>
    <td class="tg-0pky">S1B1</td>
    <td class="tg-0pky">S2B2</td>
    <td class="tg-0pky">S2B2</td>
    <td class="tg-0pky">S2B2</td>
    <td class="tg-0pky">S3B3</td>
    <td class="tg-0pky">S3B3</td>
    <td class="tg-0pky">S3B3</td>
    <td class="tg-0pky">S4B4</td>
    <td class="tg-0pky">S4B4</td>
    <td class="tg-0pky">S4B4</td>
  </tr>
  <tr>
    <td class="tg-0pky">B</td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
  </tr>
  <tr>
    <td class="tg-0pky">C</td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
  </tr>
  <tr>
    <td class="tg-0pky">D</td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
  </tr>
  <tr>
    <td class="tg-0pky">E</td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
  </tr>
  <tr>
    <td class="tg-0pky">F</td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
  </tr>
  <tr>
    <td class="tg-0pky">G</td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
    <td class="tg-0pky"></td>
  </tr>
  <tr>
    <td class="tg-0pky">H</td>
    <td class="tg-0pky">B1</td>
    <td class="tg-0pky">B1</td>
    <td class="tg-0pky">B1</td>
    <td class="tg-0pky">B2</td>
    <td class="tg-0pky">B2</td>
    <td class="tg-0pky">B2</td>
    <td class="tg-0pky">B3</td>
    <td class="tg-0pky">B3</td>
    <td class="tg-0pky">B3</td>
    <td class="tg-0pky">B4</td>
    <td class="tg-0pky">B4</td>
    <td class="tg-0pky">B4</td>
  </tr>
</tbody></table>

#### Species



## Local data parsing and plotting


