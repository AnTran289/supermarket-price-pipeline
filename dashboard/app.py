import os
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --------------------------------------------------
# Config
# --------------------------------------------------
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5431")
DB_NAME = os.getenv("DB_NAME", "postgres")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

st.set_page_config(
    page_title="Supermarket Price Intelligence Dashboard",
    layout="wide"
)

# --------------------------------------------------
# Helper functions
# --------------------------------------------------
@st.cache_data
def load_query(query: str) -> pd.DataFrame:
    return pd.read_sql(query, engine)


def format_currency(value):
    if pd.isna(value):
        return "-"
    return f"${value:,.2f}"


# --------------------------------------------------
# Load Gold Layer Data
# --------------------------------------------------
try:
    price_df = load_query("SELECT * FROM gold.mart_price_comparison;")
    promotion_df = load_query("SELECT * FROM gold.mart_promotion_summary;")
    cheapest_df = load_query("SELECT * FROM gold.mart_cheapest_unit_products;")
    quality_df = load_query("SELECT * FROM gold.mart_data_quality_summary;")
except Exception as e:
    st.error("Could not load data from PostgreSQL Gold views.")
    st.write("Please check that these views exist:")
    st.code(
        """
gold.price_comparison
gold.promotion_summary
gold.cheapest_unit_products
gold.data_quality_summary
        """
    )
    st.exception(e)
    st.stop()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Executive Overview",
        "Price Comparison",
        "Unit Price Analysis",
        "Promotion Analysis",
        "Data Quality",
        "Silver Data Explorer"
    ]
)

if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()


# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("Supermarket Price Intelligence Dashboard")

st.caption(
    "An end-to-end data engineering dashboard using PostgreSQL Gold views "
    "for Coles, Woolworths, and Aldi supermarket price analysis."
)


