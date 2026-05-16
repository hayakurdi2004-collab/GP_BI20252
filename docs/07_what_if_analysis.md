# What-If Analysis and Decision Support

# Overview

The What-If Analysis stage was one of the most important intelligent decision-support components in this project.

Unlike forecasting, which attempts to estimate future values based on historical trends, What-If Analysis explores hypothetical improvement scenarios.

The purpose of this stage was to answer questions such as:

- What could happen if Jordan improves its weakest logistics indicators?
- Which indicators have the strongest influence on Overall LPI performance?
- Which logistics reforms may generate the greatest impact?
- How sensitive is Jordan’s logistics performance to operational improvements?

This stage transformed the project from:
- descriptive analysis

into:
- interactive decision-support analysis

This significantly increased the Business Intelligence value of the project.

---

# Difference Between Forecasting and What-If Analysis

It was important to separate:
- forecasting
- scenario simulation

because both answer different business questions.

## Forecasting answers:

"What is likely to happen if current trends continue?"

Forecasting depends on:
- historical patterns
- statistical trends
- previous observations

---

## What-If Analysis answers:

"What could happen if specific improvements are introduced?"

What-If Analysis depends on:
- assumptions
- scenario simulation
- hypothetical intervention analysis

This distinction was important because:
- forecasting estimates passive future behavior
- what-if analysis explores active improvement strategies

---

# Why What-If Analysis Was Important

The project focuses on Jordan’s logistics performance.

Simply forecasting Jordan’s future score was not enough because forecasting alone does not explain:
- how performance can improve
- which areas need intervention
- what reforms matter most

Decision-makers need actionable insights.

Therefore, What-If Analysis was designed to simulate:
- logistics reform scenarios
- indicator improvements
- operational enhancement impact

This made the project more useful from a Business Intelligence and strategic planning perspective.

---

# Selecting Jordan as the Main Case Study

Jordan was selected because:
- it showed moderate logistics performance
- it demonstrated improvement potential
- it contained weaker logistics indicators
- it was relevant for regional comparison

EDA and clustering analysis showed that Jordan belongs to:
- Mid-Low Performer logistics groups

This suggested that Jordan has:
- room for development
- structural logistics challenges
- operational improvement opportunities

---

# Identifying Weak Indicators

Before building What-If scenarios, the project first identified Jordan’s weakest indicators.

The following indicators consistently showed weaker performance:

| Indicator | Description |
|---|---|
| International Shipments | Ease of arranging international shipments |
| Customs | Customs and border efficiency |

These indicators were identified through:
- ranking analysis
- EDA visualization
- indicator comparison
- country-level analysis

---

# Why These Indicators Were Selected

The weak indicators were selected because:
- they consistently showed lower scores
- they strongly influence logistics efficiency
- they directly affect trade and supply chain performance
- they demonstrated meaningful correlation with Overall LPI

The selection was therefore:
- data-driven
- analytically supported
- business-oriented

This prevented arbitrary scenario creation.

---

# Correlation-Based Impact Analysis

The project estimated indicator influence using correlation analysis.

For each major indicator:
- correlation with Overall LPI was calculated

The purpose was to estimate:
- how strongly an indicator is associated with overall logistics performance

---

# Why Correlation Was Used

The LPI dataset does not provide direct causal weights between indicators and Overall LPI.

Therefore, correlation analysis was used as a practical approximation to estimate influence strength.

This approach was selected because:
- it is interpretable
- suitable for limited datasets
- computationally simple
- useful for business-oriented simulation

---

# Important Limitation

The project does NOT claim that correlation equals causation.

Instead:
- correlation was used as an estimation mechanism
- the simulation represents approximate influence relationships

This limitation was acknowledged to avoid overstating model certainty.

---

# Building the Simulation Logic

The What-If model estimated improvement impact using the following structure:

