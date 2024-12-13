import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd

# plot one location one plot
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import gc
from config.setting import Setup

plt.rcParams["figure.figsize"] = [3, 4]
plt.rcParams["figure.autolayout"] = True
plt.rcParams["svg.fonttype"] = "none"
GRAPHIC_FOLDER = "./_graphics"
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


def plot_speed_info(
    df, var="speed_mean", x="decades", hue="video_location", x_label="Speed (m/s)"
):
    filesize = (6, 3)
    fig, ax = plt.subplots(figsize=filesize)
    sns.barplot(
        y=var,
        x=x,
        hue=hue,
        data=df,
        width=0.7,
        palette=sns.color_palette("husl", 2),
        # make line thinner
        linewidth=0.5,
        ax=ax,
    )
    sns.despine()
    # show major x grid
    ax.yaxis.grid(True, linestyle="--", color="grey", linewidth=0.5)
    ax.xaxis.grid(True, linestyle="--", color="grey", linewidth=0.5)
    ax.xaxis.set_ticks_position("bottom")
    # reduce x axis label size
    ax.tick_params(axis="x", labelsize=8)
    ax.yaxis.set_ticks_position("left")
    ax.tick_params(axis="y", labelsize=8)
    ax.set_xlabel(x_label)
    ax.set_ylabel("")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    plt.savefig(
        os.path.join(GRAPHIC_FOLDER, f"Fig3-speed_{var}_{x}_{hue}.png"),
        bbox_inches="tight",
        dpi=300,
    )
    plt.close()


def plot_speed_mean(data):
    data_site_ave = data.groupby(["video_location", "decades"]).mean().reset_index()
    fig, ax = plt.subplots(figsize=(3, 4))
    sns.boxplot(
        x="decades",
        y="moving_speed_mean",
        data=data_site_ave,
        palette=sns.color_palette("husl", 2),
        linewidth=1,
        fill=False,
        gap=0.5,
        order=["1980s", "2010s"],
        ax=ax,
    )
    sns.despine()
    # show major x grid
    ax.yaxis.grid(True, linestyle="--", color="grey", linewidth=0.5)
    ax.xaxis.grid(True, linestyle="--", color="grey", linewidth=0.5)
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    # set x-label
    ax.set_xlabel("Speed m/s", size=10)
    # put the lengend outside the plot
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    ax.set_ylabel("", size=10)
    plt.savefig(
        os.path.join(GRAPHIC_FOLDER, "Fig3a-speed_mean.png"),
        bbox_inches="tight",
        dpi=300,
    )
    plt.close()


def plot_decades_speed_info(
    df, var="moving_speed_mean", filename="speed_boxplot", y_label="Speed Mean"
):
    filesize = (4, 4)
    fig, ax = plt.subplots(figsize=filesize)
    sns.barplot(
        x="decades",
        y=var,
        data=df,
        width=0.7,
        # fill = False,
        gap=0.3,
        # whis = 1,
        # fliersize = 0,
        order=["1980s", "2010s"],
        palette="husl",
        ax=ax,
    )
    sns.despine()
    # show major x grid
    ax.yaxis.grid(True, linestyle="--", color="grey", linewidth=0.5)
    ax.xaxis.grid(True, linestyle="--", color="grey", linewidth=0.5)
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    # set x-label
    ax.set_xlabel("", size=10)
    # put the lengend outside the plot
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    ax.set_ylabel(y_label, size=10)
    plt.savefig(
        os.path.join(GRAPHIC_FOLDER, f"Fig3b-speed_barplot_{filename}.png"),
        format="png",
        dpi=200,
    )
    plt.close()


def speed_location_summary(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.violinplot(
        hue="decades",
        x="moving_speed_mean",
        y="video_location",
        data=data,
        palette=sns.color_palette("husl", 2)[::-1],
        linewidth=0.5,
        ax=ax,
    )
    sns.despine()
    # show major x grid
    ax.yaxis.grid(True, linestyle="--", color="grey", linewidth=0.5)
    ax.xaxis.grid(True, linestyle="--", color="grey", linewidth=0.5)
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    # set x-label
    ax.set_xlabel("Speed m/s", size=10)
    # put the lengend outside the plot
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    ax.set_ylabel("", size=10)
    plt.savefig(
        os.path.join(GRAPHIC_FOLDER, "Fig3c-speed_location_summary.png"),
        format="png",
        dpi=200,
        tight_layout=True,
    )


def main():
    alldf = pd.read_csv(Setup.MAIN_PATH)
    alldf = data_preprocessing(alldf)
    current_select = STAY_VARIABLE.format(staythred=SELECT_STYTHRED)
    df = (
        alldf[alldf["moving_speed"] > 0.5]
        .groupby(["video_location", "video_id", "decades", "track_id", current_select])
        .agg({"moving_speed": ["mean", "std"]})
        .reset_index()
    )
    sample_size = df[
        ["video_location", "video_id", "decades", "track_id"]
    ].drop_duplicates()
    keep_n = sample_size.shape[0]
    print("*" * 20, "after dropping", "*" * 20)
    print("keep_n", keep_n)
    print(sample_size.groupby(["decades"]).size())

    newcols = []
    for x in df.columns:
        if x[1] == "":
            newcols.append("".join(x))
        else:
            newcols.append("_".join(x))
    df.columns = newcols

    print("*" * 100)
    print("Creating location summary -- Speed mean and std")
    data = df[
        (df[STAY_VARIABLE.format(staythred=SELECT_STYTHRED)] == False)
    ].reset_index(drop=True)
    location_summary = (
        data.groupby(["video_location", "decades"])
        .agg({"moving_speed_mean": ["mean"], "moving_speed_std": ["mean"]})
        .reset_index()
    )
    plot_speed_info(
        location_summary,
        var=("moving_speed_mean", "mean"),
        hue="decades",
        x="video_location",
        x_label="Mean Speed (m/s)",
    )
    plot_speed_info(
        location_summary,
        var=("moving_speed_std", "mean"),
        hue="decades",
        x="video_location",
        x_label="Mean Speed Standard Deviation (m/s)",
    )
    print("*" * 100)
    print("Fig 3a - Creating pedestrians' speed summary across decades")
    plot_speed_mean(data)

    print("*" * 100)
    print("Fig 3b - Creating pedestrians' speed variation across decades")

    df_move_std_summary = (
        data.groupby(["video_location", "decades"])["moving_speed_std"]
        .mean()
        .reset_index()
        .groupby(["decades"])["moving_speed_std"]
        .mean()
        .reset_index()
    )
    plot_decades_speed_info(
        # df[df[STAY_VARIABLE.format(staythred = SELECT_STYTHRED)]==False],
        df_move_std_summary,
        var="moving_speed_std",
        filename="moving_speed_std",
        y_label="Speed Standard Deviation (m/s)",
    )
    print("*" * 100)
    print(
        "Fig 3c - Creating pedestrians' speed standard deviation summary across decades"
    )
    speed_location_summary(data)


if __name__ == "__main__":
    main()
