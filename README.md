<div align="center">

# **Detecting crop-fields manure application dates, exploiting Copernicus satellites and Machine Learning**

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
![Views](https://komarev.com/ghpvc/?username=AF99MasterThesis&label=Views&color=lightgrey)
<br>
![Jupyter Notebook](https://img.shields.io/badge/JUPYTER-%23FF0000.svg?style=flat&logo=jupyter&logoColor=white&color=critical)
![Google](https://img.shields.io/badge/GOOGLE_EARTH_ENGINE-90EE0?style=flat&logo=google&logoColor=white&color=success)
![Python](https://img.shields.io/badge/PYTHON-0000FF?style=flat&logo=python&logoColor=white&color=informational)

</div>

## **Description**
This is the repository for the paper [*Detecting crop-fields manure application dates, exploiting Copernicus satellites and Machine Learning*]().

## **Abstract**
> Detecting when manure has been applied in crop fields is crucial for many purposes, such as maintaining soil fertility, productivity, and environmental compliance, and for verifying farmers' compliance with nitrates directive. 
To achieve this, time series of mean spectral indexes (both radar and optical) have been extracted from specific Regions of Interest (ROI), located in the northern part of Spain (a [*Python library*](https://pypi.org/project/sentinel-satellites/), available for public use, have been published to efficiently extract these indexes).
The spectral indexes most impacted by manure application have been identified, and different Machine Learning models have been compared (using different performance metrics) to solve the problem.
The final proposed method provides a valuable foundation for developing tools to monitor manure application in crop fields and ensure compliance with environmental regulations.

## **Download**
You can download a copy of all the files in this repository by cloning the git repository:

```bash
git clone https://github.com/Amatofrancesco99/master-thesis.git
```

To install the required libraries in order to replicate the different notebooks results you need to run the following command:
```bash
pip install -r requirements.txt
```

## **Notebooks general descriptions**
### **Features extraction**
The objective of the [*features extraction notebook*](./Notebooks/1-features-extraction/notebook.ipynb) is to extract useful mean indexes values from crop fields of interest, using Sentinel satellites imagery. <br>
To facilitate the feature extraction process, a Python library called [**`sentinel-satellites`**](https://pypi.org/project/sentinel-satellites/) has been created and made available on the PyPI repository for public use.

### **Analysis**
The objective of the [*analysis notebook*](./Notebooks/2-analysis/notebook.ipynb) is to analyze the datasets generated in the previous notebook by performing data visualization, obtaining statistics, and exploring correlations between different indexes. The main goal is to identify which optical and radar indexes most affected by the application of manure on crop fields. To assess the significance of feature importance, a t-test has been used. The formula used to calculate feature importance is:

$$featImp = \frac{|featVal_{immAfterManure} - featVal_{immBeforeManure}|}{\max{|dailyFeatDiff_{\neg{manure}}|}}$$

This formula calculates the feature importance by comparing the immediate values of a feature (index) before and after manure application, normalized by the maximum daily difference in the feature values observed when manure had not applied.

### **ML models**
The [*ML models notebook*](./Notebooks/3-ml-models/notebook.ipynb) aims to build and compare various machine learning models for predicting the application of manure in crop fields. The models are evaluated based on accuracy, precision, recall, and F1 score. Several aspects are covered, including overfitting/underfitting, dataset balancing (undersampling/oversampling), feature subset selection (wrapper methods), performance evaluation (stratified K-fold cross-validation), and feature normalization techniques.
<br><br>

Please consider that each notebook has its own `utils` file or folder.

***
## **Cite this work**
```latex
@software{Amato_Detecting_crop-fields_manure_2023,
author = {Amato, F. and Dell'Acqua, F. and Marzi, D.},
doi = {10.5281/detecting-manure-application-dates.1234},
month = apr,
title = {{Detecting crop-fields manure application dates, exploiting Copernicus satellites and Machine Learning}},
url = {https://github.com/Amatofrancesco99/master-thesis},
version = {1.0.0},
year = {2023}
}
```
