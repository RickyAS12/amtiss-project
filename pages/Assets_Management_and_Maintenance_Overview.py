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
data=run_query(
    "SELECT * FROM amtiss-dashboard-performance.amtiss_lma.union_hm_gc ORDER BY date"
)
data = pd.DataFrame(data)
data['date'] = pd.to_datetime(data['date'])

st.image('amtiss_logo-bg-white-1.png', width=150)

st.markdown("<h1 style='text-align: center; color: black;'>Assets' Management and Maintenance Overview</h1>", unsafe_allow_html=True)
st.write('')
st.write('')
st.write('')

# Filter and process 'hm_record' data
df1 = data[data['source'] == 'hm_record']
df1 = df1[['asset_category', 'asset_code', 'total_hour_meter', 'date']]
df1 = df1.rename(columns={'total_hour_meter': 'hour_meter', 'date': 'asset_used_at'})
df1.drop_duplicates()
df1 = df1.groupby(['asset_category', 'asset_code', 'asset_used_at']).agg({
    'hour_meter': 'max',  # Get the max hour_meter
}).reset_index()

# Filter and process 'good_consume' data
df = data[data['source'] == 'good_consume']
df = df[['asset_category', 'asset_code', 'asset_name', 'product_id', 'product_name', 'product_bought_qty', 'total_price', 'date', 'consume_id_good_consume']]

# List of brand names to exclude
brand_names = ['toyota', 'mitsubishi', 'hino', 'dongfeng', 'mazda', 'ford', 'hilux', 
               'suzuki', 'triton', 'strada', 'dutro', 'bridgestone', 'innova', 'avanza', 
               'luxio', 'liugong','yukimura', 'weichai']

# Preprocess the product names
# def preprocess(text):
#     text = re.sub(r'\b\w*\d\w*\b', '', text)  # Remove words containing digits
#     for brand in brand_names:
#         text = re.sub(r'\b' + re.escape(brand) + r'\b', '', text, flags=re.IGNORECASE)  # Remove brand names
#     text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters
#     text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
#     return text

# df['cleaned_product_name'] = df['product_name'].apply(preprocess)
# df['cleaned_product_name'] = df['cleaned_product_name'].apply(lambda x: ' '.join(x.split()[:2]))

# # Separate single-word and multi-word product names
# single_word_df = df[df['cleaned_product_name'].str.split().str.len() == 1].copy()
# multi_word_df = df[df['cleaned_product_name'].str.split().str.len() > 1].copy()

# # Process multi-word product names with TF-IDF and KMeans
# vectorizer = TfidfVectorizer(ngram_range=(1, 1))
# X = vectorizer.fit_transform(multi_word_df['cleaned_product_name'])

# kmeans = KMeans(n_clusters=1000, random_state=0)  # Adjust n_clusters based on your needs
# kmeans.fit(X)

# # Determine cluster labels based on the top 2 most common terms
# terms = vectorizer.get_feature_names_out()
# order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

# cluster_labels = []
# for i in range(kmeans.n_clusters):
#     top_terms = sorted(list(set(terms[ind] for ind in order_centroids[i, :2])))[::-1]  # Select only the top 2 terms and sort them
#     cluster_labels.append(' '.join(top_terms))

# # Map cluster numbers to cluster labels
# cluster_label_map = dict(enumerate(cluster_labels))
# multi_word_df['product_subcategory'] = [cluster_label_map[label] for label in kmeans.labels_]

# # Assign single-word product names their own cluster labels
# single_word_df['product_subcategory'] = single_word_df['cleaned_product_name']

# # Combine results
# df = pd.concat([single_word_df, multi_word_df])

# # Ensure cluster_label is consistent with desired output format
# df['product_subcategory'] = df['product_subcategory'].astype(str)
# df['product_subcategory'] = df['product_subcategory'].str.upper()

# # Drop the 'cleaned_product_name' column
# df.drop('cleaned_product_name', axis=1, inplace=True)
# df.reset_index(drop=True, inplace=True)

# Aggregate data by grouping and summing 'product_bought_qty' and 'total_price'
df = df.groupby(
    ['asset_category', 'asset_code', 'asset_name', 'product_id', 'product_name', 'date', 'consume_id_good_consume'], as_index=False, dropna=False
).agg({
    'product_bought_qty': 'sum',
    'total_price': 'sum'
})

