import streamlit as st  # type: ignore
import plotly.express as px  # type: ignore
import pandas as pd


def render_traffic_analytics(filtered_df):
    ip_counts = filtered_df["IP Address"].value_counts()
    filtered_df["visit_count"] = filtered_df["IP Address"].map(ip_counts)
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
    col1.metric("Total Visitors", filtered_df["IP Address"].nunique())
    col2.metric("New Visitors", new_visitors)
    col3.metric("Returning Visitors", returning_visitors)
    col4.metric("Avg Session Duration", f"{avg_duration:.1f} mins")

    vis_cont = st.container()
    col1, col2 = vis_cont.columns([2, 1])
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
            margin=dict(t=50, l=25, r=25, b=25),
            paper_bgcolor="white",
        )
        st.plotly_chart(figt, use_container_width=True)
