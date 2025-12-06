"""
Market Data Models
Models for market data, price feeds, trading pairs, and market analysis
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..db.session import Base


class MarketData(Base):
    """OHLCV market data for trading pairs"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)  # e.g., "BTC/USD"
    timeframe = Column(String(10), nullable=False)  # e.g., "1m", "5m", "1h", "1d"
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # OHLCV data
    open = Column(Numeric(20, 8), nullable=False)
    high = Column(Numeric(20, 8), nullable=False)
    low = Column(Numeric(20, 8), nullable=False)
    close = Column(Numeric(20, 8), nullable=False)
    volume = Column(Numeric(20, 8), nullable=False)
    
    # Additional metrics
    trades_count = Column(Integer, default=0)
    vwap = Column(Numeric(20, 8))  # Volume Weighted Average Price
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_market_data_symbol_time', 'symbol', 'timestamp'),
        Index('idx_market_data_symbol_timeframe', 'symbol', 'timeframe'),
    )


class PriceFeed(Base):
    """Real-time price feeds for trading pairs"""
    __tablename__ = "price_feeds"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    
    # Current prices
    bid = Column(Numeric(20, 8), nullable=False)  # Best bid price
    ask = Column(Numeric(20, 8), nullable=False)  # Best ask price
    last = Column(Numeric(20, 8), nullable=False)  # Last trade price
    
    # Volume and changes
    volume_24h = Column(Numeric(20, 8), default=0)
    change_24h = Column(Numeric(10, 4), default=0)  # Percentage change
    change_24h_value = Column(Numeric(20, 8), default=0)  # Absolute change
    
    # High/Low
    high_24h = Column(Numeric(20, 8))
    low_24h = Column(Numeric(20, 8))
    
    # Spread
    spread = Column(Numeric(10, 8))
    spread_percentage = Column(Numeric(10, 4))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_tradable = Column(Boolean, default=True)
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class TradingPair(Base):
    """Trading pair configuration and information"""
    __tablename__ = "trading_pairs"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    
    # Base and quote currencies
    base_currency = Column(String(10), nullable=False)  # e.g., "BTC"
    quote_currency = Column(String(10), nullable=False)  # e.g., "USD"
    
    # Display info
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Trading configuration
    min_trade_size = Column(Numeric(20, 8), nullable=False)
    max_trade_size = Column(Numeric(20, 8))
    tick_size = Column(Numeric(20, 8), nullable=False)  # Minimum price increment
    lot_size = Column(Numeric(20, 8), nullable=False)  # Minimum quantity increment
    
    # Fees
    maker_fee = Column(Numeric(10, 6), default=0.001)  # 0.1%
    taker_fee = Column(Numeric(10, 6), default=0.002)  # 0.2%
    
    # Limits
    min_notional = Column(Numeric(20, 8))  # Minimum order value
    max_notional = Column(Numeric(20, 8))  # Maximum order value
    
    # Status
    is_active = Column(Boolean, default=True)
    is_spot = Column(Boolean, default=True)
    is_margin = Column(Boolean, default=False)
    is_futures = Column(Boolean, default=False)
    
    # Market info
    market_type = Column(String(20), default="spot")  # spot, margin, futures
    category = Column(String(50))  # crypto, forex, stocks, commodities
    
    # Timestamps
    listed_at = Column(DateTime)
    delisted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    indicators = relationship("MarketIndicator", back_populates="trading_pair")
    order_books = relationship("OrderBook", back_populates="trading_pair")


class MarketIndicator(Base):
    """Technical indicators for market analysis"""
    __tablename__ = "market_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)  # e.g., "1h", "4h", "1d"
    
    # Moving Averages
    sma_20 = Column(Numeric(20, 8))  # Simple Moving Average 20
    sma_50 = Column(Numeric(20, 8))
    sma_200 = Column(Numeric(20, 8))
    ema_12 = Column(Numeric(20, 8))  # Exponential Moving Average 12
    ema_26 = Column(Numeric(20, 8))
    
    # RSI (Relative Strength Index)
    rsi_14 = Column(Numeric(10, 4))
    
    # MACD (Moving Average Convergence Divergence)
    macd = Column(Numeric(20, 8))
    macd_signal = Column(Numeric(20, 8))
    macd_histogram = Column(Numeric(20, 8))
    
    # Bollinger Bands
    bb_upper = Column(Numeric(20, 8))
    bb_middle = Column(Numeric(20, 8))
    bb_lower = Column(Numeric(20, 8))
    
    # Volume indicators
    volume_sma_20 = Column(Numeric(20, 8))
    
    # Additional indicators
    atr_14 = Column(Numeric(20, 8))  # Average True Range
    stochastic_k = Column(Numeric(10, 4))
    stochastic_d = Column(Numeric(10, 4))
    
    # Timestamps
    calculated_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trading_pair = relationship("TradingPair", back_populates="indicators")
    
    # Indexes
    __table_args__ = (
        Index('idx_indicators_symbol_time', 'symbol', 'timeframe', 'calculated_at'),
    )


