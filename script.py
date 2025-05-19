import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid
from fake_useragent import UserAgent
import re

fake = Faker()
ua = UserAgent()

# random seed
np.random.seed(42)

# date range
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 2, 27)

page_requests = [
    ("GET", "/index.html", 0.25),
    ("GET", "/images/events.jpg", 0.05),
    ("GET", "/event.html", 0.1),
    ("POST", "/event/register.html", 0.03),
    ("POST", "/product/ai-assistant/schedule-demo.php", 0.036),
    ("POST", "/product/email-automation-ai/schedule-demo.php", 0.02),
    ("POST", "/product/performance-analytics-tool/schedule-demo.php", 0.024),
    ("POST", "/request-.php", 0.02),
    ("POST", "/bug-tickets.php", 0.015),
    ("GET", "/checkout.php", 0.01),
    ("POST", "/contact-sales.php", 0.015),
    ("GET", "/promo-events.html", 0.06),
    ("GET", "/customer-support.php", 0.042),
    ("GET", "/product/hr-support.html", 0.04),
    ("POST", "/product/performance-analytics-tool/feedback.php", 0.02),
    ("POST", "/product/ai-assistant/feedback.php", 0.03),
    ("POST", "/product/email-automation-ai/feedback.php", 0.02),
    ("GET", "/product/performance-analytics-tool.html", 0.02),
    ("GET", "/product/ai-assistant.html", 0.03),
    ("GET", "/product/email-automation-ai.html", 0.03),
    ("POST", "/product/performance-analytics-tool/request.php", 0.01),
    ("POST", "/product/ai-assistant/request.php", 0.02),
    ("POST", "/product/email-automation-ai/request.php", 0.010),
    ("GET", "/pricing.html", 0.03),
    ("POST", "/request-quote.php", 0.02),
    ("GET", "/about-us.html", 0.02),
    ("POST", "/newsletter-signup.php", 0.02),
    ("GET", "/special-offers.html", 0.008),
]

products = [
    ("AI Virtual Assistant", 599.99),
    ("Email Automation AI", 149.99),
    ("Performance Analytics Tool", 299.99),
]

sales_agents = ["Kago", "Lefika", "Mpho", "Thembi"]
sales_agents_weights = [0.3, 0.2, 0.4, 0.1]
referrer_sites = [
    "https://www.google.com",
    "https://www.bing.com",
    "https://www.facebook.com",
    "https://www.instagram.com",
    "https://www.linkedin.com",
    "https://www.tiktok.com",
    "https://www.pinterest.com",
]
referrer_sites_weights = [0.3, 0.1, 0.15, 0.05, 0.11, 0.19, 0.1]

status_codes = [200, 201, 302, 400, 401, 403, 404, 408, 429, 500, 503]
status_code_weights = [0.65, 0.10, 0.05, 0.02, 0.01, 0.01, 0.05, 0.05, 0.03, 0.01, 0.02]
"""
STATUS CODE GUIDE
200-> Ok
201-> Created
302-> Found
400-> Bad Request
401-> Unauthorized
403-> Forbidden
404-> Not Found
408-> Request Timeout
429-> Too Many Requests
500-> Internal Server Error
503-> Service Unavailable
"""
invalid_status_codes = [999, 000]


def generate_IP_addresses(ip_pool=None):
    countries = [
        "USA",
        "Canada",
        "UK",
        "Germany",
        "France",
        "Australia",
        "Italy",
        "Spain",
        "India",
        "China",
        "Brazil",
        "Mexico",
        "Japan",
        "South Korea",
        "Russia",
        "Argentina",
        "South Africa",
        "Turkey",
        "Egypt",
        "Nigeria",
    ]
    country_weights = [
        0.2,
        0.15,
        0.1,
        0.1,
        0.1,
        0.04,
        0.04,
        0.04,
        0.04,
        0.04,
        0.02,
        0.02,
        0.02,
        0.02,
        0.02,
        0.01,
        0.01,
        0.01,
        0.01,
        0.01,
    ]
    if ip_pool is None:
        ip_pool = [fake.ipv4_public() for i in range(20000)]
    country = np.random.choice(countries, p=country_weights)
    ip = random.choice(ip_pool)
    if random.random() < 0.005:
        ip = f"invalid_url_{random.randint(1000, 9999)}"

    return ip, country


