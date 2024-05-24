# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from altair import datum
from google.oauth2 import service_account
from google.cloud import bigquery
# from numerize import numerize
# import locale


if 'sbstate' not in st.session_state:
    st.session_state.sbstate = 'collapsed'
    
# Set Overall Page Layout
st.set_page_config(
    page_title='Dashboard',
    layout='wide',
    initial_sidebar_state=st.session_state.sbstate
)

# st.set_option('deprecation.showPyplotGlobalUse', False)

# The background color of the streamlit
# page_bg_img = """
# <style>
# [data-testid="stAppViewContainer"] {
#     background-color:rgba(251, 200, 59, 0)
# }
# </style>
# """
# st.markdown(page_bg_img, unsafe_allow_html=True)

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
st.write(db_search)
# db_search['date'] = pd.to_datetime(db_search['date'])

# st.dataframe(db_search)
# # 2. Query for detail product bought
# db_prod=db.query(
#     'SELECT * FROM age_product_gc_1'
#     , ttl=600
# )
# db_prod['end_date'] = pd.to_datetime(db_prod['end_date'])

# # 3. Query for value metrics hour meter
# query_df_value_metrics_hour_meter = db.query(
#     f"SELECT * FROM union_hm_gc WHERE source = 'hm_record'"
#     , ttl=600
# )

# # 4. Query for values metrics good consume
# query_df_value_metrics_good_consume = db.query(
#     f"SELECT * FROM union_hm_gc WHERE source = 'good_consume'"
#     , ttl=600
# )

# st.image('amtiss_logo-bg-white-1.png', width=150)

# st.markdown("<h1 style='text-align: center; color: black;'>Assets' Maintenance and Work Hour</h1>", unsafe_allow_html=True)
# st.write('')
# st.write('')
# st.write('')

# # Overview and Filter Options
# cols = st.columns([0.8, 0.5, 1, 0.5, 1, 0.5, 0.8])

# with cols[6]:
#     option_radio = st.radio('**Grouped :**', ['by Assets', 'by Categories'], index=0, horizontal=True, help="How the charts will be based on")
#     if option_radio == 'by Categories':
#         disable_filter_asset = True
#     else:
#         disable_filter_asset = False
    
# with cols[0]:
#     st.write('**Filter :**')
#     # --filter asset categories
#     categories = db_search['asset_category'].unique()
#     with st.popover('Category', use_container_width=True):
#         option_category = st.multiselect(
#             'Choose Categories', 
#             categories,
#             default=categories[0],
#             help="Before filtering asset categories, it's advisable to clear the 'Date Range' selectbox first."
#         )
#         if len(option_category) == 0:
#             st.error('Please choose at least 1 category', icon="🚨")

#     # --filter asset code
#     asset_codes = db_search['asset_code'].loc[db_search['asset_category'].isin(option_category)].unique()
#     with st.popover('Asset Code', use_container_width=True, disabled=disable_filter_asset):
#         if disable_filter_asset == False:
#             option_asset = st.multiselect('Choose Asset Codes', asset_codes, default=asset_codes[0])
#             if len(option_asset) == 0:
#                 st.error('Please choose at least 1 asset code', icon="🚨")
#         else :
#             option_asset = st.multiselect('Choose Asset Codes', asset_codes, default=asset_codes)
    
#     # Filter produk
#     product_codes = db_prod['product_name'].loc[db_prod['asset_code'].isin(option_asset)].unique()
#     with st.popover('Product', use_container_width=True):
#         option_product = st.multiselect('Choose Products', product_codes, default=product_codes)
#         if len(option_product) == 0:
#             st.error('Please choose at least 1 product', icon="🚨")
    
#     # --filter asset date
#     with st.popover('Filter Date', use_container_width=True):
#         option_date = st.selectbox('Choose filter', ['by date', 'Weekly', 'Monthly', 'Quarter', 'Semester', 'Yearly'], index=2)
        
#         # --conditioning option_date
#         true_false_condition = ''
#         if option_date == 'by date':
#             true_false_condition = False
#         else :
#             true_false_condition = True
        
