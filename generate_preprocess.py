import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid
from fake_useragent import UserAgent
import re
import time
from queue import Queue
import queue
from threading import Thread
import logging
from collections import defaultdict
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
fake = Faker()
ua = UserAgent()


class DataGenerator:
    def __init__(self):
        np.random.seed(42)
        self.data_queue = Queue(maxsize=10000)
        self.running = False

        self.ip_pool = [fake.ipv4() for _ in range(326895)]
        self.ip_session_map = {}
        self.session_referrers = {}
        self.session_timeout = 30
        self.start_date = datetime(2024, 1, 1)
        self.end_date = datetime(2025, 2, 27)

        self.page_requests = [
            ("GET", "/index.html", 0.25),
            ("GET", "/images/events.jpg", 0.10),
            ("GET", "/event.html", 0.08),
            ("POST", "/product/ai-assistant/schedule-demo.php", 0.03),
            ("POST", "/product/email-automation-ai/schedule-demo.php", 0.017),
            ("POST", "/product/performance-analytics-tool/schedule-demo.php", 0.013),
            ("POST", "/bug-tickets.php", 0.015),
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
            ("POST", "/request-quote.php", 0.03),
            ("GET", "/about-us.html", 0.02),
            ("GET", "/faq.html", 0.03),
            ("POST", "/newsletter-signup.php", 0.02),
            ("GET", "/special-offers.html", 0.008),
        ]

        self.products = [
            ("AI Virtual Assistant", 599.99),
            ("Email Automation AI", 149.99),
            ("Performance Analytics Tool", 299.99),
        ]

        self.sales_agents = ["Kago", "Lefika", "Mpho", "Thembi"]
        self.sales_agent_weights = [0.4, 0.3, 0.2, 0.1]
        self.referrer_sites = [
            "https://www.google.com",
            "https://www.bing.com",
            "https://www.facebook.com",
            "https://www.instagram.com",
            "https://www.linkedin.com",
            "https://www.tiktok.com",
            "https://www.pinterest.com",
        ]
        self.referrer_weights = [
            0.4,
            0.2,
            0.15,
            0.13,
            0.02,
            0.08,
            0.02,
        ]

        self.month_weights = {
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
        self.status_codes = [200, 201, 302, 400, 401, 403, 404, 408, 429, 500, 503]
        self.status_code_weights = [
            0.65,
            0.10,
            0.05,
            0.02,
            0.01,
            0.01,
            0.05,
            0.05,
            0.03,
            0.01,
            0.02,
        ]
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

        self.invalid_status_codes = [999, 000]

    def generate_IP_addresses(self):
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
        if self.ip_pool is None:
            self.ip_pool = [fake.ipv4() for _ in range(326895)]
        ip = random.choice(self.ip_pool)
        country = np.random.choice(countries, p=country_weights)
        if random.random() < 0.005:
            ip = f"invalid_url_{random.randint(1000, 9999)}"

        return ip, country

    def generate_random_date(self):
        random_days = random.choices(
            population=range((self.end_date - self.start_date).days + 1),
            weights=[
                (1.2 if (self.start_date + timedelta(days=i)).weekday() < 5 else 0.5)
                * self.month_weights[(self.start_date + timedelta(days=i)).month]
                for i in range((self.end_date - self.start_date).days + 1)
            ],
            k=1,
        )[0]
        random_date = self.start_date + timedelta(days=random_days)
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

    def generate_response_time(self):
        rt = max(50, np.random.normal(300, 100))
        if random.random() < 0.05:
            if random.random() < 0.3:
                return random.randint(500, 20000)
            else:
                return round(random.uniform(1, 50), 2)
        return round(rt, 2)

    def generate_sales_data(self, url):
        pattern = r"^/product/(performance-analytics-tool|ai-assistant|email-automation-ai)/request\.php$"
        if re.match(pattern, url):
            product, price = random.choice(self.products)
            agent = random.choice(self.sales_agents)
            return (
                product,
                round(price * random.uniform(0.9, 1.1), 2),
                agent,
            )
        return None, None, None

    def generate_web_logs(self):
        current_time_window = self.generate_random_date()
        time_window_duration = 120
        time_window_end = current_time_window + timedelta(minutes=time_window_duration)
        session_referrers = {}

        # Create timestamp within current time window (95% chance) or new window (5%)
        if random.random() < 0.05:  # 5% chance to start new time window
            current_time_window = self.generate_random_date()
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

        ip_address, country = self.generate_IP_addresses()

        # Session management with constraints
        if ip_address in self.ip_session_map:
            last_timestamp, session_id = self.ip_session_map[ip_address]
            time_since_last = (timestamp - last_timestamp).total_seconds() / 60

            # Force new session if timeout exceeded or crossed to new day
            if (
                time_since_last > self.session_timeout
                or timestamp.date() != last_timestamp.date()
            ):
                session_id = str(uuid.uuid4())
                session_referrers[session_id] = random.choice(self.referrer_sites)
        else:
            session_id = str(uuid.uuid4())
            session_referrers[session_id] = random.choice(self.referrer_sites)

        self.ip_session_map[ip_address] = (timestamp, session_id)

        request_types, urls, url_weights = zip(*self.page_requests)
        selected_index = np.random.choice(len(urls), p=url_weights)
        request_type, url = request_types[selected_index], urls[selected_index]

        valid_statuses = self.status_codes.copy()
        valid_weights = self.status_code_weights.copy()
        product, price, agent = self.generate_sales_data(url)

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
        response_time = self.generate_response_time()
        if random.random() < 0.05:
            response_time = random.choice(
                [random.randint(10000, 50000), random.uniform(0.1, 5)]
            )

        # Generate logs
        return {
            "Timestamp": timestamp,
            "IP Address": ip_address,
            "Session ID": session_id,
            "Country": country,
            "Method": request_type,
            "URL": url,
            "Status Code": status_code,
            "Response Time (ms)": response_time,
            "Sales Agent": agent,
            "Referrer": referrer,
            "Product": product,
            "Price": price,
        }

    def data_generator(self, records_per_second=10):
        self.running = True
        try:
            while self.running:
                start_time = time.time()

                for _ in range(records_per_second):
                    log_entry = self.generate_web_logs()
                    self.data_queue.put(log_entry)

                elapsed_time = time.time() - start_time
                if elapsed_time < 1:
                    time.sleep(1 - elapsed_time)
        except Exception as e:
            logger.error(f"Error in data generation: {e}")
        finally:
            self.running = False
            logger.info("Data generation stopped.")

    def _preprocessed_entry(self, entry):
        processed = entry.copy()

        # break down timestamp into components
        try:
            timestamp = pd.to_datetime(processed["Timestamp"])
        except Exception as e:
            logger.error(
                f"Error parsing timestamp: {processed['Timestamp']}", exc_info=True
            )
            raise e
        processed["Hour"] = timestamp.hour
        processed["Weekday"] = timestamp.day_of_week
        processed["Month"] = timestamp.month
        processed["Year"] = timestamp.year
        processed["Is Weekend"] = 1 if timestamp.weekday() >= 5 else 0
        processed["Timestamp"] = pd.to_datetime(processed["Timestamp"])
        processed["Price"] = pd.to_numeric(
            processed["Price"], errors="coerce", downcast="float"
        )
        processed["Response Time (ms)"] = pd.to_numeric(
            processed["Response Time (ms)"], errors="coerce", downcast="float"
        )
        processed["Hour"] = pd.to_numeric(
            processed["Hour"], errors="coerce", downcast="float"
        )
        processed["Month"] = pd.to_numeric(
            processed["Month"], errors="coerce", downcast="float"
        )
        processed["Year"] = pd.to_numeric(
            processed["Year"], errors="coerce", downcast="float"
        )
        return processed

    def data_preprocessor(self):
        while self.running or not self.data_queue.empty():
            try:
                logger.debug("Preprocessing Entry")
                log_entry = self.data_queue.get(timeout=1)
                if log_entry is None:
                    break
                if not log_entry or "Timestamp" not in log_entry:
                    logger.error(f"Invalid log entry: {log_entry}")
                    continue
                logger.debug(f"logged entry: {log_entry}")
                preprocessed_entry = self._preprocessed_entry(log_entry)

                logger.debug(f"Preprocessed Entry: {preprocessed_entry}")
                self.data_queue.task_done()

            except Exception as e:
                logger.error(f"Error in data preprocessing: {e}", exc_info=True)

    def start_pipeline(self, records_per_second=10):
        logger.info("Starting data generation and preprocessing pipeline.")

        generator_thread = Thread(
            target=self.data_generator, args=(records_per_second,), daemon=True
        )
        generator_thread.start()

        preprocessor_threads = []
        for i in range(4):
            thread = Thread(
                target=self.data_preprocessor, daemon=True, name=f"Preprocessor-{i}"
            )
            thread.start()
            preprocessor_threads.append(thread)

        return generator_thread, preprocessor_threads

    def stop_pipeline(self):
        logger.info("Stopping data pipeline.")
        self.running = False
        self.data_queue.join()
        logger.info("Data pipeline stopped.")


class DataFeeder:
    def __init__(self):
        self.data_buffer = []
        self.buffer_size = 1000
        self.last_save_time = time.time()
        self.save_interval = 60
        self.dtypes = {
            "Timestamp": "datetime64[ns]",
            "IP Address": "string",
            "Session ID": "string",
            "Country": "string",
            "Method": "category",
            "URL": "string",
            "Status Code": "int16",
            "Response Time (ms)": "float32",
            "Sales Agent": "string",
            "Referrer": "string",
            "Product": "string",
            "Price": "float32",
            "Hour": "int8",
            "Weekday": "int8",
            "Month": "int8",
            "Year": "int16",
            "Is Weekend": "bool",
        }

    def save_data(self):
        if not self.data_buffer:
            return
        try:
            df = pd.DataFrame(self.data_buffer)
            for col, dtype in self.dtypes.items():
                if col in df.columns:
                    try:
                        if dtype == "datetime64[ns]":
                            df[col] = pd.to_datetime(df[col], errors="coerce")
                        elif dtype == "bool":
                            df[col] = df[col].astype(bool)
                        elif "int" in dtype:
                            df[col] = pd.to_numeric(
                                df[col], errors="coerce", downcast="integer"
                            )
                        elif "float" in dtype:
                            df[col] = pd.to_numeric(
                                df[col], errors="coerce", downcast="float"
                            )
                        elif dtype == "category":
                            df[col] = df[col].astype("category")
                        elif dtype == "string":
                            df[col] = df[col].astype("string")
                    except Exception as e:
                        logger.error(f"Error converting {col} to {dtype}: {e}")
                        continue

            file_path = "data/realtime_server_logs.csv"

            df.to_csv(file_path, mode="a", index=False)
            logger.info(f"Saved {len(df)} records to {file_path}.")

            self.data_buffer = []
            self.last_save_time = time.time()

        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def add_data(self, processed_entry):
        self.data_buffer.append(processed_entry)

        if (
            len(self.data_buffer) >= self.buffer_size
            or time.time() - self.last_save_time >= self.save_interval
        ):
            self.save_data()


if __name__ == "__main__":
    generator = DataGenerator()
    feeder = DataFeeder()

    def data_preprocessor_with_feeding():
        while generator.running or not generator.data_queue.empty():
            try:
                log_entry = generator.data_queue.get(timeout=1)
                if log_entry:
                    preprocessed_entry = generator._preprocessed_entry(log_entry)
                    feeder.add_data(preprocessed_entry)
                else:
                    logger.warning("Received None from data queue.")

                preprocessed_entry = generator._preprocessed_entry(log_entry)
                feeder.add_data(preprocessed_entry)
                generator.data_queue.task_done()

            except queue.Empty:
                logger.debug("Data queue is empty, waiting for new data.")
                pass

            except Exception as e:
                logger.error(f"Error in data preprocessing: {e}", exc_info=True)

    logger.info("Starting data pipeline with feeding.")
    generator.running = True

    generator_thread = Thread(
        target=generator.data_generator,
        args=(10,),
        daemon=True,
    )
    generator_thread.start()

    preprocessor_threads = []
    for i in range(4):
        thread = Thread(
            target=data_preprocessor_with_feeding,
            daemon=True,
            name=f"Preprocessor-{i}",
        )
        thread.start()
        preprocessor_threads.append(thread)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping data pipeline.")
        generator.stop_pipeline()
        if feeder.data_buffer:
            feeder.save_data()
        logger.info("Data pipeline stopped.")
        os._exit(0)
