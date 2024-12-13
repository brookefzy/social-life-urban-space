"""Plot Figure 4: Group Distribution"""

from matplotlib import pyplot as plt
import os
import pandas as pd

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
colors = sns.color_palette("husl", 9)
plt.rcParams["figure.figsize"] = [3, 4]
plt.rcParams["figure.autolayout"] = True
plt.rcParams["svg.fonttype"] = "none"
GRAPHIC_FOLDER = "./_graphics"
# this is the folder where the curated data is stored for further analysis
DATA_FOLDER = "./_data/curated"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    print("Folder created")


groupmeta = {
    "1_per": "%person being alone in this frame",
    "2_per": "%person being in a group of 2 in this frame",
    "3_per": "%person being in a group of 3 in this frame",
    "4+_per": "%person being in a group of 4 or more in this frame",
    "video_location": "Location of the video",
    "decades": "Decades of the video",
    "second_from_start": "Second from the start of the video",
    "minute_from_start": "Minute from the start of the video",
    "frame_id": "Frame ID",
}
locls = ["Chestnut Street", "Bryant Park", "Downtown Crossing", "MET"]


def summary_groups(alldf_update):
    # frame level average first
    grouptimedf = (
        alldf_update.groupby(
            [
                "decades",
                "video_location",
                "video_id",
                "second_from_start",
                "minute_from_start",
                "frame_id",
                "group_size",
            ]
        )
        .agg(
            {
                "track_id": "nunique",
            }
        )
        .reset_index()
        .rename(columns={"track_id": "pedestrian_count"})
    )

    # Pivot the table to fill the nan values
    grouptimedf_loc = (
        grouptimedf.pivot(
            columns=["group_size"],
            index=[
                "decades",
                "video_location",
                "video_id",
                "second_from_start",
                "minute_from_start",
                "frame_id",
            ],
            values=["pedestrian_count"],
        )
        .fillna(0)
        .reset_index()
    )
    grouptimedf_loc.columns = ["".join(col) for col in grouptimedf_loc.columns]
    newcols = [f"pedestrian_count{i}" for i in ["1", "2", "3", "4+"]]
    # total pedestrian count per frame
    grouptimedf_loc["pedestrian_count_total"] = grouptimedf_loc[newcols].sum(axis=1)
    for i in ["1", "2", "3", "4+"]:
        grouptimedf_loc[f"{i}_per"] = (
            grouptimedf_loc[f"pedestrian_count{i}"]
            / grouptimedf_loc["pedestrian_count_total"]
        )
    grouptimedf_loc.to_csv(
        os.path.join(DATA_FOLDER, "c_group_size_distribution_by_loc.csv")
    )
    grouptimedf_loc_summary = (
        grouptimedf_loc.groupby(["video_location", "decades"])
        .agg({"1_per": "mean", "2_per": "mean", "3_per": "mean", "4+_per": "mean"})
        .reset_index()
    )
    grouptimedf_summary = (
        grouptimedf_loc.groupby(["video_location", "video_id", "decades"])
        .agg({"1_per": "mean", "2_per": "mean", "3_per": "mean", "4+_per": "mean"})
        .reset_index()
        .groupby(["decades", "video_location"])
        .mean()
        .reset_index()
        .groupby("decades")
        .mean()
    )
    return grouptimedf_loc_summary, grouptimedf_summary


def plot_all(grouptimedf_summary):
    # visualize this average score of the four sites directly
    fig, ax = plt.subplots(figsize=(5, 3))
    grouptimedf_summary.plot.barh(
        stacked=True,
        ax=ax,
        color=["#EA5455", "#002B5B", "#146C94", "#19A7CE"],
    )
    ax.set_title("All Locations")
    ax.set_xlabel("%pedestrians observed in group", fontsize=12)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.grid(which="major", axis="both", linestyle="--")
    ax.set_ylabel("Year", fontsize=12)
    ax.legend(
        ["Singles", "Dyads", "Triads", "Groups >= 4"],
        title="% Pedestrian Observed \n in Different Group size",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        borderaxespad=0,
        fontsize="large",
        title_fontsize=10,
    )
    sns.despine()
    fig.savefig(
        os.path.join(GRAPHIC_FOLDER, "Fig4-Group_size_distribution.png"),
        dpi=200,
        bbox_inches="tight",
        pad_inches=0.1,
    )
    plt.close()


def plot_by_site(grouptimedf_loc_summary):

    newcolsper = [f"{i}_per" for i in ["1", "2", "3", "4+"]]
    fig, axes = plt.subplots(4, 1, figsize=(4, 5), sharex=True, sharey=True)
    for i, loc in enumerate(locls):
        temp = (
            grouptimedf_loc_summary[grouptimedf_loc_summary["video_location"] == loc]
            .reset_index(drop=True)
            .set_index("decades")
        )
        temp[newcolsper].plot.barh(
            stacked=True,
            ax=axes[i],
            color=["#EA5455", "#002B5B", "#146C94", "#19A7CE"],
        )
        axes[i].set_title(loc, fontsize=8)
        axes[i].set_xlabel("% Pedestrians observed in group", fontsize=8)
        axes[i].xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        axes[i].grid(which="major", axis="both", linestyle="--", linewidth=0.5)
        axes[i].set_ylabel("", fontsize=8)
        # set up tick size
        axes[i].tick_params(axis="both", which="major", labelsize=8)
        sns.despine()
        if i > 50:
            axes[i].legend(
                ["% Singles", "% Dyads", "% Triads", "% Groups >= 4"],
                title="% Pedestrian Observed \n in Different Group size",
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
                borderaxespad=0,
                fontsize="large",
                title_fontsize=8,
            )
        else:
            # remove legend
            axes[i].get_legend().remove()
    plt.tight_layout()
    fig.savefig(
        os.path.join(GRAPHIC_FOLDER, "Fig4-GroupPercentageOvertime-loc.svg"),
        index=False,
        dpi=200,
    )
    plt.close()


def main():
    alldf = pd.read_csv(Setup.MAIN_PATH)
    alldf["group_size"] = (
        alldf["group_size"].astype(str).apply(lambda x: x.replace(".0", "")).fillna("1")
    )
    print("Data loaded")
    grouptimedf_loc_summary, grouptimedf_summary = summary_groups(alldf)
    plot_all(grouptimedf_summary)
    print("Figure 4: Plot all locations together")
    plot_by_site(grouptimedf_loc_summary)
    print("Figure 4: Plot by site")


if __name__ == "__main__":
    main()