# Prepare df2 for merging
df2 = data[data['source'] == 'good_consume']
df2 = df2[['consume_id_assignment', 'report_date', 'create_date']]

# Merge df and df2 on 'consume_id_good_consume' and 'consume_id_assignment'
merged_df = pd.merge(df, df2, left_on='consume_id_good_consume', right_on='consume_id_assignment', how='left')

# Merge merged_df with df1 on 'asset_category' and 'asset_code'
merged_df = pd.merge(merged_df, df1, on=['asset_category', 'asset_code'], how='outer')

# Convert 'create_date' and 'asset_used_at' columns to datetime format
merged_df['create_date'] = pd.to_datetime(merged_df['create_date'], errors='coerce')
merged_df['asset_used_at'] = pd.to_datetime(merged_df['asset_used_at'], errors='coerce')

# Ensure both datetime columns only have the date part for comparison
merged_df['create_date'] = merged_df['create_date'].dt.normalize()
merged_df['asset_used_at'] = merged_df['asset_used_at'].dt.normalize()

# Filter rows where 'create_date' is equal to 'asset_used_at'
filtered_df = merged_df[merged_df['create_date'] == merged_df['asset_used_at']].copy()

# Sort by necessary columns
filtered_df = filtered_df.sort_values(by=['asset_category', 'asset_code', 'asset_name', 'product_id', 'create_date'])

# Calculate the difference in 'hour_meter'
filtered_df['serviced_when'] = filtered_df.groupby(['asset_category', 'asset_code', 'asset_name', 'product_id'])['hour_meter'].diff()

# Calculate the minimum 'hour_meter' for each group
min_hour_meter = merged_df.groupby(['asset_category', 'asset_code', 'asset_name', 'product_id'])['hour_meter'].transform('min')

# Replace null values in 'serviced_when' with the difference to the minimum 'hour_meter'
filtered_df['serviced_when'] = filtered_df.apply(
    lambda row: row['hour_meter'] - min_hour_meter[row.name] if pd.isnull(row['serviced_when']) else row['serviced_when'],
    axis=1
)

# Calculate the average of 'serviced_when' grouped by the specified columns
filtered_df['avg_serviced_when'] = filtered_df.groupby(
    ['asset_category', 'asset_code', 'asset_name', 'product_id']
)['serviced_when'].transform('mean').round()

# Calculate the service count grouped by the specified columns
filtered_df['service_count'] = filtered_df.groupby(
    ['asset_category', 'asset_code', 'asset_name', 'product_id']
)['create_date'].transform('count')

# Aggregate filtered_df by grouping and calculating the mean of 'avg_serviced_when'
df_new = filtered_df.groupby(
    ['asset_category', 'asset_code', 'asset_name', 'product_name', 'service_count', 'consume_id_good_consume'], as_index=False, dropna=False
).agg({
    'avg_serviced_when': 'mean'
}).rename(columns={'avg_serviced_when': 'avg_service'})

# Prepare df2 for merging, selecting only 'consume_id_assignment' and 'create_date'
df_for_merge = df2[['consume_id_assignment', 'create_date']]
df_for_merge = df_for_merge.groupby(['consume_id_assignment'], as_index=False, dropna=False).agg({
    'create_date': 'max'
}).rename(columns={'create_date': 'latest_product_maintained_at'})

# Aggregate df1 by grouping and calculating the max of 'asset_used_at' and 'hour_meter'
df1_new = df1.groupby(['asset_category', 'asset_code'], as_index=False, dropna=False).agg({
    'asset_used_at': 'max',
    'hour_meter': 'max'
}).rename(columns={'asset_used_at': 'latest_asset_used_at'})

# Merge df_new with df1_new on 'asset_category' and 'asset_code'
df_new = pd.merge(df_new, df1_new, on=['asset_category', 'asset_code'], how='outer')

# Merge df_new with df_for_merge on 'consume_id_good_consume' and 'consume_id_assignment'
df_new = pd.merge(df_new, df_for_merge, right_on='consume_id_assignment', left_on='consume_id_good_consume', how='outer')

# Ensure 'latest_asset_used_at' and 'latest_product_maintained_at' are in datetime format
df_new['latest_asset_used_at'] = pd.to_datetime(df_new['latest_asset_used_at'], errors='coerce')
df_new['latest_product_maintained_at'] = pd.to_datetime(df_new['latest_product_maintained_at'], errors='coerce')

