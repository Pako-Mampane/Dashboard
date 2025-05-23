import calendar
from calendar import month_name
import streamlit as st  # type: ignore
import pandas as pd
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore


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

        div[id="header"]{
        
        }
        div[id="title"]{
            font-size:40px
        }

        div[id="Sidebar"]{
            font-size:20px
        }


        div[data-baseweb="select"]{
        height:30px}

        div[data-baseweb="select"] div {
            min-height: 30px !important;
            line-height: 30px !important;
            font-size: 0.8rem; /* Optional: smaller font */
            margin:0px
        }

        div[data-testid="stMainBlockContainer"]{
        padding-bottom:0 !important
        }

        div[data-testid="data-grid-canvas"]{
            border: 4px black
        }
        svg {
            border-radius: 0.5rem;
            box-shadow: rgba(100, 100, 111, 0.2) 0px 7px 29px 0px;
        }

        div[role='radiogroup']{
        display: flex;
        flex-direction:row;
        }

    </style>
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
<style>
.login-container {
    background-color: #f9f9f9;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
    width: 100%;
    max-width: 400px;
    margin: auto;
    margin-top: 3rem;
}

.login-container h2 {
    text-align: center;
    color: #333333;
    margin-bottom: 1.5rem;
}

.stTextInput > div > input, .stPasswordInput > div > input {
    padding: 0.5rem;
    border-radius: 6px;
    border: 1px solid #cccccc;
}

.stButton > button {
        background-color:black;
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3e638c;
    }