#         # -- conditioning the range of the date
#         if option_radio == 'by Categories':
#             date_range =st.date_input(
#                 label='Filter Date Range', 
#                 min_value=db_search['date'].loc[db_search['asset_category'].isin(option_category)].min().date(), 
#                 max_value=db_search['date'].loc[db_search['asset_category'].isin(option_category)].max().date(), 
#                 value=(),
#                 help="You can also choose not to determine the end date. The range will be specified as the start date you've picked to the latest date available in the record.",
#                 disabled=true_false_condition
#             )
#         else :
#             date_range =st.date_input(
#                 label='Filter Date Range', 
#                 min_value=db_search['date'].loc[db_search['asset_code'].isin(option_asset)].min().date(), 
#                 max_value=db_search['date'].loc[db_search['asset_code'].isin(option_asset)].max().date(), 
#                 value=(),
#                 help="You can also choose not to determine the end date. The range will be specified as the start date you've picked to the latest date available in the record.",
#                 disabled=true_false_condition
#             )
            
# with cols[2]:
#     st.metric('**Total Categories**', value = len(option_category), help='Total asset categories in the database')

#     df_temporary_categories_good_consume = query_df_value_metrics_good_consume[query_df_value_metrics_good_consume['asset_category'].isin(option_category)]
#     df_count_categories_good_consume = df_temporary_categories_good_consume['asset_category'].nunique()
#     st.metric('**Total Categories Maintenanced**', value=df_count_categories_good_consume, help='Total asset categories that have consumed values')
    
#     df_temporary_categories_hour_meter = query_df_value_metrics_hour_meter[query_df_value_metrics_hour_meter['asset_category'].isin(option_category)]
#     df_count_categories_hour_meter = df_temporary_categories_hour_meter['asset_category'].nunique()
#     st.metric('**Total Categories Used**', value = df_count_categories_hour_meter , help='Total asset categories that have hour meter values')    
        
# with cols[4]:
#     st.metric('**Total Assets**', value=len(asset_codes), help='Total asset codes in the current categories')
    
#     df_temporary_good_consume = query_df_value_metrics_good_consume[query_df_value_metrics_good_consume['asset_category'].isin(option_category)]
#     df_count_asset_good_consume = df_temporary_good_consume['asset_code'].nunique()
#     st.metric('**Total Assets Maintenanced**', value = df_count_asset_good_consume, help='Total asset codes that have consumed values')
 
#     df_temporary_hour_meter = query_df_value_metrics_hour_meter[query_df_value_metrics_hour_meter['asset_category'].isin(option_category)]
#     df_count_asset_hour_meter = df_temporary_hour_meter['asset_code'].nunique()
#     st.metric('**Total Assets Used**', value = df_count_asset_hour_meter, help='Total asset codes that have hour meter values')
    
# # Page Break
# st.divider()

# # --Making an expander to show data distribution
# with st.container(border=True):
#     st.markdown("<h3 style='text-align: center; color: black;'>Data Distribution for Each Categories</h3>", unsafe_allow_html=True)
#     cols_exp = st.columns(2)
#     # Ensure the columns are numeric
#     # db_search['total_price'] = pd.to_numeric(db_search['total_price'], errors='coerce')
#     # db_search['hour_meter_per_date'] = pd.to_numeric(db_search['hour_meter_per_date'], errors='coerce')

#     # Handle missing values
#     db_search['total_price'].fillna(0, inplace=True)
#     db_search['hour_meter_per_date'].fillna(0, inplace=True)

#     df_for_chart_exp = db_search.groupby(['source', 'asset_category']).agg(
#         mean_total_price=('total_price', 'mean'),
#         mean_hour_meter_per_date=('hour_meter_per_date', 'mean'),
#         distinct_asset_codes=('asset_code', pd.Series.nunique)
#     ).sort_values(by=['mean_total_price', 'mean_hour_meter_per_date'], ascending=[False, False]).reset_index()

#     df_for_chart_exp['mean_total_price'] = round(df_for_chart_exp['mean_total_price'])
#     df_for_chart_exp['mean_hour_meter_per_date'] = round(df_for_chart_exp['mean_hour_meter_per_date'])
    
