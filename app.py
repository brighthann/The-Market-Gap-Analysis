# The Sugar Trap Market Gap Analysis Dashboard
# Streamlit Application

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import os
import zipfile  # NEW: Add zipfile import
import io  # NEW: For handling in-memory bytes

# Page configuration
st.set_page_config(
    page_title="Sugar Trap Market Analysis",
    page_icon="",
    layout="wide"
)

# ============================================================
# DATA LOADING FROM ZIP FILE
# ============================================================

ZIP_FILE = 'categorized_products.zip'  # Single ZIP file containing all data


@st.cache_data
def load_all_data_from_zip():
    """Load all data files from a single ZIP archive"""
    data = {}

    try:
        # Open the ZIP file
        with zipfile.ZipFile(ZIP_FILE, 'r') as zipf:
            # List all files in ZIP (for debugging)
            zip_contents = zipf.namelist()

            # Load categorized products (main data)
            if 'categorized_products.csv' in zip_contents:
                with zipf.open('categorized_products.csv') as f:
                    data['df'] = pd.read_csv(f)
            else:
                st.error("categorized_products.csv not found in ZIP")
                data['df'] = None

            # Load thresholds
            if 'thresholds.csv' in zip_contents:
                with zipf.open('thresholds.csv') as f:
                    thresholds_df = pd.read_csv(f)
                    protein_thresh = thresholds_df[thresholds_df['metric'] == 'high_protein_threshold']['value'].values[
                        0]
                    sugar_thresh = thresholds_df[thresholds_df['metric'] == 'low_sugar_threshold']['value'].values[0]
                    data['protein_threshold'] = protein_thresh
                    data['sugar_threshold'] = sugar_thresh
            else:
                data['protein_threshold'] = None
                data['sugar_threshold'] = None

            # Load protein sources
            if 'top_protein_sources.csv' in zip_contents:
                with zipf.open('top_protein_sources.csv') as f:
                    data['protein_sources_df'] = pd.read_csv(f)
            else:
                data['protein_sources_df'] = None

            # Load category summary
            if 'category_summary.csv' in zip_contents:
                with zipf.open('category_summary.csv') as f:
                    data['category_summary_df'] = pd.read_csv(f, index_col=0)
            else:
                data['category_summary_df'] = None

            # Load brand data
            if 'brand_leaderboard.csv' in zip_contents:
                with zipf.open('brand_leaderboard.csv') as f:
                    data['brand_df'] = pd.read_csv(f)
            else:
                data['brand_df'] = None

            # Load recommendation text
            if 'recommendation.txt' in zip_contents:
                with zipf.open('recommendation.txt') as f:
                    data['recommendation_text'] = f.read().decode('utf-8')
            else:
                data['recommendation_text'] = "Recommendation not available. Run the analysis cells first."

    except FileNotFoundError:
        st.error(f"ZIP file not found: {ZIP_FILE}")
        st.info("Please ensure categorized_products.zip is in the same directory as app.py")
        data['df'] = None
        data['protein_threshold'] = None
        data['sugar_threshold'] = None
        data['protein_sources_df'] = None
        data['category_summary_df'] = None
        data['brand_df'] = None
        data['recommendation_text'] = "Data files not found."
    except Exception as e:
        st.error(f"Error loading data: {e}")
        data['df'] = None
        data['protein_threshold'] = None
        data['sugar_threshold'] = None
        data['protein_sources_df'] = None
        data['category_summary_df'] = None
        data['brand_df'] = None
        data['recommendation_text'] = f"Error loading data: {e}"

    return data


# Load all data
data = load_all_data_from_zip()

# Extract data from the dictionary
df = data.get('df')
protein_threshold = data.get('protein_threshold')
sugar_threshold = data.get('sugar_threshold')
protein_sources_df = data.get('protein_sources_df')
category_summary_df = data.get('category_summary_df')
brand_df = data.get('brand_df')
recommendation_text = data.get('recommendation_text')

# If thresholds couldn't be loaded, calculate them from the data
if protein_threshold is None and df is not None:
    protein_threshold = df['proteins_100g'].quantile(0.70)
    sugar_threshold = df['sugars_100g'].quantile(0.30)

# Add health flag to dataframe if not already present
if df is not None and 'is_high_protein_low_sugar' not in df.columns:
    df['is_high_protein_low_sugar'] = (
            (df['proteins_100g'] >= protein_threshold) &
            (df['sugars_100g'] <= sugar_threshold)
    )

# SIDEBAR - FILTERS
st.sidebar.title("Filters")
st.sidebar.markdown("Filter the scatter plot and analysis")

if df is not None:
    all_categories = sorted(df['primary_category'].unique().tolist())
    selected_categories = st.sidebar.multiselect(
        label="Select Product Categories",
        options=all_categories,
        default=all_categories,
        help="Choose one or more categories to display on the chart."
    )

    sugar_max = st.sidebar.slider(
        label="Max Sugar (g per 100g)",
        min_value=0,
        max_value=100,
        value=100,
        step=5
    )

    protein_min = st.sidebar.slider(
        label="Min Protein (g per 100g)",
        min_value=0,
        max_value=100,
        value=0,
        step=5
    )

    # Filter the data based on sidebar selections
    if len(selected_categories) == 0:
        df_filtered = df.copy()
    else:
        df_filtered = df[
            (df['primary_category'].isin(selected_categories)) &
            (df['sugars_100g'] <= sugar_max) &
            (df['proteins_100g'] >= protein_min)
            ].copy()
