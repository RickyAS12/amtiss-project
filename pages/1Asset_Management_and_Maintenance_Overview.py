import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
# import re
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans
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

def set_global_exception_handler(f):
    import sys
    script_runner = sys.modules["streamlit.runtime.scriptrunner.script_runner"]
    script_runner.handle_uncaught_app_exception.__code__ = f.__code__

def exception_handler(e):
    # st.error(f"Oops, something funny happened with a {type(e).__name__}")
    st.error(f"Oops, looks like an error has comes up. Logging the developer right now. Thank you")

set_global_exception_handler(exception_handler)

# st.set_option('deprecation.showPyplotGlobalUse', False)

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

st.image('amtiss_logo-bg-white-1.png', width=150)

st.markdown("<h1 style='text-align: center; color: black;'>Asset Management and Maintenance Overview</h1>", unsafe_allow_html=True)
st.write('')
st.write('')
st.write('')

st.info("The data used in this are assets' products that are registered in either the assignment, good_consume, or hm_record datasets.")

data=run_query(
    "SELECT source, asset_category, asset_code, total_hour_meter, date, asset_name, product_id, product_name, product_bought_qty, total_price, consume_id_good_consume, consume_id_assignment, report_date, due_date, fix_hm_record FROM amtiss-dashboard-performance.amtiss_lma.join_hm_gc_c_ass ORDER BY date"
)
data = pd.DataFrame(data)

# Load the necessary columns from the data
# data = pd.read_csv('product_data.csv', usecols=[
#     'source', 'asset_category', 'asset_code', 'total_hour_meter', 'date',
#     'asset_name', 'product_id', 'product_name', 'product_bought_qty',
#     'total_price', 'consume_id_good_consume', 'consume_id_assignment', 'report_date', 'due_date', 'fix_hm_record'
# ])

# Process 'hm_record' data
hm_data = data[data['source'] == 'hm_record'][['asset_category', 'asset_code', 'total_hour_meter', 'date']]
# Replace NaN values in 'asset_category' with "Unknown Category"
hm_data['asset_category'] = hm_data['asset_category'].fillna('Unknown Category')
hm_data = hm_data.rename(columns={'total_hour_meter': 'hour_meter', 'date': 'asset_used_at'}).drop_duplicates()
hm_data = hm_data.groupby(['asset_category', 'asset_code', 'asset_used_at'])['hour_meter'].max().reset_index()

# Process 'good_consume' data
gc_data = data[data['source'] == 'good_consume'][[
    'asset_category', 'asset_code', 'asset_name', 'product_id', 'product_name',
    'product_bought_qty', 'total_price', 'date', 'consume_id_good_consume', 'consume_id_assignment', 'due_date', 'fix_hm_record'
]]
# Replace NaN values in 'asset_category' with "Unknown Category"
gc_data['asset_category'] = gc_data['asset_category'].fillna('Unknown Category')

# To apply machine learning, uncomment the code below :
# List of brand names to exclude
# brand_names = ['toyota', 'mitsubishi', 'hino', 'dongfeng', 'mazda', 'ford', 'hilux', 
#                'suzuki', 'triton', 'strada', 'dutro', 'bridgestone', 'innova', 'avanza', 
#                'luxio', 'liugong', 'yukimura', 'weichai']

# Preprocess the product names
# def preprocess(text):
#     text = re.sub(r'\b\w*\d\w*\b', '', text)  # Remove words containing digits
#     for brand in brand_names:
#         text = re.sub(r'\b' + re.escape(brand) + r'\b', '', text, flags=re.IGNORECASE)  # Remove brand names
#     text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters
#     text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
#     return text

# Apply preprocessing to product names
# gc_data['cleaned_product_name'] = gc_data['product_name'].apply(preprocess)
# gc_data['cleaned_product_name'] = gc_data['cleaned_product_name'].apply(lambda x: ' '.join(x.split()[:2]))

# Separate single-word and multi-word product names
# single_word_df = gc_data[gc_data['cleaned_product_name'].str.split().str.len() == 1].copy()
# multi_word_df = gc_data[gc_data['cleaned_product_name'].str.split().str.len() > 1].copy()

