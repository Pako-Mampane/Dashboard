import streamlit as st  # type: ignore
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
import pandas as pd


def render_sales_performance(filtered_df, df):
    sales_df = df.copy()
    sales_df["Timestamp"] = pd.to_datetime(sales_df["Timestamp"])
    sales_df["year"] = sales_df["Timestamp"].dt.year
    sales_df["month"] = sales_df["Timestamp"].dt.month
    sales_df["month_name"] = sales_df["Timestamp"].dt.strftime("%b")
    sales_df["quarter"] = sales_df["Timestamp"].dt.to_period("Q").astype(str)

    filter1, filter2, filter3 = st.columns(3)
    with filter1:
        time_mode = st.selectbox(
            "Filter by", ["Monthly", "Quarterly"], key="filter_mode"
        )
    with filter2:
        if time_mode == "Monthly":
            month_opts = (
                sales_df[["year", "month", "month_name"]]
                .drop_duplicates()
                .sort_values(["year", "month"], ascending=[False, False])
            )
            month_opts["label"] = (
                month_opts["month_name"] + " " + month_opts["year"].astype(str)
            )
            selected_month_label = st.selectbox(
                "Select Month", month_opts["label"].tolist(), key="tab4_month"
            )
            selected_month_row = month_opts[
                month_opts["label"] == selected_month_label
            ].iloc[0]
            selected_year = selected_month_row["year"]
            selected_month = selected_month_row["month"]
            time_sales_df = sales_df[
                (sales_df["year"] == selected_year)
                & (sales_df["month"] == selected_month)
            ]
        else:
            quarter_opts = (
                sales_df["quarter"].drop_duplicates().sort_values(ascending=False)
            )
            selected_quarter = st.selectbox(
                "Select Quarter", quarter_opts.tolist(), key="tab4_quarter"
            )
            time_sales_df = sales_df[sales_df["quarter"] == selected_quarter]

        time_sales_df = time_sales_df.dropna(
            subset=["Sales Agent", "Revenue", "Product"]
        )
        if time_sales_df.empty:
            st.info("No data available for the selected period.")
            return

    with filter3:
        selected_agent = st.radio(
            "View Performance for:",
            options=time_sales_df["Sales Agent"].unique(),
            horizontal=True,
            key="tab4_agent",
        )

    tab4_df = time_sales_df[time_sales_df["Sales Agent"] == selected_agent]
    sales_by_referrer = (
        tab4_df.groupby("Referrer")["Revenue"].nunique()
        if not tab4_df.empty and "Referrer" in tab4_df.columns
        else pd.Series(dtype=float)
    )
    product_funnel_df = (
        tab4_df.groupby(["Product", "Request Type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        if not tab4_df.empty
        else pd.DataFrame(columns=["Product", "Demo Request", "Product Purchase"])
    )
    expected_cols = ["Demo Request", "Product Purchase"]
    available_cols = [col for col in expected_cols if col in product_funnel_df.columns]
    funnel_data = (
        product_funnel_df.melt(
            id_vars="Product",
            value_vars=available_cols,
            var_name="Stage",
            value_name="Count",
        )
        if available_cols
        else pd.DataFrame(columns=["Product", "Stage", "Count"])
    )
    funnel_data["Stage"] = pd.Categorical(
        funnel_data["Stage"], categories=expected_cols, ordered=True
    )
    product_purchases = (
        tab4_df[tab4_df["Request Type"] == "Product Purchase"]
        if "Request Type" in tab4_df
        else pd.DataFrame()
    )
    sales_volume_by_country = (
        product_purchases.groupby("Country").size().reset_index(name="Sales Made")
        if not product_purchases.empty
        else pd.DataFrame(columns=["Country", "Sales Made"])
    )

    cont = st.container()
    col1, col2, col3 = cont.columns(3)
    with col1:
        if not sales_by_referrer.empty:
            fig_sbr = px.pie(
                sales_by_referrer,
                values="Revenue",
                names=sales_by_referrer.index,
                title="Sales by Referrer",
                color_discrete_sequence=px.colors.sequential.Plasma,
                hole=0.4,
            )
            fig_sbr.update_traces(textinfo="percent+label")
            fig_sbr.update_layout(
                margin=dict(t=30, b=10, r=20, l=20),
                width=100,
                height=225,
                paper_bgcolor="white",
                showlegend=False,
            )
            st.plotly_chart(fig_sbr, use_container_width=True)
        else:
            st.info("No referrer data available.")

    with col2:
        sales = tab4_df["Revenue"].sum()
        if time_mode == "Monthly":
            rev_max_val = 50000
            rev_ref_val = 32000
            rev_steps = [
                {"range": [0, 15000], "color": "red"},
                {"range": [15000, 30000], "color": "darkorange"},
                {"range": [30000, rev_max_val], "color": "green"},
            ]
        else:
            rev_max_val = 150000
            rev_ref_val = 110000
            rev_steps = [
                {"range": [0, 50000], "color": "red"},
                {"range": [50000, 100000], "color": "darkorange"},
                {"range": [100000, rev_max_val], "color": "green"},
            ]
        fig_gauge_revenue = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=sales,
                domain={"x": [0, 1], "y": [0, 1]},
                title="Revenue Goals",
                delta={"reference": rev_ref_val},
                gauge={
                    "axis": {"range": [0, rev_max_val]},
                    "bar": {"color": "#4E79A7"},
                    "steps": rev_steps,
                },
            )
        )
        fig_gauge_revenue.update_layout(
            height=225,
            width=100,
            margin=dict(t=50, r=10, l=10, b=10),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_gauge_revenue, use_container_width=True)

    with col3:
        if not funnel_data.empty:
            fig_funnel = px.funnel(
                funnel_data,
                y="Stage",
                x="Count",
                title=f"Sales Funnel: {selected_agent}",
                color="Product",
                text="Product",
            )
            fig_funnel.update_layout(
                height=225,
                margin=dict(t=50, r=10, l=10),
                paper_bgcolor="white",
                showlegend=False,
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
        else:
            st.info("No funnel data available.")

    cont2 = st.container()
    cont2_col1, cont2_col2 = cont2.columns(2)
    with cont2_col1:
        closed = product_purchases["Product"].count()
        if time_mode == "Monthly":
            deal_max_val = 200
            deal_ref_val = 130
            deal_steps = [
                {"range": [0, 70], "color": "red"},
                {"range": [70, 150], "color": "darkorange"},
                {"range": [150, deal_max_val], "color": "green"},
            ]
        else:
            deal_max_val = 600
            deal_ref_val = 420
            deal_steps = [
                {"range": [0, 180], "color": "red"},
                {"range": [180, 400], "color": "darkorange"},
                {"range": [400, deal_max_val], "color": "green"},
            ]
        fig_gauge_closed = go.Figure(
            go.Indicator(
                mode="number+gauge+delta",
                value=closed,
                domain={"x": [0, 1], "y": [0, 1]},
                delta={"reference": deal_ref_val},
                gauge={
                    "shape": "bullet",
                    "axis": {"range": [None, deal_max_val]},
                    "bgcolor": "white",
                    "steps": deal_steps,
                    "bar": {"color": "darkblue"},
                },
            )
        )
        fig_gauge_closed.update_layout(
            height=225,
            title="<b>Deals closed</b>",
            margin=dict(t=50, r=20, l=50),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_gauge_closed)

    with cont2_col2:
        if not sales_volume_by_country.empty:
            fig_volume = px.choropleth(
                sales_volume_by_country,
                locations="Country",
                locationmode="country names",
                color="Sales Made",
                color_continuous_scale="Blues",
                title="Sales Volume by Country (Product Purchases)",
            )
            fig_volume.update_geos(
                showcountries=True,
                showcoastlines=True,
                coastlinecolor="Black",
                countrycolor="gray",
                projection_type="natural earth",
            )
            fig_volume.update_layout(
                xaxis=dict(showticklabels=False),
                margin=dict(t=40, b=20, r=20, l=20),
                width=400,
                height=225,
                paper_bgcolor="white",
            )
            st.plotly_chart(fig_volume)
        else:
            st.info("No sales volume data available.")
