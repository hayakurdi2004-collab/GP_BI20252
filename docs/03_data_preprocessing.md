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
# Gap-Filling Strategy

One of the most important preprocessing challenges in this project was handling missing observations and irregular reporting years.

The Logistics Performance Index dataset is not reported annually for all countries.
Instead, official observations exist only for selected years, and many countries contain incomplete records.

This created several analytical problems:
- inconsistent time-series continuity
- sparse country observations
- interrupted logistics trajectories
- forecasting instability
- visualization inconsistency

Therefore, a dedicated gap-filling strategy was designed instead of simply removing missing rows.

---

# Why Missing Values Could Not Be Ignored

Removing all incomplete observations would significantly reduce the usable dataset.

This would create multiple problems:
- loss of historical information
- reduced country coverage
- weaker forecasting reliability
- unstable clustering behavior
- inconsistent visualization trends

Because the dataset already contains limited historical years, preserving useful information was extremely important.

---

# Small Gap Handling

For small missing gaps between nearby observations:
- linear interpolation was applied

Linear interpolation estimates missing values by assuming gradual change between nearby years.

This method was selected because logistics performance usually changes progressively rather than abruptly over short periods.

Example:
If a country had:
- 2014 value
- 2018 value

but a missing intermediate year,
the missing value could be estimated using linear progression.

---

# Why Linear Interpolation Was Appropriate

Linear interpolation was appropriate because:
- LPI scores generally evolve gradually
- abrupt extreme yearly changes are uncommon
- the dataset contains limited observations
- simpler interpolation reduces overfitting risk

Linear interpolation also preserves:
- trend continuity
- relative country positioning
- realistic movement patterns

---

# Large Gap Handling

Large gaps required special handling.

The largest example was:
- 2018 → 2023

This five-year gap introduced substantial uncertainty because:
- logistics systems may change significantly
- economic conditions may shift
- global disruptions may occur
- simple linear estimation may become unrealistic

Therefore, large gaps were not treated identically to smaller gaps.

Instead:
- trend-based estimation
- historical behavior analysis
- weighted forecasting logic

were used to improve estimation quality.

---

# Hybrid Estimation Strategy

A hybrid strategy was adopted because no single interpolation technique was sufficient for all situations.

The project combined:
- linear interpolation
- trend estimation
- weighted historical behavior
- conservative forecasting assumptions

This hybrid approach improved:
- flexibility
- realism
- stability
- analytical consistency

---

# Conservative Estimation Philosophy

A conservative estimation philosophy was intentionally adopted.

The project avoided:
- aggressive extrapolation
- unrealistic jumps
- exaggerated country improvement
- extreme forecast behavior

This was important because:
- the dataset is limited
- overfitting risk is high
- logistics systems evolve gradually

The goal was to produce:
- stable estimates
- interpretable values
- realistic trajectories

rather than artificially optimistic predictions.

---

# Value Clipping and Constraints

All interpolated and estimated values were constrained within the valid LPI range:

- Minimum = 1
- Maximum = 5

This prevented:
- invalid scores
- unrealistic outputs
- extreme forecasting behavior

The clipping mechanism improved:
- model reliability
- analytical consistency
- visualization quality

---

# Why a Gap-Filling Strategy Was Necessary

Without a proper gap-filling strategy:
- forecasting models would become unstable
- clustering quality would decrease
- country trends would become fragmented
- visualization continuity would break

The strategy helped maintain:
- temporal continuity
- country comparability
- stable logistics trajectories
- analytical usability

---

# Limitations of Gap Filling

Although interpolation improves continuity, it also introduces uncertainty.

Interpolated values are:
- estimates
- not official observations

Therefore:
- the project used conservative assumptions
- predictions were short-term
- confidence intervals were included during forecasting

This limitation was acknowledged to maintain analytical transparency.

---

# Importance in the Overall Project

The gap-filling strategy became one of the foundational preprocessing components in the project.

It directly supported:
- forecasting
- clustering
- trend analysis
- visualization
- what-if simulation

Without this stage, later analytical components would become significantly weaker and less reliable.

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