def generate_random_date():
    """
    Implementing peak and off hours traffic
    """
    month_weights = {
        1: 0.08,
        2: 0.07,
        3: 0.06,
        4: 0.069,
        5: 0.081,
        6: 0.083,
        7: 0.082,
        8: 0.04,
        9: 0.075,
        10: 0.075,
        11: 0.09,
        12: 0.1,
    }
    random_days = random.choices(
        population=range((end_date - start_date).days + 1),
        weights=[
            (1.2 if (start_date + timedelta(days=i)).weekday() < 5 else 0.5)
            * month_weights[(start_date + timedelta(days=i)).month]
            for i in range((end_date - start_date).days + 1)
        ],
        k=1,
    )[0]
    random_date = start_date + timedelta(days=random_days)
    peak_hours = [8, 9, 10, 11, 14, 15, 16, 17]
    off_hours = [0, 1, 2, 3, 4, 5, 6]
    if random_date.weekday() < 5 and random.random() < 0.7:
        hour = random.choices(
            peak_hours + off_hours,
            weights=[10 if h in peak_hours else 1 for h in peak_hours + off_hours],
        )[0]
    else:
        hour = random.choices(
            peak_hours + off_hours,
            weights=[3 if h in peak_hours else 5 for h in peak_hours + off_hours],
        )[0]

    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return random_date.replace(hour=hour, minute=minute, second=second)


def generate_response_time():
    rt = max(50, np.random.normal(300, 100))
    if random.random() < 0.05:
        if random.random() < 0.3:
            return random.randint(500, 20000)
        else:
            return round(random.uniform(1, 50), 2)

    return round(rt, 2)


def generate_server_log():
    random_date = generate_random_date()
    timestamp = (random_date + timedelta(seconds=random.randint(1, 86400))).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    ip_address, country = generate_IP_addresses()

    # adding biases to the request types
    request_types, urls, url_weights = zip(*page_requests)
    selected_index = np.random.choice(len(urls), p=url_weights)
    request_type, url = request_types[selected_index], urls[selected_index]

    valid_statuses = status_codes.copy()
    valid_weights = status_code_weights.copy()

    if request_type != "POST":
        if 201 in valid_statuses:
            idx = valid_statuses.index(201)
            valid_statuses.pop(idx)
            valid_weights.pop(idx)
            total = sum(valid_weights)
            valid_weights = [w / total for w in valid_weights]

    status_code = np.random.choice(valid_statuses, p=valid_weights)
    if random.random() < 0.03:
        status_code = 999
    response_time = generate_response_time()
    if random.random() < 0.05:
        response_time = random.choice(
            [random.randint(10000, 50000), random.uniform(0.1, 5)]
        )
    session_id = str(uuid.uuid4())

    return [
        timestamp,
        ip_address,
        session_id,
        country,
        request_type,
        url,
        status_code,
        response_time,
    ]


def generate_sales_data(url):
    sale_pattern = r"^/product/(performance-analytics-tool|ai-assistant|email-automation-ai)/request\.php$"
    demo_pattern = r"^/product/(performance-analytics-tool|ai-assistant|email-automation-ai)/schedule-demo\.php$"
    if not re.match(sale_pattern, url) and not (re.match(demo_pattern, url)):
        return (None, 0, None)
    if re.match(sale_pattern, url):
        if random.random():
            product, price = random.choice(products)
            agent = np.random.choice(sales_agents, p=sales_agents_weights)
            return (
                product,
                round(price * random.uniform(0.9, 1.1), 2),
                agent,
            )
        else:
            return (None, 0, None)
    if re.match(demo_pattern, url):
        product, _ = random.choice(products)
        agent = np.random.choice(sales_agents, p=sales_agents_weights)
        return (product, 0, agent)


