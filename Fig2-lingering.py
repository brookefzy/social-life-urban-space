"""This scripts plot the following tables and figures:
- Fig2
- Fig S5-b
"""

import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd

# plot one location one plot
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import datetime
import gc
from config.setting import Setup

plt.rcParams["figure.figsize"] = [3, 4]
plt.rcParams["figure.autolayout"] = True
plt.rcParams["svg.fonttype"] = "none"
colors = sns.color_palette("husl", 9)

graphicfolder = "./_graphics"
if not os.path.exists(graphicfolder):
    os.makedirs(graphicfolder)
DATA_FOLDER = "./_data/curated"
##### Pre set up for the plot #################################################################
color_dict = Setup.COLOR_DICT
CURRENT_VIDEO = "v2"
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")
FPS_HISTORY = Setup.FPS_HISTORY
STAYTHREDS = (
    Setup.STAYTHREDS
)  # minimum second of time for a person to be considered as stayed. If a person
SELECT_STYTHRED = Setup.SELECT_STYTHRED  # selected threshold for the plot
# minimum observation time for a person to consider as a valid observation
VALID_TRHEAD = Setup.VALID_TRHEAD
STAY_VARIABLE = Setup.STAY_VARIABLE  # selected for the main analysis.
locls = Setup.LOC_LS


def data_preprocessing(alldf, staythreds=STAYTHREDS):
    interval_1980s = FPS_HISTORY / 10
    stay_variable = "stay_adjusted_{staythred}"
    alldf["fps"] = np.where(alldf["decades"] == "2010s", 29.97, interval_1980s)
    alldf["minute_from_start"] = alldf["second_from_start"] // 60

    print(alldf.shape[0], " rows. original")
    alldf["frame_count_person"] = alldf.groupby(["video_id", "fps", "track_id"])[
        "frame_id"
    ].transform("nunique")
    alldf["second_count_person"] = alldf["frame_count_person"] / alldf["fps"]
    for staythred in staythreds:
        print("calculating stay for ", staythred)
        alldf[stay_variable.format(staythred=staythred)] = np.where(
            alldf["second_count_person"] < staythred, False, alldf["stay"]
        )
        # estimate the total time stayed by each person
        alldf[f"stay_count_{staythred}"] = alldf.groupby(["video_id", "track_id"])[
            stay_variable.format(staythred=staythred)
        ].transform("sum")

    alldf = alldf[alldf["second_count_person"] >= VALID_TRHEAD].reset_index(drop=True)

    # hard code to only keep the conservative groups
    alldf["is_group"] = np.where(
        alldf["is_group_loose"] == False, False, alldf["is_group"]
    )
    print(alldf.shape[0], " rows. After dropping invalid detections")
    print("done calculating person frames appeared")
    print(alldf["second_count_person"].describe())
    return alldf


def get_robust_staythred(alldf, staythred):
    if staythred == "stay":
        vari = "stay"
    else:
        vari = "stay_adjusted_{staythred}".format(staythred=staythred)
    staysummary = (
        alldf.groupby(["decades", "video_location", "video_id", vari, "frame_id"])[
            "track_id"
        ]
        .nunique()
        .reset_index()
        .pivot(
            columns=[vari],
            index=["decades", "video_location", "video_id", "frame_id"],
            values="track_id",
        )
        .reset_index()
        .fillna(0)
    )
    staysummary["stay_per"] = staysummary[True] / (
        staysummary[True] + staysummary[False]
    )
    # stayresult = staysummary.groupby(['decades','video_location'])['stay_per'].mean().reset_index()
    staysummary["stay_thred"] = staythred
    return staysummary


# summarize the number of person stayed per decades per location before and after adjusting for the staying threshold
def get_robustness_all(alldf):
    robust_summary = []
    for staythred in STAYTHREDS:
        robust_summary.append(get_robust_staythred(alldf, staythred))

    robust_summary = pd.concat(robust_summary).reset_index(drop=True)
    robust_summary.columns = [str(x) for x in robust_summary.columns]
    robust_summary["stay_per"] = robust_summary["True"] / (
        robust_summary["True"] + robust_summary["False"]
    )
    robust_summary_video = (
        robust_summary.groupby(["decades", "video_location", "video_id", "stay_thred"])[
            "stay_per"
        ]
        .mean()
        .reset_index()
    )
    return robust_summary, robust_summary_video


# choose 4 seconds for the study given the observed trend
# export a table for comparing percentage of people stay per decades
def get_plot(robust_summary, select_thred=SELECT_STYTHRED, file_suffix="all"):
    robust_summary_viz = (
        robust_summary.groupby(["decades", "video_location", "stay_thred"])["stay_per"]
        .mean()
        .reset_index()
    )
    vizdata = robust_summary_viz[robust_summary_viz["stay_thred"] == select_thred]
    print("Selecte threshold for the visualization: ", select_thred)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=vizdata, hue="decades", y="stay_per", x="video_location", palette="husl"
    )
    ax.set_title("% lingers from 1980s to 2010s per location")
    ax.set_xlabel("", fontsize=12)

    ax.grid(which="major", axis="both", linestyle="--")
    ax.set_ylabel("%People linger", fontsize=12)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    # move the legend outside of the plot
    ax.legend(
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        borderaxespad=0,
        fontsize="large",
        title_fontsize=7,
    )

    sns.despine()

    fig.savefig(
        os.path.join(
            graphicfolder,
            f"Fig2-stay_per_decades_{CURRENT_VIDEO}_{select_thred}_{file_suffix}.png",
        ),
        format="png",
        dpi=300,
    )


