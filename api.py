from fastapi import FastAPI, BackgroundTasks, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid
from fake_useragent import UserAgent
import re
import asyncio
import uvicorn
from typing import Optional, Dict, List
from pathlib import Path
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

fake = Faker()
ua = UserAgent()

# Configuration
CSV_FILE_PATH = "server_logs.csv"
LOG_GENERATION_INTERVAL = 1
BATCH_SIZE = 100000
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 5, 22)
Preprocessed_csv = "final_dataset.csv"

if not Path(CSV_FILE_PATH).exists():
    pd.DataFrame(
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
            "IP_Session",
        ]
    ).to_csv(CSV_FILE_PATH, index=False)


page_requests = [
    ("GET", "/index.html", 0.25),
    ("GET", "/images/events.jpg", 0.10),
    ("GET", "/event.html", 0.08),
    ("POST", "/product/ai-assistant/schedule-demo.php", 0.02),
    ("POST", "/product/email-automation-ai/schedule-demo.php", 0.01),
    ("POST", "/product/performance-analytics-tool/schedule-demo.php", 0.01),
    ("POST", "/request-.php", 0.02),
    ("POST", "/bug-tickets.php", 0.015),
    ("GET", "/checkout.php", 0.01),
    ("POST", "/buy-product.php", 0.02),
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
    ("POST", "/product/performance-analytics-tool/request.php", 0.004),
    ("POST", "/product/ai-assistant/request.php", 0.016),
    ("POST", "/product/email-automation-ai/request.php", 0.010),
    ("GET", "/pricing.html", 0.03),
    ("POST", "/request-quote.php", 0.02),
    ("GET", "/about-us.html", 0.02),
    ("GET", "/faq.html", 0.03),
    ("POST", "/newsletter-signup.php", 0.02),
    ("GET", "/special-offers.html", 0.008),
]


products = [
    ("AI Virtual Assistant", 599.99),
    ("Email Automation AI", 149.99),
    ("Performance Analytics Tool", 299.99),
]

sales_agents = ["Kago", "Lefika", "Mpho", "Thembi"]
referrer_sites = [
    "https://www.google.com",
    "https://www.bing.com",
    "https://www.facebook.com",
    "https://www.instagram.com",
    "https://www.linkedin.com",
    "https://www.tiktok.com",
    "https://www.pinterest.com",
]

status_codes = [200, 201, 302, 400, 401, 403, 404, 408, 429, 500, 503]
status_code_weights = [0.65, 0.10, 0.05, 0.02, 0.01, 0.01, 0.05, 0.05, 0.03, 0.01, 0.02]


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
        0.20,
        0.15,
        0.12,
        0.10,
        0.08,
        0.07,
        0.06,
        0.05,
        0.04,
        0.03,
        0.025,
        0.020,
        0.015,
        0.012,
        0.010,
        0.008,
        0.004,
        0.003,
        0.002,
        0.001,
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
    random_days = random.choices(
        population=range((end_date - start_date).days + 1),
        weights=[
            1.2 if (start_date + timedelta(days=i)).weekday() < 5 else 0.5
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


def generate_sales_data(url):
    sale_pattern = r"^/product/(performance-analytics-tool|ai-assistant|email-automation-ai)/request\.php$"
    demo_pattern = r"^/product/(performance-analytics-tool|ai-assistant|email-automation-ai)/schedule-demo\.php$"
    if not re.match(sale_pattern, url) and not (re.match(demo_pattern, url)):
        return ("_", 0, "_")
    if re.match(sale_pattern, url):
        print("generating sale")
        product, price = random.choice(products)
        agent = random.choice(sales_agents)
        return (
            product,
            round(price * random.uniform(0.9, 1.1), 2),
            agent,
        )  # Random price variation
    if re.match(demo_pattern, url):
        product, _ = random.choice(products)
        agent = random.choice(sales_agents)
        return (product, 0, agent)


class DataPreprocessor:
    @staticmethod
    def preprocess_logs(raw_logs: List[Dict]) -> pd.DataFrame:
        """Process raw logs through the full preprocessing pipeline"""
        df = pd.DataFrame(raw_logs)

        # 1. Initial NaN check and imputation
        def handle_nans(df):
            """Systematically handle NaN values while preserving intentional 'N/A' placeholders"""
            # Step 1: First convert true missing values (None/np.nan) to "N/A"
            df = df.fillna(
                {
                    "Product": "N/A",
                    "Sales Agent": "N/A",
                    "Price": 0,  # Or keep as "N/A" if you prefer
                }
            )

            # Step 2: Only handle remaining true numeric NaNs
            num_cols = df.select_dtypes(include=["number"]).columns
            for col in num_cols:
                if df[col].isna().any():
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)

            return df

        df = handle_nans(df)

        # 2. Handle response time outliers
        if "Response Time (ms)" in df.columns:
            df["Response Time (ms)"] = pd.to_numeric(
                df["Response Time (ms)"], errors="coerce"
            ).replace([np.inf, -np.inf], np.nan)

            if df["Response Time (ms)"].isna().any():
                median_rt = df["Response Time (ms)"].median()
                df["Response Time (ms)"] = df["Response Time (ms)"].fillna(median_rt)

                Q1 = df["Response Time (ms)"].quantile(0.25)
                Q3 = df["Response Time (ms)"].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                cap_value = df["Response Time (ms)"].quantile(0.95)

                df["Response Time (ms)"] = df["Response Time (ms)"].clip(
                    lower_bound, upper_bound
                )

        # 3. Extract temporal features
        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
            df["hour"] = df["Timestamp"].dt.hour
            df["day_of_week"] = df["Timestamp"].dt.day_of_week
            df["month"] = df["Timestamp"].dt.month
            df["year"] = df["Timestamp"].dt.year
            df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)

        # 4. Process referrers
        if "Referrer" in df.columns:
            df["Referrer"] = (
                df["Referrer"]
                .str.extract(r"https?://www\.([a-z]+)\.com", expand=False)
                .fillna("direct")
            )

        # 5. Categorize URLs
        def categorize_url(method, path):
            path = str(path).lower()
            if "/product/" in path:
                if "schedule-demo" in path:
                    return "Demo_Request"
                elif "request.php" in path:
                    return "Product_Purchase"
                elif "feedback.php" in path:
                    return "Product_Feedback"
                else:
                    return "Product_Info"
            elif any(p in path for p in ["/buy-", "/checkout", "/request-quote"]):
                return "Sales_Conversion"
            elif any(p in path for p in ["/promo-", "/special-offers", "/newsletter"]):
                return "Marketing_Content"
            elif any(p in path for p in ["/customer-support", "/faq", "/bug-tickets"]):
                return "Support"
            elif any(p in path for p in ["/about-us", "/contact-sales"]):
                return "Company_Info"
            elif any(
                ext in path for ext in [".jpg", ".png", ".css", ".js", "/images/"]
            ):
                return "Static_Asset"
            elif path in ["/", "/index.html", "/home"]:
                return "Homepage"
            return "Other"

        if "Method" in df.columns and "URL" in df.columns:
            df["Request Type"] = df.apply(
                lambda row: categorize_url(row["Method"], row["URL"]), axis=1
            )

        # 6. Analyze visitor types
        if "IP Address" in df.columns:
            ip_counts = df["IP Address"].value_counts()
            df["visit_count"] = df["IP Address"].map(ip_counts)
            df["visitor_type"] = df["visit_count"].apply(
                lambda x: "New" if x == 1 else "Returning"
            )

        # 7. Handle Price/Revenue
        if "Price" in df.columns:
            df["Revenue"] = pd.to_numeric(df["Price"], errors="coerce")
            if df["Revenue"].isna().any():
                df["Revenue"] = df["Revenue"].fillna(0)

        # Final NaN check
        nan_cols = df.columns[df.isna().any()].tolist()
        if nan_cols:
            logger.warning(f"Remaining NaN values in: {nan_cols}")
            df = df.fillna(0)  # Final fallback

        return df


