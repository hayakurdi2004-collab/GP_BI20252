import pandas as pd
import os

os.makedirs('outputs', exist_ok=True)

# ============================================================
# Step 1: Read the data
# ============================================================
print("Step 1: Reading data...")

df_data    = pd.read_excel('data/LPIEXCEL.xlsx', sheet_name='Data')
df_country = pd.read_excel('data/LPIEXCEL.xlsx', sheet_name='Country')

print(f"  Data sheet:    {df_data.shape[0]} rows x {df_data.shape[1]} columns")
print(f"  Country sheet: {df_country.shape[0]} countries")

# ============================================================
# Step 2: Melt — convert year columns into rows
# ============================================================
print("\nStep 2: Melting year columns into rows...")

YEAR_COLS = ['2007', '2010', '2012', '2014', '2016', '2018', '2023']

df_melted = df_data.melt(
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
    value_vars=YEAR_COLS,
    var_name='Year',
    value_name='Value'
)

df_melted['Year']  = df_melted['Year'].astype(int)
df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce')

print(f"  Rows after melt: {df_melted.shape[0]}")

# ============================================================
# Step 3: Check for duplicates
# ============================================================
print("\nStep 3: Checking for duplicates...")

duplicates = df_melted[df_melted.duplicated(
    subset=['Country Code', 'Indicator Code', 'Year'], keep=False
)]

print(f"  Duplicate rows found: {len(duplicates)}")

if len(duplicates) > 0:
    df_melted = df_melted.drop_duplicates(
        subset=['Country Code', 'Indicator Code', 'Year'], keep='first'
    )
    print(f"  Rows after removing duplicates: {df_melted.shape[0]}")
else:
    print("  No duplicates — data is clean")

# ============================================================
# Step 4: Merge with Country sheet — add Region and Income Group
# ============================================================
print("\nStep 4: Merging with country info...")

df_country_clean = df_country[['Country Code', 'Short Name', 'Region', 'Income Group']].copy()
df_merged = df_melted.merge(df_country_clean, on='Country Code', how='left')

print(f"  Regions found: {df_merged['Region'].nunique()}")

# ============================================================
# Step 5: Label indicators as Score or Rank
# ============================================================
print("\nStep 5: Labeling indicators...")

df_merged['Indicator Type'] = df_merged['Indicator Code'].apply(
    lambda x: 'Score' if str(x).endswith('XQ') else 'Rank'
)

indicator_short = {
    'LP.LPI.OVRL.XQ': 'LPI Overall Score',
    'LP.LPI.OVRL.RK': 'LPI Overall Rank',
    'LP.LPI.CUST.XQ': 'Customs Score',
    'LP.LPI.INFR.XQ': 'Infrastructure Score',
    'LP.LPI.ITRN.XQ': 'Int. Shipments Score',
    'LP.LPI.LOGS.XQ': 'Logistics Quality Score',
    'LP.LPI.TRAC.XQ': 'Tracking Score',
    'LP.LPI.TIME.XQ': 'Timeliness Score',
}
df_merged['Indicator Short'] = (df_merged['Indicator Code']
                                 .map(indicator_short)
                                 .fillna(df_merged['Indicator Code']))

# ============================================================
# Step 6: Drop redundant columns and reorder
# ============================================================
print("\nStep 6: Dropping redundant columns and reordering...")

df_merged = df_merged.drop(columns=['Indicator Name', 'Short Name'])

df_merged = df_merged[[
    'Country Code',
    'Country Name',
    'Region',
    'Income Group',
    'Indicator Code',
    'Indicator Short',
    'Indicator Type',
    'Year',
    'Value'
]]

print(f"  Final columns: {list(df_merged.columns)}")
print(f"  Final shape:   {df_merged.shape[0]} rows x {df_merged.shape[1]} columns")

# ============================================================
# Step 7: Missing values analysis
# ============================================================
print("\nStep 7: Missing values analysis...")

print(f"  Total missing values: {df_merged['Value'].isna().sum()}")

print("\n  Missing per year:")
df_miss = df_merged[df_merged['Value'].isna()]
miss_year = df_miss.groupby('Year').size().rename('Missing Count')
print(miss_year.to_string())

print("\n  Missing per indicator (top 10):")
miss_ind = (df_miss.groupby('Indicator Code').size()
            .sort_values(ascending=False).head(10).rename('Missing Count'))
print(miss_ind.to_string())

print("\n  Countries with fewer than 4 years of Overall LPI data:")
df_overall   = df_merged[df_merged['Indicator Code'] == 'LP.LPI.OVRL.XQ']
country_years = (df_overall.groupby('Country Code')['Value']
                 .apply(lambda x: x.notna().sum())
                 .sort_values())
few_data = country_years[country_years < 4]
print(few_data.to_string())
print(f"  Total countries excluded from forecasting: {len(few_data)}")

# ============================================================
# Step 8: Save final clean data — only once, after all steps
# ============================================================
print("\nStep 8: Saving clean data...")

df_merged.to_csv('outputs/LPI_clean.csv', index=False)
print("  Saved: outputs/LPI_clean.csv")
print("\nDone — run next: python 02_eda.py")