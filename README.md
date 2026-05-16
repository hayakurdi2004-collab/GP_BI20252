# Jordan Logistics Performance — Business Intelligence Graduation Project

**University of Petra — Business Intelligence Graduation Project, 2025/2026**

---

## Title Page & Authors

**Project Title:** Jordan Logistics Performance Intelligence and Decision-Support Tool

**Authors:**
- Haya Kurdi, [202210598]


**Supervised by:** [Dr.Hussam Barham]

**Course:** 307498 – Graduation Project  
**Semester:** 2025/2026  
**Date:** [Submission Date]

---

## Table of Contents

1. [Abstract](#abstract)
2. [Acknowledgment](#acknowledgment)
3. [Business Intelligence Project Description and Objectives](#business-intelligence-project-description-and-objectives)
4. [Data Research and Acquiring Effort](#data-research-and-acquiring-effort)
5. [Data Description and Understanding](#data-description-and-understanding)
6. [Data Primary Cleaning and Transformation](#data-primary-cleaning-and-transformation)
7. [Data Visualization and Insights](#data-visualization-and-insights)
8. [Dashboard Design and Business Insights](#dashboard-design-and-business-insights)
9. [Advanced Analytics and AI Modeling](#advanced-analytics-and-ai-modeling)
10. [Tools Research and Selection Effort](#tools-research-and-selection-effort)
11. [Project Deployment Effort and Use Case](#project-deployment-effort-and-use-case)
12. [Results](#results)
13. [Code Setup and Dependencies](#code-setup-and-dependencies)
14. [Project Structure](#project-structure)
15. [Dashboard Preview](#dashboard-preview)
16. [References](#references)

---

## Abstract

This project analyzes Jordan’s logistics performance using the World Bank Logistics Performance Index (LPI). The objective is to understand Jordan’s logistics strengths and weaknesses, compare its performance with other countries, forecast future logistics trends, and support data-driven improvement decisions.

The implementation combines Business Intelligence dashboards, Python analytics, KNIME preprocessing, forecasting, clustering, what-if analysis, and Streamlit deployment. Power BI was used for traditional dashboard reporting and business visualizations, while Streamlit was used to build an interactive web-based simulation tool.

The main findings show that Jordan’s weakest logistics indicators are International Shipments and Customs. The what-if analysis suggests that customs reform and shipment facilitation may improve Jordan’s overall logistics performance. The final solution provides interactive visualizations, scenario simulation, reform priority scoring, and rule-based recommendations.

---

## Acknowledgment

We would like to thank the University of Petra and the Business Intelligence department for providing guidance and support throughout this graduation project. We also acknowledge the World Bank Open Data platform for providing the Logistics Performance Index and GDP datasets used in this project.

---

## Business Intelligence Project Description and Objectives

This project focuses on logistics performance analysis in Jordan.

The project addresses the logistics and supply-chain domain by analyzing how Jordan performs across logistics indicators such as Customs, Infrastructure, International Shipments, Logistics Quality, Tracking and Tracing, and Timeliness.

### Business Problem

Jordan has moderate logistics performance and faces challenges in specific logistics indicators. Weak logistics performance can affect trade efficiency, shipment reliability, supply-chain competitiveness, and economic development.

### Objectives

The project aims to:

- Analyze Jordan’s historical Logistics Performance Index trends
- Identify Jordan’s weakest logistics indicators
- Compare Jordan with regional and global countries
- Cluster countries based on logistics performance similarity
- Forecast future LPI behavior
- Simulate improvement scenarios using what-if analysis
- Build Power BI dashboards for business reporting
- Build a Streamlit interactive decision-support tool
- Provide strategic recommendations for logistics improvement

More details are available in:
[Project Description](docs/01_project_description.md)

---

## Data Research and Acquiring Effort

The project uses data from the World Bank.

### Main Dataset

**Logistics Performance Index (LPI)**  
Source: World Bank Open Data  
Link: https://data.worldbank.org/indicator/LP.LPI.OVRL.XQ

The LPI dataset was selected because it measures logistics performance across countries and includes indicators related to customs, infrastructure, shipment quality, tracking, and timeliness.

### Additional Dataset

**GDP Dataset**  
Source: World Bank Open Data  
Link: https://data.worldbank.org/indicator/NY.GDP.MKTP.CD

GDP was added as supporting economic context. It was not used as a direct forecasting feature, but it helped explain the broader economic environment around logistics development.

More details are available in:
[Data Research](docs/02_data_research.md)

---

## Data Description and Understanding

The dataset contains country-level logistics indicators across selected years.

### Main Fields

| Field | Description |
|---|---|
| Country Name | Name of the country |
| Country Code | ISO country code |
| Indicator Name | Name of the LPI indicator |
| Indicator Code | World Bank indicator code |
| Year | Reporting year |
| Value | LPI score or GDP value |

### Main LPI Indicators

| Indicator Code | Indicator |
|---|---|
| LP.LPI.OVRL.XQ | Overall LPI |
| LP.LPI.CUST.XQ | Customs |
| LP.LPI.INFR.XQ | Infrastructure |
| LP.LPI.ITRN.XQ | International Shipments |
| LP.LPI.LOGS.XQ | Logistics Quality |
| LP.LPI.TRAC.XQ | Tracking and Tracing |
| LP.LPI.TIME.XQ | Timeliness |

Exploratory analysis was used to discover patterns, compare countries, study correlations, and identify Jordan’s weakest indicators.

More details are available in:
[Exploratory Data Analysis](docs/04_exploratory_data_analysis.md)

---

## Data Primary Cleaning and Transformation

The raw dataset required several preprocessing steps before analysis.

Main preprocessing steps included:

- Loading raw World Bank files
- Removing unnecessary metadata
- Reshaping data from wide format to long format
- Renaming columns
- Converting Year and Value columns to numeric types
- Handling missing values
- Applying interpolation and gap-filling
- Removing or controlling invalid observations
- Exporting clean analytical datasets

A dedicated gap-filling strategy was used because LPI data is not reported annually. Linear interpolation and conservative estimation were applied to preserve useful time-series continuity.

KNIME was also used to preprocess the GDP dataset through a visual ETL workflow.

More details are available in:
[Data Preprocessing](docs/03_data_preprocessing.md)

---

## Data Visualization and Insights

Visualizations were created to understand:

- Jordan’s historical LPI trend
- Weak indicator ranking
- Country comparisons
- Indicator relationships
- Forecast behavior
- What-if scenarios
- GDP economic context

Key visualization insights:

- Jordan’s weakest indicators are International Shipments and Customs.
- Customs showed stronger relationship with Overall LPI than International Shipments.
- Jordan’s LPI trend shows moderate performance with limited improvement.
- GDP provides economic context but was not treated as a direct cause of LPI change.

More details are available in:
[EDA Documentation](docs/04_exploratory_data_analysis.md)

---

## Dashboard Design and Business Insights

Power BI was used to create the main Business Intelligence dashboard.

The Power BI dashboard focused on:

- KPI reporting
- Jordan LPI overview
- indicator comparison
- country comparison
- trend visualization
- business-oriented insights

### Business Questions Answered

| Business Question | Dashboard / Analysis Component |
|---|---|
| How has Jordan’s LPI changed over time? | Historical LPI trend |
| What are Jordan’s weakest logistics indicators? | Weak indicator ranking |
| How does Jordan compare with other countries? | Country comparison visuals |
| Which indicators should be prioritized? | Indicator impact and what-if analysis |
| What improvement scenario may increase LPI? | Streamlit what-if simulator |

### Streamlit Dashboard

Streamlit was used to extend the dashboard into an interactive simulation application. Users can change improvement assumptions and immediately observe projected LPI changes and recommendations.

Live application:  
https://gpbi20252-gqcxmgnwreelog4izl8syj.streamlit.app/

More details are available in:
[Streamlit Application](docs/08_streamlit_application.md)

---

## Advanced Analytics and AI Modeling

This project includes several advanced analytics components.

### 1. Clustering Analysis

K-Means clustering was used to group countries based on logistics performance similarity.

The clustering process included:

- feature scaling
- Elbow Method
- PCA visualization
- cluster labeling
- Jordan cluster movement analysis

More details:
[Clustering Analysis](docs/05_clustering_analysis.md)

### 2. Forecasting Analysis

Forecasting was used to estimate future LPI behavior.

The forecasting process included:

- train-test split
- holdout validation using 2023
- linear regression
- polynomial regression
- weighted forecasting
- adaptive model selection
- evaluation metrics

More details:
[Forecasting Analysis](docs/06_forecasting_analysis.md)

### 3. What-if Analysis

What-if analysis was used to simulate improvement scenarios for Jordan.

The simulation uses:

```text
Estimated Impact = Improvement Amount × Correlation with Overall LPI × Impact Weight