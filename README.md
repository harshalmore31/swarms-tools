# Swarms Tools

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)


Welcome to **Swarms Tools**, the ultimate package for integrating **cutting-edge APIs** into Python functions with seamless multi-agent system compatibility. Designed for enterprises at the forefront of innovation, **Swarms Tools** is your key to simplifying complexity and unlocking operational excellence.

---

## 🚀 Features

- **Unified API Integration**: Ready-to-use Python functions for financial data, social media, IoT, and more.
- **Enterprise-Grade Design**: Comprehensive type hints, structured outputs, and robust documentation.
- **Agent-Ready Framework**: Optimized for seamless integration into Swarms' multi-agent orchestration systems.
- **Expandable Architecture**: Easily extend functionality with a standardized schema for new tools.

---

## 🔧 Installation

```bash
pip3 install -U swarms-tools
```

---

## 📂 Directory Structure

```plaintext
swarms-tools/
├── swarms_tools/
│   ├── financial_data/
│   │   ├── htx_tool.py
│   │   ├── eodh_api.py
│   │   └── coingecko_tool.py
│   ├── social_media/
│   │   ├── telegram_tool.py
│   ├── utilities/
│   │   └── logging.py
├── tests/
│   ├── test_financial_data.py
│   └── test_social_media.py
└── README.md
```

---

## 💼 Use Cases

### Financial Data Retrieval
Enable precise and actionable financial insights:

#### Example 1: Fetch Historical Data
```python
from swarms_tools.financial_data.htx_tool import fetch_htx_data

# Fetch historical trading data for "Swarms Corporation"
response = fetch_htx_data("swarms")
print(response)
```

#### Example 2: Stock News Analysis
```python
from swarms_tools.financial_data.eodh_api import fetch_stock_news

# Retrieve latest stock news for Apple
news = fetch_stock_news("AAPL")
print(news)
```

#### Example 3: Cryptocurrency Metrics
```python
from swarms_tools.financial_data.coingecko_tool import coin_gecko_coin_api

# Fetch live data for Bitcoin
crypto_data = coin_gecko_coin_api("bitcoin")
print(crypto_data)
```

### Social Media Automation
Streamline communication and engagement:

#### Example: Telegram Bot Messaging
```python
from swarms_tools.social_media.telegram_tool import telegram_dm_or_tag_api

def send_alert(response: str):
    telegram_dm_or_tag_api(response)

# Send a message to a user or group
send_alert("Mission-critical update from Swarms.")
```

---

## 🧩 Standardized Schema

Every tool in **Swarms Tools** adheres to a strict schema for maintainability and interoperability:

### Schema Template

1. **Functionality**:
   - Encapsulate API logic into a modular, reusable function.

2. **Typing**:
   - Leverage Python type hints for input validation and clarity.

   Example:
   ```python
   def fetch_data(symbol: str, date_range: str) -> str:
       """
       Fetch financial data for a given symbol and date range.

       Args:
           symbol (str): Ticker symbol of the asset.
           date_range (str): Timeframe for the data (e.g., '1d', '1m', '1y').

       Returns:
           dict: A dictionary containing financial metrics.
       """
       pass
   ```

3. **Documentation**:
   - Include detailed docstrings with parameter explanations and usage examples.

4. **Output Standardization**:
   - Ensure consistent outputs (e.g., strings) for easy downstream agent integration.

5. **API-Key Management**:
    - All API keys must be fetched with `os.getenv("YOUR_KEY")`


---

## 📖 Documentation

Comprehensive documentation is available to guide developers and enterprises. Visit our [official docs](https://docs.swarms.world) for detailed API references, usage examples, and best practices.

---

## 🛠 Contributing

We welcome contributions from the global developer community. To contribute:

1. **Fork the Repository**: Start by forking the repository.
2. **Create a Feature Branch**: Use a descriptive branch name: `feature/add-new-tool`.
3. **Commit Your Changes**: Write meaningful commit messages.
4. **Submit a Pull Request**: Open a pull request for review.

---

## 🛡️ License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🌠 Join the Future

Explore the limitless possibilities of agent-based systems. Together, we can build a smarter, faster, and more interconnected world.

**Visit us:** [Swarms Corporation](https://swarms.ai)  
**Follow us:** [Twitter](https://twitter.com/swarms_corp)

---

**"The future belongs to those who dare to automate it."**  
**— The Swarms Corporation**