# ==================================================
# Page 1: Executive Overview
# ==================================================
if page == "Executive Overview":
    st.header("Executive Overview")

    total_products = len(price_df)
    total_supermarkets = price_df["supermarket"].nunique()
    promo_products = price_df[price_df["is_on_promotion"] == True].shape[0]
    avg_price = price_df["current_price"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Products", f"{total_products:,}")
    col2.metric("Supermarkets", total_supermarkets)
    col3.metric("Products on Promotion", f"{promo_products:,}")
    col4.metric("Average Price", format_currency(avg_price))

    st.divider()

    st.subheader("Product Count by Supermarket")

    product_count_df = (
        price_df.groupby("supermarket")
        .size()
        .reset_index(name="total_products")
        .sort_values("total_products", ascending=False)
    )

    fig_count = px.bar(
        product_count_df,
        x="supermarket",
        y="total_products",
        title="Total Products by Supermarket",
        text="total_products"
    )

    st.plotly_chart(fig_count, use_container_width=True)

    st.subheader("Average Current Price by Supermarket")

    avg_price_df = (
        price_df.groupby("supermarket")["current_price"]
        .mean()
        .reset_index(name="avg_current_price")
        .sort_values("avg_current_price", ascending=False)
    )

    fig_avg = px.bar(
        avg_price_df,
        x="supermarket",
        y="avg_current_price",
        title="Average Product Price by Supermarket",
        text=avg_price_df["avg_current_price"].round(2)
    )

    st.plotly_chart(fig_avg, use_container_width=True)

    st.subheader("Promotion Summary")

    st.dataframe(promotion_df, use_container_width=True)


# ==================================================
# Page 2: Price Comparison
# ==================================================
elif page == "Price Comparison":
    st.header("Price Comparison")

    st.write(
        "Search and compare products across Coles, Woolworths, and Aldi using "
        "the Gold price comparison view."
    )

    search_term = st.text_input("Search product name")

    supermarkets = sorted(price_df["supermarket"].dropna().unique())

    selected_supermarkets = st.multiselect(
        "Filter by supermarket",
        options=supermarkets,
        default=supermarkets
    )

    promotion_filter = st.selectbox(
        "Promotion filter",
        ["All products", "Only promotion products", "Only non-promotion products"]
    )

    filtered_df = price_df.copy()

    if search_term:
        filtered_df = filtered_df[
            filtered_df["product_name"].str.contains(
                search_term,
                case=False,
                na=False
            )
        ]

    filtered_df = filtered_df[
        filtered_df["supermarket"].isin(selected_supermarkets)
    ]

    if promotion_filter == "Only promotion products":
        filtered_df = filtered_df[filtered_df["is_on_promotion"] == True]
    elif promotion_filter == "Only non-promotion products":
        filtered_df = filtered_df[filtered_df["is_on_promotion"] == False]

    st.metric("Matching Products", f"{len(filtered_df):,}")

    columns_to_show = [
        "supermarket",
        "product_name",
        "brand",
        "pack_size",
        "current_price",
        "unit_price",
        "unit_quantity",
        "unit_type",
        "is_on_promotion",
        "save_amount",
        "was_price"
    ]

    existing_columns = [col for col in columns_to_show if col in filtered_df.columns]

    st.dataframe(
        filtered_df[existing_columns].sort_values(
            ["product_name", "supermarket"]
        ),
        use_container_width=True
    )

    st.subheader("Average Price of Filtered Products by Supermarket")

    if not filtered_df.empty:
        filtered_avg_df = (
            filtered_df.groupby("supermarket")["current_price"]
            .mean()
            .reset_index(name="avg_current_price")
        )

        fig = px.bar(
            filtered_avg_df,
            x="supermarket",
            y="avg_current_price",
            title="Average Current Price by Supermarket"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No products match the current filters.")


# ==================================================
# Page 3: Unit Price Analysis
# ==================================================
elif page == "Unit Price Analysis":
    st.header("Unit Price Analysis")

    st.write(
        "This section uses the Gold cheapest unit products view. "
        "It helps compare products more fairly using unit price."
    )

    unit_types = sorted(cheapest_df["unit_type"].dropna().unique())

    selected_unit_types = st.multiselect(
        "Filter by unit type",
        options=unit_types,
        default=unit_types
    )

    unit_search = st.text_input("Search product name in unit price table")

    unit_filtered_df = cheapest_df.copy()

    unit_filtered_df = unit_filtered_df[
        unit_filtered_df["unit_type"].isin(selected_unit_types)
    ]

    if unit_search:
        unit_filtered_df = unit_filtered_df[
            unit_filtered_df["product_name"].str.contains(
                unit_search,
                case=False,
                na=False
            )
        ]

    st.subheader("Cheapest Products by Unit Price")

    st.dataframe(
        unit_filtered_df[
            [
                "supermarket",
                "product_name",
                "brand",
                "pack_size",
                "current_price",
                "unit_price",
                "unit_quantity",
                "unit_type"
            ]
        ].sort_values("unit_price").head(100),
        use_container_width=True
    )

    st.subheader("Average Unit Price by Supermarket")

    if not unit_filtered_df.empty:
        avg_unit_df = (
            unit_filtered_df.groupby("supermarket")["unit_price"]
            .mean()
            .reset_index(name="avg_unit_price")
            .sort_values("avg_unit_price", ascending=True)
        )

        fig_unit = px.bar(
            avg_unit_df,
            x="supermarket",
            y="avg_unit_price",
            title="Average Unit Price by Supermarket"
        )

        st.plotly_chart(fig_unit, use_container_width=True)
    else:
        st.info("No unit price data matches the current filters.")


# ==================================================
# Page 4: Promotion Analysis
# ==================================================
elif page == "Promotion Analysis":
    st.header("Promotion Analysis")

    st.write(
        "This section uses the Gold promotion summary view and product-level "
        "promotion data from the Gold price comparison view."
    )

    st.subheader("Promotion Summary by Supermarket")

    st.dataframe(promotion_df, use_container_width=True)

    fig_promo = px.bar(
        promotion_df,
        x="supermarket",
        y="promotion_percentage",
        title="Promotion Percentage by Supermarket",
        text="promotion_percentage"
    )

    st.plotly_chart(fig_promo, use_container_width=True)

    st.subheader("Products Currently on Promotion")

    promo_products_df = price_df[price_df["is_on_promotion"] == True].copy()

    if "was_price" in promo_products_df.columns:
        promo_products_df["discount_amount"] = (
            promo_products_df["was_price"] - promo_products_df["current_price"]
        )
    else:
        promo_products_df["discount_amount"] = None

    promo_products_df = promo_products_df.sort_values(
        "discount_amount",
        ascending=False
    )

    st.dataframe(
        promo_products_df[
            [
                "supermarket",
                "product_name",
                "pack_size",
                "current_price",
                "was_price",
                "discount_amount"
            ]
        ].head(100),
        use_container_width=True
    )


# ==================================================
# Page 5: Data Quality
# ==================================================
elif page == "Data Quality":
    st.header("Data Quality Summary")

    st.write(
        "This section uses the Gold data quality summary view. "
        "It shows missing unit data and invalid promotion price rows by supermarket."
    )

    st.dataframe(quality_df, use_container_width=True)

    st.subheader("Data Quality Issues by Supermarket")

    issue_columns = [
        "missing_product_name",
        "missing_current_price",
        "missing_unit_price",
        "missing_unit_type",
        "invalid_promotion_price"
    ]

    available_issue_columns = [
        col for col in issue_columns if col in quality_df.columns
    ]

    if available_issue_columns:
        fig_quality = px.bar(
            quality_df,
            x="supermarket",
            y=available_issue_columns,
            title="Data Quality Issues by Supermarket",
            barmode="group"
        )

        st.plotly_chart(fig_quality, use_container_width=True)

    st.subheader("Data Quality Interpretation")

    st.markdown(
        """
        - `missing_unit_price`: Products that cannot be compared fairly by unit price.
        - `missing_unit_type`: Products missing unit type such as kg, g, L, ml, or each.
        - `invalid_promotion_price`: Rows where `was_price` is lower than `current_price`.
        - These rows should usually be flagged, not deleted, so the pipeline remains auditable.
        """
    )


# ==================================================
# Page 6: Silver Data Explorer
# ==================================================
elif page == "Silver Data Explorer":
    st.header("Silver Data Explorer")

    st.warning(
        "This section reads directly from the Silver layer for debugging only. "
        "Main dashboard analytics should use Gold views."
    )

    try:
        silver_df = load_query(
            """
            SELECT *
            FROM silver.supermarket_prices
            """
        )

        st.dataframe(silver_df, use_container_width=True)

    except Exception as e:
        st.error("Could not load Silver table.")
        st.exception(e)