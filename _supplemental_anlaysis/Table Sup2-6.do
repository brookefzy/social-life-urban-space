*************************************************************************
* All analysis **************
** DATE: Nov 10th 2024******
** Author: Zhuangyuan Fan ****
*************************************************************************
set more off

clear all
* Set directory to location of data

global setting "/Users/yuan/MIT Dropbox/Zhuangyuan Fan/whyte_CV/_script/social-life-urban-space"
global datasource "${setting}/_data/curated"
cd "${datasource}"
global graphic "${setting}/_graphics"
global savefile "${setting}/_table"

* Run the Fig2-5.py scripts first to generate the source data for these two tables.

***********************************************************************************
***********Table S2: Summary Statistics on group size distribution ****************
***********************************************************************************
import delimited using "c_group_size_distribution_by_loc.csv", clear
label var _per "Single($\%$)"
label var v14 "Dyads($\%$)"
label var v15 "Triads($\%$)"
label var v16 "Others($\%$)"

tabulate video_location
global comp _per v14 v15 v16
eststo clear
eststo hk: estpost summarize $comp if (decades == "2010s")
eststo hkb: estpost summarize $comp if (decades == "1980s")

eststo hk02_2: estpost summarize $comp if (decades == "2010s" & video_location == "Bryant Park")
eststo hk02_2b: estpost summarize $comp if (decades == "1980s" & video_location == "Bryant Park")

eststo hk02_1: estpost summarize $comp if (decades == "2010s" & video_location == "Chestnut Street")
eststo hk02_1b: estpost summarize $comp if (decades == "1980s" & video_location == "Chestnut Street")

eststo hk02_3: estpost summarize $comp if (decades == "2010s" & video_location == "Downtown Crossing")
eststo hk02_3b: estpost summarize $comp if (decades == "1980s" & video_location == "Downtown Crossing")

eststo hk02_4: estpost summarize $comp if (decades == "2010s" & video_location == "MET")
eststo hk02_4b: estpost summarize $comp if (decades == "1980s" & video_location == "MET")


esttab hk02_1 hk02_1b hk02_2 hk02_2b hk02_3 hk02_3b hk02_4 hk02_4b using "${savefile}/TableS2_place_group_size_summary_2ys2.tex", replace booktabs label ///
cells("mean(pattern(1 1) fmt(2)) " "sd(pattern(1 1 1) par([ ]))") ///
mtitle("All sample" "Chestnut Street" "Bryant Park" "Downtown Crossing" "MET") nogaps compress ///
title(Summary Statistics on Group Sizes Per Frame\label{summary2y})

***********************************************************************************
** TABLE S6
***********************************************************************************
import delimited using "${datasource}/c_stay_summary.csv"
global comp total_pedestrian stay stay_per100 single_stayper100  group_stayper100 
browse
gen stay_per100 = stay_per*100
gen single_stayper100 = stay_per_single*100
gen group_stayper100 = stay_per_group*100


* Label the variables
label var total_pedestrian "$\#$ Pedestrian"
label var stay "$\#$ Ped. Staying"
label var single_stayper100 "$\%$ Ped. Staying Alone"
label var group_stayper100 "$\%$ Ped. Staying in Groups"
label var stay_per100 "$\%$ Ped. Staying"

***********************************************************************************
* Summarize the data by location by decades
tabulate video_location decades, summarize(total_pedestrian)
// summarize(minute_from_start)
eststo clear

eststo hk02_2: estpost summarize $comp if (decades == "2010s" & video_location == "Bryant Park")
eststo hk02_2b: estpost summarize $comp if (decades == "1980s" & video_location == "Bryant Park")

eststo hk02_1: estpost summarize $comp if (decades == "2010s" & video_location == "Chestnut Street")
eststo hk02_1b: estpost summarize $comp if (decades == "1980s" & video_location == "Chestnut Street")

eststo hk02_3: estpost summarize $comp if (decades == "2010s" & video_location == "Downtown Crossing")
eststo hk02_3b: estpost summarize $comp if (decades == "1980s" & video_location == "Downtown Crossing")

eststo hk02_4: estpost summarize $comp if (decades == "2010s" & video_location == "MET")
eststo hk02_4b: estpost summarize $comp if (decades == "1980s" & video_location == "MET")

esttab  hk02_1 hk02_1b hk02_2 hk02_2b hk02_3 hk02_3b hk02_4 hk02_4b using "${savefile}/place_summary_2ys2.tex", replace booktabs label ///
cells("mean(pattern(1 1) fmt(2)) " "sd(pattern(1 1 1) par([ ]))") ///
mtitle("Chestnut Street" "Bryant Park" "Downtown Crossing" "MET") nogaps compress ///
title(Summary Statistics By Location table\label{summary2y})

eststo clear

eststo hk02_0: estpost summarize $robust if (decades == "2010s")
eststo hk02_0b: estpost summarize $robust if (decades == "1980s")
eststo comp_2d: estpost ttest $robust, by(decades) unequal

esttab hk02_0 hk02_0b comp_2d using "${savefile}/robust_sp_ttest.tex", replace booktabs label ///
cells("mean(pattern(1 1 0) fmt(3)) sd(pattern(1 1 0)) b(star pattern(0 0 1) fmt(3)) t(pattern(0 0 1) par fmt(3))") ///
mtitle("2010s" "1980s" "2010s - 1980s") ///
nogaps compress




