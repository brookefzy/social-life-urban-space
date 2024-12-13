"""Plot Figure 5: Pedestrian Churn Over different thresholds"""

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
    Setup.STAYTHREDS
)  # minimum second of time for a person to be considered as stayed. If a person
SELECT_STYTHRED = Setup.SELECT_STYTHRED  # selected threshold for the plot
# minimum observation time for a person to consider as a valid observation
VALID_TRHEAD = Setup.VALID_TRHEAD
STAY_VARIABLE = Setup.STAY_VARIABLE  # selected for the main analysis.
locls = Setup.LOC_LS
GRAPHIC_FOLDER = "./_graphics"


def barplot_retention_time(frame_summary_update):
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=frame_summary_update,
        hue="decades",
        y="retention_seconds",
        x="video_location",
        palette="husl",
    )
    ax.set_title("Retention time from 1980s to 2010s per location")
    ax.set_xlabel("Decades", fontsize=12)

    ax.grid(which="major", axis="both", linestyle="--")
    ax.set_ylabel("Retention time/s", fontsize=12)

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
        os.path.join(GRAPHIC_FOLDER, "Fig5-retention_time_per_location.png"),
        format="png",
        dpi=300,
        bbox_inches="tight",
    )


def get_churn(alldf_frame, unit_col, interval_churn):
    key = ["decades", "video_location", "video_id"]
    alldf_frame[unit_col] = alldf_frame[unit_col].astype(int)
    alldf_frame_summary = alldf_frame.merge(
        alldf_frame.drop(["frame_id"], axis=1),
        left_on=key + ["frame_id"],
        right_on=key + [unit_col],
        suffixes=("", "_" + unit_col),
    ).drop([unit_col + "_" + unit_col], axis=1)
    alldf_frame_summary["person_left"] = alldf_frame_summary.apply(
        lambda x: len(set(x["track_id"]) - set(x["track_id" + "_" + unit_col])), axis=1
    )

    alldf_frame_summary["person_enter"] = alldf_frame_summary.apply(
        lambda x: len(set(x["track_id" + "_" + unit_col]) - set(x["track_id"])), axis=1
    )
    alldf_frame_summary["num_person_current"] = alldf_frame_summary["track_id"].apply(
        lambda x: len(x)
    )
    alldf_frame_summary[f"num_person_after_{interval_churn}s"] = alldf_frame_summary[
        f"track_id" + "_" + unit_col
    ].apply(lambda x: len(x))
    alldf_frame_summary["churn_rate"] = (
        alldf_frame_summary["person_left"] / alldf_frame_summary["num_person_current"]
    )
    alldf_frame_summary["enter_rate"] = (
        alldf_frame_summary["person_enter"] / alldf_frame_summary["num_person_current"]
    )
    alldf_frame_churnrate_summary = (
        alldf_frame_summary.groupby(["decades", "video_location", "video_id"])
        .agg({"churn_rate": "mean", "enter_rate": "mean"})
        .reset_index()
    )
    return alldf_frame_churnrate_summary


def loop_churn(alldf, interval_churn):
    """Loop through the interval churn to get the churn rate at different intervals"""
    result = []
    for interval_churn in range(1, 21):
        print(interval_churn)
        print("*" * 100)
        unit_col = f"frame_id_{interval_churn}sec"
        alldf[unit_col] = alldf["frame_id"] + interval_churn * alldf["fps"]
        alldf_frame = (
            alldf.groupby(
                ["decades", "video_location", "video_id", "frame_id", unit_col]
            )["track_id"]
            .unique()
            .reset_index()
        )
        summary_temp = get_churn(alldf_frame, unit_col, interval_churn)
        summary_temp["interval"] = interval_churn
        result.append(summary_temp)
        gc.collect()
    result = pd.concat(result).reset_index(drop=True)
    return result


def plot_churn_rate(result):
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.pointplot(
        data=result[result["decades"] == "2010s"],
        x="interval",
        y="churn_rate",
        linestyles="--",
        linewidth=1,
        markersize=4,
        ax=ax,
        color="#35aca4",
        # label = '2010s'
        errorbar=None,
    )
    sns.pointplot(
        data=result[result["decades"] == "1980s"],
        x="interval",
        y="churn_rate",
        linestyles="-",
        linewidth=1,
        markersize=4,
        ax=ax,
        color="#f67088",
        # label = '2010s'
        errorbar=None,
    )
    sns.despine()
    # add major grid
    ax.grid(which="major", axis="y", linestyle="--")
    ax.set_title("")
    ax.set_xlabel("Interval window(s)", fontsize=12)
    ax.set_ylabel("Churn rate", fontsize=12)
    # show y-axis as percentage
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    # revise legend text to add 2010s and 1980s seperately
    handles, labels = ax.get_legend_handles_labels()
    labels = ["2010s " + i for i in labels[:4]] + ["1980s " + i for i in labels[4:]]

    # save the figure
    fig.savefig(
        os.path.join(GRAPHIC_FOLDER, "Fig5-churn_rate_per_decades.svg"),
        format="svg",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def main():
    alldf = pd.read_csv(Setup.MAIN_PATH)
    interval_1980s = FPS_HISTORY / 10
    alldf["fps"] = np.where(alldf["decades"] == "2010s", 29.97, interval_1980s)
    gc.collect()
    churn_result = loop_churn(alldf, interval_churn=20)
    plot_churn_rate(churn_result)
    print("*" * 100)
    print("Churn rate plot is saved")


if __name__ == "__main__":
    main()
