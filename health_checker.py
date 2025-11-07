import requests
import ssl
import socket
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime


def check_website_health(url):
    results = {}
    parsed_url = urlparse(url)

    if not parsed_url.scheme:
        url = "https://" + url
        parsed_url = urlparse(url)

    # --- Check response time and status ---
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        end = time.time()
        results["status_code"] = response.status_code
        results["response_time_ms"] = round((end - start) * 1000, 2)
        results["is_online"] = response.status_code == 200
        results["page_size_kb"] = round(len(response.content) / 1024, 2)
    except requests.exceptions.RequestException as e:
        results["error"] = str(e)
        results["is_online"] = False
        return results

    # --- SSL Certificate Check ---
    if parsed_url.scheme == "https":
        try:
            hostname = parsed_url.hostname
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                s.settimeout(5.0)
                s.connect((hostname, 443))
                cert = s.getpeercert()
                exp_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (exp_date - datetime.utcnow()).days
                results["ssl_valid"] = True
                results["ssl_expires_in_days"] = days_left
        except Exception as e:
            results["ssl_valid"] = False
            results["ssl_error"] = str(e)

    # --- Metadata Extraction ---
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "N/A"
        desc = soup.find("meta", attrs={"name": "description"})
        desc_content = desc["content"] if desc else "N/A"
        results["page_title"] = title.strip()
        results["meta_description"] = desc_content.strip()
    except Exception:
        results["page_title"] = "N/A"
        results["meta_description"] = "N/A"

    return results
