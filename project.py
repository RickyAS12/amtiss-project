# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Set Overall Page Layout
st.set_page_config(
    page_title='Dashboard',
    layout='wide'
)
st.set_option('deprecation.showPyplotGlobalUse', False)

# st.session_state
# for key in st.session_state.keys():
#     del st.session_state[key]

# Query
db = st.connection('mysql', type='sql')

# 1.Query for Cost and Hour Meter Trend
db_search=db.query(
    'SELECT * FROM union_hm_gc ORDER BY date'
    , ttl=600
)
db_search['date'] = pd.to_datetime(db_search['date'])

# 2. Query for detail product bought
db_prod=db.query(
    'SELECT * FROM age_product_gc_1'
    , ttl=600
)
db_prod['end_date'] = pd.to_datetime(db_prod['end_date'])

cols = st.columns(5)

with cols[4]:
    option_radio = st.radio('Grouping :', ['by Assets', 'by Categories'], index=0, horizontal=True)
    if option_radio == 'by Categories':
        disable_filter_asset = True
    else:
        disable_filter_asset = False
    
with cols[0]:
    # --filter asset categories
    categories = db_search['asset_category'].unique()
    with st.popover(f'Filter Asset(s) Category ({len(categories)})', use_container_width=True):
        option_category = st.multiselect(
            'Choose A Category', 
            categories,
            default=categories[0],
            help="Before filtering asset categories, it's advisable to clear the 'Date Range' selectbox first."
        )
        if len(option_category) == 0:
            st.error('Please choose at least 1 category', icon="🚨")
    count_categories = len(option_category)
    st.write(f'Include {count_categories} categories')

    # --filter asset code
    asset_codes = db_search['asset_code'].loc[db_search['asset_category'].isin(option_category)].unique()
    with st.popover(f'Filter Asset(s) Code ({len(asset_codes)})', use_container_width=True, disabled=disable_filter_asset):
        if disable_filter_asset == False:
            option_asset = st.multiselect('Choose Asset Codes', asset_codes, default=asset_codes[0])
            if len(option_asset) == 0:
                st.error('Please choose at least 1 asset code', icon="🚨")
    if disable_filter_asset == False:
        count_asset = len(option_asset)
        st.write(f'Include {count_asset} assets')
    
    # Filter produk
    product_codes = db_prod['product_name'].loc[db_prod['asset_code'].isin(asset_codes)].unique()
    with st.popover(f'Filter Product ({len(product_codes)})', use_container_width=True):
        option_product = st.multiselect('Choose Product', product_codes, default=product_codes)
        if len(option_product) == 0:
            st.error('Please choose at least 1 product', icon="🚨")
    count_product = len(option_product)
    st.write(f'Include {count_product} products')
    
    # --filter asset date
    with st.popover('Filter Date', use_container_width=True):
        option_date = st.selectbox('Choose filter', ['by date', 'Weekly', 'Monthly', 'Quarter', 'Semester', 'Yearly'], index=2)
        
        # --conditioning option_date
        true_false_condition = ''
        if option_date == 'by date':
            true_false_condition = False
        else :
            true_false_condition = True
        
        date_range =st.date_input(
            label='Filter Date Range', 
            min_value=db_search['date'].loc[db_search['asset_category'].isin(option_category)].min().date(), 
            max_value=db_search['date'].loc[db_search['asset_category'].isin(option_category)].max().date(), 
            value=(),
            help="You can also choose not to determine the end date. The range will be specified as the start date you've picked to the latest date available in the record.",
            disabled=true_false_condition
        )
    st.write(f'View : {option_date}')
    if option_date == 'by date' and len(date_range) > 0:
        if len(date_range) == 2:
            st.write(f'From {date_range[0]} to {date_range[1]}')
        elif len(date_range) == 1:
            st.write(f'From {date_range[0]} to Today')

# Page Break
st.divider()