# pull all locations together
def plot_all_sites(robust_summary, select_thred=SELECT_STYTHRED, file_suffix="all"):
    robust_summary_viz = (
        robust_summary.groupby(["decades", "video_location", "stay_thred"])["stay_per"]
        .mean()
        .reset_index()
    )
    vizdata = robust_summary_viz[
        robust_summary_viz["stay_thred"] == select_thred
    ].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(3, 4))
    sns.barplot(
        data=vizdata,
        x="decades",
        y="stay_per",
        palette="husl",
        width=0.7,
        errwidth=0,
        capsize=0,
    )
    ax.set_title("% lingers from 1980s to 2010s per location")
    ax.set_xlabel("Decades", fontsize=12)

    ax.grid(which="major", axis="both", linestyle="--")
    ax.set_ylabel("%People linger", fontsize=12)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    # move the legend outside of the plot

    sns.despine()
    fig.savefig(
        os.path.join(
            graphicfolder,
            f"Fig2-stay_per_decades_allloc_{CURRENT_VIDEO}_{select_thred}_{file_suffix}.png",
        ),
        format="png",
        dpi=300,
    )


def supple_robustness(robust_summary_video):
    # plot S5 -b
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.boxplot(
        data=robust_summary_video,
        x="stay_thred",
        y="stay_per",
        hue="decades",
        fill=False,
        width=0.7,
        gap=0.2,
        palette="husl",
        linewidth=1,
        # hide outliers
        flierprops=dict(markerfacecolor="0.75", markersize=1),
    )
    ax.set_title("Mean of all location - Robustness test")
    ax.set_xlabel("Seconds of observation time", fontsize=12)
    # change y xis to percentage
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    ax.grid(which="major", axis="both", linestyle="--")
    ax.set_ylabel("Percentage of people stay", fontsize=12)
    sns.despine()
    fig.savefig(
        os.path.join(
            graphicfolder, f"Fig2-stay_observation_robustness_test_{CURRENT_VIDEO}.png"
        ),
        dpi=300,
        format="png",
    )


def main():
    alldf = pd.read_csv(Setup.MAIN_PATH)
    alldf = data_preprocessing(alldf)
    # hard code to only keep the conservative groups
    singles = alldf[alldf["is_group"] == False].reset_index(drop=True)
    # use this to calculate the stay for each selected thredshold and location
    robust_summary, robust_summary_video = get_robustness_all(alldf)
    gc.collect()
    print("*" * 100)
    print("Now Plotting Fig-2 Lingering site by site")
    get_plot(robust_summary, select_thred=SELECT_STYTHRED)
    print("*" * 100)
    print("Now Plotting Fig-2 Lingering all sites together")
    plot_all_sites(robust_summary, select_thred=SELECT_STYTHRED)

    # Singles only
    print("*" * 100)
    print("Now Plotting Fig-2 Lingering site by site for singles")
    robust_summary_singles, robust_summary_video_singles = get_robustness_all(singles)
    get_plot(
        robust_summary_singles, select_thred=SELECT_STYTHRED, file_suffix="singles"
    )
    print("*" * 100)
    print("Now Plotting Fig-2 Lingering all sites together for singles")
    plot_all_sites(
        robust_summary_singles, select_thred=SELECT_STYTHRED, file_suffix="singles"
    )

    print("Now summarize the data for supplemental materials")

    stay_summary = get_robust_staythred(alldf, SELECT_STYTHRED)
    stay_summary["total"] = stay_summary[False] + stay_summary[True]

    # get the percentage of singles staying
    stay_summary_single = get_robust_staythred(singles, SELECT_STYTHRED)
    print(SELECT_STYTHRED)
    # get the percentage of groups staying
    stay_summary_group = get_robust_staythred(
        alldf[alldf["is_group"] == True], SELECT_STYTHRED
    )

    # merge summary
    allsummary = stay_summary.merge(
        stay_summary_single.drop([False, True], axis=1),
        on=["decades", "video_location", "video_id", "frame_id"],
        suffixes=["", "_single"],
        how="left",
    ).merge(
        stay_summary_group.drop([False, True], axis=1),
        on=["decades", "video_location", "video_id", "frame_id"],
        suffixes=["", "_group"],
        how="left",
    )
    allsummary.rename(
        columns={True: "stay", False: "move", "total": "total_pedestrian"}, inplace=True
    )
    allsummary.to_csv(os.path.join(DATA_FOLDER, f"c_stay_summary.csv"), index=False)


if __name__ == "__main__":
    main()