else:
    selected_categories = []
    sugar_max = 100
    protein_min = 0
    df_filtered = None

# Dashboard Header
st.title("Sugar Trap: Market Gap Analysis")
st.markdown("Identifying Blue Ocean opportunities in the snack aisle")

if df is not None:
    st.markdown(f"Analyzing **{len(df):,}** snack products from the Open Food Facts database.")
else:
    st.error("No data loaded. Please check that categorized_products.zip exists in the app directory.")
    st.stop()

st.markdown("---")

# TOP ROW: METRIC CARDS
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Products Analyzed",
        value=f"{len(df):,}"
    )
with col2:
    st.metric(
        label="Product Categories",
        value=df['primary_category'].nunique()
    )
with col3:
    healthy_count = df['is_high_protein_low_sugar'].sum()
    healthy_pct = (healthy_count / len(df) * 100)
    st.metric(
        label="High Protein / Low Sugar Products",
        value=f"{healthy_count:,}",
        delta=f"{healthy_pct:.1f}% of total"
    )
with col4:
    st.metric(
        label="Filtered Products (current view)",
        value=f"{len(df_filtered):,}" if df_filtered is not None else "0"
    )

st.markdown("---")

# MAIN CHART: NUTRIENT MATRIX
st.subheader("Nutrient Matrix: Sugar vs. Protein")
st.markdown(
    "Each point is one product. The shaded region is the "
    "high-protein / low-sugar quadrant the market opportunity zone."
)

if df_filtered is not None and len(df_filtered) == 0:
    st.warning("No products match the current filter settings. Please adjust the filters.")
elif df_filtered is not None:
    # Limit to 2000 points for performance
    plot_sample = df_filtered.sample(min(2000, len(df_filtered)), random_state=42)

    fig = px.scatter(
        plot_sample,
        x='sugars_100g',
        y='proteins_100g',
        color='primary_category',
        hover_name='product_name',
        hover_data={
            'sugars_100g': ':.1f',
            'proteins_100g': ':.1f',
            'primary_category': True
        },
        labels={
            'sugars_100g': 'Sugar (g per 100g)',
            'proteins_100g': 'Protein (g per 100g)',
            'primary_category': 'Category'
        },
        opacity=0.6,
        height=550
    )

    # Add the opportunity zone shaded region
    fig.add_shape(
        type="rect",
        x0=0, y0=protein_threshold,
        x1=sugar_threshold, y1=df['proteins_100g'].max(),
        fillcolor="rgba(0, 200, 100, 0.12)",
        line=dict(color="rgba(0, 200, 100, 0.8)", width=2, dash="dash"),
    )

    # Add threshold lines
    fig.add_hline(
        y=protein_threshold,
        line_dash="dash",
        line_color="green",
        annotation_text=f"High Protein: {protein_threshold:.1f}g",
        annotation_position="top left"
    )
    fig.add_vline(
        x=sugar_threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Low Sugar: {sugar_threshold:.1f}g",
        annotation_position="bottom right"
    )

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# SECOND ROW: CATEGORY HEALTH GAP CHART + RECOMMENDATION
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("Health Gap by Category")
    st.markdown("Percentage of products in each category that meet the high-protein / low-sugar criteria.")

    if category_summary_df is not None:
        gap_data = category_summary_df.reset_index()
        gap_data.columns = ['category', 'total_products', 'healthy_products', 'health_ratio']
        gap_data = gap_data.sort_values('health_ratio', ascending=True)

        fig_gap = px.bar(
            gap_data,
            x='health_ratio',
            y='category',
            orientation='h',
            color='health_ratio',
            color_continuous_scale=['red', 'orange', 'green'],
            labels={
                'health_ratio': '% Products Meeting Health Criteria',
                'category': 'Category'
            },
            text='health_ratio',
            height=400
        )
        fig_gap.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_gap.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=60, t=30, b=40))
        st.plotly_chart(fig_gap, use_container_width=True)
    else:
        # Calculate on the fly if summary not available
        if df is not None:
            gap_data = df.groupby('primary_category').agg(
                total=('product_name', 'count'),
                healthy=('is_high_protein_low_sugar', 'sum')
            ).reset_index()
            gap_data['health_pct'] = (gap_data['healthy'] / gap_data['total'] * 100).round(1)
            gap_data = gap_data.sort_values('health_pct', ascending=True)

            fig_gap = px.bar(
                gap_data,
                x='health_pct',
                y='primary_category',
                orientation='h',
                color='health_pct',
                color_continuous_scale=['red', 'orange', 'green'],
                labels={
                    'health_pct': '% Products Meeting Health Criteria',
                    'primary_category': 'Category'
                },
                text='health_pct',
                height=400
            )
            fig_gap.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_gap.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=60, t=30, b=40))
            st.plotly_chart(fig_gap, use_container_width=True)
        else:
            st.info("Category data not available.")