#     if 'start_index_chart' not in st.session_state:
#         st.session_state.start_index_chart = 0
        
#     if 'next_index_chart' not in st.session_state:
#         st.session_state.next_index_chart = 10

#     def next_button_chart() :
#         st.session_state.start_index_chart += 10
#         st.session_state.next_index_chart += 10

#     def previous_button_chart():
#         st.session_state.start_index_chart -= 10
#         st.session_state.next_index_chart -= 10
        
#     disable_start_session_button_chart = False
#     disable_next_session_button_chart = False

#     if st.session_state.start_index_chart == 0 :
#         disable_start_session_button_chart = True    

#     if st.session_state.next_index_chart >= len(df_for_chart_exp[df_for_chart_exp['source'] == 'good_consume']) :
#         disable_next_session_button_chart = True

#     with cols_exp[0]:
#         with st.container(border=True, height=450):
#             st.subheader('**AVG Maintenance Price per Category**')
#             st.write('')
#             st.write('')
            
#             # Bar Chart distribusi vertikal untuk good_consume
#             df_good_consume = df_for_chart_exp[df_for_chart_exp['source'] == 'good_consume'][st.session_state.start_index_chart:st.session_state.next_index_chart]

#             bar_chart_good_consume = alt.Chart(df_good_consume).mark_bar().encode(
#                 x=alt.X('mean_total_price:Q', title='Total Price'),
#                 y=alt.Y('asset_category:N', sort=alt.SortField(field='mean_total_price', order='descending'), title=None),
#                 text=alt.Text('mean_total_price:Q', format=",.0f", formatType="number"),
#                 tooltip = [
#                     alt.Tooltip('asset_category', title='Category Name'),
#                     alt.Tooltip('mean_total_price', title='Average Total Maintenance Price', format=",.0f", formatType="number"),
#                     alt.Tooltip('distinct_asset_codes', title='Number of Assets')
#                 ]
#             )
#             label_bar_exp_good_consume = bar_chart_good_consume.mark_text(align='left', dx=3)
#             combo_chart_exp_good_consume = bar_chart_good_consume + label_bar_exp_good_consume
#             st.altair_chart(combo_chart_exp_good_consume, use_container_width=True)

#     with cols_exp[1]:
#         with st.container(border=True, height=450):
#             st.subheader('**AVG Hour Used per Category**')
#             st.write('')
#             st.write('')
            
#             # Bar Chart distribusi vertikal untuk hour_meter
#             df_hour_meter = df_for_chart_exp[df_for_chart_exp['source'] == 'hm_record'][st.session_state.start_index_chart:st.session_state.next_index_chart]

#             bar_chart_hour_meter = alt.Chart(df_hour_meter).mark_bar().encode(
#                 x=alt.X('mean_hour_meter_per_date:Q', title='Work Hour'),
#                 y=alt.Y('asset_category:N', sort=alt.SortField(field='mean_hour_meter_per_date', order='descending'), title=None),
#                 text=alt.Text('mean_hour_meter_per_date:Q'),
#                 tooltip = [
#                     alt.Tooltip('asset_category', title='Category Name'),
#                     alt.Tooltip('mean_hour_meter_per_date', title='Average Work Hour'),
#                     alt.Tooltip('distinct_asset_codes', title='Number of Assets')
#                 ]
#             )
#             label_bar_exp_hour_meter = bar_chart_hour_meter.mark_text(align='left', dx=3)
#             combo_chart_exp_hour_meter = bar_chart_hour_meter + label_bar_exp_hour_meter
#             st.altair_chart(combo_chart_exp_hour_meter, use_container_width=True)
        
#     # --Making the buttons for paginating the bar charts
#     cols_button = st.columns([0.11, 0.89])
#     with cols_button[0]:
#         if st.button("⏮️ Previous", on_click=previous_button_chart, disabled=disable_start_session_button_chart):
#             pass

#     with cols_button[1]:
#         if st.button("Next ⏭️", on_click=next_button_chart, disabled=disable_next_session_button_chart):
#                 pass
 
# st.write('')
# st.write('')
    
