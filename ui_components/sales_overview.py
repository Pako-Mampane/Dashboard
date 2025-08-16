import streamlit as st  # type: ignore
import plotly.express as px  # type: ignore
import pandas as pd
import calendar


def render_sales_overview(filtered_df, filters):
    print("Hitting")
    card_style = """
        <style>
            .metric-card {
                border: 1px solid #e0e0e0;
                border-radius: 0.5rem;
                padding: 0.1rem;
                width: 100%;
                min-height: 85px;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                font-family: sans-serif;
                background-color: #f9f9f9;
                margin-bottom: 0.2rem;
            }
            .metric-title { font-size: 0.85rem; color: #666; margin-bottom: 0.3rem; }
            .metric-value { font-size: 1.5rem; font-weight: 700; margin: 0.3rem 0; }
            .metric-change { font-size: 0.85rem; }
            .positive { color: green; }
            .negative { color: red; }
            @keyframes pulse-red {
                0% { background-color: #f8d7da; }
                50% { background-color: #f5c6cb; }
                100% { background-color: #f8d7da; }
            }
            .metric-card.negative { background-color: #f8d7da; animation: pulse-red 2s infinite; }
            .metric-card.positive { background-color: #d4edda; }
            .metric-card.neutral { background-color: #f8f9fa; }
            @media (max-width: 768px) {
                .metric-value { font-size: 1rem; }
                .metric-title, .metric-change { font-size: 0.75rem; }
            }
        </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

    month_filter = filters["month_filter"]
    start_date = filters["start_date"]
    end_date = filters["end_date"]
    df = filters["df"]

    if month_filter == "All":
        latest_date = filtered_df["Timestamp"].max()
        current_year = latest_date.year
        prev_year = current_year - 1
        ytd_cutoff = latest_date.replace(year=prev_year)
        curr_df = filtered_df[
            (filtered_df["Timestamp"] >= f"{current_year}-01-01")
            & (filtered_df["Timestamp"] <= latest_date)
        ]
        prev_df = filtered_df[
            (filtered_df["Timestamp"] >= f"{prev_year}-01-01")
            & (filtered_df["Timestamp"] <= ytd_cutoff)
        ]
        period_label = "YTD vs Last Year"
    else:
        latest_year = filtered_df["year"].max()
        latest_month = filtered_df[filtered_df["year"] == latest_year]["month"].max()
        prev_month = 12 if latest_month == 1 else latest_month - 1
        prev_year = latest_year - 1 if latest_month == 1 else latest_year
        curr_df = df[(df["month"] == latest_month) & (df["year"] == latest_year)]
        prev_df = df[(df["month"] == prev_month) & (df["year"] == prev_year)]
        period_label = f"M-o-M {calendar.month_name[prev_month]}"

    curr_sales = curr_df[curr_df["Request Type"] == "Product Purchase"].shape[0]
    prev_sales = prev_df[prev_df["Request Type"] == "Product Purchase"].shape[0]
    sales_growth = (
        ((curr_sales - prev_sales) / prev_sales * 100) if prev_sales != 0 else 0
    )

    curr_revenue = curr_df["Revenue"].sum()
    prev_revenue = prev_df["Revenue"].sum()
    mom_revenue_growth = (
        ((curr_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue != 0 else 0
    )

    curr_conversion = (
        curr_df[curr_df["Product"].notna()]["IP Address"].nunique()
        / curr_df["IP Address"].nunique()
        * 100
        if curr_df["IP Address"].nunique() > 0
        else 0
    )
    prev_conversion = (
        prev_df[prev_df["Product"].notna()]["IP Address"].nunique()
        / prev_df["IP Address"].nunique()
        * 100
        if prev_df["IP Address"].nunique() > 0
        else 0
    )
    conversion_growth = (
        ((curr_conversion - prev_conversion) / prev_conversion * 100)
        if prev_conversion != 0
        else 0
    )

    curr_reach = curr_df["IP Address"].nunique()
    prev_reach = prev_df["IP Address"].nunique()
    reach_growth = (
        ((curr_reach - prev_reach) / prev_reach * 100) if prev_reach != 0 else 0
    )

    def get_change_label(value, label):
        return f"{label}: {'▲' if value >= 0 else '▼'} {abs(value):.1f}%"

    def get_performance_class(change):
        if change >= 10:
            return "positive"
        elif change >= 0:
            return "positive"
        elif change > -10:
            return "neutral"
        else:
            return "negative"

    c = st.container()
    col1, col2, col3, col4, col5 = c.columns(5)
    col1.markdown(
        f"""
        <div class="metric-card {get_performance_class(sales_growth)}">
            <div class="metric-title">🛒 Total Sales</div>
            <div class="metric-value">{filters["total_sales"]}</div>
            <div class="metric-change {"positive" if sales_growth >= 0 else "negative"}">
                {get_change_label(sales_growth, period_label)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col2.markdown(
        f"""
        <div class="metric-card {get_performance_class(mom_revenue_growth)}">
            <div class="metric-title">💵 Total Revenue</div>
            <div class="metric-value">P {filters["total_sales_revenue"]:,.2f}</div>
            <div class="metric-change {"positive" if mom_revenue_growth >= 0 else "negative"}">
                {get_change_label(mom_revenue_growth, period_label)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col3.markdown(
        f"""
        <div class="metric-card {get_performance_class(conversion_growth)}">
            <div class="metric-title">🎯 Conversion Rate</div>
            <div class="metric-value">{filters["conversion_rate"]:.2f}%</div>
            <div class="metric-change {"positive" if conversion_growth >= 0 else "negative"}">
                {get_change_label(conversion_growth, period_label)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col4.markdown(
        f"""
        <div class="metric-card {get_performance_class(reach_growth)}">
            <div class="metric-title">🌍 Total Reach</div>
            <div class="metric-value">{filters["total_visitors"]}</div>
            <div class="metric-change {"positive" if reach_growth >= 0 else "negative"}">
                {get_change_label(reach_growth, period_label)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col5.markdown(
        """
        <style>
            .metric-card_key {
                background-color: #f8f9fa;
                border-radius: 8px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.05);
                font-family: sans-serif;
                font-size: 0.9rem;
            }
            .metric-title { font-weight: bold; margin-bottom: 0.5rem; }
            ol { list-style-type:none; text-align:start }
            .good, .neutral_key, .bad {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 0.5rem;
            }
            .good { background-color: green; }
            .neutral_key { background-color:#FFBF00 ; }
            .bad { background-color: red; }
        </style>
        <div class="metric-card_key">
            <div class="metric-title">Key</div>
            <ol>
                <li><span class="good"></span>Good Performance</li>
                <li><span class="neutral_key"></span>Neutral Performance</li>
                <li><span class="bad"></span>Bad Performance</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        filtered_df["month"] = filtered_df["month"].apply(
            lambda x: calendar.month_name[x]
        )
        month_order = list(calendar.month_name)[1:]
        filtered_df["month"] = pd.Categorical(
            filtered_df["month"], categories=month_order, ordered=True
        )
        monthly_sales = (
            filtered_df.groupby("month")["Revenue"]
            .sum()
            .reset_index()
            .sort_values("month")
        )
        fig1 = px.line(
            monthly_sales,
            x="month",
            y="Revenue",
            title="Monthly Sales Trend",
            markers=True,
            line_shape="spline",
        )
        fig1.update_layout(
            margin=dict(t=50, b=20, r=20, l=20),
            width=400,
            height=225,
            paper_bgcolor="white",
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            filters["product_sales"],
            x="Product",
            y="Revenue",
            title="Revenue by Product",
            labels={"Revenue": "Total Revenue (BWP)"},
            color="Product",
        )
        fig2.update_layout(
            xaxis=dict(showticklabels=False),
            margin=dict(t=50, b=20, r=20, l=20),
            width=100,
            height=225,
            paper_bgcolor="white",
            legend=dict(
                title="Products",
                orientation="v",
                x=2.5,
                xanchor="center",
                traceorder="normal",
                y=0.5,
                yanchor="bottom",
                bgcolor="rgba(255,255,255,0.5)",
                font=dict(family="Arial", size=10, color="black"),
                itemwidth=30,
            ),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = px.bar(
            filters["product_sales_by_agent"],
            x="Sales Agent",
            y="Revenue",
            title="Revenue by Agent",
            labels={"Revenue": "Total Revenue (BWP)"},
            color="Sales Agent",
        )
        fig3.update_layout(
            xaxis=dict(showticklabels=True),
            margin=dict(t=50, b=20, r=20, l=20),
            width=400,
            height=225,
            showlegend=False,
            paper_bgcolor="white",
        )
        st.plotly_chart(fig3, use_container_width=True)

    con = st.container()
    with con:
        column1, column2, column3 = con.columns(3)
        with column1:
            world_fig = px.scatter_geo(
                filters["sales_by_country"],
                locations="Country",
                locationmode="country names",
                size="Revenue",
                color="Revenue",
                hover_name="Country",
                hover_data=["Revenue"],
                color_continuous_scale=px.colors.sequential.Plasma,
                title="Sales Revenue by Country",
            )
            world_fig.update_geos(
                showcountries=True,
                showcoastlines=True,
                coastlinecolor="Black",
                countrycolor="gray",
                projection_type="natural earth",
            )
            world_fig.update_layout(
                xaxis=dict(showticklabels=False),
                margin=dict(t=40, b=20, r=20, l=20),
                width=400,
                height=225,
                paper_bgcolor="white",
            )
            st.plotly_chart(world_fig, use_container_width=True)

        with column2:
            demo_requests = filtered_df[
                filtered_df["Request Type"] == "Demo Request"
            ].shape[0]
            product_views = filtered_df[
                filtered_df["Request Type"] == "Product View"
            ].shape[0]
            conversion_df = pd.DataFrame(
                {
                    "Stage": [
                        "Total Reach",
                        "Product Views",
                        "Demo Requests",
                        "Purchases",
                    ],
                    "Count": [
                        filters["total_visitors"],
                        product_views,
                        demo_requests,
                        filters["total_sales"],
                    ],
                }
            )
            fig_conversions = px.funnel(
                conversion_df, x="Count", y="Stage", title="Lead Conversion"
            )
            fig_conversions.update_layout(
                height=225,
                paper_bgcolor="white",
                margin=dict(t=50, b=20, r=20, l=20),
            )
            st.plotly_chart(fig_conversions, use_container_width=True)

        with column3:
            product_volume_df = filtered_df[
                filtered_df["Request Type"] == "Product Purchase"
            ]
            product_volume = product_volume_df["Product"].value_counts().reset_index()
            product_volume.columns = ["Product", "Volume"]
            fig_product_volume = px.pie(
                product_volume,
                names="Product",
                values="Volume",
                title="Product Volume Distribution",
            )
            fig_product_volume.update_layout(
                height=225,
                paper_bgcolor="white",
                legend=dict(font=dict(size=10)),
                margin=dict(t=50, b=20, r=20, l=20),
            )
            st.plotly_chart(fig_product_volume, use_container_width=True)