class MarketNews(Base):
    """Market news and events"""
    __tablename__ = "market_news"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # News info
    title = Column(String(500), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    source = Column(String(100))
    author = Column(String(200))
    url = Column(String(1000))
    
    # Categories and tags
    category = Column(String(50), index=True)  # general, crypto, forex, regulation, etc.
    tags = Column(Text)  # Comma-separated tags
    symbols = Column(Text)  # Related trading symbols
    
    # Sentiment
    sentiment_score = Column(Numeric(5, 4))  # -1 to 1
    sentiment_label = Column(String(20))  # negative, neutral, positive
    
    # Impact
    impact_level = Column(String(20))  # low, medium, high
    is_breaking = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    published_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_news_published', 'published_at'),
        Index('idx_news_category', 'category', 'published_at'),
    )


class MarketSentiment(Base):
    """Market sentiment analysis aggregated data"""
    __tablename__ = "market_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Sentiment scores
    overall_score = Column(Numeric(5, 4), nullable=False)  # -1 (very bearish) to 1 (very bullish)
    overall_label = Column(String(20))  # very_bearish, bearish, neutral, bullish, very_bullish
    
    # Sentiment breakdown
    news_sentiment = Column(Numeric(5, 4))
    social_sentiment = Column(Numeric(5, 4))
    technical_sentiment = Column(Numeric(5, 4))
    
    # Metrics
    bullish_percentage = Column(Numeric(5, 2))
    bearish_percentage = Column(Numeric(5, 2))
    neutral_percentage = Column(Numeric(5, 2))
    
    # Volume metrics
    sentiment_volume = Column(Integer, default=0)  # Number of data points used
    confidence_score = Column(Numeric(5, 4))  # Confidence in the sentiment
    
    # Fear & Greed Index
    fear_greed_index = Column(Integer)  # 0-100
    fear_greed_label = Column(String(20))  # extreme_fear, fear, neutral, greed, extreme_greed
    
    # Timestamps
    analyzed_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_sentiment_symbol_time', 'symbol', 'analyzed_at'),
    )


class OrderBook(Base):
    """Order book snapshot data"""
    __tablename__ = "order_books"
    
    id = Column(Integer, primary_key=True, index=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Best bid/ask
    best_bid = Column(Numeric(20, 8))
    best_ask = Column(Numeric(20, 8))
    spread = Column(Numeric(20, 8))
    
    # Depth metrics
    bid_depth_10 = Column(Numeric(20, 8))  # Total volume in top 10 bid levels
    ask_depth_10 = Column(Numeric(20, 8))  # Total volume in top 10 ask levels
    total_bid_volume = Column(Numeric(20, 8))
    total_ask_volume = Column(Numeric(20, 8))
    
    # Order book data (stored as JSON)
    bids = Column(Text)  # JSON array of [price, volume] pairs
    asks = Column(Text)  # JSON array of [price, volume] pairs
    
    # Market pressure
    buy_pressure = Column(Numeric(5, 4))  # 0 to 1
    sell_pressure = Column(Numeric(5, 4))  # 0 to 1
    imbalance_ratio = Column(Numeric(10, 4))  # bid_volume / ask_volume
    
    # Timestamp
    snapshot_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trading_pair = relationship("TradingPair", back_populates="order_books")
    
    # Indexes
    __table_args__ = (
        Index('idx_orderbook_symbol_time', 'symbol', 'snapshot_at'),
    )


class TradeHistory(Base):
    """Historical trade data (tape)"""
    __tablename__ = "trade_history"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Trade info
    trade_id = Column(String(100), unique=True, index=True)
    price = Column(Numeric(20, 8), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    notional = Column(Numeric(20, 8))  # price * quantity
    
    # Trade side
    side = Column(String(10), nullable=False)  # buy or sell
    is_buyer_maker = Column(Boolean)  # True if buyer is maker
    
    # Trade source
    source = Column(String(50))  # exchange, internal, aggregated
    exchange = Column(String(50))
    
    # Timestamps
    traded_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_trade_symbol_time', 'symbol', 'traded_at'),
        Index('idx_trade_id', 'trade_id'),
    )