# # --Grouped by Asset
# if disable_filter_asset == False:
#     if option_date == 'by date':
#         # --make a new dataframe for the filtered dataframe called db_search_filtered
#         if len(date_range) == 2:
#             start_datetime = datetime.combine(date_range[0], datetime.min.time())
#             end_datetime = datetime.combine(date_range[1], datetime.max.time())
#             db_search_filtered = db_search[
#                 (db_search['asset_code'].isin(option_asset)) & 
#                 (db_search['date'] >= start_datetime) & 
#                 (db_search['date'] <= end_datetime)
#             ]
#             db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
#         elif len(date_range) == 1:
#             start_datetime = datetime.combine(date_range[0], datetime.min.time())
#             end_datetime = datetime.today()
#             db_search_filtered = db_search[
#                 (db_search['asset_code'].isin(option_asset)) & 
#                 (db_search['date'] >= start_datetime) & 
#                 (db_search['date'] <= end_datetime)
#             ]
#             db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
#         else :
#             db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
#             db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # --make a new dataframe for the chart for convenience
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'asset_code', 'reset_hm', db_search_filtered['date'].dt.date, 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'max'
#         }).reset_index(drop=False)
#         grouped_df['date'] = grouped_df['date'].astype(str)

#         # --Making annotation for the line chart if User reset the hour meter value
#         # --Filter rows where reset_hm is 'true'
#         reset_rows = grouped_df[grouped_df['reset_hm'] == 'true']

#         # --Create a list of tuples containing annotation_date_and_text
#         annotation_list = [(row['date'], f'{row['asset_code']} hour meter is reset') for index, row in reset_rows.iterrows()]
        
#         # --Create the dataframe of the annotation
#         df_annotation = pd.DataFrame(annotation_list, columns=['date', 'annotation'])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["date"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('date:O', title=None, sort=alt.SortField(field='date', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_code')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("date", title="Date"),
#                     alt.Tooltip("asset_code", title="Asset Code"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_code'),
#             tooltip=[
#                 alt.Tooltip("date", title="Date"),
#                 alt.Tooltip("asset_code", title="Asset Code"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_code:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_code'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')

#         # --The chart of the annotation
#         chart_annotation = alt.Chart(df_annotation).mark_rule().encode(
#             x="date:O",
#             size=alt.value(2),
#             tooltip = [
#                     alt.Tooltip('annotation', title='Event'),
#                     alt.Tooltip('date', title='Date')
#                 ],
#             color = alt.value('black')
#         )
        
#         combo_bar_chart_1 = bar_chart_1 + chart_annotation
        
#         combo = (line_chart_1 + combo_bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(combo_bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)
        
#     elif option_date == 'Weekly':
#         db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'asset_code', 'reset_hm', 'week_column_1', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_code', 'week_column_1'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["week_column_1"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('week_column_1:O', title=None, sort=alt.SortField(field='week_column_1', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_code')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("week_column_1", title="Week"),
#                     alt.Tooltip("asset_code", title="Asset Code"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_code'),
#             tooltip=[
#                 alt.Tooltip("week_column_1", title="Week"),
#                 alt.Tooltip("asset_code", title="Asset Code"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_code:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_code'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)

#     elif option_date == 'Monthly':
#         db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'asset_code', 'reset_hm', 'month_column_1', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_code', 'month_column_1'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["month_column_1"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('month_column_1:O', title=None, sort=alt.SortField(field='month_column_1', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_code')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("month_column_1", title="Month"),
#                     alt.Tooltip("asset_code", title="Asset Code"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_code'),
#             tooltip=[
#                 alt.Tooltip("month_column_1", title="Month"),
#                 alt.Tooltip("asset_code", title="Asset Code"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_code:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_code'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)
        
#     elif option_date == 'Quarter':
#         db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'asset_code', 'reset_hm', 'quarter_column_1', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_code', 'quarter_column_1'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["quarter_column_1"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('quarter_column_1:O', title=None, sort=alt.SortField(field='quarter_column_1', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_code')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("quarter_column_1", title="Quarter"),
#                     alt.Tooltip("asset_code", title="Asset Code"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_code'),
#             tooltip=[
#                 alt.Tooltip("quarter_column_1", title="Quarter"),
#                 alt.Tooltip("asset_code", title="Asset Code"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_code:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_code'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)