def generate_web_logs(num, file_name="data/raw_logs/final_server_logs12.csv"):
    logs = []
    ip_session_map = {}
    session_timeout = 30
    ip_pool = [fake.ipv4_public() for _ in range(326895)]

    current_time_window = generate_random_date()
    time_window_duration = 120
    time_window_end = current_time_window + timedelta(minutes=time_window_duration)
    session_referrers = {}
    session_count = int(num / 6)
    demo_metadata = {}
    purchase_info = {}
    for _ in range(session_count):
        num_pages = np.random.choice(
            [1, 2, 3, 4, 5, 6, 7], p=[0.05, 0.15, 0.25, 0.2, 0.15, 0.1, 0.1]
        )
        for _ in range(num_pages):
            # Create timestamp within current time window (95% chance) or new window (5%)
            if random.random() < 0.05:  # 5% chance to start new time window
                current_time_window = generate_random_date()
                time_window_end = current_time_window + timedelta(
                    minutes=time_window_duration
                )

            # Generate timestamp within current window
            timestamp = current_time_window + timedelta(
                seconds=random.randint(0, time_window_duration * 60)
            )

            # Ensure timestamp doesn't exceed window end
            if timestamp > time_window_end:
                timestamp = time_window_end - timedelta(seconds=random.randint(1, 300))

            ip_address, country = generate_IP_addresses(ip_pool)

            # Session management with constraints
            if ip_address in ip_session_map:
                last_timestamp, session_id = ip_session_map[ip_address]
                time_since_last = (timestamp - last_timestamp).total_seconds() / 60

                # Force new session if timeout exceeded or crossed to new day
                if (
                    time_since_last > session_timeout
                    or timestamp.date() != last_timestamp.date()
                ):
                    session_id = str(uuid.uuid4())
                    session_referrers[session_id] = np.random.choice(
                        referrer_sites, p=referrer_sites_weights
                    )
            else:
                session_id = str(uuid.uuid4())
                session_referrers[session_id] = random.choice(referrer_sites)

            ip_session_map[ip_address] = (timestamp, session_id)

            request_types, urls, url_weights = zip(*page_requests)
            selected_index = np.random.choice(len(urls), p=url_weights)
            request_type, url = request_types[selected_index], urls[selected_index]
            if random.random() < 0.02:
                url = f"invalid_url_{random.randint(1000, 9999)}"

            valid_statuses = status_codes.copy()
            valid_weights = status_code_weights.copy()

            product, price, agent = generate_sales_data(url)

            if request_type != "POST":
                if 201 in valid_statuses:
                    idx = valid_statuses.index(201)
                    valid_statuses.pop(idx)
                    valid_weights.pop(idx)
                    total = sum(valid_weights)
                    valid_weights = [w / total for w in valid_weights]

            status_code = np.random.choice(valid_statuses, p=valid_weights)
            referrer = session_referrers[session_id]
            if random.random() < 0.03:
                status_code = 999

            # Response Time
            response_time = generate_response_time()
            if random.random() < 0.05:
                response_time = random.choice(
                    [random.randint(10000, 50000), random.uniform(0.1, 5)]
                )

        # Generate logs
        log_entry = [
            timestamp,
            ip_address,
            session_id,
            country,
            request_type,
            url,
            status_code,
            response_time,
            agent,
            referrer,
            product,
            price,
        ]
        logs.append(log_entry)

    df = pd.DataFrame(
        logs,
        columns=[
            "Timestamp",
            "IP Address",
            "Session ID",
            "Country",
            "Method",
            "URL",
            "Status Code",
            "Response Time (ms)",
            "Sales Agent",
            "Referrer",
            "Product",
            "Price",
        ],
    )

    df["IP_Session"] = df["IP Address"] + "_" + df["Session ID"]
    df["viewed_pricing_after_demo"] = df["IP Address"].map(
        lambda ip: demo_metadata.get(ip, {}).get("pricing_after_demo", False)
    )
    df["pages_after_demo"] = df["IP Address"].map(
        lambda ip: demo_metadata.get(ip, {}).get("pages", 0)
    )
    df["sessions_after_demo"] = df["IP Address"].map(
        lambda ip: len(demo_metadata.get(ip, {}).get("sessions", set()))
    )
    df["time_to_purchase"] = df["IP Address"].map(
        lambda ip: (
            (purchase_info[ip] - demo_metadata[ip]["demo_time"]).total_seconds() / 60
            if ip in purchase_info and ip in demo_metadata
            else np.nan
        )
    )

    df.to_csv(file_name, index=False)
    print(f"{num} server logs saved to {file_name}")