with col_right:
    st.subheader("Key Insight")
    st.info(recommendation_text)
    st.markdown("**Why this matters:**")
    st.markdown(
        "Consumer demand for healthier snacking alternatives is growing. "
        "Categories dominated by high-sugar, low-protein products represent "
        "underserved segments where a new product launch has the least competition "
        "and the most room for differentiation."
    )

st.markdown("---")

# BOTTOM ROW: BRAND ANALYSIS AND PROTEIN SOURCES
try:
    col_bottom_left, col_bottom_right = st.columns(2)
except:
    # If column creation fails, create them manually
    st.error("Column creation failed - using fallback layout")
    col_bottom_left = st.container()
    col_bottom_right = st.container()

with col_bottom_left:
    st.subheader("Brand Health Leaderboard")
    
    if brand_df is not None and len(brand_df) > 0:
        # Show raw data first to debug
        with st.expander("Debug: Brand Data Structure"):
            st.write("Columns:", list(brand_df.columns))
            st.dataframe(brand_df.head())
        
        # Try to find brand column
        brand_col = None
        for col in brand_df.columns:
            if any(x in col.lower() for x in ['brand', 'primary']):
                brand_col = col
                break
        
        # Try to find percentage column
        pct_col = None
        for col in brand_df.columns:
            if any(x in col.lower() for x in ['healthy', 'pct', 'percent']):
                pct_col = col
                break
        
        if brand_col and pct_col:
            top_brands = brand_df.head(10)
            fig_brand = px.bar(
                top_brands,
                x=brand_col,
                y=pct_col,
                color=pct_col,
                color_continuous_scale='Greens',
                title="Top 10 Brands by % Healthy Products",
                labels={brand_col: 'Brand', pct_col: '% Healthy Products'},
                text=pct_col,
                height=400
            )
            fig_brand.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_brand.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
            st.plotly_chart(fig_brand, use_container_width=True)
        else:
            st.warning("Could not create chart - showing data table instead")
            st.dataframe(brand_df.head(10), use_container_width=True)
        
        with st.expander("View Full Brand Leaderboard"):
            st.dataframe(brand_df, use_container_width=True, hide_index=True)
    else:
        st.info("Brand data not available.")

with col_bottom_right:
    st.subheader("Hidden Gem: Top Protein Sources")
    st.markdown(
        "Among products that fall in the high-protein / low-sugar quadrant, "
        "these are the most commonly listed ingredients that drive high protein content."
    )
    
    if protein_sources_df is not None and len(protein_sources_df) > 0:
        # Debug info
        with st.expander("Debug: Protein Sources Structure"):
            st.write("Columns:", list(protein_sources_df.columns))
            st.dataframe(protein_sources_df.head())
        
        # Find ingredient column
        ingredient_col = None
        for col in protein_sources_df.columns:
            if any(x in col.lower() for x in ['ingredient', 'source']):
                ingredient_col = col
                break
        
        # Find count column
        count_col = None
        for col in protein_sources_df.columns:
            if any(x in col.lower() for x in ['count', 'frequency']):
                count_col = col
                break
        
        if ingredient_col and count_col:
            top_sources = protein_sources_df.head(10)
            fig_protein = px.bar(
                top_sources,
                x=count_col,
                y=ingredient_col,
                orientation='h',
                color=count_col,
                color_continuous_scale='Blues',
                title="Most Common Protein Sources",
                labels={count_col: 'Number of Products', ingredient_col: 'Ingredient'},
                height=350
            )
            fig_protein.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_protein, use_container_width=True)
        else:
            st.warning("Could not create chart - showing data table instead")
            st.dataframe(protein_sources_df.head(10), use_container_width=True)
        
        with st.expander("View Protein Source Data"):
            st.dataframe(protein_sources_df, use_container_width=True, hide_index=True)
    else:
        st.info("Protein source data not available.")

st.markdown("---")

# SAMPLE PRODUCTS TABLE
st.subheader("Sample Products in Blue Ocean Quadrant")

if df_filtered is not None and len(df_filtered) > 0:
    hpls_sample = df_filtered[df_filtered['is_high_protein_low_sugar']].head(20)

    if len(hpls_sample) > 0:
        display_cols = ['product_name', 'primary_category', 'brands', 'proteins_100g', 'sugars_100g', 'fat_100g']
        display_cols = [col for col in display_cols if col in hpls_sample.columns]

        st.dataframe(
            hpls_sample[display_cols],
            use_container_width=True,
            height=400,
            hide_index=True
        )

        st.caption(
            f"Showing {min(20, len(hpls_sample))} of {len(df_filtered[df_filtered['is_high_protein_low_sugar']])} high-protein, low-sugar products")
    else:
        st.info("No high-protein, low-sugar products match the current filters.")
else:
    st.info("No products match the current filter settings.")

st.markdown("---")
st.caption("Data source: Open Food Facts (openfoodfacts.org) | Built with Streamlit and Plotly")
