import pandas as pd
from os.path import join, exists
from os import walk, makedirs
from datetime import time, timedelta
import numpy as np
import sys
from logging import getLogger, DEBUG, INFO, StreamHandler, FileHandler, Formatter


def create_log(name, log_file):
    # Create a logger which is initialized for every experiment
    logger = getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(DEBUG)  # Set the base logger level

    # Create a file handler for logging to a file
    file_handler = FileHandler(log_file, mode="w")
    file_handler.setLevel(DEBUG)  # Set the file handler level

    # Create a console handler for logging to the console
    console_handler = StreamHandler()
    console_handler.setLevel(INFO)  # Set the console handler level

    # Create a formatter and set it for both handlers
    formatter = Formatter("%(asctime)s - %(levelname)s - Plate: %(name)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def parse_technical_data(data_dir, project, plate_name, logger):
    # Parses details about the experiment from the Metadata sheet
    df = pd.read_excel(
        join(data_dir, project, plate_name, "combined_metadata.xlsx"),
        sheet_name="Metadata",
    )
    exp_ID = project + "_" + plate_name
    experimenter = df["Experimenter's Name"]
    date = df["Date of Experiment (DD/MM/YY)"]
    device = df["Device Used"]
    temperature = df["Temperature"]
    shaking = df["Shaking (Y/N)"]
    co2 = df["CO2 (Y/N)"]
    technical_data = pd.DataFrame(
        {
            "exp_ID": exp_ID,
            "Experimenter": experimenter,
            "Date": date,
            "Device": device,
            "Temperature": temperature,
            "Shaking": shaking,
            "CO2": co2,
        }
    )
    for column, value in technical_data.items():
        if pd.isna(value.loc[0]):
            logger.error(column + " field in the Metadata sheet is empty.")
            sys.exit()
    logger.info("Succesfully parsed technical metadata.")
    return technical_data


def parse_sheet(meta, data_dir, project, plate_name, sheet_name, key_name, logger):
    # Parsed the information that have the format of the 96 well plate.
    # All fields are mandatory.
    df = pd.read_excel(
        join(data_dir, project, plate_name, "combined_metadata.xlsx"),
        sheet_name=sheet_name,
        index_col=0,
        keep_default_na=False,
    )
    for sample_name, sample in meta.items():
        well = sample["samples"][0]
        i, c = well[0], int(well[1:])
        value = df.at[i, c]
        meta[sample_name][key_name] = value
        if value == "":
            logger.error(
                "Missing value for " + i + str(c) + " in the " + sheet_name + " sheet."
            )
            sys.exit()
    logger.info("Succesfully parsed " + sheet_name + " metadata.")
    return meta


def parse_meta_data(data_dir, project, plate_name, logger):
    # Parses the sample names and the corresponding blanks from the Groups sheet.
    df = pd.read_excel(
        join(data_dir, project, plate_name, "combined_metadata.xlsx"),
        sheet_name="Groups",
        index_col=0,
    )
    sample_names = []
    blanks = 0
    for entry in df.to_numpy().flatten():
        # Samples must start with a capital S, followed by a number and the
        # name of the blank which must start with a B.
        # For example S00B00 where B00 is the name of the blank.
        if isinstance(entry, str):
            if entry[0] == "S":
                sample_names.append(entry)

    meta = {
        key: {
            "samples": [],
            "blanks": [],
            "linegroup": [],
            "species": None,
            "carbon_source": None,
            "cs_conc": None,
            "base_media": None,
            "inhibitor": None,
            "inhibitor_conc": None,
            "comments": None,
        }
        for key in set(sample_names)
    }
    # Storing well names of corresponding samples
    for c in df.columns:
        for i in df.index:
            well = i + str(c)
            entry = df.at[i, c]
            if isinstance(entry, str):
                if entry[0] == "S":
                    meta[df.at[i, c]]["samples"].append(well)
                    meta[df.at[i, c]]["linegroup"].append(
                        "_".join([project, plate_name, well])
                    )
                if entry[0] == "B":
                    blanks += 1

    # Stroring corresponding blank wells
    for sample in meta.keys():
        blank = sample[sample.find("B") :]
        for c in df.columns:
            for i in df.index:
                well = i + str(c)
                entry = df.at[i, c]
                if entry == blank:
                    meta[sample]["blanks"].append(well)

    if len(sample_names) > 0:
        logger.info(
            "Detected "
            + str(len(meta.keys()))
            + " samples and "
            + str(blanks)
            + " blanks."
        )
    else:
        logger.error("No samples found in the Groups sheet.")
        sys.exit()

    if blanks == 0:
        logger.warning("No blanks found in the Groups sheet.")

    meta = parse_sheet(
        meta, data_dir, project, plate_name, "Species", "species", logger
    )
    meta = parse_sheet(
        meta, data_dir, project, plate_name, "Carbon Source", "carbon_source", logger
    )
    meta = parse_sheet(
        meta, data_dir, project, plate_name, "CS Concentration", "cs_conc", logger
    )
    meta = parse_sheet(
        meta, data_dir, project, plate_name, "Base Media", "base_media", logger
    )
    meta = parse_sheet(
        meta, data_dir, project, plate_name, "Inhibitor", "inhibitor", logger
    )
    meta = parse_sheet(
        meta, data_dir, project, plate_name, "Inhibitor Conc", "inhibitor_conc", logger
    )
    meta = parse_sheet(
        meta, data_dir, project, plate_name, "Comments", "comments", logger
    )

    return meta


def parse_raw_data(dir, logger):
    # Parsed time series data, with columns Time, followed by well names.
    df = pd.read_excel(join(dir, "data.xlsx"))
    for c in df.columns[1:]:
        if str(c[0]).isalpha():
            pass
        else:
            logger.error(
                "Data must be a time series where the first columns is called Time, followed by the well names as further columns"
            )
            sys.exit()
    ts = []
    for i in df["Time"]:
        # Excel has a weird time formatting where format changes after 24 hours.
        # In case format is HH:MM:SS as time
        if type(i) is time:
            ts.append(i.hour * 60 * 60 + i.minute * 60 + i.second)
        # In case format is D:H:MM:SS
        elif type(i) is timedelta:
            ts.append(i.total_seconds())
        # In case format is HH:MM:SS as string
        elif type(i) is str:
            hour, minute, second = i.split(":")
            ts.append(int(hour) * 60 * 60 + int(minute) * 60 + int(second))
        else:
            logger.error("Format of time stamps is not recognized")
            sys.exist()
    df["Time"] = np.array(ts) / 60 / 60
    return df


def parse_meta_to_df(meta, raw, project, plate_name):
    # Converts metadate stored in dictionary into tables.
    df_run = pd.DataFrame()
    df_carbon_source = pd.DataFrame()
    df_species = pd.DataFrame()
    df_inhibitor = pd.DataFrame()
    df_measurement = pd.DataFrame()
    df_comments = pd.DataFrame()
    df_measurement = pd.DataFrame()

    measurement_dfs = []

    for sample_name, sample in meta.items():
        blank = raw[sample["blanks"]].mean(axis=1)
        for wellID in range(len(sample["samples"])):
            well = sample["samples"][wellID]
            linegroup = sample["linegroup"][wellID]
            df_run = pd.concat(
                [
                    df_run,
                    pd.DataFrame(
                        {
                            "project": project,
                            "exp_ID": project + "_" + plate_name,
                            "linegroup": linegroup,
                        },
                        index=[0],
                    ),
                ]
            )
            df_carbon_source = pd.concat(
                [
                    df_carbon_source,
                    pd.DataFrame(
                        {
                            "linegroup": linegroup,
                            "carbon_source": sample["carbon_source"],
                            "cs_conc": sample["cs_conc"],
                            "base_media": sample["base_media"],
                        },
                        index=[0],
                    ),
                ]
            )
            df_species = pd.concat(
                [
                    df_species,
                    pd.DataFrame(
                        {"linegroup": linegroup, "species": sample["species"]},
                        index=[0],
                    ),
                ]
            )
            df_inhibitor = pd.concat(
                [
                    df_inhibitor,
                    pd.DataFrame(
                        {
                            "linegroup": linegroup,
                            "inhibitor": sample["inhibitor"],
                            "inhibitor_conc": sample["inhibitor_conc"],
                        },
                        index=[0],
                    ),
                ]
            )
            df_comments = pd.concat(
                [
                    df_comments,
                    pd.DataFrame(
                        {"linegroup": linegroup, "comments": sample["comments"]},
                        index=[0],
                    ),
                ]
            )

            measurement = raw[well] - blank
            cur_measurement_df = pd.DataFrame(
                {
                    "linegroup": linegroup,
                    "time": raw["Time"],
                    "measurement": measurement,
                }
            )
            measurement_dfs.append(cur_measurement_df)

    df_measurement = pd.concat(measurement_dfs)
    return (
        df_run,
        df_carbon_source,
        df_species,
        df_inhibitor,
        df_comments,
        df_measurement,
    )


def main(data_dir, project):
    # Main function to parse the data of the different experiments of the same project. Stores parsed tables in export directory.
    # Creating necessary folders
    save_folder = join("export", project)
    makedirs(save_folder, exist_ok=True)
    log_dir = join("export", project, "logs")
    makedirs(log_dir, exist_ok=True)
    # Finds different experiements in the same projects
    dir = join(data_dir, project)
    plate_names = next(walk(dir))[1]
    # Creates dataframes for combined experiments
    technical_data = pd.DataFrame()
    run_data = pd.DataFrame()
    carbon_source_data = pd.DataFrame()
    species_data = pd.DataFrame()
    inhibitor_data = pd.DataFrame()
    measurement_data = pd.DataFrame()
    comment_data = pd.DataFrame()
    # Iterates over different experiments
    for plate_name in plate_names:
        log_file = join("export", project, "logs", plate_name + ".log")
        logger = create_log(plate_name, log_file)
        # Parses meta data for the samples
        meta = parse_meta_data(data_dir, project, plate_name, logger)
        # Parsed meta data for the experiment.
        technical_data = pd.concat(
            [
                technical_data,
                parse_technical_data(data_dir, project, plate_name, logger),
            ]
        )
        # Parses measurement data
        raw = parse_raw_data(join(data_dir, project, plate_name), logger)
        # Creates tables for the meta data for the samples
        run, carbon_source, species, inhibitor, comment, measurement = parse_meta_to_df(
            meta, raw, project, plate_name
        )
        run_data = pd.concat([run_data, run])
        carbon_source_data = pd.concat([carbon_source_data, carbon_source])
        species_data = pd.concat([species_data, species])
        inhibitor_data = pd.concat([inhibitor_data, inhibitor])
        comment_data = pd.concat([comment_data, comment])
        measurement_data = pd.concat([measurement_data, measurement])

    # Stores parsed data in export directory
    technical_data.to_csv(join(save_folder, "technical_data.csv"), index=False)
    run_data.to_csv(join(save_folder, "run_data.csv"), index=False)
    carbon_source_data.to_csv(join(save_folder, "carbon_source_data.csv"), index=False)
    species_data.to_csv(join(save_folder, "species_data.csv"), index=False)
    inhibitor_data.to_csv(join(save_folder, "inhibitor_data.csv"), index=False)
    comment_data.to_csv(join(save_folder, "comment_data.csv"), index=False)
    measurement_data.to_csv(join(save_folder, "measurement_data.csv"), index=False)


project = "240808_acetate_glutarate_l-glutamate"
main("data", project)