# Process multi-word product names with TF-IDF and KMeans
# vectorizer = TfidfVectorizer(ngram_range=(1, 1))
# X = vectorizer.fit_transform(multi_word_df['cleaned_product_name'])

# kmeans = KMeans(n_clusters=1000, random_state=0)  # Adjust n_clusters based on your needs
# kmeans.fit(X)

# Determine cluster labels based on the top 2 most common terms
# terms = vectorizer.get_feature_names_out()
# order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

# cluster_labels = []

# for i in range(kmeans.n_clusters):
#     top_terms = sorted(list(set(terms[ind] for ind in order_centroids[i, :2])))[::-1]   # Select only the top 2 terms and sort them
#     cluster_labels.append(' '.join(top_terms))

# Map cluster numbers to cluster labels
# cluster_label_map = dict(enumerate(cluster_labels))
# multi_word_df['product_subcategory'] = [cluster_label_map[label] for label in kmeans.labels_]

# Assign single-word product names their own cluster labels
# single_word_df['product_subcategory'] = single_word_df['cleaned_product_name']

# Combine results
# gc_data = pd.concat([single_word_df, multi_word_df])

# Ensure cluster_label is consistent with desired output format
# gc_data['product_subcategory'] = gc_data['product_subcategory'].astype(str)
# gc_data['product_subcategory'] = gc_data['product_subcategory'].str.upper()

# Drop the 'cleaned_product_name' column
# gc_data.drop('cleaned_product_name', axis=1, inplace=True)

# Optional: Reset index if necessary
# gc_data.reset_index(drop=True, inplace=True)

gc_agg = gc_data.groupby([
    'asset_category', 'asset_code', 'asset_name', 'product_id', # 'product_subcategory',
    'product_name', 'date', 'consume_id_good_consume'
]).agg({
    'product_bought_qty': 'sum',
    'total_price': 'sum'
}).reset_index()

# Merge dataframes
merged_df = pd.merge(gc_agg, gc_data[['consume_id_assignment', 'due_date', 'fix_hm_record']].drop_duplicates(), 
                     left_on='consume_id_good_consume', right_on='consume_id_assignment', how='left')
merged_df = pd.merge(merged_df, hm_data, on=['asset_category', 'asset_code'], how='outer')

# Convert dates to datetime
merged_df['due_date'] = pd.to_datetime(merged_df['due_date'], errors='coerce').dt.normalize()
merged_df['asset_used_at'] = pd.to_datetime(merged_df['asset_used_at'], errors='coerce').dt.normalize()

# Filter and sort data
filtered_df = merged_df[merged_df['due_date'] == merged_df['asset_used_at']].copy()
filtered_df = filtered_df.sort_values(by=['asset_category', 'asset_code', 'asset_name', # 'product_subcategory',
                                          'product_id', 'due_date'])

# Calculate 'serviced_when'
filtered_df['serviced_when'] = filtered_df.groupby(['asset_category', 'asset_code', 'asset_name', # 'product_subcategory',
                                                    'product_id'])['fix_hm_record'].diff()
min_hour_meter = merged_df.groupby(['asset_category', 'asset_code', 'asset_name', # 'product_subcategory',
                                    'product_id'])['fix_hm_record'].transform('min')
filtered_df['serviced_when'] = filtered_df.apply(
    lambda row: row['fix_hm_record'] - min_hour_meter[row.name] if pd.isnull(row['serviced_when']) else row['serviced_when'],
    axis=1
)

# Calculate average 'serviced_when' and service count
filtered_df['avg_serviced_when'] = filtered_df.groupby(['asset_category', 'asset_code', 'asset_name', # 'product_subcategory',
                                                        'product_id'])['serviced_when'].transform('mean').round()
filtered_df['service_count'] = filtered_df.groupby(['asset_category', 'asset_code', 'asset_name', # 'product_subcategory',
                                                    'product_id'])['due_date'].transform('count')

# Aggregate final data
df_new = filtered_df.groupby([
    'asset_category', 'asset_code', 'asset_name', # 'product_subcategory',
    'product_name', 'service_count', 'consume_id_good_consume'
], as_index=False).agg({
    'avg_serviced_when': 'mean'
}).rename(columns={'avg_serviced_when': 'avg_service'})

