class Setup:
    """Here are the shared set up for all scripts"""

    STAYTHREDS = [0.5, 2, 4, 6, 8, 10]
    STAY_VARIABLE = "stay_adjusted_{staythred}"
    FPS_HISTORY = 119.88
    VALID_TRHEAD = 2
    SELECT_STYTHRED = 4
    COLOR_DICT = {
        "Bryant Park": "#f77189",
        "Chestnut Street": "#97a431",
        "Downtown Crossing": "#36ada4",
        "MET": "#a48cf4",
    }
    LOC_LS = ["Chestnut Street", "Bryant Park", "Downtown Crossing", "MET"]
    MAIN_PATH = "./_data/c_alldf_update.csv"
    DATA_META = {
        "order": "video order in one location",
        "video_location": "video location name",
        "track_id": "reconstructed track id, unique within each video",
        "video_id": "video id, unique within each location",
        "lat": "prejected latitude",
        "lon": "prejected longitude",
        "track_id_backup": "original track id from the tracking file",
        "move_speed": "speed in meter per second",
        "hex_id": "h3 level 15 index",
        "frame_id": "reconstructed frame_id, across videos in a location, unique within one location",
        "second_from_start": "calculated second from start based on the frame_id, 48 frames per real second",
        "individual_frame_total": "total number of frames the track appeared in the video",
        "frame_social_track": "frame_id + Social + track_id",
        "group_id_social": "frame_id + Social, unique within each video",
        "group_size": "number of tracks in the group",
        "is_group": "whether the track is in a group or not",
        "group_first_frame": "first frame_id when the track is in a group",
        "track_first_frame": "first frame_id when the track appear in this video",
        "group_track_delta": "difference between group_first_frame and track_first_frame",
        "emerging_group": "whether the group is newly formed or not",
        "group_size_combined": "grouping the group size into buckets",
        "cross_frame_group_id": "this is a group id that can be used to identify the group across frames (only available for current videos)",
        "gender": "gender of each pedestrian",
        "age": "age of each pedestrian",
        "timestamp": "timestamp of each frame (Only available for modern videos). use for reference.",
        "is_group_loose": "if the group only satisfy the spatial constriants",
    }