# --Grouped by Asset
if disable_filter_asset == False:
    if option_date == 'by date':
        # --make a new dataframe for the filtered dataframe called db_search_filtered
        if len(date_range) == 2:
            start_datetime = datetime.combine(date_range[0], datetime.min.time())
            end_datetime = datetime.combine(date_range[1], datetime.max.time())
            db_search_filtered = db_search[
                (db_search['asset_code'].isin(option_asset)) & 
                (db_search['date'] >= start_datetime) & 
                (db_search['date'] <= end_datetime)
            ]
            db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
        elif len(date_range) == 1:
            start_datetime = datetime.combine(date_range[0], datetime.min.time())
            end_datetime = datetime.today()
            db_search_filtered = db_search[
                (db_search['asset_code'].isin(option_asset)) & 
                (db_search['date'] >= start_datetime) & 
                (db_search['date'] <= end_datetime)
            ]
            db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])
        else :
            db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
            db_search_filtered = db_search_filtered.sort_values(by=['asset_code', 'date'], ascending=[True, True])

        # --make a new dataframe for the chart for convenience
        grouped_df = db_search_filtered.groupby(['asset_code', db_search_filtered['date'].dt.date]).agg({
            'total_price':'sum',
            'hour_meter_per_date':'max'
        }).reset_index(drop=False)

        grouped_df['date'] = grouped_df['date'].astype(str)

        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('date:O', title='Date')
        )

        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_price:Q', title='Cost'),
            color=alt.Color('asset_code')
        ).properties(
            title='Asset(s) Cost Trend'
        )

        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_code')
        ).add_params(
            brush
        ).properties(
            title='Asset(s) Hour Meter Trend',
            width = 900
        )
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_code:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_code'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')

        # Layout
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2))
        st.altair_chart(combo)

        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)

        # --make a new dataframe for the filtered dataframe called db_prod_filtered
        if len(date_range) == 2:
            start_datetime = datetime.combine(date_range[0], datetime.min.time())
            end_datetime = datetime.combine(date_range[1], datetime.max.time())
            db_prod_filtered = db_prod[
                (db_prod['asset_code'].isin(option_asset)) & 
                (db_prod['end_date'] >= start_datetime) & 
                (db_prod['end_date'] <= end_datetime)
            ]
            db_prod_filtered = db_prod_filtered.sort_values(by=['asset_code', 'end_date'], ascending=[True, True])
        elif len(date_range) == 1:
            start_datetime = datetime.combine(date_range[0], datetime.min.time())
            end_datetime = datetime.today()
            db_prod_filtered = db_prod[
                (db_prod['asset_code'].isin(option_asset)) & 
                (db_prod['end_date'] >= start_datetime) & 
                (db_prod['end_date'] <= end_datetime)
            ]
            db_prod_filtered = db_prod_filtered.sort_values(by=['asset_code', 'end_date'], ascending=[True, True])
        else :
            db_prod_filtered = db_prod[db_prod['asset_code'].isin(option_asset)]
            db_prod_filtered = db_prod_filtered.sort_values(by=['asset_code', 'end_date'], ascending=[True, True])

        grouped_df_product = db_prod_filtered.groupby(['asset_code', 'product_name']).agg({
            'age_column':'mean',
            'end_date':'count'
        }).reset_index(drop=False)
        
        grouped_df_product = grouped_df_product.rename(columns={'age_column': 'mean_age', 'end_date': 'time_bought'})
        
        st.dataframe(db_prod_filtered)
        st.dataframe(grouped_df_product)
        
    elif option_date == 'Weekly':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
        grouped_df = db_search_filtered.groupby(['asset_code', 'asset_category', 'week_year']).agg({
            'total_price':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_code', 'week_year'], ascending=[True, True])
        
        db_prod_filtered = db_prod[db_prod['asset_code'].isin(option_asset)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('week_year:N', title=None)
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_price:Q', title='Cost'),
            color=alt.Color('asset_code')
        ).properties(
            title='Asset(s) Cost Trend'
        )

        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_code')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_code:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_code'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)
        
        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)
        st.dataframe(db_prod_filtered)

    elif option_date == 'Monthly':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
        grouped_df = db_search_filtered.groupby(['asset_code', 'asset_category', 'month_year']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_code', 'month_year'], ascending=[True, True])
        
        db_prod_filtered = db_prod[db_prod['asset_code'].isin(option_asset)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('month_year:N', title='Date', sort=alt.SortField(field='month_year', order='ascending'))
        )

        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_code')
        ).properties(
            title='Asset(s) Cost Trend'
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_code')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_code:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_code'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)
        
        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)
        st.dataframe(db_prod_filtered)
        
    elif option_date == 'Quarter':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
        grouped_df = db_search_filtered.groupby(['asset_code', 'asset_category', 'quarter_year']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_code', 'quarter_year'], ascending=[True, True])
        
        db_prod_filtered = db_prod[db_prod['asset_code'].isin(option_asset)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('quarter_year:N', title='Date', sort=alt.SortField(field='quarter_year', order='ascending'))
        )        
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_code')
        ).properties(
            title='Asset(s) Cost Trend'
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_code')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_code:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_code'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)

    elif option_date == 'Semester':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
        grouped_df = db_search_filtered.groupby(['asset_code', 'asset_category', 'semester_year']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_code', 'semester_year'], ascending=[True, True])
        
        db_prod_filtered = db_prod[db_prod['asset_code'].isin(option_asset)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('semester_year:N', title='Date', sort=alt.SortField(field='semester_year', order='ascending'))
        )
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_code')
        ).properties(
            title='Asset(s) Cost Trend'
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_code')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_code:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_code'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)
        
    elif option_date == 'Yearly':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_code'].isin(option_asset)]
        grouped_df = db_search_filtered.groupby(['asset_code', 'asset_category', 'year_column']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_code', 'year_column'], ascending=[True, True])
        
        db_prod_filtered = db_prod[db_prod['asset_code'].isin(option_asset)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('year_column:N', title='Date', sort=alt.SortField(field='year_column', order='ascending'))
        )
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_code')
        ).properties(
            title='Asset(s) Cost Trend'
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_code')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_code:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_code'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)

