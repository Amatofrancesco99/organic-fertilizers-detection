<div align="center">

# **Detection of manure application on crop fields leveraging satellite data and Machine Learning**

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
![Views](https://komarev.com/ghpvc/?username=DetectionOfManureApplication&label=Views&color=lightgrey)
<br>
![Jupyter Notebook](https://img.shields.io/badge/JUPYTER-%23FF0000.svg?style=flat&logo=jupyter&logoColor=white&color=critical)
![Google](https://img.shields.io/badge/GOOGLE_EARTH_ENGINE-90EE0?style=flat&logo=google&logoColor=white&color=success)
![Python](https://img.shields.io/badge/PYTHON-0000FF?style=flat&logo=python&logoColor=white&color=informational)

</div>

## **Description**
This is the repository for the project *"Detection of manure application on crop fields leveraging satellite data and Machine Learning"* [[thesis]]().

## **Abstract**
> Detecting application of manure on crop fields is crucial for remotely assessing the correct management of crops; this is important for various goals such as maintaining soil fertility, productivity, environmental compliance, and - in the EU - also for verifying farmers' compliance with the nitrates directive. 
In the framework outlined above, this thesis research aims at developing an automated, Machine Learning (ML) based, method for detecting manure application leveraging Earth Observation (EO) satellite data.
Time series of spectral indexes (radar, optical and thermal) have been extracted from specific regions of interest (ROIs), located in Spain and Italy, using different EO satellites; a [Python library](https://pypi.org/project/ee-satellites/), made available for public use, has been developed to efficiently accomplish this purpose.
After that, the spectral indexes most impacted by manure application have been identified and selected as input to different ML models, which have been compared - especially for what regards their generalization capabilities.
Tests have been conducted over both ROIs, including mixed cases where training was carried out on fields from one country and classification on fields located in another (or same).
In short, results suggest that the spectral signature of manure application is homogeneous within fields located in the same country, and that combining optical and thermal data allows achieving the best classification performances.
Radar data, instead, provides no significant contribution to system performances.
The proposed method provides a valuable foundation toward development of a tool to monitor manure application in crop fields and ensure compliance with environmental regulations.

## **Download**
You can download a copy of all the files in this repository by cloning the git repository:

```bash
git clone https://github.com/Amatofrancesco99/master-thesis.git
```

To install the required libraries in order to replicate the different notebooks results you need to run the following command:
```bash
pip install -r requirements.txt
```

## **Notebooks**
### Features extraction
The objective of the [*features extraction notebook*](./Notebooks/1-features-extraction/notebook.ipynb) is to extract useful mean indexes values from crop fields of interest, using satellites imagery.
To facilitate the feature extraction process, a Python library called [`ee-satellites`](https://pypi.org/project/ee-satellites/) has been created and made available on the PyPI repository for public use.

### Analysis
The objective of the [*analysis notebook*](./Notebooks/2-analysis/notebook.ipynb) is to analyze the datasets generated in the previous notebook by performing data visualization, obtaining statistics, and exploring correlations between different indexes. The main goal is to identify which spectral indexes are most affected by the application of manure on crop fields. To assess the significance of feature importance, a t-test has been used.

### ML models
The [*ML models notebook*](./Notebooks/3-ml-models/notebook.ipynb) aims to build and compare various machine learning models for detecting the application of manure in crop fields. The models are evaluated based on accuracy, precision, recall, and F1 score. Several critical aspects are covered, including overfitting and underfitting, dataset balancing (undersampling or oversampling), feature subset selection (wrapper methods), performance evaluation (stratified K-fold cross-validation), and feature normalization techniques.

### Generalization
The notebooks inside the [*generalization folder*](./Notebooks/4-generalization) are designed to assess the generalization capabilities of a *selected pre-trained model*. The objective are: [(i)](./Notebooks/4-generalization/notebook1.ipynb) to evaluate the performances (of model) in detecting when crop fields have been manured in a completely different context from the one it was trained on (different country, soil types, climate conditions, farming practices, ...); [(ii)](./Notebooks/4-generalization/notebook2.ipynb) to check, using a model trained on all available manured crops located in a country of interest (Italy), the distribution of detections during a whole reference year for crops (same country) where there are no information about the actual manure application date/s. <br>
Generalization is a critical issue, as it determines how well a given model can perform on new, unseen data. 
<br><br>

Please consider that each notebook has its own `utils` file or folder.

***
## **Cite this work**
```latex
@software{Amato_Detection_of_manure_2023,
author = {Amato, F. and Dell'Acqua, F. and Marzi, D.},
month = may,
title = {{Detection of manure application on crop fields leveraging satellite data and Machine Learning}},
url = {https://github.com/Amatofrancesco99/master-thesis},
version = {1.0.0},
year = {2023}
}
```