# Calculate the difference in hours between 'latest_asset_used_at' and 'latest_product_maintained_at'
df_new['hours_after_maintained'] = ((df_new['latest_asset_used_at'] - df_new['latest_product_maintained_at']).dt.total_seconds() / 3600).round()

# Define the conditions for determining the 'status' of each asset
conditions = [
    (df_new['hours_after_maintained'] > df_new['avg_service']),
    (df_new['hours_after_maintained'] >= df_new['avg_service'] - 24) & (df_new['hours_after_maintained'] <= df_new['avg_service']),
    (df_new['hours_after_maintained'] < df_new['avg_service']),
    (df_new['product_name'].isna())
]

# Define the corresponding statuses for each condition
choices = ['Needed service', 'Incoming Service', 'Good condition', 'Product not registered in good consume']

# Create the 'status' column based on the defined conditions and choices
df_new['status'] = np.select(conditions, choices, default=np.nan)

# Select the necessary columns for the final DataFrame
df_final = df_new[['asset_category', 'asset_code', 'asset_name', 'product_name', 'status', 'service_count', 'latest_product_maintained_at', 'latest_asset_used_at', 'avg_service', 'hours_after_maintained']]

# Add filters for asset_category and asset_code using Streamlit
asset_categories = df_final['asset_category'].unique()
selected_asset_category = st.multiselect('Asset Category', asset_categories, default=[])

# Filter asset_code options based on selected asset_category
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
if selected_asset_category and selected_asset_code:
    filtered_df_st = df_final[(df_final['asset_category'].isin(selected_asset_category)) & 
                              (df_final['asset_code'].isin(selected_asset_code))]
elif selected_asset_category:
    filtered_df_st = df_final[df_final['asset_category'].isin(selected_asset_category)]
elif selected_asset_code:
    filtered_df_st = df_final[df_final['asset_code'].isin(selected_asset_code)]
else:
    filtered_df_st = df_final

# Define the custom order for the status
status_order = ['Needed service', 'Incoming Service', 'Good condition', 'Product not registered in good consume']

# Ensure the 'status' column is categorical with the custom order
filtered_df_st['status'] = pd.Categorical(filtered_df_st['status'], categories=status_order, ordered=True)

# Sort the filtered DataFrame based on the 'status' column
filtered_df_st = filtered_df_st.sort_values('status')

# Filter for products with status 'Needed Service'
needed_service_df = filtered_df_st[filtered_df_st['status'] == 'Needed service']

# Group by asset category and asset code to count occurrences
needed_service_count = needed_service_df.groupby(['asset_category', 'asset_code']).size().reset_index(name='count')

# Select the asset category you want to focus on
if selected_asset_category:
    selected_category_count = needed_service_count[needed_service_count['asset_category'].isin(selected_asset_category)]
else:
    selected_category_count = needed_service_count

# Sort the DataFrame by count of needed services and select the top 10
top_10_asset_codes = selected_category_count.sort_values(by='count', ascending=False).head(10)

# Plotting the bar chart for the top 10 asset codes using Altair
bar_chart = alt.Chart(top_10_asset_codes).mark_bar().encode(
    x=alt.X('asset_code', title='Asset Code', sort='-y'),
    y=alt.Y('count', title='Number of Products Needed Service'),
    color=alt.value('red')
)

# Display the chart in Streamlit
st.altair_chart(bar_chart, use_container_width=True)

# Display the filtered DataFrame
st.write("### Detailed Asset Information")

# Pagination settings
rows_per_page = 20
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# Pagination controls
total_rows = len(filtered_df_st)
total_pages = total_rows // rows_per_page + (total_rows % rows_per_page > 0)

st.write(f'Total rows: {total_rows}, Total pages: {total_pages}')

start_row = st.session_state.current_page * rows_per_page
end_row = start_row + rows_per_page

# Display the current page of data
st.table(filtered_df_st.iloc[start_row:end_row])

# Place the buttons next to each other using columns
col1, col2 = st.columns(2)

# Place the buttons next to each other using columns with custom width
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

with col4:
    if st.button('Previous') and st.session_state.current_page > 0:
        st.session_state.current_page -= 1

with col5:
    if st.button('Next') and end_row < total_rows:
        st.session_state.current_page += 1

st.info("When 'Average Age' value is lower than the 'Days Difference from Latest Used at' value, will be considered as product that needed service!")
