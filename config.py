"""
Configuration management for Autonomous Market Strategy Development System.
Centralizes environment variables, constants, and configuration validation.
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AssetClass(Enum):
    """Supported asset classes for the trading system."""
    CRYPTO = "crypto"
    EQUITIES = "equities"
    FOREX = "forex"
    COMMODITIES = "commodities"

class DataSource(Enum):
    """Supported data sources."""
    CCXT = "ccxt"
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    POLYGON = "polygon"

@dataclass
class DatabaseConfig:
    """Firebase database configuration."""
    project_id: str
    credentials_path: str = "credentials/firebase_credentials.json"
    
    @property
    def firestore_collections(self) -> Dict[str, str]:
        return {
            "market_data": "market_data",
            "strategies": "trading_strategies",
            "backtests": "strategy_backtests",
            "live_trades": "live_trades",
            "system_state": "system_state"
        }

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/autonomous_trader.log"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class DataIngestionConfig:
    """Data ingestion configuration."""
    default_timeframe: str = "1h"
    batch_size: int = 1000
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    max_data_age_hours: int = 24

@dataclass
class TradingConfig:
    """Trading execution configuration."""
    default_exchange: str = "binance"
    paper_trading: bool = True
    max_position_size_percent: float = 2.0
    max_daily_loss_percent: float = 5.0
    slippage_percent: float = 0.1

class Config:
    """Main configuration class."""
    
    def __init__(self):
        # Core settings
        self.env = os.getenv("ENVIRONMENT", "development")
        self.system_id = os.getenv("SYSTEM_ID", "autonomous_trader_v1")
        
        # Database
        self.database = DatabaseConfig(
            project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
            credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH", "credentials/firebase_credentials.json")
        )
        
        # Logging
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE_PATH", "logs/autonomous_trader.log")
        )
        
        # Data ingestion
        self.data_ingestion = DataIngestionConfig()
        
        # Trading
        self.trading = TradingConfig(
            paper_trading=os.getenv("PAPER_TRADING", "true").lower() == "true"
        )
        
        # External APIs
        self.api_keys = {
            "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY"),
            "polygon": os.getenv("POLYGON_API_KEY"),
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID")
        }
        
        # Validation
        self._validate()
    
    def _validate(self) -> None:
        """Validate configuration and set up logging."""
        # Ensure required directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("credentials", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Check Firebase credentials
        if not os.path.exists(self.database.credentials_path):
            logging.warning(f"Firebase credentials not found at {self.database.credentials_path}")
        
        # Validate environment
        if self.env not in ["development", "staging", "production"]:
            raise ValueError(f"Invalid environment: {self.env}")
    
    @property
    def is_production(self) -> bool:
        return self.env == "production"
    
    @property
    def is_development(self) -> bool:
        return self.env == "development"

# Global config instance
config = Config()