```text
Estimated Impact =
Improvement Amount × Correlation × Impact Weight

Explanation of Each Component
1. Improvement Amount

This represents the hypothetical increase in a weak indicator.

Examples:

improving Customs by 0.25
improving International Shipments by 0.35

These values were selected as:

realistic moderate improvements
not extreme unrealistic jumps
2. Correlation

The correlation value estimates how strongly the indicator is associated with Overall LPI.

Higher correlation means:

improving the indicator may influence Overall LPI more strongly
3. Impact Weight

A conservative impact weight was added to avoid unrealistic simulation results.

This was extremely important because:

not all indicator improvements fully translate into overall score improvement
logistics systems are complex
real-world improvements contain uncertainty

The impact weight acts as a moderation factor.

Why Conservative Modeling Was Important

Without conservative control:

the simulation could exaggerate improvements
unrealistic scores could appear
the model would lose credibility

The project intentionally avoided:

overly optimistic scenarios
unrealistic growth assumptions

This made the simulation:

more responsible
more interpretable
more realistic
Baseline Scenario

Before applying improvements, a baseline future scenario was generated.

The baseline represents:

expected future performance if current trends continue

The baseline was derived from:

historical trend estimation
previous forecasting results

This baseline acted as the comparison point for all scenarios.

Improvement Scenarios

Several improvement scenarios were generated.

Scenario 1 — Improve Customs

This scenario simulated:

customs modernization
border process improvement
customs digitization
operational efficiency gains

The simulation estimated how Overall LPI might respond if Customs improves.

Scenario 2 — Improve International Shipments

This scenario simulated:

shipment facilitation
logistics coordination improvement
reduced shipment barriers
smoother international logistics operations
Scenario 3 — Combined Improvement

This scenario combined:

Customs improvement
International Shipments improvement

This represented a broader logistics reform strategy.

The combined scenario produced the strongest simulated improvement.

Scenario 4 — Decline Scenario

A decline scenario was also included.

This simulated:

operational deterioration
logistics inefficiencies
weaker shipment performance

This scenario was important because decision-support systems should analyze:

positive outcomes
negative outcomes
risk conditions
Why Multiple Scenarios Were Necessary

Using multiple scenarios improves:

strategic understanding
comparative interpretation
policy evaluation

A single scenario would oversimplify logistics behavior.

Multiple scenarios allow:

comparison between reforms
evaluation of trade-offs
understanding improvement sensitivity
Streamlit Decision-Support Application

The What-If Analysis was integrated into an interactive Streamlit application.

The application allows users to:

modify improvement values
simulate different logistics reforms
observe projected LPI changes
compare scenarios interactively

This transformed the project into:

an interactive BI tool
a decision-support dashboard
a simulation system
Why Streamlit Was Used

Streamlit was selected because:

it supports rapid interactive dashboard development
it integrates easily with Python
it supports sliders and simulation interfaces
it improves project presentation quality

The Streamlit application significantly improved:

usability
visualization
interaction
demonstration capability
Recommendation Engine

The Streamlit application also included a recommendation engine.

The recommendation engine generates:

alternative logistics solutions
reform suggestions
operational recommendations

based on:

selected scenario values
improvement intensity

Examples:

customs digitization
border automation
shipment coordination improvements

This increased the practical value of the project.

Why Recommendation Systems Matter

Business Intelligence projects should not only visualize data.

They should also:

support decisions
guide improvements
provide actionable insights

The recommendation engine transformed the project from:

passive analytics

into:

actionable decision-support
Challenges Faced During What-If Development

Several challenges appeared during development.

Challenge 1 — Lack of Direct Causal Weights

The dataset did not provide:

exact mathematical relationships
between indicators and Overall LPI.

Solution:

correlation-based estimation was used
Challenge 2 — Risk of Unrealistic Improvements

Large hypothetical improvements could produce unrealistic forecasts.

Solution:

conservative impact weights were introduced
predictions were clipped within valid LPI range
Challenge 3 — Limited Historical Observations

The dataset contains relatively few official years.

This limits:

statistical certainty
advanced causal modeling

Solution:

short-term simulation
moderate assumptions
simplified interpretable logic
Challenge 4 — Balancing Simplicity and Intelligence

The simulation needed to remain:

understandable
interactive
academically acceptable

while still providing:

meaningful analysis
intelligent behavior
realistic interpretation

Solution:

interpretable simulation logic
clear mathematical structure
business-oriented explanations
Outputs Generated

Several outputs were generated during What-If Analysis.

Examples:

LPI_WhatIf.png
LPI_WhatIf_Jordan.png
LPI_WhatIf_Results.csv
Jordan indicator ranking charts

The Streamlit application also became a major project output.

Business Interpretation

The What-If Analysis showed that Jordan’s logistics performance may improve significantly if:

customs efficiency improves
shipment facilitation improves
logistics coordination becomes more efficient

The analysis also showed that:

some indicators influence Overall LPI more strongly than others
combined reforms are more effective than isolated improvements
Strategic Insights

Several strategic insights were obtained.

1. Customs modernization matters significantly

Customs improvements demonstrated strong estimated influence on Overall LPI.

2. Shipment facilitation improves logistics competitiveness

Reducing shipment barriers may improve logistics performance and trade efficiency.

3. Combined reforms are stronger

Simultaneously improving multiple indicators generates larger estimated benefits.

4. Jordan has realistic improvement potential

Jordan’s logistics performance is not structurally weak beyond recovery.

Moderate reforms may generate measurable logistics improvement.

Importance of What-If Analysis in the Project

The What-If Analysis stage significantly increased the Business Intelligence sophistication of the project.

It introduced:

interactive simulation
decision-support analysis
recommendation generation
strategic interpretation

Without What-If Analysis:

the project would remain mainly descriptive and predictive

With What-If Analysis:

the project became actionable and decision-oriented

This transformed the project into:

an intelligent logistics decision-support system

rather than only a forecasting project.

Final Summary

The What-If Analysis stage:

identified Jordan’s weak logistics dimensions
estimated improvement impact
generated simulation scenarios
supported strategic logistics interpretation
powered the Streamlit interactive application

The stage combined:

EDA
forecasting
correlation analysis
scenario simulation
recommendation logic

into a unified decision-support framework.

This made What-If Analysis one of the most innovative and practically valuable components of the entire project.