#     elif option_date == 'Semester':
#         db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'asset_code', 'reset_hm', 'semester_column_1', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_code', 'semester_column_1'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["semester_column_1"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('semester_column_1:O', title=None, sort=alt.SortField(field='semester_column_1', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_code')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("semester_column_1", title="Semester"),
#                     alt.Tooltip("asset_code", title="Asset Code"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_code'),
#             tooltip=[
#                 alt.Tooltip("semester_column_1", title="Semester"),
#                 alt.Tooltip("asset_code", title="Asset Code"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_code:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_code'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)
        
#     elif option_date == 'Yearly':
#         db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'asset_code', 'reset_hm', 'year_column', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_code', 'year_column'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["year_column"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('year_column:O', title=None, sort=alt.SortField(field='year_column', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_code')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("year_column", title="Year"),
#                     alt.Tooltip("asset_code", title="Asset Code"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_code'),
#             tooltip=[
#                 alt.Tooltip("year_column", title="Year"),
#                 alt.Tooltip("asset_code", title="Asset Code"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_code:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_code'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)

# # --Grouped by Categories
# else:
#     if option_date == 'by date':
#         # --make a new dataframe for the filtered dataframe called db_search_filtered
#         if len(date_range) == 2:
#             start_datetime = datetime.combine(date_range[0], datetime.min.time())
#             end_datetime = datetime.combine(date_range[1], datetime.max.time())
#             db_search_filtered = db_search[
#                 (db_search['asset_category'].isin(option_category)) & 
#                 (db_search['date'] >= start_datetime) & 
#                 (db_search['date'] <= end_datetime)
#             ]
#             db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
#         elif len(date_range) == 1:
#             start_datetime = datetime.combine(date_range[0], datetime.min.time())
#             end_datetime = datetime.today()
#             db_search_filtered = db_search[
#                 (db_search['asset_category'].isin(option_category)) & 
#                 (db_search['date'] >= start_datetime) & 
#                 (db_search['date'] <= end_datetime)
#             ]
#             db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
#         else :
#             db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
#             db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
            