# Prepare for final merges
df2_agg = data[['consume_id_assignment', 'due_date', 'fix_hm_record']].drop_duplicates().groupby('consume_id_assignment').agg({
    'due_date': 'max',
    'fix_hm_record' : 'max'
}).rename(columns={'due_date': 'latest_product_maintained_at', 'fix_hm_record' : 'maintained_hour_meter'}).reset_index()

hm_agg = hm_data.groupby(['asset_category', 'asset_code'], as_index=False).agg({
    'asset_used_at': 'max',
    'hour_meter': 'max'
}).rename(columns={'asset_used_at': 'latest_asset_used_at', 'hour_meter' : 'latest_used_hour_meter'})

df_new = pd.merge(df_new, hm_agg, on=['asset_category', 'asset_code'], how='outer')
df_new = pd.merge(df_new, df2_agg, left_on='consume_id_good_consume', right_on='consume_id_assignment', how='outer')

# Calculate 'hours_after_maintained'
df_new['latest_asset_used_at'] = pd.to_datetime(df_new['latest_asset_used_at'], errors='coerce')
df_new['latest_product_maintained_at'] = pd.to_datetime(df_new['latest_product_maintained_at'], errors='coerce')
df_new['hours_after_maintained'] = ((df_new['latest_used_hour_meter'] - df_new['maintained_hour_meter']))

# Define asset status
conditions = [
    (df_new['hours_after_maintained'] > df_new['avg_service']),
    (df_new['hours_after_maintained'] >= df_new['avg_service'] - 24) & (df_new['hours_after_maintained'] <= df_new['avg_service']),
    (df_new['hours_after_maintained'] < df_new['avg_service']),
    (df_new['product_name'].isna() & df_new['latest_asset_used_at'].notna())
]
choices = ['Needed service', 'Incoming Service', 'Good condition', 'Product not registered in good consume record']
df_new['status'] = np.select(conditions, choices, default=np.nan)

# Drop rows with null values in all columns of df_new
df_new.dropna(how='all', inplace=True)

# Final DataFrame
df_final = df_new[[
    'asset_category', 'asset_code', 'asset_name', # 'product_subcategory',
    'product_name', 'status', 'service_count',
    'latest_product_maintained_at', 'maintained_hour_meter','latest_asset_used_at', 
    'latest_used_hour_meter','avg_service', 'hours_after_maintained'
]]


# Add filters for asset_category and asset_code using Streamlit
asset_categories = df_final['asset_category'].unique()
selected_asset_category = st.multiselect('Asset Category', asset_categories, default=[])

if selected_asset_category:
    filtered_codes = df_final[df_final['asset_category'].isin(selected_asset_category)]
    asset_codes = filtered_codes['asset_code'].unique()
else:
    asset_codes = df_final['asset_code'].unique()

selected_asset_code = st.multiselect('Asset Code', asset_codes, default=[])

# Add filter for product_subcategory based on selected asset_category and asset_code
# if selected_asset_category and selected_asset_code:
#     filtered_subcategories = df_final[(df_final['asset_category'].isin(selected_asset_category)) & 
#                                       (df_final['asset_code'].isin(selected_asset_code))]
#     product_subcategories = filtered_subcategories['product_subcategory'].unique()
# elif selected_asset_category:
#     filtered_subcategories = df_final[df_final['asset_category'].isin(selected_asset_category)]
#     product_subcategories = filtered_subcategories['product_subcategory'].unique()
# elif selected_asset_code:
#     filtered_subcategories = df_final[df_final['asset_code'].isin(selected_asset_code)]
#     product_subcategories = filtered_subcategories['product_subcategory'].unique()
# else:
#     product_subcategories = df_final['product_subcategory'].unique()

# selected_product_subcategory = st.multiselect('Product Subcategory', product_subcategories, default=[])

# Filter the DataFrame based on selected filters
if selected_asset_category and selected_asset_code: # and selected_product_subcategory:
    filtered_df = df_final[(df_final['asset_category'].isin(selected_asset_category)) & 
                           (df_final['asset_code'].isin(selected_asset_code))] # & 
                           # (df_final['product_subcategory'].isin(selected_product_subcategory))]
