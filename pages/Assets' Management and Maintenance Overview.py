import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from google.oauth2 import service_account
from google.cloud import bigquery

if 'sbstate' not in st.session_state:
    st.session_state.sbstate = 'collapsed'

# Set Overall Page Layout
st.set_page_config(
    page_title='Dashboard',
    layout='wide',
    initial_sidebar_state=st.session_state.sbstate
)

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

@st.cache_data(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows

# Query
# 1.Query for Cost and Hour Meter Trend
db_search=run_query(
    "SELECT * FROM amtiss-dashboard-performance.amtiss_lma.union_hm_gc ORDER BY date"
)
db_search = pd.DataFrame(db_search)
db_search['date'] = pd.to_datetime(db_search['date'])

# # 1. Query for detail product bought
# db_search=db.query(
#     'SELECT * FROM union_hm_gc ORDER BY date'
#     , ttl=600
# )
# db_search['date'] = pd.to_datetime(db_search['date'])

st.image('amtiss_logo-bg-white-1.png', width=150)

st.markdown("<h1 style='text-align: center; color: black;'>Assets' Management and Maintenance Overview</h1>", unsafe_allow_html=True)
st.write('')
st.write('')
st.write('')

# Aggregate data by grouping
db_good_consume = db_search[db_search['source']=='good_consume']
df_good_consume = db_good_consume.groupby(
    ['asset_category', 'asset_code', 'asset_name','product_id', 'product_name', 'date'], as_index=False, dropna=False
).agg({
    'product_bought_qty': 'sum',
    'total_price': 'sum'
}).sort_values(
    by=['asset_category', 'asset_code', 'asset_name','product_id', 'date'], 
    ascending=[True, True, True, True, True]
)

df_good_consume['date'] = pd.to_datetime(df_good_consume['date'])

df_good_consume['purchase_count'] = df_good_consume.groupby(
    ['asset_category', 'asset_code', 'asset_name','product_id']
)['date'].transform('count')

df_good_consume['start_date'] = df_good_consume['date']

df_good_consume['end_date'] = df_good_consume.groupby(['asset_category', 'asset_code', 'asset_name','product_id'])['date'].shift(-1)

df_good_consume['product_age'] = (df_good_consume['end_date'] - df_good_consume['start_date']).dt.days

df_good_consume['average_age'] = df_good_consume.groupby(['asset_category', 'asset_code', 'asset_name','product_id'])['product_age'].transform('mean')

# Create a summarized dataframe with the latest product maintained date and average age
df_good_consume_2 = df_good_consume.groupby(['asset_category', 'asset_code', 'asset_name','product_name', 'purchase_count'], as_index=False, dropna=False).agg({
    'date': 'max',
    'average_age': 'mean'
}).rename(columns={'date': 'latest_product_maintained_at'})
df_good_consume_2['average_age'] = df_good_consume_2['average_age'].round(0)

# Retrieve and process data for the hm_record table
db_hm_record = db_search[db_search['source'] == 'hm_record'][['source', 'asset_category', 'asset_code', 'asset_name','date']]
db_hm_record = db_hm_record.rename(columns={'date': 'latest_asset_used_at'}).groupby(['asset_category', 'asset_code','asset_name'], as_index=False, dropna=False)['latest_asset_used_at'].max()
db_hm_record['latest_asset_used_at'] = pd.to_datetime(db_hm_record['latest_asset_used_at'])

# --Merge the two dataframes
merged_df = pd.merge(df_good_consume_2, db_hm_record, on=['asset_category', 'asset_code', 'asset_name'], how='outer')
merged_df['days_difference_from_latest_used_at'] = (merged_df['latest_asset_used_at'] - merged_df['latest_product_maintained_at']).dt.days
# Calculate the difference from today's date (ini kalau machine learningnya gabisa, nanti pake kondisi ini)
# today = pd.to_datetime("today")
# merged_df['days_since_latest_use'] = (today - merged_df['latest_asset_used_at']).dt.days

# Define the conditions and choices for status
conditions = [
    (merged_df['days_difference_from_latest_used_at'] > merged_df['average_age']),
    (merged_df['days_difference_from_latest_used_at'] >= merged_df['average_age'] - 10) & (merged_df['days_difference_from_latest_used_at'] <= merged_df['average_age']),
    (merged_df['days_difference_from_latest_used_at'] < merged_df['average_age']),
    (merged_df['average_age'].isna() & (merged_df['purchase_count'] == 1) & merged_df['latest_asset_used_at'].notna()),
    (merged_df['latest_asset_used_at'].isna() & merged_df['days_difference_from_latest_used_at'].isna()),
    (merged_df['latest_product_maintained_at'].isna() & merged_df['days_difference_from_latest_used_at'].isna())
    #, (merged_df['days_since_latest_use'] > 1000) (ini kalau machine learningnya gabisa, nanti pake kondisi ini)
]
choices = [
    'Needed service', 
    'Service in a few days', 
    'Good condition', 
    'Average age unknown', 
    'Asset not registered in hour meter', 
    'Asset not registered in good consume' 
    #, 'Asset is not used' (ini kalau machine learningnya gabisa, nanti pake kondisi ini)
]

# Create the 'status' column
merged_df['status'] = np.select(conditions, choices, default=np.nan)

# Select and finalize columns
df_final = merged_df[['asset_category', 'asset_code', 'asset_name','product_name', 'status', 'purchase_count', 'latest_product_maintained_at', 'latest_asset_used_at', 'average_age', 'days_difference_from_latest_used_at']]

# Add filters for asset_category and asset_code
asset_categories = df_final['asset_category'].unique()
selected_asset_category = st.multiselect('Asset Category', asset_categories, default=[])

# Filter asset_code options based on selected asset_category
if selected_asset_category:
    filtered_codes = df_final[df_final['asset_category'].isin(selected_asset_category)]
    asset_codes = filtered_codes['asset_code'].unique()
else:
    asset_codes = df_final['asset_code'].unique()

selected_asset_code = st.multiselect('Asset Code', asset_codes, default=[])

# Filter the DataFrame based on selected filters
if selected_asset_category and selected_asset_code:
    filtered_df = df_final[(df_final['asset_category'].isin(selected_asset_category)) & (df_final['asset_code'].isin(selected_asset_code))]
elif selected_asset_category:
    filtered_df = df_final[df_final['asset_category'].isin(selected_asset_category)]
elif selected_asset_code:
    filtered_df = df_final[df_final['asset_code'].isin(selected_asset_code)]
else:
    filtered_df = df_final

if selected_asset_category:
    filtered_df_for_top_10_chart = df_final[(df_final['asset_category'].isin(selected_asset_category))]
else:
    filtered_df_for_top_10_chart = df_final

# Define the custom order for the status
status_order = [
    "Needed service", 
    "Service in a few days", 
    "Good condition", 
    "Average age unknown", 
    "Asset not registered in hour meter", 
    "Asset not registered in good consume"
]

# Ensure the 'status' column is categorical with the custom order
filtered_df['status'] = pd.Categorical(filtered_df['status'], categories=status_order, ordered=True)

# Sort the filtered DataFrame based on the 'status' column
filtered_df = filtered_df.sort_values('status', ascending=True)

# Filter for products with status 'Needed Service'
needed_service_df = filtered_df_for_top_10_chart[filtered_df_for_top_10_chart['status'] == 'Needed service']

# Group by asset category and asset code to count occurrences
needed_service_count = needed_service_df.groupby(['asset_category', 'asset_code']).size().reset_index(name='count')

st.write('')
st.write('')
st.write('')

st.write('### Top 10 Asset Codes with "Needed Service" Status')

# Select the asset category you want to focus on
if selected_asset_category:
    selected_category_count = needed_service_count[needed_service_count['asset_category'].isin(selected_asset_category)]
else:
    selected_category_count = needed_service_count

# Sort the DataFrame by count of needed services and select the top 10
top_10_asset_codes = selected_category_count.sort_values(by='count', ascending=False).head(10)

# Plotting the bar chart for the top 10 asset codes using Altair
bar_chart = alt.Chart(top_10_asset_codes).mark_bar().encode(
    y=alt.Y('asset_code', title=None, sort=alt.SortField(field='count', order='descending')),
    x=alt.X('count', title='Number of Products Needed Service'),
    tooltip=[
        alt.Tooltip('asset_code', title='Asset Code'),
        alt.Tooltip('count', title='# Product Needed Service')
    ]
).properties(
    height=400
)

cols_show = st.columns(2)
with cols_show[1]:
    # Display the dataframe in Streamlit
    st.dataframe(top_10_asset_codes.reset_index(drop=True) ,use_container_width=True, hide_index=True)
with cols_show[0]:
    # Display the chart in Streamlit
    st.altair_chart(bar_chart, use_container_width=True)

# Display the filtered DataFrame
st.write("### Detailed Asset Information")

filtered_df = filtered_df.rename(
    columns={
        'asset_category' : 'Asset Category',
        'asset_code' : 'Asset Code',
        'asset_name' : 'Asset Name',
        'product_name' : 'Product Name',
        'status' : 'Status',
        'purchase_count' : 'Purchase Count',
        'latest_product_maintained_at' : 'Latest Product Maintained at',
        'latest_asset_used_at' : 'Latest Asset Used at',
        'average_age' : 'Average Age' ,
        'days_difference_from_latest_used_at' : 'Days Difference from Latest Used at'
    }
)

# Display the filtered DataFrame
st.dataframe(filtered_df.reset_index(drop=True))

st.info("When 'Average Age' value is lower than the 'Days Difference from Latest Used at' value, will be considered as product that needed service!")
