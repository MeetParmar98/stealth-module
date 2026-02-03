# 🕵️ Stealth Scraper Framework

> **Agentic, self-healing web scraping with advanced stealth capabilities**

A production-ready Python framework combining async scraping, browser fingerprinting evasion, human behavior simulation, and LLM-powered self-healing.

---

## 🚀 Features

### Core Capabilities
- ⚡ **Async-first architecture** - High-performance concurrent scraping with `httpx` + `asyncio`
- 🎭 **Advanced stealth** - Browser fingerprinting, human behavior simulation, self-healing evasion
- 🤖 **Agentic behavior** - LLM-powered decision making and automatic failure recovery
- 🔄 **Self-healing** - Automatically adapts to site changes and anti-bot measures
- 🌐 **Universal** - Works with static HTML and JavaScript-rendered sites

### Stealth System
- **Browser Fingerprinting** - Realistic user agents, screen sizes, fonts, WebGL, canvas
- **Human Behavior** - Natural mouse movements, typing patterns, scroll behavior
- **Cognitive States** - Fatigue simulation, attention modeling, realistic timing
- **Hardware Simulation** - CPU throttling, memory constraints, network jitter

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stealth-scraper.git
cd stealth-scraper

# Install dependencies
pip install -r requirements.txt

# Optional: Install Playwright for browser automation
playwright install chromium
```

---

## 🎯 Quick Start

### Basic Async Scraping with Stealth

```python
import asyncio
from core.scraper import StealthScraper

async def main():
    scraper = StealthScraper()
    
    # Single URL
    result = await scraper.get("https://example.com")
    print(result.text)
    
    # Multiple URLs concurrently
    urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
    results = await scraper.get_many(urls)
    
    await scraper.close()

asyncio.run(main())
```

### Agentic Self-Healing Scraper

```python
from core.agent_scraper import AgentScraper

async def main():
    scraper = AgentScraper(llm_provider="openai")  # or "anthropic"
    
    # Automatically heals when selectors break
    result = await scraper.scrape(
        url="https://example.com",
        extract={
            "title": "h1.title",
            "price": ".product-price",
            "description": "#description"
        }
    )
    
    print(result)

asyncio.run(main())
```

### Browser Automation with Stealth

```python
from core.browser import StealthBrowser

async def main():
    async with StealthBrowser() as browser:
        page = await browser.new_page()
        
        # Automatically applies stealth fingerprinting
        await page.goto("https://example.com")
        
        # Human-like interactions
        await page.human_type("#search", "query text")
        await page.human_click("button[type=submit]")
        
        content = await page.content()
        print(content)

asyncio.run(main())
```

---

## 🏗️ Architecture

```
stealth-module/
├── core/                      # Core scraping engine
│   ├── scraper.py            # Async HTTP scraper with stealth
│   ├── browser.py            # Playwright wrapper with stealth
│   ├── agent_scraper.py      # LLM-powered agentic scraper
│   └── session.py            # Session management & pooling
│
├── stealth-sys/              # Stealth evasion system
│   ├── browser-fingerprinting/
│   │   ├── user_agents.py
│   │   ├── screen_sizes.py
│   │   ├── fonts.py
│   │   └── webgl_canvas.py
│   ├── human-behavior/
│   │   ├── brain.py          # Cognitive simulation
│   │   ├── motion_engine.py  # Mouse movement
│   │   └── behavioral_models.py
│   └── self_healing/
│       └── evasion_tactics.py
│
├── extractors/               # Data extraction utilities
│   ├── html_parser.py
│   ├── json_extractor.py
│   └── schema_validator.py
│
├── storage/                  # Data persistence
│   ├── database.py
│   ├── cache.py
│   └── export.py
│
├── examples/                 # Usage examples
│   ├── basic_scraping.py
│   ├── agentic_healing.py
│   ├── browser_automation.py
│   └── distributed_scraping.py
│
└── tests/                    # Test suite
    ├── test_scraper.py
    ├── test_stealth.py
    └── test_agent.py
```

---

## 🧠 How It Works

### 1. Stealth Layer
Every request automatically includes:
- Realistic browser fingerprints (user agent, screen size, fonts, WebGL)
- Human-like headers and TLS fingerprints
- Natural timing variations and jitter

### 2. Async Engine
- Concurrent requests with `asyncio` and `httpx`
- Connection pooling and session management
- Automatic retries with exponential backoff

### 3. Agentic Self-Healing
When a scraper fails:
1. **Detect** - Identifies the failure (selector not found, CAPTCHA, etc.)
2. **Analyze** - LLM examines the HTML and error context
3. **Adapt** - Generates new selectors or strategies
4. **Retry** - Attempts scraping with the fix
5. **Learn** - Stores successful adaptations

---

## ⚙️ Configuration

```python
# config.py
SCRAPER_CONFIG = {
    "max_concurrent": 100,
    "timeout": 30,
    "retry_attempts": 3,
    "stealth_level": "high",  # low, medium, high, paranoid
}

AGENT_CONFIG = {
    "llm_provider": "openai",  # or "anthropic"
    "model": "gpt-4",
    "max_healing_attempts": 3,
    "enable_learning": True,
}

STEALTH_CONFIG = {
    "fingerprint_rotation": True,
    "human_behavior": True,
    "cognitive_simulation": True,
}
```

---

## 🎓 Advanced Usage

### Custom Stealth Profiles

```python
from stealth_sys import StealthProfile

profile = StealthProfile(
    browser="chrome",
    os="windows",
    screen_size=(1920, 1080),
    timezone="America/New_York",
)

scraper = StealthScraper(profile=profile)
```

### Distributed Scraping

```python
from core.distributed import DistributedScraper

scraper = DistributedScraper(
    redis_url="redis://localhost:6379",
    workers=10,
)

await scraper.enqueue_urls(urls)
await scraper.start()
```

---

## 🔬 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=agent --cov=stealth-sys

# Run specific test
pytest tests/test_agent.py -v
```

---

## 📊 Performance

- **HTTP Scraping**: 10,000+ requests/sec (async)
- **Browser Automation**: 50+ concurrent browser instances
- **Self-Healing**: <2s average recovery time
- **Memory**: ~50MB per scraper instance

---

## 🛡️ Ethics & Legal

This framework is designed for:
- ✅ Research and education
- ✅ Testing your own applications
- ✅ Legitimate data collection with permission

**NOT for:**
- ❌ Bypassing authentication or paywalls
- ❌ Violating Terms of Service
- ❌ Malicious activities

Always respect `robots.txt` and rate limits.

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Built with:
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Playwright](https://playwright.dev/) - Browser automation
- [OpenAI](https://openai.com/) / [Anthropic](https://anthropic.com/) - LLM APIs

---

**Made with 🔥 for the scraping community**
