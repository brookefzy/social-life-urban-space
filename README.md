# The social life of urban public space
This repo allow researchers to repeat the analysis from the paper (Shifting Patterns of Social Interaction: Exploring the Social Life of Urban Spaces Through AI)[https://www.nber.org/system/files/working_papers/w33185/w33185.pdf].
## Content
### 1.Pedetrian tracking from video
Click [here](https://github.com/brookefzy/uvi-yolov5-deepsort) to download the fine-tuned model weights and instructions for this projects.

### 2. Pedestrian group detection
Click [here](https://github.com/brookefzy/uvi-public-space) for grouping behavior detection after pedestrian detection results.


### 3. Replicate the analysis:
* Analysis Environment
```python=3.8, stataBE17```
* create a folder `_data` and save the data here first.
Run the *.py files to repeat the analysis and reproduce the figures.
- Figure 2: Lingering behavior and public space
- Figure 3: Speed analysis
- Figure 4: Group size analysis
- Figure 5: Pedestrian churn rate and encounter

## Data
Data to reproduce the analysis is available upon requests from the researcher

## Citation
```
@techreport{salazar2024shifting,
  title={Shifting Patterns of Social Interaction: Exploring the Social Life of Urban Spaces Through AI},
  author={Salazar-Miranda, Arianna and Fan, Zhuangyuan and Baick, Michael B and Hampton, Keith N and Duarte, Fabio and Loo, Becky PY and Glaeser, Edward L and Ratti, Carlo},
  year={2024},
  institution={National Bureau of Economic Research}
}
```