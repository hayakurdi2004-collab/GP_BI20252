# Forecasting Analysis

## Overview

Forecasting was one of the most important advanced analytics stages in this project.

The goal of forecasting was to estimate future Logistics Performance Index (LPI) scores for selected countries, especially Jordan, using historical LPI data.

The forecasting stage was designed to answer the question:

**How might logistics performance evolve in the near future based on historical patterns?**

The forecasting analysis focused on:
- understanding historical LPI movement
- predicting future values
- evaluating model reliability
- comparing country-level forecasting results
- supporting what-if and decision-support analysis

---

# Why Forecasting Was Needed

The LPI dataset provides historical observations, but decision-makers need forward-looking insights.

Forecasting helps answer:
- Is Jordan expected to improve?
- Is Jordan’s logistics performance stagnating?
- Which countries show stronger future trends?
- How reliable are future predictions?

This makes forecasting useful for:
- business planning
- policy analysis
- logistics strategy
- performance monitoring

---

# Forecasting Challenge

The LPI dataset introduced several challenges.

## 1. Limited Number of Years

The LPI dataset is not reported every year.

The available official years were:

- 2007
- 2010
- 2012
- 2014
- 2016
- 2018
- 2023

This means the dataset has few historical points for each country.

This created a challenge because machine learning and forecasting models usually perform better with more data.

---

## 2. Irregular Time Gaps

The time gaps between observations were not equal.

Examples:
- 2007 to 2010 = 3-year gap
- 2010 to 2012 = 2-year gap
- 2018 to 2023 = 5-year gap

This was a major issue because normal forecasting assumes consistent time intervals.

To address this, the project used:
- interpolation for smaller gaps
- trend-based handling for larger gaps
- weighted modeling to give importance to recent observations

---

## 3. Large Gap Between 2018 and 2023

The gap between 2018 and 2023 was the largest gap in the dataset.

This gap created uncertainty because:
- logistics systems may change significantly over five years
- economic and global events may affect performance
- direct interpolation may be too simplistic

Therefore, the large gap was handled carefully using a hybrid approach rather than simple direct filling.

---

## 4. Country-Level Differences

Different countries showed different patterns.

Some countries showed:
- stable improvement
- decline
- fluctuation
- stagnation

This meant one model could not perfectly fit all countries.

For this reason, the forecasting approach included adaptive model selection.

---

# Data Used for Forecasting

The forecasting model focused mainly on the Overall LPI indicator:

| Indicator Code | Indicator |
|---|---|
| LP.LPI.OVRL.XQ | Overall LPI Score |

Selected focus countries were used for comparison:

- Jordan
- Saudi Arabia
- United Arab Emirates
- Egypt
- Germany
- Singapore
- China
- United States

These countries were selected to compare:
- Jordan
- regional countries
- high-performing global logistics systems
- large economies

---

# Forecasting Preparation

Before forecasting, the data was prepared through several steps:

1. Cleaning the raw LPI dataset
2. Removing invalid values
3. Handling missing observations
4. Creating interpolated values
5. Keeping values within valid LPI range
6. Selecting countries with enough historical data
7. Splitting data into training and testing periods

Countries with fewer than four valid observations were excluded because their data was insufficient for reliable forecasting.

---

# Train-Test Split

A holdout validation approach was used.

The model was trained on:

- 2007 to 2018

The year 2023 was used as a test year.

This means the model attempted to predict 2023 using only past data.

Then the predicted 2023 value was compared with the actual 2023 value.

This was important because it tested whether the forecasting model could reasonably estimate unseen data.

---

# Why 2023 Was Used as Holdout

2023 was selected as the test year because:
- it is the latest official LPI year
- it was not included in the training period
- it allows comparison between predicted and actual values

This helped evaluate:
- forecasting accuracy
- model reliability
- prediction error

---

# Forecasting Models Used

Two model types were considered:

## 1. Linear Regression

Linear regression was used to model simple trend behavior.

It assumes that logistics performance changes in a relatively stable direction over time.

Linear regression is useful when:
- the trend is gradual
- the dataset is small
- overfitting should be avoided
- interpretation is important

---

## 2. Polynomial Regression

Polynomial regression was used to capture non-linear movement.

It can model curves and changes that are not purely straight-line trends.

Polynomial regression is useful when:
- countries show curved improvement
- growth is not constant
- historical patterns are non-linear

However, polynomial models can overfit when data is limited.

---

# Why Adaptive Model Selection Was Used

Because countries behave differently, the project did not force one model on all countries.

Instead, the model compared linear and polynomial behavior and selected the more suitable approach.

For declining or unstable countries, linear regression was often preferred because it is more conservative.

This was especially important for Jordan because using polynomial regression could exaggerate the decline or create unrealistic forecasts.

---

# Why Jordan Used a Conservative Model

Jordan showed a relatively weak or declining logistics pattern compared to some other countries.

A highly flexible model could produce unrealistic results due to the small number of observations.

Therefore, a more conservative forecasting approach was preferred.

This helped avoid:
- overfitting
- exaggerated future decline
- unrealistic upward or downward curves

---

# Weighted Forecasting

A weighted approach was applied to give more importance to recent observations.