</style>
""",
    unsafe_allow_html=True,
)

USER_CREDENTIALS = {
    "manager": {"password": "p@k0123"},
    "member": {"password": "member123"},
}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


def login_form():
    with st.container():
        st.subheader("🔐 Login")
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if (
                    username in USER_CREDENTIALS
                    and USER_CREDENTIALS[username]["password"] == password
                ):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username} 👋")
                else:
                    st.error("Invalid username or password")
        st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.logged_in:
    c1, c2, c3 = st.columns(3)
    with c2:
        login_form()
        st.stop()
else:
    print("----------------Refreshing-------------------")
    # Auth logic

    with open("style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

    @st.cache_data
    def load_data(file):
        data = pd.read_csv(file, on_bad_lines="skip")
        return data

    with st.sidebar:
        # st.logo("image.png")
        st.markdown(
            f"""
                    <div style=" padding-top:0;" id="header">
                    <div id='title'>AI Solutions</div>
                    <div id="greetings">Hello, {st.session_state.username}!</div>
                    </div>""",
            unsafe_allow_html=True,
        )

    file = st.sidebar.file_uploader("Choose a dataset")
    if file is not None:
        df = load_data(file)
    else:
        st.warning("Please upload a dataset to continue")
        st.stop()
    st.sidebar.header("Filters")

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    min_date = df["Timestamp"].min()
    max_date = df["Timestamp"].max()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[
            (df["Timestamp"] >= pd.to_datetime(start_date))
            & (df["Timestamp"] <= pd.to_datetime(end_date))
        ]
    else:
        st.warning("Please select both a start and end date to filter the dashboard.")
        st.stop()
    country_filter = st.sidebar.selectbox(
        "**Country**", options=["All"] + list(df["Country"].unique()), index=0
    )

    product_filter = st.sidebar.selectbox(
        "**Product Category**",
        options=["All"] + list(df["Product"].dropna().unique()),
        index=0,
    )

    unique_months = sorted(df["month"].dropna().unique())
    month_names = [calendar.month_name[m] for m in unique_months]
    month_name_to_num = {calendar.month_name[m]: m for m in unique_months}
    month_filter = st.sidebar.selectbox(
        "**Month**", options=["All"] + month_names, index=0
    )

    year_filter = st.sidebar.selectbox(
        "**Year**", options=["All"] + list(df["year"].unique()), index=0
    )

    filtered_df = df[
        (df["Timestamp"] >= pd.to_datetime(start_date))
        & (df["Timestamp"] <= pd.to_datetime(end_date))
    ]

    if country_filter != "All":
        filtered_df = filtered_df[filtered_df["Country"] == country_filter]

    if product_filter != "All":
        filtered_df = filtered_df[
            filtered_df["Product"].notna() & (filtered_df["Product"] == product_filter)
        ]

    if month_filter != "All":
        selected_month_num = month_name_to_num[month_filter]
        filtered_df = filtered_df[filtered_df["month"] == selected_month_num]

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

    monthly_sessions = filtered_df.groupby("month")["Session ID"].nunique()
    total_sales = filtered_df[filtered_df["Request Type"] == "Product Purchase"].shape[
        0
    ]
    total_sales_revenue = filtered_df["Revenue"].sum()
    total_visitors = filtered_df["IP Address"].nunique()
    conversion_by_IP = filtered_df[filtered_df["Product"].notna()][
        "IP Address"
    ].nunique()
    conversion_rate = (conversion_by_IP / total_visitors) * 100

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "💰 Sales Overview",
            "🏆 Sales Performance",
            "🌐 Traffic Analytics",
            "📊 Descriptive Statistics",
            "Raw Data"
        ]
    )

    with tab1:
        c = st.container()

        card_style = """
            <style>
                .metric-card {
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    padding: 0.1rem;
                    width: 100%;  /* Fill column width */
                    min-height: 85px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    font-family: sans-serif;
                    background-color: #f9f9f9;
                    margin-bottom: 0.2rem;
                }
                .metric-title {
                    font-size: 0.85rem;
                    color: #666;
                    margin-bottom: 0.3rem;
                }
                .metric-value {
                    font-size: 1.5rem;
                    font-weight: 700;
                    margin: 0.3rem 0;
                }
                .metric-change {
                    font-size: 0.85rem;
                }
                .positive {
                    color: green;
                }

                .negative {
                    color: red;
                }
                @keyframes pulse-red {
                    0% { background-color: #f8d7da; }
                    50% { background-color: #f5c6cb; }
                    100% { background-color: #f8d7da; }
                }

                .metric-card.negative { background-color: #f8d7da;  animation: pulse-red 2s infinite;}  /* red-ish */
                .metric-card.positive { background-color: #d4edda; }  /* green-ish */
                .metric-card.neutral  { background-color: #f5f5f5; }
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
            latest_month = filtered_df[filtered_df["year"] == latest_year][
                "month"
            ].max()

            if latest_month == 1:
                prev_month = 12
                prev_year = latest_year - 1
            else:
                prev_month = latest_month - 1
                prev_year = latest_year

            curr_df = df[(df["month"] == latest_month) & (df["year"] == latest_year)]
            prev_df = df[(df["month"] == prev_month) & (df["year"] == prev_year)]
            prev_month_name = month_name[prev_month]
            period_label = f"M-o-M {prev_month_name}"

        # Total Sales
        curr_sales = curr_df[curr_df["Request Type"] == "Product Purchase"].shape[0]
        prev_sales = prev_df[prev_df["Request Type"] == "Product Purchase"].shape[0]
        sales_growth = (
            ((curr_sales - prev_sales) / prev_sales * 100) if prev_sales != 0 else 0
        )

        # Revenue
        curr_revenue = curr_df["Revenue"].sum()
        prev_revenue = prev_df["Revenue"].sum()
        mom_revenue_growth = (
            ((curr_revenue - prev_revenue) / prev_revenue * 100)
            if prev_revenue != 0
            else 0
        )

        # Conversion Rate
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

        # Total Reach
        curr_reach = curr_df["IP Address"].nunique()
        prev_reach = prev_df["IP Address"].nunique()
        reach_growth = (
            ((curr_reach - prev_reach) / prev_reach * 100) if prev_reach != 0 else 0
        )

        st.markdown(card_style, unsafe_allow_html=True)

        def get_change_label(value, label):
            return f"{label}: {'▲' if value >= 0 else '▼'} {abs(value):.1f}%"

        sales_label = get_change_label(sales_growth, period_label)
        revenue_label = get_change_label(mom_revenue_growth, period_label)
        conversion_label = get_change_label(conversion_growth, period_label)
        reach_label = get_change_label(reach_growth, period_label)

        def get_performance_class(change):
            if change >= 10:
                return "positive"
            elif change >= 0:
                return "positive"
            elif change > -10:
                return "neutral"
            else:
                return "negative"

        css_class = get_performance_class(sales_growth)
        col1, col2, col3, col4, col5 = c.columns(5)
        col1.markdown(
            f"""
                <div class="metric-card {css_class}">
                    <div class="metric-title">🛒 Total Sales</div>
                    <div class="metric-value">{total_sales}</div>
                    <div class="metric-change {"positive" if sales_growth >= 0 else "negative"}">
                    {sales_label}
                    </div>
                </div>
                """,
            unsafe_allow_html=True,
        )
        css_class = get_performance_class(mom_revenue_growth)
        col2.markdown(
            f"""
    <div class="metric-card {css_class}">
        <div class="metric-title">💵 Total Revenue</div>
        <div class="metric-value">P {total_sales_revenue:,.2f}</div>
        <div class="metric-change {"positive" if mom_revenue_growth >= 0 else "negative"}">
            {revenue_label}        
        </div>
    </div>
    """,
            unsafe_allow_html=True,
        )
        css_class = get_performance_class(conversion_growth)
        col3.markdown(
            f"""
    <div class="metric-card  {css_class}">
        <div class="metric-title">🎯 Conversion Rate</div>
        <div class="metric-value">{conversion_rate:.2f}%</div>
        <div class="metric-change {"positive" if conversion_growth >= 0 else "negative"}">
            {conversion_label}
        </div>
    </div>
    """,
            unsafe_allow_html=True,
        )
        css_class = get_performance_class(reach_growth)
        col4.markdown(
            f"""
    <div class="metric-card {css_class}">
        <div class="metric-title">🌍 Total Reach</div>
        <div class="metric-value">{total_visitors}</div>
        <div class="metric-change {"positive" if reach_growth >= 0 else "negative"}">
            {reach_label}
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
                .metric-title {
                    font-weight: bold;
                    margin-bottom: 0.5rem;
                }

                ol{
                list-style-type:none;
                text-align:start
                }

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
                            total_visitors,
                            product_views,
                            demo_requests,
                            total_sales,
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
                product_volume = (
                    product_volume_df["Product"].value_counts().reset_index()
                )
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

    with tab2:
        # Prepare date features
        sales_df = df.copy()
        sales_df["Timestamp"] = pd.to_datetime(sales_df["Timestamp"])
        sales_df["year"] = sales_df["Timestamp"].dt.year
        sales_df["month"] = sales_df["Timestamp"].dt.month
        sales_df["month_name"] = sales_df["Timestamp"].dt.strftime("%b")
        sales_df["quarter"] = sales_df["Timestamp"].dt.to_period("Q").astype(str)

        filter1, filter2, filter3 = st.columns(3)

        with filter1:
            time_mode = st.selectbox(
                "Filter by", ["Monthly", "Quarterly"], key="filter mode"
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

            else:  # Quarterly
                quarter_opts = (
                    sales_df["quarter"].drop_duplicates().sort_values(ascending=False)
                )
                selected_quarter = st.selectbox(
                    "Select Quarter", quarter_opts.tolist(), key="tab4_quarter"
                )
                time_sales_df = sales_df[sales_df["quarter"] == selected_quarter]

            # Continue with filtering
            time_sales_df = time_sales_df.dropna(
                subset=["Sales Agent", "Revenue", "Product"]
            )
            if time_sales_df.empty:
                st.info("No data available for the selected period.")
                st.stop()
        with filter3:
            selected_agent = st.radio(
                "View Performance for:",
                options=time_sales_df["Sales Agent"].unique(),
                horizontal=True,
                key="tab4_agent",
            )

        tab4_df = time_sales_df[time_sales_df["Sales Agent"] == selected_agent]

        # Safe groupings
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
        available_cols = [
            col for col in expected_cols if col in product_funnel_df.columns
        ]

        if available_cols:
            funnel_data = product_funnel_df.melt(
                id_vars="Product",
                value_vars=available_cols,
                var_name="Stage",
                value_name="Count",
            )
            funnel_data["Stage"] = pd.Categorical(
                funnel_data["Stage"], categories=expected_cols, ordered=True
            )
        else:
            funnel_data = pd.DataFrame(columns=["Product", "Stage", "Count"])

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

        # --- Charts and Indicators ---
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
                    margin=dict(t=50, b=20, r=20, l=20),
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
                )
                fig_funnel.update_layout(
                    height=225, margin=dict(t=50, r=10, l=10), paper_bgcolor="white",
                    showlegend=False,
                    legend=dict(font=dict(size=10)),
                )
                st.plotly_chart(fig_funnel, use_container_width=True)
            else:
                st.info("No funnel data available.")

        # Additional charts
        cont2 = st.container()
        cont2_col1, cont2_col2 = cont2.columns(2)

        with cont2_col1:
            closed = product_purchases["Product"].count()

            if time_mode == "Monthly":
                deal_max_val = 200
                deal_ref_val = 130
                deal_steps = [
                    {"range": [0, 70], "color": "red"},
                    {"range": [70, 120], "color": "darkorange"},
                    {"range": [120, deal_max_val], "color": "green"},
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

    with tab3:
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
        session_duration = filtered_df.groupby("Session ID")["Timestamp"].agg(
            lambda x: (x.max() - x.min()).seconds / 60
        )
        avg_duration = session_duration.mean()

        cont_traffic = st.container()
        col1, col2, col3, col4 = cont_traffic.columns(4)

        with col1:
            st.metric("Total Visitors", total_visitors)
        with col2:
            st.metric("New Visitors", new_visitors)
        with col3:
            st.metric("Returning Visitors", returning_visitors)
        with col4:
            st.metric("Avg Session Duration", f"{avg_duration:.1f} mins")

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
            figt.update_layout(
                margin=dict(t=50, l=25, r=25, b=25), paper_bgcolor="white"
            )
            st.plotly_chart(figt, use_container_width=True)

    with tab4:
        st.header("Summary Statistics")
        request_counts = filtered_df["Request Type"].value_counts().reset_index()
        request_counts.columns = ["Request Type", "Count"]
        total_revenue = filtered_df["Revenue"].sum()

        # Count rows where revenue is not zero or null (valid revenue entries)
        revenue_non_zero_count = filtered_df[filtered_df["Revenue"] > 0][
            "Revenue"
        ].count()
        avg_revenue = total_revenue / revenue_non_zero_count
        col1, col2, col3 = st.columns(3)
        col1.metric("Mean Revenue", f"P {avg_revenue:.2f}")
        col2.metric(
            "Median Revenue",
            f"P {filtered_df['Revenue'][filtered_df['Revenue'] > 0].median():.2f}",
        )
        col3.metric(
            "Std Dev",
            f"P {filtered_df['Revenue'][filtered_df['Revenue'] > 0].std():.2f}",
        )
        fig_requests = px.bar(
            request_counts,
            x="Request Type",
            y="Count",
            title="Distribution of Request Types",
            color="Request Type",
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Safe,
        )

        st.plotly_chart(fig_requests, use_container_width=True)

    # with tab4:
    #     filtered_df = filtered_df.dropna(subset=["Sales Agent", "Revenue", "Product"])
    #     selected_agent = st.radio(
    #         "View Performance for: ",
    #         options=filtered_df["Sales Agent"].unique(),
    #         # default=filtered_df["Sales Agent"].unique(),
    #     )
    #     tab4_df = (
    #         filtered_df[filtered_df["Sales Agent"] == selected_agent]
    #         if selected_agent
    #         else filtered_df
    #     )
    #     sales_by_referrer = tab4_df.groupby("Referrer")["Revenue"].nunique()
    #     scheduled_demo_requests = tab4_df[tab4_df["Request Type"] == "Demo Request"][
    #         "Sales Agent"
    #     ].value_counts()

    #     product_funnel_df = (
    #         tab4_df.groupby(["Product", "Request Type"])
    #         .size()
    #         .unstack(fill_value=0)
    #         .reset_index()
    #     )
    #     funnel_data = product_funnel_df.melt(
    #         id_vars="Product",
    #         value_vars=["Demo Request", "Product Purchase"],
    #         var_name="Stage",
    #         value_name="Count",
    #     )
    #     stage_order = ["Demo Request", "Product Purchase"]
    #     funnel_data["Stage"] = pd.Categorical(
    #         funnel_data["Stage"], categories=stage_order, ordered=True
    #     )
    #     product_purchases = tab4_df[tab4_df["Request Type"] == "Product Purchase"]
    #     sales_volume_by_country = (
    #         product_purchases.groupby("Country").size().reset_index(name="Sales Made")
    #     )

    #     cont = st.container()
    #     col1, col2, col3 = cont.columns(3)

    #     with col1:
    #         fig_sbr = px.pie(
    #             sales_by_referrer,
    #             values="Revenue",
    #             names=sales_by_referrer.index,
    #             title="Sales by Referrer",
    #             color_discrete_sequence=px.colors.sequential.Plasma,
    #             hole=0.4,
    #         )
    #         fig_sbr.update_traces(textinfo="percent+label")
    #         fig_sbr.update_layout(
    #             margin=dict(t=50, b=20, r=20, l=20),
    #             width=100,
    #             height=225,
    #             paper_bgcolor="white",
    #             showlegend=False,
    #         )
    #         st.plotly_chart(fig_sbr, use_container_width=True)

    #     with col2:
    #         sales = tab4_df["Revenue"].sum()
    #         fig_gauge_revenue = go.Figure(
    #             go.Indicator(
    #                 mode="gauge+number+delta",
    #                 value=sales,
    #                 domain={"x": [0, 1], "y": [0, 1]},
    #                 title="Revenue Goals",
    #                 delta={"reference": 1600000},
    #                 gauge={
    #                     "axis": {"range": [0, 2400000]},
    #                     "bar": {"color": "#4E79A7"},
    #                     "steps": [
    #                         {"range": [0, 800000], "color": "red"},
    #                         {"range": [800000, 1600000], "color": "darkorange"},
    #                         {"range": [1600000, 2400000], "color": "green"},
    #                     ],
    #                 },
    #             )
    #         )
    #         fig_gauge_revenue.update_layout(
    #             height=225,
    #             width=100,
    #             margin=dict(t=50, r=10, l=10, b=10),
    #             paper_bgcolor="white",
    #         )

    #         st.plotly_chart(fig_gauge_revenue, use_container_width=True)
    #     with col3:
    #         fig_funnel = px.funnel(
    #             funnel_data,
    #             y="Stage",
    #             x="Count",
    #             title=f"Sales Funnel: {selected_agent}",
    #             color="Product",
    #         )
    #         fig_funnel.update_layout(
    #             height=225,
    #             margin=dict(t=50, r=20, l=20),
    #             paper_bgcolor="white",
    #         )

    #         st.plotly_chart(fig_funnel, use_container_width=True)
    #     cont2 = st.container()
    #     cont2_col1, cont2_col2 = cont2.columns(2)
    #     with cont2_col1:
    #         closed = tab4_df[tab4_df["Request Type"] == "Product Purchase"][
    #             "Product"
    #         ].count()
    #         fig_gauge_closed = go.Figure(
    #             go.Indicator(
    #                 mode="number+gauge+delta",
    #                 value=closed,
    #                 domain={"x": [0, 1], "y": [0, 1]},
    #                 delta={"reference": 5000},
    #                 gauge={
    #                     "shape": "bullet",
    #                     "axis": {"range": [None, 7000]},
    #                     "bgcolor": "white",
    #                     "steps": [
    #                         {"range": [0, 2000], "color": "red"},
    #                         {"range": [2000, 5000], "color": "darkorange"},
    #                         {"range": [5000, 7000], "color": "green"},
    #                     ],
    #                     "bar": {"color": "darkblue"},
    #                 },
    #             )
    #         )
    #         fig_gauge_closed.update_layout(
    #             height=200,
    #             title="<b>Deals closed</b>",
    #             margin=dict(t=50, r=20, l=50),
    #             paper_bgcolor="white",
    #         )
    #         st.plotly_chart(fig_gauge_closed)

    #     with cont2_col2:
    #         fig_volume = px.choropleth(
    #             sales_volume_by_country,
    #             locations="Country",
    #             locationmode="country names",
    #             color="Sales Made",
    #             color_continuous_scale="Blues",
    #             title="Sales Volume by Country (Product Purchases)",
    #         )
    #         fig_volume.update_geos(
    #             showcountries=True,
    #             showcoastlines=True,
    #             coastlinecolor="Black",
    #             countrycolor="gray",
    #             projection_type="natural earth",
    #         )
    #         fig_volume.update_layout(
    #             xaxis=dict(showticklabels=False),
    #             margin=dict(t=40, b=20, r=20, l=20),
    #             width=400,
    #             height=225,
    #             paper_bgcolor="white",
    #         )

    #         st.plotly_chart(fig_volume)
    with tab5:
        st.header("Data Set")
        st.dataframe(filtered_df.head(500))
    with st.sidebar:
        st.button("Log out", on_click=st.logout)
