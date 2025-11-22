from fake_useragent import UserAgent
import random

ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "fr-FR,fr;q=0.9"
]

ACCEPT = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
]

REFERERS = [
    "https://www.youtube.com/",
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/"
]

SEC_FETCH_DEST = ["document", "empty"]
SEC_FETCH_MODE = ["navigate", "no-cors"]
SEC_FETCH_SITE = ["none", "same-origin", "cross-site"]

def get_realistic_headers() -> dict:
    """
    Creates realistic headers for mimic browser behavior which reduces the changes of getting banned immediatly.\n
    Uses `fake_useragent` package for creating random user agents.
    """
    ua = UserAgent(platforms='desktop', os='Windows')
    user_agent = ua.random
    return {
        "User-Agent": user_agent,
        "Accept": random.choice(ACCEPT),
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Referer": random.choice(REFERERS),
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Accept-Encoding": "gzip, deflate",

        # Optional but can help mimic modern Chrome/Firefox more
        "Sec-Fetch-Dest": random.choice(SEC_FETCH_DEST),
        "Sec-Fetch-Mode": random.choice(SEC_FETCH_MODE),
        "Sec-Fetch-Site": random.choice(SEC_FETCH_SITE),
        "Sec-CH-UA-Platform": "\"Windows\"",
        "Sec-CH-UA": f"\"{random.choice(['Chromium', 'Google Chrome', 'Not.A/Brand'])}\";v=\"{random.randint(100, 135)}\"",
    }