elif selected_asset_category and selected_asset_code:
    filtered_df = df_final[(df_final['asset_category'].isin(selected_asset_category)) & 
                           (df_final['asset_code'].isin(selected_asset_code))]
elif selected_asset_category: # and selected_product_subcategory:
    filtered_df = df_final[(df_final['asset_category'].isin(selected_asset_category))] # & 
                           # (df_final['product_subcategory'].isin(selected_product_subcategory))]
elif selected_asset_code: # and selected_product_subcategory:
    filtered_df = df_final[(df_final['asset_code'].isin(selected_asset_code))] # & 
                           # (df_final['product_subcategory'].isin(selected_product_subcategory))]
elif selected_asset_category:
    filtered_df = df_final[df_final['asset_category'].isin(selected_asset_category)]
elif selected_asset_code:
    filtered_df = df_final[df_final['asset_code'].isin(selected_asset_code)]
# elif selected_product_subcategory:
#     filtered_df = df_final[df_final['product_subcategory'].isin(selected_product_subcategory)]
else:
    filtered_df = df_final


# Filter for products with status 'Needed Service'
needed_service_df = filtered_df[filtered_df['status'] == 'Needed service']

# Count occurrences for needed services
needed_service_count = needed_service_df.groupby(['asset_category', 'asset_code', 'asset_name']).size().reset_index(name='count')

# Select the asset category to focus on
if selected_asset_category:
    selected_category_count = needed_service_count[needed_service_count['asset_category'].isin(selected_asset_category)]
else:
    selected_category_count = needed_service_count

# Sort and select the top 10 asset codes
top_10_asset_codes = selected_category_count.sort_values(by='count', ascending=False).head(10)
top_10_asset_codes = top_10_asset_codes[['asset_category', 'asset_code', 'asset_name', 'count']]

# Plotting the bar chart for the top 10 asset codes using Altair
bar_chart = alt.Chart(top_10_asset_codes).mark_bar().encode(
    x=alt.X('asset_code', title='Asset Code', sort='-y'),
    y=alt.Y('count', title='Number of Products Needed Service'),
    color=alt.value('red'),
    tooltip=[
        alt.Tooltip('asset_category', title='Asset Category'),
        alt.Tooltip('asset_code', title='Asset Code'),
        alt.Tooltip('asset_name', title='Asset Name'),
        alt.Tooltip('count', title='Number of Products that Needed Service')
    ]
)

st.write("### Top 10 Assets with Highest Number of Products in 'Needed Service' Status")

st.altair_chart(bar_chart, use_container_width=True)

st.write("### Detailed Asset Information")

# Add filter for status column
status_order = ['Needed service', 'Incoming Service', 'Good condition',  'Product not registered in good consume record']
selected_statuses = st.multiselect('Filter by Status', status_order, default=status_order)

# Apply status filter
filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]

# Pagination settings
rows_per_page = 20
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# Pagination controls
total_rows = len(filtered_df)
total_pages = (total_rows // rows_per_page) + (total_rows % rows_per_page > 0)

st.write(f'Total rows: {total_rows}, Total pages: {total_pages}')

start_row = st.session_state.current_page * rows_per_page
end_row = start_row + rows_per_page

# Display the current page of data with reset index
st.dataframe(filtered_df.iloc[start_row:end_row].reset_index(drop=True))

# Pagination buttons
col1, col2, _ = st.columns([2, 2, 6]) 

with col1:
    if st.button('Previous') and st.session_state.current_page > 0:
        st.session_state.current_page -= 1

with col2:
    if st.button('Next') and end_row < total_rows:
        st.session_state.current_page += 1

# Explanation of each status
st.write("### Explanation of Status:")
st.write("- **Needed service**: Products that have surpassed the average service interval, indicating they require maintenance.")
st.write("- **Incoming Service**: Products that are approaching the average service interval within the next 24 hours, calculated from the latest asset ussage records in the hour meter.")
st.write("- **Good condition**: Products that are within the average service interval and do not require immediate maintenance.")
st.write("- **Product not registered in good consume record**: Products that doesn't have a valid product name but have a record in the hour meter dataset, suggesting they have not been registered for good consume dataset.")
