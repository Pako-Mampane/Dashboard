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
from threading import Thread
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

fake = Faker()
ua = UserAgent()


class RealTimeDataGenerator:
    def __init__(self):
        # Initialize all the configuration from your original script
        np.random.seed(42)

        # Shared data structures
        self.ip_pool = [fake.ipv4_public() for _ in range(326895)]
        self.ip_session_map = {}
        self.session_referrers = {}
        self.session_timeout = 30  # minutes

        # Configuration from original script
        self.page_requests = [
            ("GET", "/index.html", 0.25),
            ("GET", "/images/events.jpg", 0.10),
            ("GET", "/event.html", 0.08),
            ("POST", "/product/performance-analytics-tool/schedule-demo.php", 0.04),
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

        self.products = [
            ("AI Virtual Assistant", 599.99),
            ("Email Automation AI", 149.99),
            ("Performance Analytics Tool", 299.99),
        ]

        self.sales_agents = ["Kago", "Lefika", "Mpho", "Thembi"]
        self.referrer_sites = [
            "https://www.google.com",
            "https://www.bing.com",
            "https://www.facebook.com",
            "https://www.instagram.com",
            "https://www.linkedin.com",
            "https://www.tiktok.com",
            "https://www.pinterest.com",
        ]

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

        # Data processing queue
        self.data_queue = Queue(maxsize=10000)
        self.running = False

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

        country = np.random.choice(countries, p=country_weights)
        ip = random.choice(self.ip_pool)
        if random.random() < 0.005:
            ip = f"invalid_url_{random.randint(1000, 9999)}"

        return ip, country

    def generate_random_date(self):
        """Generate a timestamp with peak/off hours weighting"""
        now = datetime.now()

        # Implement peak hours (8am-6pm weekdays)
        if now.weekday() < 5:  # Weekday
            if 8 <= now.hour <= 17:  # Peak hours
                # Add some randomness but keep in peak hours
                hour = now.hour + random.randint(-1, 1)
                hour = max(8, min(17, hour))
            else:  # Off hours
                hour = now.hour + random.randint(-2, 2)
                hour = max(0, min(23, hour))
        else:  # Weekend
            hour = now.hour + random.randint(-3, 3)
            hour = max(0, min(23, hour))

        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        return now.replace(hour=hour, minute=minute, second=second)

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

    def generate_log_entry(self):
        """Generate a single log entry with current timestamp"""
        timestamp = self.generate_random_date()
        ip_address, country = self.generate_IP_addresses()

        # Session management
        if ip_address in self.ip_session_map:
            last_timestamp, session_id = self.ip_session_map[ip_address]
            time_since_last = (timestamp - last_timestamp).total_seconds() / 60

            # New session if timeout exceeded or new day
            if (
                time_since_last > self.session_timeout
                or timestamp.date() != last_timestamp.date()
            ):
                session_id = str(uuid.uuid4())
                self.session_referrers[session_id] = random.choice(self.referrer_sites)
        else:
            session_id = str(uuid.uuid4())
            self.session_referrers[session_id] = random.choice(self.referrer_sites)

        self.ip_session_map[ip_address] = (timestamp, session_id)

        # Select request type and URL
        request_types, urls, url_weights = zip(*self.page_requests)
        selected_index = np.random.choice(len(urls), p=url_weights)
        request_type, url = request_types[selected_index], urls[selected_index]
        if random.random() < 0.02:
            url = f"invalid_url_{random.randint(1000, 9999)}"

        # Status code
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
        referrer = self.session_referrers[session_id]
        if random.random() < 0.03:
            status_code = 999

        # Response time
        response_time = self.generate_response_time()
        if random.random() < 0.05:
            response_time = random.choice(
                [random.randint(10000, 50000), random.uniform(0.1, 5)]
            )

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
        """Generate data at a controlled rate"""
        self.running = True
        try:
            while self.running:
                start_time = time.time()

                # Generate a batch of records
                for _ in range(records_per_second):
                    log_entry = self.generate_log_entry()
                    self.data_queue.put(log_entry)

                # Sleep to maintain rate
                elapsed = time.time() - start_time
                if elapsed < 1:
                    time.sleep(1 - elapsed)

        except Exception as e:
            logger.error(f"Error in data generator: {e}")
        finally:
            self.running = False

    def data_preprocessor(self):
        """Preprocess data before feeding to dataset"""
        while self.running or not self.data_queue.empty():
            try:
                # Get data from queue
                log_entry = self.data_queue.get(timeout=1)

                # Preprocessing steps
                processed_entry = self._preprocess_entry(log_entry)

                # Here you would feed to your dataset
                # For demo purposes, we'll just log it
                logger.debug(f"Processed entry: {processed_entry}")

                # Mark task as done
                self.data_queue.task_done()

            except Exception as e:
                logger.error(f"Error in preprocessor: {e}")

    def _preprocess_entry(self, entry):
        """Apply preprocessing to a single log entry"""
        processed = entry.copy()

        # 1. Clean IP addresses
        if processed["IP Address"].startswith("invalid_url"):
            processed["IP Address"] = "0.0.0.0"

        # 2. Categorize URLs
        url = processed["URL"]
        if url.startswith("/product/"):
            processed["URL Category"] = "Product"
        elif url.startswith("/images/"):
            processed["URL Category"] = "Image"
        elif "checkout" in url or "buy" in url:
            processed["URL Category"] = "Checkout"
        elif "contact" in url or "request" in url:
            processed["URL Category"] = "Lead Generation"
        else:
            processed["URL Category"] = "Other"

        # 3. Response time categories
        rt = processed["Response Time (ms)"]
        if rt < 100:
            processed["Response Category"] = "Fast"
        elif rt < 500:
            processed["Response Category"] = "Normal"
        elif rt < 2000:
            processed["Response Category"] = "Slow"
        else:
            processed["Response Category"] = "Very Slow"

        # 4. Status code categories
        status = processed["Status Code"]
        if status in [200, 201]:
            processed["Status Category"] = "Success"
        elif status in [302]:
            processed["Status Category"] = "Redirect"
        elif status in [400, 401, 403, 404]:
            processed["Status Category"] = "Client Error"
        elif status in [500, 503]:
            processed["Status Category"] = "Server Error"
        else:
            processed["Status Category"] = "Unknown"

        # 5. Add derived features
        processed["Is Conversion"] = 1 if processed["Product"] is not None else 0
        processed["Is Peak Hours"] = 1 if 8 <= processed["Timestamp"].hour <= 17 else 0

        return processed

    def start_pipeline(self, records_per_second=10):
        """Start the real-time data pipeline"""
        logger.info("Starting real-time data pipeline")

        # Start generator thread
        generator_thread = Thread(
            target=self.data_generator, args=(records_per_second,), daemon=True
        )
        generator_thread.start()

        # Start preprocessor threads (multiple for parallel processing)
        preprocessor_threads = []
        for i in range(4):  # 4 preprocessing threads
            thread = Thread(
                target=self.data_preprocessor, daemon=True, name=f"Preprocessor-{i}"
            )
            thread.start()
            preprocessor_threads.append(thread)

        # Return threads for monitoring
        return generator_thread, preprocessor_threads

    def stop_pipeline(self):
        """Stop the data pipeline"""
        logger.info("Stopping data pipeline")
        self.running = False
        self.data_queue.join()  # Wait for queue to empty


class DatasetFeeder:
    """Class to handle feeding processed data to a dataset"""

    def __init__(self):
        self.data_buffer = []
        self.buffer_size = 1000  # Number of records to buffer before saving
        self.last_save_time = time.time()
        self.save_interval = 60  # Seconds between saves

    def add_data(self, processed_entry):
        """Add processed data to the buffer"""
        self.data_buffer.append(processed_entry)

        # Check if we should save
        if (
            len(self.data_buffer) >= self.buffer_size
            or time.time() - self.last_save_time >= self.save_interval
        ):
            self.save_data()

    def save_data(self):
        """Save buffered data to persistent storage"""
        if not self.data_buffer:
            return

        try:
            # Convert to DataFrame
            df = pd.DataFrame(self.data_buffer)

            # Save to CSV (append if file exists)
            file_path = "realtime_server_logs.csv"
            header = not pd.io.common.file_exists(file_path)

            df.to_csv(file_path, mode="a", header=header, index=False)
            logger.info(f"Saved {len(df)} records to {file_path}")

            # Reset buffer and timer
            self.data_buffer = []
            self.last_save_time = time.time()

        except Exception as e:
            logger.error(f"Error saving data: {e}")


if __name__ == "__main__":
    # Initialize components
    generator = RealTimeDataGenerator()
    feeder = DatasetFeeder()

    # Modified preprocessor to feed data to dataset
    def data_preprocessor_with_feeding():
        while generator.running or not generator.data_queue.empty():
            try:
                log_entry = generator.data_queue.get(timeout=1)
                processed_entry = generator._preprocess_entry(log_entry)
                feeder.add_data(processed_entry)
                generator.data_queue.task_done()
            except Exception as e:
                logger.error(f"Error in preprocessor: {e}")

    # Start pipeline with feeding
    logger.info("Starting real-time data pipeline with dataset feeding")
    generator.running = True

    # Start generator thread
    generator_thread = Thread(
        target=generator.data_generator,
        args=(10,),  # 10 records per second
        daemon=True,
    )
    generator_thread.start()

    # Start preprocessor threads with feeding
    preprocessor_threads = []
    for i in range(4):
        thread = Thread(
            target=data_preprocessor_with_feeding, daemon=True, name=f"Preprocessor-{i}"
        )
        thread.start()
        preprocessor_threads.append(thread)

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down pipeline...")
        generator.stop_pipeline()
        # Ensure all data is saved before exiting
        if feeder.data_buffer:
            feeder.save_data()
        logger.info("Pipeline shutdown complete")
