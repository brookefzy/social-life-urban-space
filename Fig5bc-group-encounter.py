"""Plot Figure 5 BC: Pedestrian group encounters over time"""

import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd
import gc

# plot one location one plot
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
from config.setting import Setup

##### Pre set up for the plot #################################################################
color_dict = Setup.COLOR_DICT
FPS_HISTORY = Setup.FPS_HISTORY
STAYTHREDS = (
    Setup.TAYTHREDS
)  # minimum second of time for a person to be considered as stayed. If a person
SELECT_STYTHRED = Setup.SELECT_STYTHRED  # selected threshold for the plot
# minimum observation time for a person to consider as a valid observation
VALID_TRHEAD = Setup.VALID_TRHEAD
STAY_VARIABLE = Setup.STAY_VARIABLE  # selected for the main analysis.
locls = Setup.LOC_LS
GRAPHIC_FOLDER = "./_graphics"


def get_full_frame(alldf_update):
    framecount_min = (
        alldf_update.groupby(
            ["decades", "video_location", "video_id", "minute_from_start"]
        )
        .agg(
            {
                "frame_id": "nunique",
            }
        )
        .reset_index()
        .rename(
            columns={
                "frame_id": "frame_count",
            }
        )
    )
    return framecount_min


def get_time_agg(df):
    """df is defnied by people's stages, in group, stay, move, etc
    Here we need to maintain the video_id given that some times a minute can cross two videos, then they may share frame ids.
    """
    # This function aggregates number of people per unique frames and then sum all peopel across frames.
    # therefore one person can be counted more than once in one minutes.
    person_frame = (
        df.groupby(
            ["decades", "video_location", "video_id", "frame_id", "minute_from_start"]
        )
        .agg({"track_id": "nunique"})
        .reset_index()
        .rename(
            columns={
                "track_id": "pedestrian_count",
            }
        )
    )
    person_time = (
        person_frame.groupby(
            ["decades", "video_location", "video_id", "minute_from_start"]
        )
        .agg(
            {
                "pedestrian_count": "sum",
            }
        )
        .reset_index()
    )
    return person_time


def create_rb_df(alldf):
    groupdf = alldf[alldf["is_group"] == True].reset_index(drop=True)
    emerging_groupdf = alldf[alldf["is_emerging_group"] == True].reset_index(drop=True)
    person_time = get_time_agg(alldf)
    person_group_time = get_time_agg(groupdf)
    emerging_group_time = get_time_agg(emerging_groupdf)
    framecount_min = get_full_frame(alldf)
    timedf = (
        framecount_min.merge(
            person_time,
            on=["decades", "minute_from_start", "video_location", "video_id"],
            how="left",
        )
        .merge(
            person_group_time,
            on=["decades", "minute_from_start", "video_location", "video_id"],
            how="left",
            suffixes=("_all", "_group"),
        )
        .fillna(0)
        .merge(
            emerging_group_time,
            on=["decades", "minute_from_start", "video_location", "video_id"],
            how="left",
            suffixes=("_group", "_emerging_group"),
        )
        .fillna(0)
        .rename(columns={"pedestrian_count": "pedestrian_count_emerging_group"})
    )
    for delta in range(2, 11):
        emerging_group_time_delta = get_time_agg(
            alldf[alldf[f"is_emerging_group_{delta}"] == True]
        )
        timedf = (
            timedf.merge(
                emerging_group_time_delta,
                on=["decades", "minute_from_start", "video_location", "video_id"],
                how="left",
            )
            .fillna(0)
            .rename(
                columns={
                    "pedestrian_count": "pedestrian_count_emerging_group_" + str(delta)
                }
            )
        )
    timedf_min = (
        timedf.groupby(["decades", "video_location", "video_id", "minute_from_start"])
        .max()
        .reset_index()
    )
    timedf_min["pedestrian_count_group_per"] = (
        timedf_min["pedestrian_count_group"] / timedf_min["pedestrian_count_all"]
    )
    timedf_min["pedestrian_count_emerging_group_per"] = (
        timedf_min["pedestrian_count_emerging_group"]
        / timedf_min["pedestrian_count_all"]
    )
    for delta in range(2, 11):
        timedf_min[f"pedestrian_count_emerging_group_{delta}_per"] = (
            timedf_min[f"pedestrian_count_emerging_group_{delta}"]
            / timedf_min["pedestrian_count_all"]
        )
    option_dict = {
        "pedestrian_count_emerging_group_per": "mean",
        "pedestrian_count_group_per": "mean",
    }
    for delta in range(2, 11):
        option_dict[f"pedestrian_count_emerging_group_{delta}_per"] = "mean"
    spc = (
        timedf_min.groupby(["video_location", "video_id", "decades"])
        .agg(option_dict)
        .groupby(["video_location", "decades"])
        .mean()
        .reset_index()
    )
    viz = spc.groupby("decades").mean().reset_index()
    # convert the viz to a long format
    longdf = pd.DataFrame()
    for delta in range(2, 11):
        temp = viz[["decades", f"pedestrian_count_emerging_group_{delta}_per"]].rename(
            columns={
                f"pedestrian_count_emerging_group_{delta}_per": "pedestrian_count_emerging_group_per"
            }
        )
        temp["delta"] = delta
        if delta == 2:
            longdf = temp
        else:
            longdf = longdf.append(temp)

    longdf_loc = pd.DataFrame()
    for delta in range(2, 11):
        temp = spc[
            [
                "video_location",
                "decades",
                f"pedestrian_count_emerging_group_{delta}_per",
            ]
        ].rename(
            columns={
                f"pedestrian_count_emerging_group_{delta}_per": "pedestrian_count_emerging_group_per"
            }
        )
        temp["delta"] = delta
        if delta == 2:
            longdf_loc = temp
        else:
            longdf_loc = longdf_loc.append(temp)
    return longdf, longdf_loc