# def generate_web_logs(num, file_name="final_server_logs8.csv"):
#     logs = []
#     ip_session_map = {}
#     session_timeout = 30
#     ip_pool = [fake.ipv4_public() for _ in range(326895)]

#     current_time_window = generate_random_date()
#     time_window_duration = 120
#     time_window_end = current_time_window + timedelta(minutes=time_window_duration)
#     session_referrers = {}
#     ip_addresses = [generate_IP_addresses(ip_pool)[0] for _ in range(int(num/1))]

#     session_count = int(num / 6)

#     for _ in range(session_count):
#         session_id = str(uuid.uuid4())
#         ip_address, country = generate_IP_addresses(ip_pool)
#         if random.random() < 0.05:  # 5% chance to start new time window
#             current_time_window = generate_random_date()
#             time_window_end = current_time_window + timedelta(
#                 minutes=time_window_duration
#             )
#         referrer_session = np.random.choice(referrer_sites, p=referrer_sites_weights)
#         num_pages = np.random.choice(
#             [1, 2, 3, 4, 5, 6, 7], p=[0.05, 0.15, 0.25, 0.2, 0.15, 0.1, 0.1]
#         )

#         demo_viewed = False
#         pricing_viewed = False

#         for _ in range(num_pages):

#             timestamp = current_time_window + timedelta(
#                 seconds=random.randint(0, time_window_duration * 60)
#             )

#             # Ensure timestamp doesn't exceed window end
#             if timestamp > time_window_end:
#                 timestamp = time_window_end - timedelta(seconds=random.randint(1, 300))

#             request_types, urls, url_weights = zip(*page_requests)
#             selected_index = np.random.choice(len(urls), p=url_weights)
#             request_type, url = request_types[selected_index], urls[selected_index]
#             if random.random() < 0.02:
#                 url = f"invalid_url_{random.randint(1000, 9999)}"

#             if "schedule-demo" in url:
#                 demo_viewed = True
#             if "pricing" in url:
#                 pricing_viewed = True

#             valid_statuses = status_codes.copy()
#             valid_weights = status_code_weights.copy()
#             product, price, agent = generate_sales_data(
#                 url, demo_viewed=demo_viewed, pricing_viewed=pricing_viewed
#             )
#             referrer = referrer_session

#             if request_type != "POST":
#                 if 201 in valid_statuses:
#                     idx = valid_statuses.index(201)
#                     valid_statuses.pop(idx)
#                     valid_weights.pop(idx)
#                     total = sum(valid_weights)
#                     valid_weights = [w / total for w in valid_weights]

#             status_code = np.random.choice(valid_statuses, p=valid_weights)
#             if random.random() < 0.03:
#                 status_code = 999

#             # Response Time
#             response_time = generate_response_time()
#             if random.random() < 0.05:
#                 response_time = random.choice(
#                     [random.randint(10000, 50000), random.uniform(0.1, 5)]
#                 )

#             # Generate logs
#             log_entry = [
#                 timestamp,
#                 ip_address,
#                 session_id,
#                 country,
#                 request_type,
#                 url,
#                 status_code,
#                 response_time,
#                 agent,
#                 referrer,
#                 product,
#                 price,
#             ]
#             logs.append(log_entry)

#     df = pd.DataFrame(
#         logs,
#         columns=[
#             "Timestamp",
#             "IP Address",
#             "Session ID",
#             "Country",
#             "Method",
#             "URL",
#             "Status Code",
#             "Response Time (ms)",
#             "Sales Agent",
#             "Referrer",
#             "Product",
#             "Price",
#         ],
#     )

#     df["IP_Session"] = df["IP Address"] + "_" + df["Session ID"]

#     df.to_csv(file_name, index=False)
#     print(f"{num} server logs saved to {file_name}")


# def generate_web_logs(num, file_name="final_server_logs4.csv"):
#     logs = []
#     ip_session_map = {}
#     session_timeout = 30  # minutes
#     ip_pool = [fake.ipv4_public() for _ in range(326895)]
#     session_referrers = {}

