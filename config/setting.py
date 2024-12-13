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