#         # --make a new dataframe for the chart for convenience
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'reset_hm', db_search_filtered['date'].dt.date, 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'max'
#         }).reset_index(drop=False)        
#         grouped_df['date'] = grouped_df['date'].astype(str)
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["date"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('date:O', title=None, sort=alt.SortField(field='date', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_category')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("date", title="Date"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_category'),
#             tooltip=[
#                 alt.Tooltip("date", title="Date"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_category:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_category'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)
        
#     elif option_date == 'Weekly':
#         db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'reset_hm', 'week_column_1', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_category', 'week_column_1'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["week_column_1"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('week_column_1:O', title=None, sort=alt.SortField(field='week_column_1', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_category')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("week_column_1", title="Week"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_category'),
#             tooltip=[
#                 alt.Tooltip("week_column_1", title="Week"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_category:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_category'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)
        
#     elif option_date == 'Monthly':
#         db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'reset_hm', 'month_column_1', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_category', 'month_column_1'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["month_column_1"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('month_column_1:O', title=None, sort=alt.SortField(field='month_column_1', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_category')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("month_column_1", title="Month"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_category'),
#             tooltip=[
#                 alt.Tooltip("month_column_1", title="Month"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_category:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_category'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)

#     elif option_date == 'Quarter':
#         db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'reset_hm', 'quarter_column_1', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_category', 'quarter_column_1'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["quarter_column_1"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('quarter_column_1:O', title=None, sort=alt.SortField(field='quarter_column_1', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_category')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("quarter_column_1", title="Quarter"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_category'),
#             tooltip=[
#                 alt.Tooltip("quarter_column_1", title="Quarter"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_category:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_category'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)

#     elif option_date == 'Semester':
#         db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'reset_hm', 'semester_column_1', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_category', 'semester_column_1'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["semester_column_1"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('semester_column_1:O', title=None, sort=alt.SortField(field='semester_column_1', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_category')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("semester_column_1", title="Semester"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_category'),
#             tooltip=[
#                 alt.Tooltip("semester_column_1", title="Semester"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_category:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_category'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)

#     elif option_date == 'Yearly':
#         db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
#         db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
        
#         # --Break the db_search_filtered down for a moment so the user can imply the product filter
#         hour_meter_rows = db_search_filtered[db_search_filtered['source'] == 'hm_record']
#         good_consume_rows = db_search_filtered[db_search_filtered['source'] == 'good_consume']
        
#         good_consume_rows = good_consume_rows[good_consume_rows['product_name'].isin(option_product)]
        
#         # --The final dataframe before making the chart dataframe
#         db_search_filtered = pd.concat([hour_meter_rows, good_consume_rows])
        
#         # Making a New DataFrame for Interactive Chart
#         grouped_df = db_search_filtered.groupby(['source', 'asset_category', 'reset_hm', 'year_column', 'product_name']).agg({
#             'total_price':'sum',
#             'hour_meter_per_date':'sum'
#         }).reset_index(drop=False)
#         grouped_df = grouped_df.sort_values(by=['asset_category', 'year_column'], ascending=[True, True])
        
#         # Chart Making
#         hover = alt.selection_point(
#             fields=["year_column"],
#             nearest=True,
#             on="mouseover",
#             empty=False,
#         )
        
#         # --The base of the overall chart
#         base = alt.Chart(grouped_df).encode(
#             x=alt.X('year_column:O', title=None, sort=alt.SortField(field='year_column', order='ascending'))
#         )

#         # --The line chart of the total price of assets
#         line_chart_1 = base.mark_line().encode(
#             y=alt.Y('sum(total_price):Q', title=None),
#             color=alt.Color('asset_category')
#         ).properties(
#             title='Asset(s) Cost Trend',
#             height=400
#         )
        
#         # --The points at the line chart single date to better view where the mouse is hovered
#         points = line_chart_1.transform_filter(hover).mark_circle(size=65)

#         # --The tooltips when hovered to a line chart single date
#         tooltips = (
#             base
#             .mark_rule()
#             .encode(
#                 y=alt.Y('total_price:Q', title=None),
#                 opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
#                 tooltip=[
#                     alt.Tooltip("year_column", title="Year"),
#                     alt.Tooltip("asset_category", title="Asset Category"),
#                     alt.Tooltip("total_price", title="Total Price", format=",.0f", formatType="number")
#                 ],
#             )
#             .add_params(hover)
#         )
        
#         combo_line_chart_1 = line_chart_1 + points + tooltips
        
#         # Brushing selection to help better view of the bar chart
#         brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
#         # --The bar chart of the hour meter of assets
#         bar_chart_1 = base.mark_bar(opacity=0.6).encode(
#             y=alt.Y('hour_meter_per_date:Q', title=None),
#             color=alt.Color('asset_category'),
#             tooltip=[
#                 alt.Tooltip("year_column", title="Year"),
#                 alt.Tooltip("asset_category", title="Asset Category"),
#                 alt.Tooltip("hour_meter_per_date", title="Hour Meter")
#             ]
#         ).add_params(
#             brush
#         ).properties(
#             title='Asset(s) Hour Meter Trend',
#             width = 900,
#             height=400
#         )
        
#         # --The helper view of different bars in bar chart
#         bar_chart_2 = alt.Chart(grouped_df).mark_bar(opacity=0.6).encode(
#             x=alt.X('asset_category:N', title=None),
#             y=alt.Y('sum(hour_meter_per_date):Q', title=None),
#             color=alt.Color('asset_category'),
#             text=alt.Text('sum(hour_meter_per_date):Q')
#         ).transform_filter(
#             brush
#         ).properties(
#             width=100,
#             height=400
#         )
        
#         # --The label at the top of the bar_chart_2 to help distinguished number faster between bars
#         label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
#         combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')

#         # Layout
#         st.altair_chart(combo_line_chart_1, use_container_width=True)
#         st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
#         st.altair_chart(combo, use_container_width=True)