#     # First generate all IP addresses we'll use
#     ip_addresses = [
#         generate_IP_addresses(ip_pool)[0] for _ in range(int(num / 2))
#     ]  # Half as many IPs as requests

#     # Generate sessions first
#     sessions = {}
#     for ip in ip_addresses:
#         session_id = str(uuid.uuid4())
#         start_time = generate_random_date()
#         sessions[session_id] = {
#             "ip": ip,
#             "start_time": start_time,
#             "referrer": np.random.choice(referrer_sites, p=referrer_sites_weights),
#             "page_count": random.choices(
#                 [1, 2, 3, 4, 5, 6, 7, 8],
#                 weights=[0.1, 0.2, 0.25, 0.2, 0.1, 0.08, 0.05, 0.02],
#             )[0],  # Weighted distribution of pages per session
#         }

#     # Now generate page views assigned to sessions
#     session_ids = list(sessions.keys())
#     session_weights = [
#         sessions[sid]["page_count"] for sid in session_ids
#     ]  # Weight by page count

#     generated = 0
#     while generated < num:
#         # Select a session weighted by its page count
#         # session_id = random.choices(session_ids, weights=session_weights)[0]
#         session_id = session_ids[
#             np.random.choice(
#                 len(session_ids), p=session_weights / np.sum(session_weights)
#             )
#         ]
#         session = sessions[session_id]

#         # If session has remaining page views
#         if session["page_count"] > 0:
#             # Generate timestamp within session duration (up to 30 minutes from start)
#             time_offset = random.randint(0, session_timeout * 60)  # seconds
#             timestamp = session["start_time"] + timedelta(seconds=time_offset)

#             ip_address = session["ip"]
#             country = generate_IP_addresses(ip_pool)[1]  # Get country for the IP

#             request_types, urls, url_weights = zip(*page_requests)
#             selected_index = np.random.choice(len(urls), p=url_weights)
#             request_type, url = request_types[selected_index], urls[selected_index]

#             if random.random() < 0.02:
#                 url = f"invalid_url_{random.randint(1000, 9999)}"

#             valid_statuses = status_codes.copy()
#             valid_weights = status_code_weights.copy()
#             product, price, agent = generate_sales_data(url)

#             if request_type != "POST":
#                 if 201 in valid_statuses:
#                     idx = valid_statuses.index(201)
#                     valid_statuses.pop(idx)
#                     valid_weights.pop(idx)
#                     total = sum(valid_weights)
#                     valid_weights = [w / total for w in valid_weights]

#             status_code = np.random.choice(valid_statuses, p=valid_weights)
#             referrer = session["referrer"]

#             if random.random() < 0.03:
#                 status_code = 999

#             response_time = generate_response_time()
#             if random.random() < 0.05:
#                 response_time = random.choice(
#                     [random.randint(10000, 50000), random.uniform(0.1, 5)]
#                 )

#             log_entry = [
#                 timestamp,
#                 ip_address,
#                 session_id,
#                 country,
#                 request_type,
#                 url,
#                 status_code,
#                 response_time,
#                 agent,
#                 referrer,
#                 product,
#                 price,
#             ]
#             logs.append(log_entry)

#             session["page_count"] -= 1
#             generated += 1
#             # Update weights
#             session_weights = [sessions[sid]["page_count"] for sid in session_ids]

#     df = pd.DataFrame(
#         logs,
#         columns=[
#             "Timestamp",
#             "IP Address",
#             "Session ID",
#             "Country",
#             "Method",
#             "URL",
#             "Status Code",
#             "Response Time (ms)",
#             "Sales Agent",
#             "Referrer",
#             "Product",
#             "Price",
#         ],
#     )

#     df["IP_Session"] = df["IP Address"] + "_" + df["Session ID"]

#     df.to_csv(file_name, index=False)
#     print(f"{num} server logs saved to {file_name}")
#     print(f"Total sessions generated: {len(sessions)}")
#     print(f"Average pages per session: {num / len(sessions):.2f}")


if __name__ == "__main__":
    print("Starting generation...")
    generate_web_logs(num=750000)
