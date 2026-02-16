
# The Sugar Trap Market Gap Analysis Dashboard
# Streamlit Application

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import os

# Page configuration
st.set_page_config(
    page_title="Sugar Trap Market Analysis",
    page_icon="",
    layout="wide"
)

# Data loading with relative paths

#relative paths
processed_data_dir = 'data/processed'
output_dir = 'outputs'

categorized_data_file = os.path.join(processed_data_dir, 'categorized_products.csv')
thresholds_file = os.path.join(output_dir, 'thresholds.csv')
protein_sources_file = os.path.join(output_dir, 'top_protein_sources.csv')
category_summary_file = os.path.join(output_dir, 'category_summary.csv')
brand_file = os.path.join(output_dir, 'brand_leaderboard.csv')
recommendation_file = os.path.join(output_dir, 'recommendation.txt')

@st.cache_data
def load_categorized_data():
    #load cleaned and categorized product data
    try:
        df = pd.read_csv(categorized_data_file)
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at {categorized_data_file}")
        return None

@st.cache_data
def load_thresholds():
    #load the protein and sugar thresholds
    try:
        df = pd.read_csv(thresholds_file)
        protein_thresh = df[df['metric'] == 'high_protein_threshold']['value'].values[0]
        sugar_thresh = df[df['metric'] == 'low_sugar_threshold']['value'].values[0]
        return protein_thresh, sugar_thresh
    except:
        return None, None

@st.cache_data
def load_protein_sources():
    #load the top protein sources data
    try:
        df = pd.read_csv(protein_sources_file)
        return df
    except:
        return None

@st.cache_data
def load_category_summary():
    #load the category health summary
    try:
        df = pd.read_csv(category_summary_file, index_col=0)
        return df
    except:
        return None

@st.cache_data
def load_brand_data():
    #load the brand leaderboard
    try:
        df = pd.read_csv(brand_file)
        return df
    except:
        return None

@st.cache_data
def load_recommendation():
    #load the recommendation text
    try:
        with open(recommendation_file, 'r') as f:
            text = f.read()
        return text
    except:
        return "Recommendation not available. Run the analysis cells first."

#load all data
df = load_categorized_data()
protein_threshold, sugar_threshold = load_thresholds()
protein_sources_df = load_protein_sources()
category_summary_df = load_category_summary()
brand_df = load_brand_data()
recommendation_text = load_recommendation()

#if thresholds couldn't be loaded, calculate them from the data
if protein_threshold is None and df is not None:
    protein_threshold = df['proteins_100g'].quantile(0.70)
    sugar_threshold = df['sugars_100g'].quantile(0.30)

#add health flag to dataframe if not already present
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
    st.error("No data loaded. Please check that the data files exist.")
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
# ============================================================
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

with col_right:
    st.subheader("Key Insight")

    # Display the recommendation
    st.info(recommendation_text)

    st.markdown("**Why this matters:**")
    st.markdown(
        "Consumer demand for healthier snacking alternatives is growing. "
        "Categories dominated by high-sugar, low-protein products represent "
        "underserved segments where a new product launch has the least competition "
        "and the most room for differentiation."
    )

st.markdown("---")

# ============================================================
# BOTTOM ROW: BRAND ANALYSIS AND PROTEIN SOURCES
# ============================================================
col_bottom_left, col_bottom_right = st.columns(2)

with col_bottom_left:
    st.subheader("Brand Health Leaderboard")
    
    if brand_df is not None and len(brand_df) > 0:
        top_brands = brand_df.head(10)
        
        fig_brand = px.bar(
            top_brands,
            x='primary_brand',
            y='healthy_pct',
            color='healthy_pct',
            color_continuous_scale='Greens',
            title="Top 10 Brands by % Healthy Products",
            labels={
                'primary_brand': 'Brand',
                'healthy_pct': '% Healthy Products'
            },
            text='healthy_pct',
            height=400
        )
        fig_brand.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_brand.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
        st.plotly_chart(fig_brand, use_container_width=True)
        
        with st.expander("View Full Brand Leaderboard"):
            st.dataframe(brand_df, use_container_width=True, hide_index=True)
    else:
        st.info("Brand data not available. Run the brand analysis cell first.")

with col_bottom_right:
    st.subheader("Hidden Gem: Top Protein Sources")
    st.markdown(
        "Among products that fall in the high-protein / low-sugar quadrant, "
        "these are the most commonly listed ingredients that drive high protein content."
    )

    if protein_sources_df is not None:
        top_sources = protein_sources_df.head(10)
        
        fig_protein = px.bar(
            top_sources,
            x='count',
            y='ingredient',
            orientation='h',
            color='count',
            color_continuous_scale='Blues',
            title="Most Common Protein Sources",
            labels={
                'count': 'Number of Products',
                'ingredient': 'Ingredient'
            },
            height=350
        )
        fig_protein.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_protein, use_container_width=True)
        
        with st.expander("View Protein Source Data"):
            st.dataframe(protein_sources_df, use_container_width=True, hide_index=True)
    else:
        st.info("Protein source data not available. Run the ingredient analysis cell first.")

st.markdown("---")

# ============================================================
# SAMPLE PRODUCTS TABLE
# ============================================================
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
        
        st.caption(f"Showing {min(20, len(hpls_sample))} of {len(df_filtered[df_filtered['is_high_protein_low_sugar']])} high-protein, low-sugar products")
    else:
        st.info("No high-protein, low-sugar products match the current filters.")
else:
    st.info("No products match the current filter settings.")

st.markdown("---")
st.caption("Data source: Open Food Facts (openfoodfacts.org) | Built with Streamlit and Plotly")
