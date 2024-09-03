from dash import dcc, html, register_page
import dash_bootstrap_components as dbc
import pandas as pd
from os.path import join

register_page(__name__, path="/Documentation", name="Documentation")  # '/' is home page
f_meta = join("data", "240623_growth_phenotyping", "at", "combined_metadata.xlsx")
f_data = join("data", "240623_growth_phenotyping", "at", "data.xlsx")

layout = html.Div(
    [
        # Inline CSS for smooth scrolling
        html.Div(
            [
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content", style={"scroll-behavior": "smooth"}),
            ]
        ),
        # Table of Contents
        html.Div(
            [
                html.H2("Table of Contents"),
                html.Ul(
                    [
                        html.Li(html.A("Introduction", href="#Introduction")),
                        html.Li(
                            [
                                html.A(
                                    "Adding data within the Mitri lab",
                                    href="#Adding-data-within-the-Mitri-lab",
                                ),
                                html.Ul(
                                    [  # Sublist for the second main section
                                        html.Li(
                                            html.A(
                                                "Preparing data submission",
                                                href="#Preparing-data-submission",
                                            )
                                        ),
                                        html.Li(
                                            html.A(
                                                "Filling out the combined_metadata table",
                                                href="#Filling-out-the-combined-metadata-table",
                                            )
                                        ),
                                        html.Ul(
                                            [
                                                html.Li(
                                                    html.A(
                                                        "Metadata",
                                                        href="#Metadata",
                                                    ),
                                                ),
                                                html.Li(
                                                    html.A(
                                                        "Groups",
                                                        href="#Groups",
                                                    ),
                                                ),
                                                html.Li(
                                                    html.A(
                                                        "Species",
                                                        href="#Species",
                                                    ),
                                                ),
                                                html.Li(
                                                    html.A(
                                                        "Base Media",
                                                        href="#Base-media",
                                                    ),
                                                ),
                                                html.Li(
                                                    html.A(
                                                        "Carbon source",
                                                        href="#Carbon-source",
                                                    ),
                                                ),
                                                html.Li(
                                                    html.A(
                                                        "CS Concentration",
                                                        href="#CS-Concentration",
                                                    ),
                                                ),
                                                html.Li(
                                                    html.A(
                                                        "Inhibitor and Inhibitor Conc",
                                                        href="#Inhibitor-and-Inhibitor-Conc",
                                                    ),
                                                ),
                                                html.Li(
                                                    html.A(
                                                        "Comments",
                                                        href="#Comments",
                                                    ),
                                                ),
                                            ],
                                        ),
                                        html.Li(
                                            html.A(
                                                "Filling out the data table",
                                                href="#Filling-out-the-data-table",
                                            ),
                                        ),
                                        html.Li(
                                            html.A(
                                                "Submitting data to the databasse",
                                                href="#Submitting-data-to-the-database",
                                            ),
                                        ),
                                    ]
                                ),
                                html.Li(
                                    html.A(
                                        "Local data parsing and plotting",
                                        href="#Local-data-parsing-and-plotting",
                                    ),
                                ),
                                html.Li(
                                    html.A(
                                        "Working with data exported via the dashboard",
                                        href="#Working-with-data-exported-via-the-dashboard",
                                    ),
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),
        # Content with Headers
        html.Div(
            [
                html.H1("Introduction", id="Introduction"),
                dcc.Markdown("""Curves lets you parse 96-well plate OD time series along with relevant metadata. Adding metadata to your growth curves not only simplifies data analysis but also enhances the reproducibility of your experiments. Additionally, Curves makes your data accessible and downloadable online through an interactive dashboard, enabling quick analysis and easy data sharing.  
                You can also use the dashboard to browse existing growth curve data for various bacteria and carbon sources, allowing you to streamline your experimental planning and assisting in deciding on conditions to test your hypothesis experimentally.
                Future versions will also include the ability to fit various growth models, with the goal of creating a database of experimentally determined growth parameters that can be used for theoretical modeling.
                """),
                html.H1(
                    "Adding data within the Mitri lab",
                    id="Adding-data-within-the-Mitri-lab",
                ),
                html.H2("Preparing data submission", id="Preparing-data-submission"),
                dcc.Markdown("""The code for `curves` is on [GitHub](https://github.com/nahanoo/curves). This repository is cloned in the `NAS` from where data is submitted. If you want to parse and visualize data yourself without submitting it, clone the repository locally. See the section [Local data parsing and plotting](#Local-data-parsing-and-plotting). 
                `Curves` treats each 96-well plate as a single experiment. For every experiment, you are required to complete a metadata file called `combined_metadata.xlsx` and a data file called `data.xlsx`. Multiple experiments can be grouped into projects, with data parsed on a per-project basis. This grouping is reflected in the file structure as follows:"""),
                dcc.Markdown("""
                ```bash                 
                data/
                ├─ project/
                │  ├─ experiment/
                │  │  ├─ combined_metadata.xlsx
                │  │  ├─ data.xlsx
                ```
                """),
                dcc.Markdown("""
                To submit data, navigate the curves `data` directory on the `NAS` located in `FAC/FBM/DMF/smitri/default/D2c/curves/data`. Within the data directory, create a new folder for your project.  It is recommended to include the date in YY/MM/DD format along with a short, meaningful name. For example, you might name the folder `240820_at_phenotyping`. Within the project folder create a new folder for your experiment with a meaningful name, for example `acetate_adenosine_cysteine_arabinose`. Within the experiment folder, copy the `combined_metadata.xlsx` and the `data.xlsx` data from the templates located in:"""),
                dcc.Markdown("""
                ```bash
                data/
                ├─ TEMPLATE_PROJECT
                │  ├─ TEMPLATE_EXPERIMENT
                │  │  ├─ combined_metadata.xlsx
                │  │  ├─ data.xlsx
                ``` 
                """),
                html.H2(
                    "Filling out the combined_metadata",
                    id="Filling-out-the-combined-metadata-table",
                ),
                dcc.Markdown("""
                The `combined_metadata.xlsx` contains multiple sheets which includes all the metadata of your experiment. Below is explained how each sheet needs to be filled out.
                """),
                html.H3("Metadata", id="Metadata"),
                dcc.Markdown("""The Metadata sheet contains mandatory information about the technical aspects of your experiment.
                """),
                dbc.Table.from_dataframe(pd.read_excel(f_meta, sheet_name="Metadata")),
                html.H3("Groups", id="Groups"),
                dcc.Markdown("""In this sheet, you specify in which wells replicates of a sample and the corresponding blanks are located. Sample IDs must start with `S`, followed by the blank ID, which must start with `B`, for example, S1B1. Replicates of the same sample share the same name. Wells that are not used must be left empty.  
                In the example below, Sample 1 has three replicates in A1-A3, with corresponding blanks in H10-H12"""),
                dbc.Table.from_dataframe(pd.read_excel(f_meta, sheet_name="Groups")),
                html.H3("Species", id="Species"),
                dcc.Markdown(
                    """The Species sheet is used to indicate which species was grown in each well. Currently, Curves only supports monoculture data. For every well specified in the `Groups` sheet, you must define the full name of the grown bacteria. In the example below, all samples previously specified in Groups are Agrobacterium tumefaciens. """
                ),
                html.H3("Base media", id="Base-media"),
                dcc.Markdown("""If you conduct your experiments in simple media, a base media containing all necessary resources in excess—except for the carbon source—is used. This base media is specified in this sheet. You can provide additional information in the `Comments` sheet. In the example above, the experiment was done in a simple media with M9 and HMB as base media.  
                If you did your experiments in rich media such as TSB, enter TSB."""),
                dbc.Table.from_dataframe(
                    pd.read_excel(f_meta, sheet_name="Base Media")
                ),
                html.H3("Carbon source", id="Carbon-source"),
                dcc.Markdown(
                    """This sheet stores the information which carbon source was used in which well. If the experiment was done in rich media, enter the name of the rich media."""
                ),
                dbc.Table.from_dataframe(
                    pd.read_excel(f_meta, sheet_name="Carbon Source")
                ),
                html.H3("CS concentration", id="CS-Concentration"),
                dcc.Markdown(
                    """This sheet stores the information which carbon source was used in which well. If the experiment was done in rich media, enter the name of the rich media."""
                ),
                html.H3(
                    "Inhibitor and Inhibitor Conc", id="Inhibitor-and-Inhibitor-Conc"
                ),
                dcc.Markdown(
                    """If you used inhibitors for your experiments, such as antibiotics, enter the names of the inhibitors in the according wells and state the concentration in the `Inhibitor Conc` sheet. The concentration in the `Inhibitor Conc` is in µM. If you didn't use any inhibitors, enter None in the `Inhibitor` and 0 in the `Inhibitor Conc` sheets for the wells you used."""
                ),
                html.H3("Comments", id="Comments"),
                dcc.Markdown(
                    """Here you can provide additional information for the different wells, such as protocols, observations or other useful information. If you have no comments, add None for the used wells."""
                ),
                html.H2("Filling out the data table", id="Filling-out-the-data-table"),
                dcc.Markdown(
                    """The `data.xlsx` contains the time series OD data with time and the different wells as columns. You can find the data in this format for most plate readers if you export your data in excel.  
                    Below you can find an example for three wells for the first 5 hours."""
                ),
                dbc.Table.from_dataframe(
                    pd.read_excel(f_data)[["Time", "A1", "A2", "A3"]].loc[:9]
                ),
                html.H1(
                    "Submitting data to the database",
                    id="Submitting-data-to-the-database",
                ),
                dcc.Markdown(
                    """For now you can contact [Prajwal Padmanabha](https://applicationspub.unil.ch/interpub/noauth/php/Un/UnPers.php?PerNum=1262133&LanCode=8) or [Eric Ulrich](https://applicationspub.unil.ch/interpub/noauth/php/Un/UnPers.php?PerNum=1242399&LanCode=8) to add the data to the dashboard for visualization and exporting. Shortly after, the data will be available for exploration and exportation under [https://curves.onrender.com/](https://curves.onrender.com/)."""
                ),
                html.H1(
                    "Local data parsing and plotting",
                    id="Local-data-parsing-and-plotting",
                ),
                dcc.Markdown(
                    """If you want to parse and visualize the data yourself you can do so by cloning the [curves](https://github.com/nahanoo/curves) repository locally."""
                ),
                dcc.Markdown("""

                ```bash
                git clone https://github.com/nahanoo/curves.git
                ```
                """),
                dcc.Markdown("""
                You fill out the `combined_metadata.xlsx` and the `data.xlsx` file as explained in the section [Adding data within the Mitri lab](#Adding-data-within-the-Mitri-lab).
                within an experiment folder belonging to a project. Next, execute the `parse_data.py` script with the project name as an argument."""),
                dcc.Markdown("""
                ```python
                python parse_data.py your_project_name
                ```
                """),
                dcc.Markdown(
                    """The logger of the script will provide you with information about the success of the parsing and tell you if you forgot to provide certain information for a well in the `combined_metadata.xlsx` file."""
                ),
                dcc.Markdown(
                    """The exported parsed data is located in several files under the following directory."""
                ),
                dcc.Markdown("""
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
                """),
                dcc.Markdown("""This acts as a backbone for the dasbhoard and is for now a little bit clumsy to work with directly. You can join the different tables via the `linegroup` column. For now it's easier to work with the data exported from the dashboard. See also [Working with data exported via the dasboard](#working-with-data-exported-via-the-dasboard).
                After you parsed your data, you can execute the `dashboard.py` script for data visualization."""),
                dcc.Markdown("""
                ```python
                python dashboard.py
                ```
                """),
                dcc.Markdown(
                    """Select your project and start exploring the data. You can export the data buy clicking the `Download` button."""
                ),
                html.H2(
                    "Working with data exported via the dashboard",
                    id="Working-with-data-exported-via-the-dashboard",
                ),
                dcc.Markdown(
                    """After you selected the conditions that are interesting for you in the `Export Data` tab, you can download the data by clicking the Download Data button.
                    This gives you a zip file containing two files, `measurements.csv` and `metadata.csv`. You can filter the Metadata according to your interests and mask the measurements. Below is a short example how this can be done."""
                ),
                dcc.Markdown(
                    """
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
                """
                ),
            ]
        ),
    ]
)
