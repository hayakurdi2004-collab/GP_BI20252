# Data Research

## Project Dataset

This project uses the World Bank Logistics Performance Index (LPI) dataset.

Source:
https://data.worldbank.org/indicator/LP.LPI.OVRL.XQ

The dataset contains logistics performance indicators for multiple countries across different years.

---

# Main Indicators

The project focuses on the following LPI indicators:

| Indicator Code | Indicator Name |
|---|---|
| LP.LPI.OVRL.XQ | Overall LPI |
| LP.LPI.CUST.XQ | Customs |
| LP.LPI.INFR.XQ | Infrastructure |
| LP.LPI.ITRN.XQ | International Shipments |
| LP.LPI.LOGS.XQ | Logistics Quality |
| LP.LPI.TRAC.XQ | Tracking & Tracing |
| LP.LPI.TIME.XQ | Timeliness |

---

# Additional Dataset

An additional GDP dataset was collected from the World Bank to support explanatory economic analysis.

GDP Source:
https://data.worldbank.org/indicator/NY.GDP.MKTP.CD

The GDP dataset was not used as a predictive feature inside the forecasting model.
Instead, it was used as a secondary analytical component to study possible economic relationships with logistics performance.

---

# Data Challenges

Several data challenges were identified during preprocessing:

- Missing values
- Irregular reporting years
- Sparse country observations
- Inconsistent availability across indicators

To solve these problems:
- Data cleaning was applied using Python
- Missing values were handled using interpolation and hybrid estimation
- KNIME workflows were used for GDP preprocessing and transformation

---

# Why This Dataset?

The Logistics Performance Index dataset is useful because it measures important logistics and trade-related dimensions such as customs efficiency, infrastructure quality, shipment reliability, and timeliness.

These indicators are strongly related to supply chain performance and national logistics competitiveness.

The dataset also allows:
- forecasting analysis
- clustering analysis
- what-if simulations
- decision-support applications