This was important because recent years are more relevant for predicting future performance.

Older data still matters, but logistics systems can change over time.

The weighting approach helped balance:
- historical trend
- recent performance
- time gap effects

---

# Why Weighting Was Needed

Without weighting, all years would contribute equally.

However, LPI values from 2007 may not represent the current logistics environment as strongly as values from 2018 or 2023.

Weighting helps make the model more realistic by giving stronger influence to newer data.

---

# Forecast Years

The model generated forecasts for:

- 2024
- 2025
- 2026

These years were selected because they represent short-term future performance.

Short-term forecasting is more realistic than long-term forecasting because uncertainty increases over time.

---

# Confidence Intervals

Confidence intervals were added to show uncertainty around forecasts.

Forecasting is never perfectly certain, especially with:
- limited data
- irregular year gaps
- country-specific changes

The confidence interval gives a range around the predicted value.

This helps communicate that forecasts are estimates, not exact future facts.

---

# Why Confidence Intervals Matter

Confidence intervals are important because they show model uncertainty.

A narrow interval means:
- the forecast is more stable
- the model is more confident

A wide interval means:
- there is higher uncertainty
- the country has more unstable historical behavior

This is useful for decision-makers because it prevents overconfidence in exact numbers.

---

# Model Evaluation Metrics

Several metrics were used to evaluate forecasting performance.

## R² Score

R² measures how well the model explains variation in the training data.

Higher R² means the model fits historical data better.

However, R² alone is not enough because a model can fit training data well but still predict poorly.

---

## RMSE

Root Mean Squared Error measures the average prediction error.

It penalizes larger errors more heavily.

Lower RMSE indicates better prediction performance.

---

## MAE

Mean Absolute Error measures the average absolute difference between predicted and actual values.

It is easy to interpret because it uses the same scale as the LPI score.

---

## Test Error

Test error compared:
- predicted 2023 value
- actual 2023 value

This was one of the most important evaluation measures because it tested unseen performance.

---

# Evaluation Findings

The forecasting results showed that model performance differed by country.

Some countries had strong prediction quality because their historical trends were stable.

Other countries had weaker forecasting reliability due to:
- fluctuations
- limited observations
- unusual changes
- large gaps between years

Jordan showed moderate reliability but also some uncertainty, which is expected due to its historical fluctuations.

---

# Why Some Countries Forecast Better Than Others

Countries with stable logistics systems forecast better because their historical patterns are smoother.

Examples:
- Germany
- Singapore
- United States

Countries with more unstable logistics behavior are harder to forecast.

This is because sudden improvements or declines are difficult to predict from limited historical points.

---

# Forecasting Limitations

The forecasting model has several limitations.

## 1. Limited Historical Data

The dataset contains only a small number of official LPI years.

This limits the model’s ability to learn complex patterns.

---

## 2. Irregular Time Intervals

The years are not evenly spaced, which creates forecasting difficulty.

---

## 3. External Factors Not Included

The model does not directly include external events such as:
- economic shocks
- political changes
- trade disruptions
- infrastructure investments
- regional instability

---

## 4. Forecasts Are Estimates

The predicted values should not be treated as guaranteed outcomes.

They should be interpreted as trend-based estimates.

---

# How Limitations Were Handled

The project handled these limitations by:

- using short-term forecasting only
- comparing multiple models
- applying conservative model selection
- adding confidence intervals
- evaluating predictions using 2023 holdout testing
- keeping predictions within the valid LPI range

This made the forecasting process more responsible and interpretable.

---

# Forecasting Outputs

Several outputs were generated:

- LPI_Forecast.png
- LPI_Forecast_Results.csv
- LPI_Evaluation.csv
- LPI_Evaluation.png

These outputs were later used for:
- documentation
- dashboard design
- interpretation
- presentation
- decision-support analysis

---

# Relationship Between Forecasting and What-if Analysis

Forecasting and what-if analysis are related but different.

## Forecasting answers:

**What is likely to happen if historical trends continue?**

## What-if analysis answers:

**What could happen if specific improvements are applied?**

This distinction is important.

Forecasting provides the baseline future expectation.

What-if analysis provides improvement scenarios.

Together, they support stronger decision-making.

---

# Business Interpretation

Forecasting showed that Jordan’s logistics performance may remain moderate if no major changes happen.

This means that improvement requires targeted interventions.

The forecasting results supported the need for:
- customs improvement
- international shipment facilitation
- logistics policy reforms

This connected the forecasting analysis directly to the what-if simulation stage.

---

# Importance of Forecasting in the Project

Forecasting added predictive analytics value to the project.

It moved the analysis beyond historical description and allowed the project to provide future-oriented insights.

This made the project stronger from a Business Intelligence perspective because BI is not only about describing the past but also supporting future decisions.

---

# Final Summary

The forecasting stage provided:
- future LPI estimates
- model evaluation
- uncertainty analysis
- country comparison
- Jordan-focused interpretation

Despite data limitations, the forecasting approach was designed carefully using:
- train-test validation
- adaptive model selection
- weighted regression
- confidence intervals
- short-term forecasting

This made the forecasting stage one of the most important advanced analytics components of the project.