def plot_rb_df(longdf):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=longdf,
        x="delta",
        y="pedestrian_count_emerging_group_per",
        hue="decades",
        ax=ax,
        palette="husl",
    )
    # set y axis to percentage
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_xlabel("From Individual to Group Time (s)")
    ax.set_ylabel("%People in a spontenous group")
    # hide the right and top spines
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    # add major grids
    ax.yaxis.grid(color="gray", linestyle="--", linewidth=0.5)
    ax.xaxis.grid(color="gray", linestyle="--", linewidth=0.5)
    fig.savefig(
        f"{GRAPHIC_FOLDER}/Fig5b-emerging_group_percentage.png",
        dpi=200,
        bbox_inches="tight",
        pad_inches=0.1,
    )


def plot_by_site(longdf_loc):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(
        data=longdf_loc,
        x="delta",
        y="pedestrian_count_emerging_group_per",
        hue="video_location",
        style="decades",
        palette="husl",
    )
    # set y axis to percentage
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_xlabel("From Individual to Group Time (s)")
    ax.set_ylabel("%People in a spontenous group")
    # hide the right and top spines
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    # set legend to be outside
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    # add major grids
    ax.yaxis.grid(color="gray", linestyle="--", linewidth=0.5)
    ax.xaxis.grid(color="gray", linestyle="--", linewidth=0.5)
    fig.savefig(
        f"{GRAPHIC_FOLDER}/Fig5c-emerging_group_percentage_loc.svg",
        dpi=300,
        format="svg",
        bbox_inches="tight",
        pad_inches=0.1,
    )


def main():
    alldf = pd.read_csv("./_data/c_alldf_update.csv")
    interval_1980s = FPS_HISTORY / 10
    alldf["fps"] = np.where(alldf["decades"] == "2010s", 29.97, interval_1980s)
    gc.collect()
    print("data loaded")
    longdf, longdf_loc = create_rb_df(alldf)
    plot_rb_df(longdf)
    # save the table:
    print("Save the Table S4 for the supplementary material")
    table_s4 = longdf.pivot(
        index="delta", columns="decades", values="pedestrian_count_emerging_group_per"
    )
    table_s4["2010s-1980s"] = table_s4["2010s"] - table_s4["1980s"]
    table_s4.to_csv(f"{GRAPHIC_FOLDER}/c_table_s4.csv")
    plot_by_site(longdf_loc)
    print("Save Fig 5b and 5c")


if __name__ == "__main__":
    main()
