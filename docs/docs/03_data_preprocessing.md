# Data Preprocessing

## Overview

Data preprocessing was one of the most important stages in this project because the original LPI dataset contained missing values, irregular year availability, duplicated structures, and inconsistent country observations.

The preprocessing stage aimed to transform the raw World Bank dataset into a clean analytical dataset suitable for:
- exploratory analysis
- clustering
- forecasting
- what-if analysis
- dashboard visualization

Python and KNIME were both used during preprocessing.

---

# Step 1 — Loading the Raw Dataset

The original dataset was downloaded from the World Bank in Excel format.

The dataset contained:
- country information
- indicator codes
- yearly observations
- metadata columns
- missing values across many years

Python Pandas was used to load the dataset.

Main libraries used:
- pandas
- numpy

---

# Step 2 — Data Cleaning

Several cleaning operations were applied to the raw dataset.

## Cleaning Tasks

### 1. Removing unnecessary metadata rows

The raw Excel dataset contained extra rows and metadata that were not required for analysis.

These rows were removed before processing.

---

### 2. Renaming columns

Column names were standardized to improve readability and consistency during analysis.

Examples:
- Country Name
- Country Code
- Indicator Name
- Indicator Code
- Year
- Value

---

### 3. Converting wide format to long format

The original dataset stored years as separate columns.

Using Pandas melt operation, the dataset was transformed into long format where:
- each row represents one country + one indicator + one year

This structure is more suitable for:
- filtering
- aggregation
- machine learning
- visualization

---

### 4. Data type conversion

Several columns were converted into proper data types.

Examples:
- Year → integer
- Value → numeric/float

Invalid or corrupted values were automatically converted into missing values (NaN).

---

### 5. Duplicate handling

Duplicate rows were checked and removed to avoid biased analysis results.

---

# Step 3 — Missing Value Analysis

One of the largest challenges in the LPI dataset was missing values.

Many countries did not report observations for all years.

Some indicators also had missing observations across different periods.

A missing value analysis was performed to:
- identify sparse countries
- identify incomplete indicators
- understand data quality issues

---

# Step 4 — Interpolation and Estimation

Instead of removing all incomplete rows, interpolation techniques were used to preserve useful information.

A hybrid interpolation strategy was implemented.

## Small gaps

For small missing gaps between nearby years:
- linear interpolation was applied

This assumes gradual changes between close observations.

---

## Large gaps

For larger gaps:
- trend-based estimation was used
- polynomial estimation and country trends were considered

This approach reduced unrealistic jumps in values.

---

## Confidence control

Predicted/interpolated values were clipped within valid LPI boundaries:
- minimum = 1
- maximum = 5

This prevented invalid or unrealistic scores.

---

# Step 5 — Outlier Detection

Outlier analysis was performed to identify abnormal logistics scores.

Visualizations and statistical analysis were used to:
- detect extreme values
- compare countries
- identify unusual changes across years

The purpose was not to remove all outliers, but to understand important country behavior differences.

---

# Step 6 — KNIME GDP Preprocessing

KNIME was used as an additional ETL and preprocessing tool for the GDP dataset.

## KNIME workflow tasks

The KNIME workflow included:
- importing GDP data
- reshaping data
- handling missing values
- type conversion
- filtering years
- exporting clean GDP outputs

The workflow was saved as part of the project documentation.

---

# Step 7 — Final Clean Dataset

After preprocessing, the final datasets were exported as CSV files.

Main outputs included:
- LPI_clean.csv
- LPI_interpolated.csv
- GDP clean outputs

These datasets were later used for:
- clustering
- forecasting
- dashboard development
- Streamlit application
- what-if analysis

---

# Why Preprocessing Was Important

Without preprocessing:
- forecasting models would fail
- clustering quality would decrease
- missing values would distort analysis
- visualizations would become inconsistent

The preprocessing stage significantly improved:
- data consistency
- analytical reliability
- model usability
- visualization quality

This stage formed the foundation of the entire project.