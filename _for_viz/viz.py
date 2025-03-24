import numpy as np
import cv2
import os
import pandas as pd
import random
import argparse

DATAFOLDER = "../_data/viz_sample" # replace here with your DATAFOLDER
VIDEO_FOLDER = "../_data/raw/sample_video" # replace here with your VIDEO_FOLDER

VIDEO_VIZ_FOLDER = "../_data/curated/video_viz/"
VIZ_FILE_DICT = {
    "bryant_park": {
        "1980": f"{DATAFOLDER}/B16_G8_Env5_0001-Scene-005_W2xEX_VFI_mp4_0_60_viz.csv",
        "2010": f"{DATAFOLDER}/20081008-141944b03_120_180_viz.csv",
    },
    "chestnut_street":{
        "1980": f"{DATAFOLDER}/B18_G1_Env15_0001-Scene-007_W2xEX_VFI_mp4_0_60_viz.csv",
        "2010": f"{DATAFOLDER}/20100519-083343b07_10_70_viz.csv",
    },
    "met":{
        "1980": f"{DATAFOLDER}/B10_G2_Env5_0001-Scene-006_W2xEX_VFI_mp4_viz.csv",
        "2010": f"{DATAFOLDER}/20100612-120118b02_10_70_viz.csv",
    },
    "downtown_crossing":{
        "1980": f"{DATAFOLDER}/B11_G1_Env3_0001-Scene-001_W2xEX_VFI_mp4_0_60_viz.csv",
        "2010": f"{DATAFOLDER}/20100521-115755b02_10_70_viz.csv",
    }
}

SUFFIX_1980 = "_W2xEX_VFI_mp4_0_60.mp4"
VIDEO_FILE_DICT = {
    "met":{
    "1980":f"{VIDEO_FOLDER}/B10_G2_Env5_0001-Scene-006{SUFFIX_1980}",
    "2010":f"{VIDEO_FOLDER}/20100612-120118b02_10_70.mp4"
    },
    "bryant_park":{
    "1980":f"{VIDEO_FOLDER}/B16_G8_Env5_0001-Scene-005{SUFFIX_1980}",
    "2010":f"{VIDEO_FOLDER}/20081008-141944b03_120_180.mp4"
    },
    "downtown_crossing":{
    "1980":f"{VIDEO_FOLDER}/B11_G1_Env3_0001-Scene-001{SUFFIX_1980}",
    "2010":f"{VIDEO_FOLDER}/20100521-115755b02_10_70.mp4"
    },
    "chestnut_street":{
    "1980":f"{VIDEO_FOLDER}/B18_G1_Env15_0001-Scene-007{SUFFIX_1980}",
    "2010":f"{VIDEO_FOLDER}/20100519-083343b07_10_70.mp4"
    }
}


def getbasics(file_path):
    video = cv2.VideoCapture(file_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    print("frames per second =", fps)
    size = (
        int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    )
    print("frames size =", size)
    # video.release()
    return video, fps, size


def viz_group(trait_ingroup, frame, group_colors):
    for group_id in trait_ingroup["cross_frame_group_id"].unique():
        temp = trait_ingroup[
            trait_ingroup["cross_frame_group_id"] == group_id
        ].reset_index(drop=True)

        if len(temp) > 1:
            color = group_colors[group_id]
            for track_id in temp["track_id"].unique():
                temp2 = temp[temp["track_id"] == track_id].reset_index(drop=True)
                width = 2
                frame = cv2.rectangle(
                    frame,
                    (int(temp2["x1"]), int(temp2["y1"])),
                    (int(temp2["x2"]), int(temp2["y2"])),
                    color,
                    width,
                )
    return frame


def viz_video(
    location:str,
    year:str,
    viz_start=0,
    viz_end=60,
    video_viz_folder=VIDEO_VIZ_FOLDER,
):
    video_path = VIDEO_FILE_DICT[location][year]
    videoname = video_path.split("/")[-1].split(".")[0]
    print(videoname)
    video, fps, size = getbasics(video_path)
    frame_start = int(viz_start * fps)
    frame_end = int(viz_end * fps)
    # output video
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    outputfile = os.path.join(
        video_viz_folder, f"{videoname}_{viz_start}_{viz_end}_n=2.mp4"
    )
    # out.release()
    out = cv2.VideoWriter(outputfile, fourcc, fps, size)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_start)
    viz_file_path = VIZ_FILE_DICT[location][year]
    # read the traceGDF file
    traceGDF_people = pd.read_csv(viz_file_path)

    def get_xy(temp2):
        temp2["x1"] = temp2["x"] - temp2["w"] / 2
        temp2["y1"] = temp2["y"] - temp2["h"] / 2
        temp2["x2"] = temp2["x"] + temp2["w"] / 2
        temp2["y2"] = temp2["y"] + temp2["h"] / 2
        return temp2

    traceGDF_people = traceGDF_people.apply(get_xy, axis=1)

    trait_ingroup = traceGDF_people[traceGDF_people["is_group"] == True].reset_index(
        drop=True
    )
    group_colors = {
        group_id: (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        for group_id in trait_ingroup["cross_frame_group_id"].unique()
    }

    for frame_id in range(frame_start, frame_end):
        ret, frame = video.read()
        if ret:
            trait_merged_current = traceGDF_people[
                traceGDF_people["frame_id"] == frame_id
            ].reset_index(drop=True)
            trait_ingroup_current = trait_ingroup[
                trait_ingroup["frame_id"] == frame_id
            ].reset_index(drop=True)
            # break
            # Step 1: plot all individuals first
            for track_id in trait_merged_current["track_id"].unique():
                temp = trait_merged_current[
                    trait_merged_current["track_id"] == track_id
                ].reset_index(drop=True)
                width = 1
                frame = cv2.rectangle(
                    frame,
                    (int(temp["x1"]), int(temp["y1"])),
                    (int(temp["x2"]), int(temp["y2"])),
                    (255, 255, 255),
                    width,
                )
            # Step 2: visualize the group detection result
            if len(trait_ingroup_current) > 0:
                frame = viz_group(trait_ingroup_current, frame, group_colors)
            out.write(frame)
            # break
        else:
            break
    out.release()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", "-y", type=str, help="year, choose from 1980, 2010", default="2010"
    )
    parser.add_argument(
        "--location", "-l", type=str, help="location, choose from met, bryant_park, downtown_crossing, chestnut_street", 
        default="met"
    )
    parser.add_argument(
        "--total_secs", "-s", type=int, help="total seconds to visualize", default=10
    )
    parser.add_argument(
        "--output_folder",
        "-o",
        type=str,
        help="output folder for the visualization video",
        default=VIDEO_VIZ_FOLDER,
    )

    args = parser.parse_args()
    year = str(args.year)
    location = str(args.location)
    video_path = VIDEO_FILE_DICT[location][year]
    video_name = video_path.split("/")[-1].split(".")[0]
    output_folder = args.output_folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print(
        "Now visualize ",
        video_name,
        " from ",
        video_path,
        "\n for ",
        args.total_secs,
        " seconds",
    )
    viz_video(
        location=location,
        year=year,
        viz_end=int(args.total_secs),
        video_viz_folder=output_folder,
    )


if __name__ == "__main__":
    main()
