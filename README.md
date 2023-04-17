# **master-thesis** 🎓🌍

The objective is to build a Machine Learning (ML) model capable of detecting the dates when crop fields have been manured, exploiting Sentinel satellites data. 

![Views](https://komarev.com/ghpvc/?username=AF99MasterThesis&label=Views&style=for-the-badge&color=blueviolet)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FF0000.svg?style=for-the-badge&logo=jupyter&logoColor=white)
![Google](https://img.shields.io/badge/google-90EE0?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-0000FF?style=for-the-badge&logo=python&logoColor=white)

*** 
## **What is satellite data analysis?**
The market for satellite data analytics services is witnessing notable expansion, attributed to the rise in investment in the space sector. These services encompass the provision of big data geo-analytics using advanced machine learning techniques and proprietary algorithms to deliver valuable insights for enterprises, utilizing data from satellites orbiting the Earth. 

By leveraging Earth observation (EO) data, satellite data analytics services facilitate informed decision-making in critical areas like commodity markets, infrastructure monitoring, agriculture management, and forestry management. Furthermore, satellite data services employ image processing to analyze the data captured by satellites, providing businesses with data analytics capabilities that drive operational efficiency and transparency across various industries.

*** 
## **Why manure detection is relevant in EO context?**
It is important to detect when a crop field has been manured, especially during unauthorized periods, because it can help prevent environmental pollution and ensure compliance with regulations such as the EU Directive on nitrates.

When manure is applied to agricultural fields, it contains high levels of nitrogen and phosphorus, which can leach into groundwater or runoff into nearby water bodies. This can lead to excessive nutrient concentrations in the water, causing eutrophication, harmful algal blooms, and other environmental problems.

To prevent these issues, many countries have regulations in place that restrict the use of manure during certain periods, such as winter or rainy seasons when the risk of nutrient leaching is higher. In the EU, the Directive on nitrates regulates the use of fertilizers, including manure, in agriculture to prevent water pollution from nitrate runoff.

By detecting when a crop field has been manured, and whether it was done during unauthorized periods, Earth Observation can help authorities enforce regulations and prevent environmental pollution. This can be done using satellite data to detect the spectral signature of manure on agricultural fields, as well as other indicators such as soil moisture and vegetation health, which can provide additional information on the timing and extent of manure application.

***
## **Notebooks summary description**

### **1. Features extraction**
The objective of the [*features extraction notebook*](./Notebooks/1-features-extraction/notebook.ipynb) is to extract useful mean indexes values from crop fields of interest, using Sentinel satellites imagery. These features have been used for performing analysis and building machine learning models with a specific focus on detecting manure. 

To facilitate the feature extraction process, a Python library called [**`sentinel-satellites`**](https://pypi.org/project/sentinel-satellites/) has been created and made available on the PyPI repository for public use.

### **2. Analysis**
The objective of the [*analysis notebook*](./Notebooks/2-analysis/notebook.ipynb) is to analyze the datasets generated in the previous notebook by performing data visualization, obtaining statistics, and exploring correlations between different indexes. The main goal is to identify which optical and radar indexes most affected by the application of manure on crop fields. To assess the significance of feature importance, a t-test has been used. The formula used to calculate feature importance is:

$$feat\_imp = \frac{|feat\_val_{imm\_after\_manure} - feat\_val_{imm\_before\_manure}|}{\max{|daily\_feat\_diff_{\neg{manure}}|}}$$

This formula calculates the feature importance by comparing the immediate values of a feature (index) before and after manure application, normalized by the maximum daily difference in the feature values observed when manure had not applied.

### **3. ML models**
The [*ML models notebook*](./Notebooks/3-ml-models/notebook.ipynb) aims to build and compare various machine learning models for predicting the application of manure in crop fields. The models are evaluated based on accuracy, precision, recall, and F1 score. Several aspects are covered, including overfitting/underfitting, dataset balancing (undersampling/oversampling), feature subset selection (wrapper methods), performance evaluation (stratified K-fold cross-validation), and feature normalization techniques.

<br>

Please consider that each notebook has its own `utils` file or folder.

*** 
## **Install requirements**

In order to install the required libraries to replicate the different notebooks results, you have to run the following command in bash/terminal:
```bash
$ pip install -r requirements.txt
```