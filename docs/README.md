# Jordan Logistics Performance Intelligence and Decision-Support System

## Overview

This project is an integrated Business Intelligence and intelligent analytics system designed to analyze, forecast, and simulate Logistics Performance Index (LPI) behavior with a primary focus on Jordan.

The project combines:
- data preprocessing
- exploratory data analysis
- clustering analysis
- forecasting
- what-if simulation
- interactive decision-support
- dashboard visualization
- cloud deployment

The system transforms raw World Bank logistics data into:
- analytical insights
- predictive outputs
- interactive simulations
- recommendation-oriented decision support

---

# Main Objectives

The project aims to:

- analyze Jordan’s logistics performance
- identify weak logistics indicators
- forecast future logistics trends
- group countries using clustering analysis
- simulate logistics improvement scenarios
- provide interactive Business Intelligence dashboards
- support logistics-related strategic decision-making

---

# Main Technologies Used

| Technology | Purpose |
|---|---|
| Python | Data preprocessing, forecasting, analytics |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Matplotlib | Visualization |
| Scikit-learn | Clustering and forecasting |
| Streamlit | Interactive dashboard |
| KNIME | ETL and GDP preprocessing |
| GitHub | Version control and documentation |

---

# Main Analytical Components

## 1. Data Preprocessing

The project includes:
- cleaning
- reshaping
- interpolation
- missing value handling
- gap filling
- type conversion

A hybrid gap-filling strategy was designed to handle irregular LPI years and sparse country observations.

---

## 2. Exploratory Data Analysis (EDA)

EDA was performed to:
- analyze logistics trends
- identify weak indicators
- compare countries
- understand indicator relationships

Jordan was selected as the primary focus country.

---

## 3. Clustering Analysis

K-Means clustering was used to group countries according to logistics performance similarity.

The clustering stage included:
- feature scaling
- Elbow Method
- PCA visualization
- cluster interpretation

---

## 4. Forecasting

Forecasting models were developed to estimate future LPI scores.

The forecasting stage included:
- train-test split
- weighted forecasting
- linear and polynomial regression
- adaptive model selection
- confidence intervals
- evaluation metrics

---

## 5. What-If Analysis

A What-If simulation framework was developed to estimate how improving Jordan’s weak indicators may affect Overall LPI performance.

The simulation focused on:
- Customs
- International Shipments

The system generates:
- scenario comparisons
- KPI updates
- recommendation logic
- projected impact estimation

---

## 6. Interactive Streamlit Dashboard

An interactive Streamlit dashboard was developed to:
- visualize logistics performance
- simulate scenarios
- support decision-making
- generate recommendations

The dashboard includes:
- KPI cards
- historical trends
- weak indicator ranking
- simulation sliders
- recommendation engine
- scenario visualization

---

# Streamlit Application

## Live Application

https://gpbi20252-gqcxmgnwreelog4izl8syj.streamlit.app/

---

# Project Structure

```text
LPI_Project/
│
├── data/
├── outputs/
├── docs/
├── knime/
├── app.py
├── requirements.txt
├── 01_cleaning.py
├── 01b_interpolation.py
├── 02a_eda.py
├── 02c_clustering.py
├── 03_forecasting.py
├── 04_whatif.py

Main Outputs

The project generates multiple outputs including:

cleaned datasets
interpolated datasets
forecasting results
evaluation reports
clustering outputs
visualization charts
what-if simulation results
Streamlit dashboard
Documentation

Detailed project documentation is available inside the docs folder.

The documentation includes:

preprocessing explanation
EDA analysis
clustering methodology
forecasting analysis
what-if simulation logic
Streamlit architecture
project architecture
limitations and future work
Key Features
Intelligent Analytics
forecasting
clustering
simulation
recommendation logic
Interactive BI Dashboard
scenario sliders
KPI cards
visual analytics
dynamic updates
Decision Support
recommendation generation
strategic interpretation
impact estimation
Cloud Deployment
publicly accessible dashboard
GitHub integration
Streamlit deployment
Challenges Addressed

The project handled several major challenges:

irregular LPI reporting years
missing observations
sparse country data
forecasting instability
simulation realism
deployment integration

Solutions included:

hybrid interpolation
conservative forecasting
weighted estimation
modular architecture
cloud deployment
Future Improvements

Potential future extensions include:

real-time logistics data
advanced machine learning models
Power BI integration
GIS visualization
causal modeling
API integration
multi-country simulation
Academic and Business Intelligence Value

The project combines:

Business Intelligence
Machine Learning
Forecasting
Visualization
Decision Support

within a single integrated analytical system.

The project demonstrates how logistics analytics can support:

strategic planning
logistics optimization
operational interpretation
scenario simulation
Final Summary

This project developed a complete logistics intelligence and decision-support framework using:

Python analytics
KNIME preprocessing
Streamlit dashboards
GitHub documentation
cloud deployment

The final system integrates:

preprocessing
forecasting
clustering
simulation
recommendation logic
visualization

into a unified Business Intelligence workflow focused on Jordan’s logistics performance.
# Dashboard Preview

## Main Dashboard
![Main Dashboard](images/home_dashboard.png)

## Decision-Support Features
![Decision Support](images/decision_support.png)

## What-if Simulation
![What-if](images/what_if_analysis.png)

## GDP Economic Context
![GDP](images/gdp_context.png)

## Indicator Impact Details
![Impact](images/indicator_impact.png)

## Sidebar Inputs
![Sidebar](images/sidebar_inputs.png)