async def generate_and_store_logs():
    """Generate a batch of logs and append to CSV"""
    logs = []
    ip_session_map = {}
    session_timeout = 30
    ip_pool = [fake.ipv4_public() for _ in range(326895)]

    current_time_window = generate_random_date()
    time_window_duration = 120
    time_window_end = current_time_window + timedelta(minutes=time_window_duration)
    session_referrers = {}

    for _ in range(BATCH_SIZE):
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
                session_referrers[session_id] = random.choice(referrer_sites)
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
        print(url)
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

    new_df = pd.DataFrame(
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

    # new_df.to_csv(CSV_FILE_PATH, mode="a", header=False, index=False)
    preprocessed_df = DataPreprocessor.preprocess_logs(new_df)
    preprocessed_df.to_csv(
        Preprocessed_csv,
        mode="a",
        header=not Path(Preprocessed_csv).exists(),
        index=False,
    )
    return preprocessed_df.to_dict(orient="records")


@app.get("/generate-logs")
async def generate_logs_endpoint(background_tasks: BackgroundTasks):
    """
    Endpoint to trigger log generation

    Args:
        background_tasks: FastAPI BackgroundTasks object

    Returns:
        dict: Status message with background task ID
    """
    try:
        # Generate a unique task ID for tracking
        task_id = str(uuid.uuid4())

        logger.info(f"Starting background log generation (Task ID: {task_id})")
        logger.debug("Adding generate_and_store_logs to background tasks")

        # Add task with additional logging context
        background_tasks.add_task(generate_and_store_logs_with_logging, task_id=task_id)

        logger.info(f"Background task started successfully (Task ID: {task_id})")

        return {
            "message": "Log generation started in background",
            "task_id": task_id,
            "status": "queued",
        }

    except Exception as e:
        logger.error(f"Failed to start log generation: {str(e)}", exc_info=True)
        return {
            "message": "Failed to start log generation",
            "error": str(e),
            "status": "error",
        }


async def generate_and_store_logs_with_logging(task_id: str = None):
    """
    Wrapper function for generate_and_store_logs with enhanced logging

    Args:
        task_id: Optional task identifier for logging
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Starting log generation task (Task ID: {task_id})")

        # Time the operation
        start_time = time.time()

        # Call the original function
        result = await generate_and_store_logs()

        duration = time.time() - start_time
        logger.info(
            f"Completed log generation (Task ID: {task_id}) in {duration:.2f} seconds. "
        )

        return result

    except Exception as e:
        logger.error(
            f"Error in log generation task (Task ID: {task_id}): {str(e)}",
            exc_info=True,
        )
        raise


@app.get("/data")
async def get_latest_logs(limit: int = 1000000, processed: bool = False):
    """Endpoint to retrieve latest logs (raw or processed)"""
    try:
        file_path = Preprocessed_csv
        df = pd.read_csv(file_path)
        df = df.fillna(
            {
                "Price": 0.0,
                "Response Time (ms)": 0.0,
            }
        )
        print(df.isna().sum())
        return df.tail(limit).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time streaming
@app.websocket("/ws-logs")
async def websocket_logs(websocket: WebSocket, processed: bool = False):
    await websocket.accept()
    try:
        while True:
            data = await generate_and_store_logs()
            if processed:
                await websocket.send_json(data["processed_logs"])
            await asyncio.sleep(LOG_GENERATION_INTERVAL)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
