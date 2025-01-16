from typing import List, Dict, Any, Optional
from swarms_tools.utils.formatted_string import (
    format_object_to_string,
)

try:
    import yfinance as yf
except ImportError:
    import subprocess

    subprocess.check_call(
        ["python", "-m", "pip", "install", "yfinance"]
    )
    import yfinance as yf

from loguru import logger


class YahooFinanceAPI:
    """
    A production-grade tool for fetching stock data from Yahoo Finance.
    """

    @staticmethod
    @logger.catch
    def fetch_stock_data(
        stock_symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch all possible data about one or more stocks from Yahoo Finance.

        Args:
            stock_symbols (Optional[List[str]]): A list of stock symbols (e.g., ['AAPL', 'GOOG']).
                                                 If None, raises a ValueError as stocks must be specified.

        Returns:
            Dict[str, Any]: A dictionary containing the formatted stock data.

        Raises:
            ValueError: If no stock symbols are provided or the data for the symbols cannot be retrieved.
            Exception: For any other unforeseen issues.
        """
        if not stock_symbols:
            raise ValueError(
                "No stock symbols provided. Please specify at least one stock symbol."
            )

        logger.info(f"Fetching data for stocks: {stock_symbols}")

        stock_data = {}
        for symbol in stock_symbols:
            try:
                logger.debug(
                    f"Fetching data for stock symbol: {symbol}"
                )
                stock_info = YahooFinanceAPI._get_stock_info(symbol)
                stock_data[symbol] = stock_info
                logger.info(f"Data fetched successfully for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                stock_data[symbol] = {"error": str(e)}

        return stock_data

    @staticmethod
    def _get_stock_info(symbol: str) -> Dict[str, Any]:
        """
        Fetch and format stock data for a single stock symbol.

        Args:
            symbol (str): The stock symbol to fetch data for.

        Returns:
            Dict[str, Any]: A formatted dictionary containing stock data.

        Raises:
            ValueError: If the stock symbol is invalid or data is not found.
        """
        try:
            stock = yf.Ticker(symbol)
            stock_info = stock.info

            # if not stock_info or "regularMarketPrice" not in stock_info:
            #     raise ValueError(
            #         f"Invalid stock symbol or no data available for: {symbol}"
            #     )

            # Format the stock data into a structured dictionary
            formatted_data = {
                "symbol": stock_info.get("symbol", symbol),
                "name": stock_info.get("shortName", "N/A"),
                "sector": stock_info.get("sector", "N/A"),
                "industry": stock_info.get("industry", "N/A"),
                "current_price": stock_info.get(
                    "regularMarketPrice", "N/A"
                ),
                "previous_close": stock_info.get(
                    "regularMarketPreviousClose", "N/A"
                ),
                "open_price": stock_info.get(
                    "regularMarketOpen", "N/A"
                ),
                "day_high": stock_info.get(
                    "regularMarketDayHigh", "N/A"
                ),
                "day_low": stock_info.get(
                    "regularMarketDayLow", "N/A"
                ),
                "volume": stock_info.get(
                    "regularMarketVolume", "N/A"
                ),
                "market_cap": stock_info.get("marketCap", "N/A"),
                "52_week_high": stock_info.get(
                    "fiftyTwoWeekHigh", "N/A"
                ),
                "52_week_low": stock_info.get(
                    "fiftyTwoWeekLow", "N/A"
                ),
                "dividend_yield": stock_info.get(
                    "dividendYield", "N/A"
                ),
                "description": stock_info.get(
                    "longBusinessSummary", "N/A"
                ),
            }

            # print(formatted_data)

            return formatted_data
        except Exception as error:
            logger.error(error)


def yahoo_finance_api(
    stock_symbols: Optional[List[str]] = None,
) -> str:
    """
    Fetch and display data for one or more stocks using Yahoo Finance.

    Args:
        stock_symbols (Optional[List[str]]): A list of stock symbols to fetch data for.

    Returns:
        Dict[str, Any]: A dictionary containing the fetched stock data.
    """
    try:
        stock_data = YahooFinanceAPI.fetch_stock_data(stock_symbols)
        return format_object_to_string(stock_data)
    except ValueError as ve:
        logger.error(f"ValueError occurred: {ve}")
        return f"error: {str(ve)}"
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        return f"error: {str(e)}"


# if __name__ == "__main__":
#     # Set up logging
#     logger.add(
#         "yahoo_finance_api.log", rotation="500 MB", level="INFO"
#     )

#     # Example usage
#     single_stock = yahoo_finance_api(
#         ["AAPL"]
#     )  # Fetch data for a single stock
#     print("Single Stock Data:", single_stock)

#     # multiple_stocks = yahoo_finance_api(
#     #     ["AAPL", "GOOG", "MSFT"]
#     # )  # Fetch data for multiple stocks
#     # print("Multiple Stocks Data:", multiple_stocks)
