import pandas as pd
import os
from os.path import join
from functools import reduce

parsed_data_dir = "export"
parsed_projects = next(os.walk(parsed_data_dir))[1]
update_flag = False

# Load the data
try:
    pooled_df_joint_metadata = pd.read_csv("metadata/pooled_df_joint_metadata.csv")
    file_present = True
except FileNotFoundError:
    pooled_df_joint_metadata = pd.DataFrame()
    file_present = False
for project in parsed_projects:
    df_technical = pd.read_csv(join(parsed_data_dir, project, "technical_data.csv"))
    df_species = pd.read_csv(join(parsed_data_dir, project, "species_data.csv"))
    df_carbon_source = pd.read_csv(
        join(parsed_data_dir, project, "carbon_source_data.csv")
    )
    
    df_comments = pd.read_csv(join(parsed_data_dir, project, "comment_data.csv"))
    df_run = pd.read_csv(join(parsed_data_dir, project, "run_data.csv"))
    df_inhibitor = pd.read_csv(join(parsed_data_dir, project, "inhibitor_data.csv"))

    df_joint_technical = df_run.merge(df_technical, on="exp_ID", how="outer")
    df_joint_metadata = reduce(
        lambda x, y: pd.merge(x, y, on="linegroup", how="outer"),
        [df_joint_technical, df_species, df_carbon_source,df_inhibitor, df_comments],
    )

    new_exp_IDs = df_technical["exp_ID"].unique()
    if not file_present:
        pooled_df_joint_metadata = pd.concat([pooled_df_joint_metadata, df_joint_metadata])
        update_flag = True
        file_present = True
        continue

    existing_exp_IDs = pooled_df_joint_metadata["exp_ID"].unique()
    to_add_exp_IDs = list(set(new_exp_IDs) - set(existing_exp_IDs))

    if len(to_add_exp_IDs) > 0:
        df_joint_metadata = df_joint_metadata[df_joint_metadata["exp_ID"].isin(to_add_exp_IDs)]
        pooled_df_joint_metadata = pd.concat([pooled_df_joint_metadata, df_joint_metadata])
        update_flag = True
    else:
        continue

if update_flag:
    print("Updated metadata successfully")
else:
    print("No new metadata to add")
pooled_df_joint_metadata.to_csv("metadata/pooled_df_joint_metadata.csv", index=False)

