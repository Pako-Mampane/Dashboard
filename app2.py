from datetime import datetime
from re import X
from turtle import color, hideturtle
import calendar
from matplotlib import legend
from traitlets import default
import streamlit as st  # type: ignore
import pandas as pd
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
import requests


st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")
st.markdown(
    """
    <style>
        body{
            overflow:hidden;
            margin-bottom:0px;
        }
        .block-container {
            padding-top: 0 !important;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[]

        section[data-testid="stSidebar"]{
            width:100px;
            
        }
        div[id="title"]{
            font-size:60px
        }

        div[id="Sidebar"]{
            font-size:20px
        }

        div[data-testid="stMainBlockContainer"]{
        padding-bottom:0 !important
        }

        div[data-testid="data-grid-canvas"]{
            border: 4px black
        }
        svg {
            border-radius: 0.5rem;
            box-shadow: 0 5px 8px rgba(54, 69, 79, 1);
        }

    </style>
""",
    unsafe_allow_html=True,
)


print("----------------Refreshing-------------------")
# Auth logic
if not st.experimental_user.is_logged_in:
    if st.button("Log in"):
        st.login()
else:
    with open("style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

    API_URL = "http://127.0.0.1:8000"

    if "processed_data" not in st.session_state:
        st.session_state.processed_data = pd.DataFrame()

    REFRESH_INTERVAL = 5
    last_refresh = datetime.now()

    def fetch_data():
        """Fetch processed data and metrics from API"""
        try:
            processed_response = requests.get(
                f"{API_URL}/data?limit=500000&processed=true"  # Add timeout
            )

            if processed_response.status_code == 200:
                data = processed_response.json()
                if not data:
                    st.warning("API returned empty data")
                    return pd.DataFrame()

                df = pd.DataFrame(data)
                if df.empty:
                    st.warning("No data available after conversion")
                else:
                    print("Data fetch successful")
                    print(df)
                return df

            st.error(f"API request failed: {processed_response.status_code}")
            return pd.DataFrame()

        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()

    with st.sidebar:
        st.logo("image.png")
        st.markdown(
            f"""
                    <div style=" padding-top:0;">
                    <div id="title">AI Solutions</div>
                    <div id="Sidebar">Prototype v0.1.1</div>
                    <div id="greetings">Hello, {st.experimental_user.name}!</div>
                    </div>""",
            unsafe_allow_html=True,
        )

        # st.markdown("_Author: Pako Mampane_")
    #     csv_file = st.file_uploader("Choose a file to upload")

    # if csv_file is None:
    #     st.info("Please upload a file to get started", icon="ℹ️")
    #     st.stop()

    df = fetch_data()
    print("fetching df")
    print(df.empty)
    if df.empty:
        st.warning("No data available. Please ensure the API is running.")
        st.stop()
    st.sidebar.header("Filters")
    country_filter = st.sidebar.selectbox(
        "**Country**", options=["All"] + list(df["Country"].unique()), index=0
    )

    product_filter = st.sidebar.selectbox(
        "**Product Category**", options=["All"] + list(df["Product"].unique()), index=0
    )

    month_filter = st.sidebar.selectbox(
        "**Month**", options=["All"] + list(df["month"].unique()), index=0
    )

    year_filter = st.sidebar.selectbox(
        "**Year**", options=["All"] + list(df["year"].unique()), index=0
    )

    # Start with the full dataset
    filtered_df = df.copy()

    # Apply filters only if a specific value is selected
    if country_filter != "All":
        filtered_df = filtered_df[filtered_df["Country"] == country_filter]

    if product_filter != "All":
        filtered_df = filtered_df[filtered_df["Product"] == product_filter]

    if month_filter != "All":
        filtered_df = filtered_df[filtered_df["month"] == month_filter]

    if year_filter != "All":
        filtered_df = filtered_df[filtered_df["year"] == year_filter]
    # aggregations
    product_sales = (
        filtered_df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values(by="Revenue", ascending=False)
    )

    sales_by_country = (
        filtered_df.groupby("Country")["Revenue"]
        .sum()
        .reset_index()
        .sort_values(by="Revenue", ascending=False)
    )
    product_sales_by_agent = (
        filtered_df.groupby("Sales Agent")["Revenue"].sum().reset_index()
    )
    conversion_by_referrer = filtered_df.groupby("Referrer").agg(
        {"Session ID": "nunique", "Product": lambda x: x.notnull().sum()}
    )
    sales_by_referrer = filtered_df.groupby("Referrer")["Revenue"].nunique()

    monthly_sessions = filtered_df.groupby("month")["Session ID"].nunique()
    total_sales = filtered_df[filtered_df["Product"] != "0"].shape[0]
    total_sales_revenue = filtered_df["Revenue"].sum()
    total_visitors = filtered_df["IP Address"].nunique()
    conversion_by_IP = filtered_df[filtered_df["Product"].notna()][
        "IP Address"
    ].nunique()
    conversion_rate = (conversion_by_IP / total_visitors) * 100

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Sales Overview", "Traffic Analytics", "Descriptive Statistics", "Marketing"]
    )

    with tab1:
        c = st.container()

        col1, col2, col3, col4, col5 = c.columns(5)
        card_style = """
<style>
    .metric-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 0.5rem;
        width: 100%;  /* Fill column width */
        min-height: 85px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-family: sans-serif;
        background-color: #f9f9f9;
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0.3rem 0;
    }
    .metric-change {
        font-size: 0.85rem;
    }
    .positive {
        color: green;
    }
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1rem;
        }
        .metric-title, .metric-change {
            font-size: 0.75rem;
        }
    }
</style>
"""
        st.markdown(card_style, unsafe_allow_html=True)
        col1.markdown(
            f"""
    <div class="metric-card">
        <div class="metric-title">Total Sales</div>
        <div class="metric-value">{total_sales}</div>
        <div class="metric-change positive">▲ 8.4%</div>
    </div>
    """,
            unsafe_allow_html=True,
        )
        col2.markdown(
            f"""
    <div class="metric-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value">P {total_sales_revenue:,.2f}</div>
        <div class="metric-change positive">▲ 8.4%</div>
    </div>
    """,
            unsafe_allow_html=True,
        )
        col3.markdown(
            f"""
    <div class="metric-card">
        <div class="metric-title">Conversion Rate</div>
        <div class="metric-value">{conversion_rate:.2f}%</div>
        <div class="metric-change positive">▲ 8.4%</div>
    </div>
    """,
            unsafe_allow_html=True,
        )
        col4.markdown(
            f"""
    <div class="metric-card">
        <div class="metric-title">Total Reach</div>
        <div class="metric-value">{total_visitors}%</div>
        <div class="metric-change positive">▲ 8.4%</div>
    </div>
    """,
            unsafe_allow_html=True,
        )

        with col5:
            if st.button("🔄 Refresh Data"):
                fetch_data()
            st.caption(f"Last refreshed: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

        col1, col2, col3 = st.columns(3)

        with col1:
            filtered_df["month"] = filtered_df["month"].apply(
                lambda x: calendar.month_name[x]
            )
            month_order = list(calendar.month_name)[1:]
            filtered_df["month"] = pd.Categorical(
                filtered_df["month"], categories=month_order, ordered=True
            )
            monthly_sales = filtered_df.groupby("month")["Revenue"].sum().reset_index()
            monthly_sales = monthly_sales.sort_values("month")
            filtered_df.head()
            fig1 = px.line(
                monthly_sales,
                x="month",
                y="Revenue",
                title="Monthly Sales Trend",
                markers=True,
                # color="Product",
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
                product_sales,
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
                    orientation="v",  # 'v' for vertical, 'h' for horizontal
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
                product_sales_by_agent,
                x="Sales Agent",
                y="Revenue",
                title="Revenue by Agent",
                labels={"Revenue": "Total Revenue (BWP)"},
                color="Sales Agent",
            )
            fig3.update_layout(
                xaxis=dict(showticklabels=False),
                margin=dict(t=50, b=20, r=20, l=20),
                width=400,
                height=225,
                paper_bgcolor="white",
            )
            st.plotly_chart(fig3, use_container_width=True)
        con = st.container()
        with con:
            column1, column2 = con.columns([2, 1])
            with column1:
                world_fig = px.scatter_geo(
                    sales_by_country,
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
                config = {"Revenue": st.column_config.NumberColumn("Revenue (BWP)")}
                sales_df = (
                    df.groupby("Sales Agent")
                    .agg(
                        Closed=("Product", "count"),
                        Revenue=("Revenue", "sum"),
                    )
                    .reset_index()
                )
                st.dataframe(sales_df, hide_index=True, column_config=config)

    with tab2:
        ip_counts = filtered_df["IP Address"].value_counts()

        # Map counts to the original dataframe
        filtered_df["visit_count"] = filtered_df["IP Address"].map(ip_counts)

        # Classify visitor type
        filtered_df["visitor_type"] = filtered_df["visit_count"].apply(
            lambda x: "New" if x == 1 else "Returning"
        )
        day_map = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        filtered_df["day_name"] = filtered_df["day_of_week"].map(day_map)

        visitors_by_day = (
            filtered_df.groupby("day_name")["IP Address"].nunique().reset_index()
        )
        visitors_by_day.columns = ["Day", "Visitors"]

        day_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        visitors_by_day["Day"] = pd.Categorical(
            visitors_by_day["Day"], categories=day_order, ordered=True
        )
        visitors_by_day = visitors_by_day.sort_values("Day")

        # Now calculate totals
        new_visitors = filtered_df[filtered_df["visitor_type"] == "New"][
            "IP Address"
        ].nunique()
        returning_visitors = filtered_df[filtered_df["visitor_type"] == "Returning"][
            "IP Address"
        ].nunique()

        cont_traffic = st.container()
        col1, col2, col3 = cont_traffic.columns(3)

        with col1:
            st.metric("Total Visitors", total_visitors)
        with col2:
            st.metric("New Visitors", new_visitors)
        with col3:
            st.metric("Returning Visitors", returning_visitors)

        vis_cont = st.container()
        (
            col1,
            col2,
        ) = vis_cont.columns([2, 1])

        with col1:
            col1_cont = st.container()
            cont_col1, cont_col2 = col1_cont.columns(2)

            with cont_col1:
                fig_weekly = px.line(
                    visitors_by_day,
                    x="Day",
                    y="Visitors",
                    title="Weekly Traffic Distribution",
                    labels={"Visitors": "Unique Visitors", "Day": "Day of Week"},
                    markers=True,
                    line_shape="spline",
                )
                fig_weekly.update_layout(
                    xaxis_title=None,
                    yaxis_title=None,
                    paper_bgcolor="white",
                    height=200,
                    width=400,
                    margin=dict(t=40, b=20, l=20, r=20),
                )
                st.plotly_chart(fig_weekly, use_container_width=True)

            with cont_col2:
                visitors_by_hour = (
                    filtered_df.groupby("hour")["IP Address"].nunique().reset_index()
                )
                visitors_by_hour.columns = ["hour", "visitors"]
                heatmap_data = []
                for _, row in visitors_by_hour.iterrows():
                    heatmap_data.extend(
                        [[row["hour"], row["visitors"]]] * row["visitors"]
                    )

                heat_df = pd.DataFrame(heatmap_data, columns=["hour", "visitors"])

                fig_area = px.area(
                    visitors_by_hour,
                    x="hour",
                    y="visitors",
                    title="Peak Traffic Hours",
                    labels={"hour": "Hour of Day", "visitors": "Number of Visitors"},
                )

                fig_area.update_layout(
                    margin=dict(t=50, b=20, r=20, l=20),
                    xaxis=dict(tickmode="linear", tick0=0, dtick=1),
                    yaxis=dict(title="Unique Visitors"),
                    width=400,
                    height=200,
                    paper_bgcolor="white",
                )

                st.plotly_chart(fig_area, use_container_width=True)
            users_vs_new_users = (
                filtered_df.groupby("month")
                .agg(
                    total_visitors=("IP Address", "nunique"),
                    new_users=("visitor_type", lambda x: (x == "New").sum()),
                )
                .reset_index()
            )
            fig_v_n = px.line(
                users_vs_new_users,
                x="month",
                y=["total_visitors", "new_users"],
                title="Visitors vs New Visitors Over Time",
                labels={"value": "Count", "month": "Month"},
                markers=True,
            )

            fig_v_n.update_layout(
                margin=dict(t=50, b=20, r=20, l=20),
                width=600,
                height=225,
                paper_bgcolor="white",
                legend_title="User Type",
            )
            st.plotly_chart(fig_v_n, use_container_width=True)

        with col2:
            traffic_by_referrer = (
                filtered_df.groupby("Referrer")["IP Address"]
                .nunique()
                .reset_index()
                .rename(columns={"IP Address": "Visitors"})
            )
            figt = px.treemap(
                traffic_by_referrer,
                path=["Referrer"],
                values="Visitors",
                color="Visitors",
                color_continuous_scale="Blues",
                title="Traffic Share by Referrer",
            )
            figt.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(figt, use_container_width=True)

    with tab3:
        users_vs_new_users = (
            filtered_df.groupby("month")
            .agg(
                total_visitors=("IP Address", "nunique"),
                new_users=("visitor_type", lambda x: (x == "New").sum()),
            )
            .reset_index()
        )
        session_url_count = filtered_df.groupby("Session ID")["URL"].nunique()
        bounced_sessions = session_url_count[session_url_count == 1].count()
        total_sessions = filtered_df["Session ID"].nunique()

        bounce_rate = (bounced_sessions / total_sessions) * 100

        total_page_views = filtered_df.groupby("Session ID")["URL"].count()
        total_page_views = total_page_views.sum()
        avg_pages_per_session = total_page_views / total_sessions

        behaviour_merics = (
            filtered_df.groupby("Referrer")
            .agg(
                total_sessions=("Session ID", "nunique"),
                total_users=("IP Address", "nunique"),
                new_users=("visitor_type", lambda x: (x == "New").sum()),
            )
            .reset_index()
        )

        acquisition_metrics = (
            filtered_df.groupby("Referrer")
            .agg(
                total_sessions=("Session ID", "nunique"),
                total_page_views=("URL", "count"),
                total_bounces=(
                    "Session ID",
                    lambda x: (
                        filtered_df.loc[x.index].groupby("Session ID")["URL"].nunique()
                        == 1
                    ).sum(),
                ),
            )
            .reset_index()
        )

        acquisition_metrics["bounce_rate"] = (
            acquisition_metrics["total_bounces"] / acquisition_metrics["total_sessions"]
        ) * 100

        acquisition_metrics["avg_pages_per_session"] = (
            acquisition_metrics["total_page_views"]
            / acquisition_metrics["total_sessions"]
        )

        # filtered_df["Timestamp"] = pd.to_datetime(filtered_df["Timestamp"])

        # session_duration = (
        #     filtered_df.groupby("Session ID")
        #     .agg(
        #         duration=(
        #             "Timestamp",
        #             lambda x: (x.max() - x.min()).total_seconds() / 60,
        #         )
        #     )
        #     .reset_index()
        # )

        # avg_session_duration = (
        #     session_duration / filtered_df["Session ID"].nunique().sum()
        # )
        # print(f"AVG session duration: {avg_session_duration}")
        cont2 = st.container()
        col11, col22 = cont2.columns(2)

        with col11:
            st.markdown("Acquisition")
            total_sessions = filtered_df["Session ID"].nunique()

            cont3 = st.container()
            col1, col2, col3 = cont3.columns(3)

            col1.markdown(
                f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    margin-top:0;
                    padding: 0.2rem;
                    width: 100px;
                    height: 55px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    font-family: sans-serif;
                    background-color: #f9f9f9;
                ">
                    <div style="font-size: 0.85rem; color: #666;">Sessions</div>
                    <div style="font-size: 1.09rem; font-weight: 600;">{total_sessions}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col2.markdown(
                f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    padding: 0.2rem;
                    width: 100px;
                    height: 55px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    font-family: sans-serif;
                    background-color: #f9f9f9;
                ">
                    <div style="font-size: 0.85rem; color: #666;">Visitors</div>
                    <div style="font-size: 1.09rem; font-weight: 600;">{total_visitors}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col3.markdown(
                f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    padding: 0.2rem;
                    width: 100px;
                    height: 55px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    font-family: sans-serif;
                    background-color: #f9f9f9;
                ">
                    <div style="font-size: 0.85rem; color: #666;">New Visitors</div>
                    <div style="font-size: 1.09rem; font-weight: 600;">{new_visitors}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.dataframe(
                acquisition_metrics,
                use_container_width=True,
                height=300,
                hide_index=True,
            )
        with col22:
            st.markdown("Behavior")
            cont4 = st.container()
            colum1, colum2, colum3 = cont4.columns(3)
            with colum1:
                colum1.markdown(
                    f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    padding: 0.2rem;
                    width: 100px;
                    height: 55px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    font-family: sans-serif;
                    background-color: #f9f9f9;
                ">
                    <div style="font-size: 0.85rem; color: #666;">Bounce Rate</div>
                    <div style="font-size: 1.09rem; font-weight: 600;">{bounce_rate:.2f} %</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                colum2.markdown(
                    f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    padding: 0.2rem;
                    width: 100px;
                    height: 55px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    font-family: sans-serif;
                    background-color: #f9f9f9;
                ">
                    <div style="font-size: 0.85rem; color: #666;">Pages/Session</div>
                    <div style="font-size: 1.09rem; font-weight: 600;">{avg_pages_per_session:.2f}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                colum3.markdown(
                    f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    padding: 0.2rem;
                    width: 100px;
                    height: 55px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    font-family: sans-serif;
                    background-color: #f9f9f9;
                ">
                    <div style="font-size: 0.85rem; color: #666;">New Visitors</div>
                    <div style="font-size: 1.09rem; font-weight: 600;">{bounce_rate:.2f}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            st.dataframe(
                behaviour_merics.style.set_properties(**{"height": "20px"}),
                use_container_width=True,
                height=300,
                hide_index=True,
            )
    st.dataframe(filtered_df)
    print((filtered_df["URL"] == "Product_Purchase").sum())

    with tab4:
        selected_agent = st.multiselect(
            "View Performance for: ",
            options=filtered_df["Sales Agent"].unique(),
            default=filtered_df["Sales Agent"].unique(),
        )
        tab4_df = filtered_df[
            filtered_df["Sales Agent"].isin(selected_agent)
            if selected_agent
            else filtered_df
        ]
        cont = st.container()
        col1, col2 = cont.columns([1, 2])

        with col1:
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
                margin=dict(t=50, b=20, r=20, l=20),
                width=100,
                height=225,
                paper_bgcolor="white",
                showlegend=False,
            )
            st.plotly_chart(fig_sbr, use_container_width=True)

        with col2:
            sales = tab4_df["Revenue"].sum()
            fig_gauge_revenue = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=sales,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title="Revenue Goals",
                    gauge={
                        "axis": {"range": [0, 10000000]},
                        "bar": {"color": "#4E79A7"},
                        "steps": [
                            {"range": [0, 2000000], "color": "red"},
                            {"range": [2000000, 6000000], "color": "lightgreen"},
                            {"range": [6000000, 10000000], "color": "green"},
                        ],
                    },
                )
            )
            fig_gauge_revenue.update_layout(
                height=225,
                width=100,
                margin=dict(t=50, r=0, l=0, b=10),
                paper_bgcolor="white",
            )

            st.plotly_chart(fig_gauge_revenue, use_container_width=True)
        cont2 = st.container()
        cont2_col1, cont2_col2 = cont2.columns(2)
        with cont2_col1:
            closed = tab4_df["Product"].count()
            fig_gauge_closed = go.Figure(
                go.Indicator(
                    mode="number+gauge+delta",
                    value=closed,
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 20000},
                    gauge={
                        "shape": "bullet",
                        "axis": {"range": [None, 20000]},
                        "bgcolor": "white",
                        "steps": [
                            {"range": [0, 7000], "color": "lightblue"},
                            {"range": [7000, 15000], "color": "lightgreen"},
                            {"range": [15000, 20000], "color": "green"},
                        ],
                        "bar": {"color": "darkblue"},
                    },
                )
            )
            fig_gauge_closed.update_layout(
                height=200,
                title="<b>Deals closed</b>",
                margin=dict(t=50, r=20, l=50),
                paper_bgcolor="white",
            )
            st.plotly_chart(fig_gauge_closed)

        with cont2_col2:
            st.markdown("Visual 2")
    with st.sidebar:
        if st.button("Log out"):
            st.logout()