# --Grouped by Categories
else:
    if option_date == 'by date':
        # --make a new dataframe for the filtered dataframe called db_search_filtered
        if len(date_range) == 2:
            start_datetime = datetime.combine(date_range[0], datetime.min.time())
            end_datetime = datetime.combine(date_range[1], datetime.max.time())
            db_search_filtered = db_search[
                (db_search['asset_category'].isin(option_category)) & 
                (db_search['date'] >= start_datetime) & 
                (db_search['date'] <= end_datetime)
            ]
            db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
        elif len(date_range) == 1:
            start_datetime = datetime.combine(date_range[0], datetime.min.time())
            end_datetime = datetime.today()
            db_search_filtered = db_search[
                (db_search['asset_category'].isin(option_category)) & 
                (db_search['date'] >= start_datetime) & 
                (db_search['date'] <= end_datetime)
            ]
            db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
        else :
            db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
            db_search_filtered = db_search_filtered.sort_values(by=['asset_category', 'date'], ascending=[True, True])
            
        # Make a new dataframe for the chart
        grouped_df = db_search_filtered.groupby(['asset_category', db_search_filtered['date'].dt.date]).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'max'
        }).reset_index(drop=False)
        
        grouped_df['date'] = grouped_df['date'].astype(str)
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('date:O', title='Date', sort=alt.SortField(field='date', order='ascending'))
        )

        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_category')
        ).properties(
            title='Asset(s) Cost Trend'
        )

        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_category')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_category:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_category'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')

        # Layout
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)

        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)
        
    elif option_date == 'Weekly':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
        grouped_df = db_search_filtered.groupby(['asset_category', 'week_year']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_category', 'week_year'], ascending=[True, True])
        
        # db_prod_filtered = db_prod[db_prod['asset_category'].isin(option_category)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('week_year:N', title=None, sort=alt.SortField(field='week_year', order='ascending'))
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_category')
        ).properties(
            title='Asset(s) Cost Trend'
        )

        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_category')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_category:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_category'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)
        
        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)
        
    elif option_date == 'Monthly':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
        grouped_df = db_search_filtered.groupby(['asset_category', 'month_year']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_category', 'month_year'], ascending=[True, True])
        
        # db_prod_filtered = db_prod[db_prod['asset_category'].isin(option_category)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('month_year:N', title=None, sort=alt.SortField(field='month_year', order='ascending'))
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_category')
        ).properties(
            title='Asset(s) Cost Trend'
        )

        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_category')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_category:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_category'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)
        
        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)

    elif option_date == 'Quarter':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
        grouped_df = db_search_filtered.groupby(['asset_category', 'quarter_year']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_category', 'quarter_year'], ascending=[True, True])
        
        # db_prod_filtered = db_prod[db_prod['asset_category'].isin(option_category)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('quarter_year:N', title=None, sort=alt.SortField(field='quarter_year', order='ascending'))
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_category')
        ).properties(
            title='Asset(s) Cost Trend'
        )

        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_category')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_category:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_category'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)
        
        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)

    elif option_date == 'Semester':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
        grouped_df = db_search_filtered.groupby(['asset_category', 'semester_year']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_category', 'semester_year'], ascending=[True, True])
        
        # db_prod_filtered = db_prod[db_prod['asset_category'].isin(option_category)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('semester_year:N', title=None, sort=alt.SortField(field='semester_year', order='ascending'))
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_category')
        ).properties(
            title='Asset(s) Cost Trend'
        )

        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_category')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_category:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_category'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)
        
        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)

    elif option_date == 'Yearly':
        # Making a New DataFrame for Interactive Chart
        db_search_filtered = db_search[db_search['asset_category'].isin(option_category)]
        grouped_df = db_search_filtered.groupby(['asset_category', 'year_column']).agg({
            'total_hour_meter':'sum',
            'hour_meter_per_date':'sum'
        }).reset_index(drop=False)
        grouped_df = grouped_df.sort_values(by=['asset_category', 'year_column'], ascending=[True, True])
        
        # db_prod_filtered = db_prod[db_prod['asset_category'].isin(option_category)]
        
        # Chart Making
        base = alt.Chart(grouped_df).encode(
            x=alt.X('year_column:N', title=None, sort=alt.SortField(field='year_column', order='ascending'))
        )
        
        brush = alt.selection_interval(encodings=['x'], name='brush', empty=False)
        
        line_chart_1 = base.mark_line().encode(
            y=alt.Y('total_hour_meter:Q', title='Cost'),
            color=alt.Color('asset_category')
        ).properties(
            title='Asset(s) Cost Trend'
        )

        bar_chart_1 = base.mark_bar(opacity=0.4).encode(
            y=alt.Y('hour_meter_per_date:Q', title='Hour Meter'),
            color=alt.Color('asset_category')
        ).add_params(
            brush
        ).properties(
            width=900,
            title='Asset(s) Hour Meter Trend'
        )
        
        bar_chart_2 = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('asset_category:N'),
            y=alt.Y('sum(hour_meter_per_date):Q', title='Hour Meter'),
            color=alt.Color('asset_category'),
            text=alt.Text('sum(hour_meter_per_date):Q')
        ).transform_filter(
            brush
        ).properties(
            width=100
        )
        
        label_bar_chart_2 = bar_chart_2.mark_text(baseline='bottom')
        
        combo = (line_chart_1 + bar_chart_1).resolve_scale(y='independent').properties(title='Combo Chart')
        
        st.altair_chart(line_chart_1, use_container_width=True)
        st.altair_chart(bar_chart_1 | (bar_chart_2+label_bar_chart_2), use_container_width=True)
        st.altair_chart(combo, use_container_width=True)
        
        st.dataframe(db_search_filtered)
        st.dataframe(grouped_df)