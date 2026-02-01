# Self-Healing Stealth Module 🛡️

A powerful, modular system that automatically detects and bypasses bot detection mechanisms using realistic human-like profiles.

## Features ✨

- **🔍 Bot Detection**: Automatically detects CAPTCHAs, rate limits, IP blocks, and JavaScript challenges
- **🎭 Realistic Profiles**: Generates human-like browser fingerprints and behavior patterns
- **🔧 Self-Healing**: Automatically adapts and retries with different strategies when detected
- **📊 JSON Reports**: Creates detailed failure reports for analysis
- **🧠 Adaptive Learning**: Tracks strategy success rates and optimizes over time
- **🎯 Easy to Use**: Simple API with sensible defaults

## Quick Start 🚀

### Basic Usage

```python
from stealth_sys.self_healing import SelfHealer

# Initialize healer
healer = SelfHealer(max_retries=3)

# Check response for bot detection
success, profile, report = healer.check_and_heal(
    html_content=response_html,
    status_code=response.status_code,
    headers=response.headers
)

if success:
    print("✅ No detection or successfully bypassed!")
    # Use the profile for your next request
else:
    print("❌ Failed to bypass detection")
    # Check the report for details
```

### With Action Callback

```python
def my_scraping_action():
    # Your scraping logic here
    return scrape_website()

# Healer will automatically retry your action if detection occurs
success, profile, report = healer.check_and_heal(
    html_content=html,
    status_code=status,
    action_callback=my_scraping_action
)
```

## Components 🧩

### 1. **BotDetector**
Detects various bot detection mechanisms:
- CAPTCHA challenges (reCAPTCHA, hCaptcha, Cloudflare)
- Rate limiting (429 errors, retry-after headers)
- IP blocks (403 errors, access denied)
- JavaScript-based detection

### 2. **ProfileGenerator**
Creates realistic human-like profiles:
- Browser fingerprints (user agent, screen size, fonts, plugins)
- Behavior configurations (mouse speed, typing patterns, scroll behavior)
- Multiple profile types: `random`, `conservative`, `aggressive`

### 3. **SelfHealer**
Automatically heals from detection:
- Tries multiple strategies in order of priority
- Generates detailed JSON failure reports
- Tracks success rates and adapts
- Supports custom retry logic

## Healing Strategies 🔧

The module uses these strategies (in order of priority):

1. **Add Delays** - Slow down to appear more human
2. **Change Behavior Profile** - Switch to different interaction patterns
3. **Change Fingerprint** - Generate new browser fingerprint
4. **Rotate Profile** - Switch to best-performing profile
5. **Reset Session** - Start fresh with new profile

## Profile Types 🎭

### Random (Balanced)
- Mouse DPI: 800-1600
- Typing: 50-70 WPM
- Best for general use

### Conservative
- Mouse DPI: 400-800
- Typing: 30-50 WPM
- Best for strict detection

### Aggressive
- Mouse DPI: 1600-3200
- Typing: 70-100 WPM
- Best for speed-focused tasks

## JSON Reports 📄

When detection occurs, detailed reports are saved:

```json
{
  "report_id": "uuid",
  "timestamp": "2026-02-01T18:00:00",
  "detection_result": {
    "detected": true,
    "detection_type": "captcha",
    "confidence": 0.95,
    "indicators": ["CAPTCHA pattern found: recaptcha"]
  },
  "profile_used": {
    "profile_id": "uuid",
    "fingerprint": {...},
    "behavior_config": {...}
  },
  "strategies_attempted": [...],
  "final_outcome": "success",
  "error_messages": []
}
```

## Examples 📚

Run the examples:

```bash
python self_healing_examples.py
```

This demonstrates:
- ✅ Bot detection
- ✅ Profile generation
- ✅ Self-healing in action
- ✅ Complete workflows
- ✅ JSON report viewing

## Integration 🔌

### With Playwright/Selenium

```python
from stealth_sys.self_healing import SelfHealer

healer = SelfHealer()

# Get profile
profile = healer.get_current_profile()

# Apply to browser
page.set_extra_http_headers({
    'User-Agent': profile.fingerprint['user_agent']
})

# After each request, check for detection
success, new_profile, report = healer.check_and_heal(
    html_content=page.content(),
    url=page.url
)

if not success:
    # Apply new profile and retry
    page.set_extra_http_headers({
        'User-Agent': new_profile.fingerprint['user_agent']
    })
```

### With Requests/HTTPX

```python
import requests
from stealth_sys.self_healing import SelfHealer

healer = SelfHealer()
profile = healer.get_current_profile()

response = requests.get(
    url,
    headers={'User-Agent': profile.fingerprint['user_agent']}
)

success, profile, report = healer.check_and_heal(
    html_content=response.text,
    status_code=response.status_code,
    headers=dict(response.headers)
)
```

## Statistics 📊

Track healing performance:

```python
stats = healer.get_statistics()
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Total detections: {stats['total_detections']}")
```

## Directory Structure 📁

```
self-healing/
├── __init__.py           # Module exports
├── models.py             # Data models
├── detector.py           # Bot detection logic
├── profile_generator.py  # Profile generation
└── healer.py            # Self-healing engine
```

## Tips 💡

1. **Start Conservative**: Use conservative profiles for strict sites
2. **Monitor Reports**: Check JSON reports to understand detection patterns
3. **Adjust Retries**: Increase `max_retries` for difficult sites
4. **Clean Profiles**: Periodically remove failed profiles with `remove_failed_profiles()`
5. **Combine with Human Behavior**: Use with the `human-behavior` module for best results

## Advanced Usage 🎓

### Custom Strategy Priority

```python
healer = SelfHealer()

# Reorder strategies
healer.strategies.sort(key=lambda s: custom_priority(s))
```

### Profile Management

```python
generator = ProfileGenerator()

# Generate multiple profiles
profiles = [generator.generate_profile() for _ in range(10)]

# Get best performing
best = generator.get_best_profile()

# Clean up failed profiles
generator.remove_failed_profiles(threshold=0.3)
```

## License

MIT License - Use freely in your projects!

---

**Made with ❤️ for stealthy automation**
