"""
Trading module endpoints - DB-based
Implements complete trading functionality with database integration
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ...schemas.trading import (
    PlaceOrderRequest, OrderResponse, OrdersListResponse, CancelOrderRequest, CancelOrderResponse,
    PositionResponse, PositionsListResponse, ClosePositionRequest, ClosePositionResponse,
    MarketPrice, MarketPricesResponse, OrderBookResponse, TradeHistoryResponse
)
from ...dependencies import get_current_user, get_trading_service, get_financial_service
from ...db.session import get_db
from ...models.user import User
from ...models.trading import TradingOrder, PortfolioPosition
from ...models.financial import WalletBalance
from ...models.audit import AuditLog
from ...services.trading_service import TradingService
from ...services.financial_service import FinancialService

router = APIRouter(tags=["trading"])


# ========== HELPER FUNCTIONS ==========

def format_order_response(order: TradingOrder) -> Dict[str, Any]:
    """Format TradingOrder to response format"""
    return {
        "id": str(order.id),
        "user_id": str(order.user_id),
        "symbol": order.symbol,
        "side": order.side,
        "type": order.order_type,
        "quantity": float(order.quantity),
        "price": float(order.price) if order.price else None,
        "stop_price": float(order.stop_price) if order.stop_price else None,
        "leverage": 1,  # Default, can be added to model
        "status": order.status,
        "executed_quantity": float(order.filled_quantity or 0),
        "executed_price": float(order.filled_price) if order.filled_price else 0,
        "filled_amount": float((order.filled_quantity or 0) * (order.filled_price or order.price or 0)),
        "fee": float(order.commission or 0),
        "filled_time": order.filled_at.isoformat() if order.filled_at else None,
        "create_time": order.created_at.isoformat(),
        "update_time": order.updated_at.isoformat(),
        "is_maker": False
    }


def format_position_response(position: PortfolioPosition, current_price: Optional[float] = None) -> Dict[str, Any]:
    """Format PortfolioPosition to response format"""
    # Calculate unrealized PnL if current_price provided
    unrealized_pnl = 0
    if current_price and not position.is_closed:
        if position.position_type == "long":
            unrealized_pnl = float((Decimal(str(current_price)) - position.average_price) * position.quantity)
        else:  # short
            unrealized_pnl = float((position.average_price - Decimal(str(current_price))) * position.quantity)
    
    return {
        "id": str(position.id),
        "user_id": str(position.user_id),
        "symbol": position.symbol,
        "side": position.position_type,
        "quantity": float(position.quantity),
        "entry_price": float(position.average_price),
        "current_price": current_price,
        "unrealized_pnl": unrealized_pnl,
        "realized_pnl": float(position.realized_pnl or 0),
        "leverage": float(position.leverage or 1),
        "margin": float(position.margin_used or 0),
        "status": "closed" if position.is_closed else "open",
        "create_time": position.entry_time.isoformat() if position.entry_time else position.created_at.isoformat(),
        "close_time": position.closed_at.isoformat() if position.closed_at else None,
        "exit_price": float(position.closed_price) if position.closed_price else None
    }


def log_audit(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    result: str = "success"
):
    """Log audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            category="trading"
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Audit logging error: {e}")


def get_market_price(symbol: str, db: Session) -> float:
    """Get current market price - fetch from exchange API or WebSocket"""
    # TODO: Integrate with real market data source
    base_prices = {
        'BTCUSDT': 45000.0,
        'ETHUSDT': 2500.0,
        'BNBUSDT': 300.0,
        'ADAUSDT': 0.5,
        'DOTUSDT': 6.0,
    }
    return base_prices.get(symbol, 100.0)


# ========== ORDER ENDPOINTS ==========

@router.post("/orders", response_model=OrderResponse)
async def place_order(
    request: Request,
    order_data: PlaceOrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trading_service: TradingService = Depends(get_trading_service),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Place new trading order - DB-based"""
    
    try:
        # Check account status
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản không hoạt động"
            )
        
        if user.kyc_status != "verified":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vui lòng xác minh KYC trước khi giao dịch"
            )
        
        # Validate balance
        quote_currency = "USDT"  # Default quote currency
        if "USDT" in order_data.symbol:
            quote_currency = "USDT"
        
        # Get user balance
        balance = db.query(WalletBalance).filter(
            and_(
                WalletBalance.user_id == user.id,
                WalletBalance.asset == quote_currency
            )
        ).first()
        
        if not balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không tìm thấy số dư {quote_currency}"
            )
        
        # Calculate required balance
        order_price = order_data.price or get_market_price(order_data.symbol, db)
        required_balance = Decimal(str(order_data.quantity)) * Decimal(str(order_price))
        
        if balance.available_balance < required_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số dư {quote_currency} không đủ để thực hiện giao dịch"
            )
        
        # Lock balance
        balance.locked_balance += required_balance
        balance.available_balance -= required_balance
        db.commit()
        
        # Create order
        order = trading_service.create_order(
            user_id=user.id,
            symbol=order_data.symbol,
            side=order_data.side.value,
            order_type=order_data.type.value,
            quantity=Decimal(str(order_data.quantity)),
            price=Decimal(str(order_price)) if order_data.price else None,
            stop_price=Decimal(str(order_data.stop_price)) if order_data.stop_price else None
        )
        
        # For market orders, simulate immediate execution
        if order_data.type.value == 'market':
            current_price = get_market_price(order_data.symbol, db)
            order = trading_service.update_order_status(
                order.id,
                "filled",
                filled_quantity=Decimal(str(order_data.quantity)),
                filled_price=Decimal(str(current_price))
            )
            
            # Calculate fee (0.1%)
            fee = required_balance * Decimal("0.001")
            order.commission = fee
            db.commit()
            
            # Unlock balance and deduct fee
            balance.locked_balance -= required_balance
            balance.available_balance -= fee
            db.commit()
            
            # Create position for filled buy orders
            if order_data.side.value == "buy":
                trading_service.create_or_update_position(
                    user_id=user.id,
                    symbol=order_data.symbol,
                    quantity=Decimal(str(order_data.quantity)),
                    price=Decimal(str(current_price)),
                    position_type="long"
                )
        
        # Log audit
        log_audit(
            db, user.id, "place_order", "trading_order",
            resource_id=str(order.id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return OrderResponse(**format_order_response(order))
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Place order error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đặt lệnh"
        )


@router.get("/orders", response_model=OrdersListResponse)
async def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    symbol: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    side: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get user's orders with pagination and filters - DB-based"""
    
    try:
        # Get orders from DB
        orders = trading_service.get_user_orders(
            user_id=user.id,
            status=status,
            symbol=symbol,
            limit=limit * 10  # Get more for filtering
        )
        
        # Filter by side if provided
        if side:
            orders = [o for o in orders if o.side == side]
        
        # Sort by created_at desc
        orders.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total_count = len(orders)
        offset = (page - 1) * limit
        paginated_orders = orders[offset:offset + limit]
        
        # Format response
        orders_response = [OrderResponse(**format_order_response(order)) for order in paginated_orders]
        
        return OrdersListResponse(
            orders=orders_response,
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            },
            total_count=total_count
        )
        
    except Exception as e:
        print(f"Get orders error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách lệnh"
        )


@router.get("/orders/history", response_model=OrdersListResponse)
async def get_orders_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    symbol: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get completed/cancelled orders history - DB-based"""
    
    try:
        # Get completed/cancelled orders
        orders = db.query(TradingOrder).filter(
            and_(
                TradingOrder.user_id == user.id,
                TradingOrder.status.in_(["filled", "cancelled", "rejected"])
            )
        )
        
        if symbol:
            orders = orders.filter(TradingOrder.symbol == symbol)
        
        orders = orders.order_by(TradingOrder.created_at.desc()).all()
        
        # Pagination
        total_count = len(orders)
        offset = (page - 1) * limit
        paginated_orders = orders[offset:offset + limit]
        
        # Format response
        orders_response = [OrderResponse(**format_order_response(order)) for order in paginated_orders]
        
        return OrdersListResponse(
            orders=orders_response,
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            },
            total_count=total_count
        )
        
    except Exception as e:
        print(f"Get orders history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy lịch sử lệnh"
        )


@router.put("/orders/{order_id}/cancel", response_model=CancelOrderResponse)
@router.delete("/orders/{order_id}", response_model=CancelOrderResponse)
async def cancel_order(
    request: Request,
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Cancel a pending order - DB-based"""
    
    try:
        # Cancel order
        order = trading_service.cancel_order(order_id, user.id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy lệnh hoặc lệnh không thể hủy"
            )
        
        # Unlock balance
        quote_currency = "USDT"
        balance = db.query(WalletBalance).filter(
            and_(
                WalletBalance.user_id == user.id,
                WalletBalance.asset == quote_currency
            )
        ).first()
        
        if balance and order.price:
            locked_amount = order.quantity * order.price
            balance.locked_balance -= locked_amount
            balance.available_balance += locked_amount
            db.commit()
        
        # Log audit
        log_audit(
            db, user.id, "cancel_order", "trading_order",
            resource_id=str(order_id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return CancelOrderResponse(
            order_id=str(order.id),
            status=order.status,
            cancelled_time=order.cancelled_at or datetime.utcnow(),
            message="Hủy lệnh thành công"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Cancel order error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể hủy lệnh"
        )


# ========== POSITION ENDPOINTS ==========

@router.get("/positions", response_model=PositionsListResponse)
async def get_positions(
    symbol: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get user's current positions - DB-based"""
    
    try:
        # Get open positions
        positions = trading_service.get_user_positions(
            user_id=user.id,
            is_closed=False,
            symbol=symbol
        )
        
        # Calculate PnL for each position
        positions_with_pnl = []
        total_unrealized_pnl = 0
        
        for position in positions:
            current_price = get_market_price(position.symbol, db)
            pos_data = format_position_response(position, current_price)
            positions_with_pnl.append(pos_data)
            total_unrealized_pnl += pos_data["unrealized_pnl"]
        
        return PositionsListResponse(
            positions=[PositionResponse(**pos) for pos in positions_with_pnl],
            summary={
                "total_positions": len(positions_with_pnl),
                "total_unrealized_pnl": round(total_unrealized_pnl, 2)
            }
        )
        
    except Exception as e:
        print(f"Get positions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách vị thế"
        )


@router.post("/positions/{position_id}/close", response_model=ClosePositionResponse)
@router.delete("/positions/{position_id}", response_model=ClosePositionResponse)
async def close_position(
    request: Request,
    position_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Close a position - DB-based"""
    
    try:
        # Get position
        position = trading_service.get_position(position_id)
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy vị thế"
            )
        
        if position.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền đóng vị thế này"
            )
        
        if position.is_closed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vị thế đã được đóng"
            )
        
        # Get current market price
        current_price = get_market_price(position.symbol, db)
        
        # Calculate realized PnL
        if position.position_type == "long":
            realized_pnl = (Decimal(str(current_price)) - position.average_price) * position.quantity
        else:  # short
            realized_pnl = (position.average_price - Decimal(str(current_price))) * position.quantity
        
        # Update position
        position.is_closed = True
        position.closed_at = datetime.utcnow()
        position.closed_price = Decimal(str(current_price))
        position.realized_pnl = (position.realized_pnl or 0) + realized_pnl
        position.closed_reason = "user_close"
        
        # Update balance (add realized PnL)
        quote_currency = "USDT"
        balance = db.query(WalletBalance).filter(
            and_(
                WalletBalance.user_id == user.id,
                WalletBalance.asset == quote_currency
            )
        ).first()
        
        if balance:
            balance.available_balance += realized_pnl
            db.commit()
        
        db.commit()
        db.refresh(position)
        
        # Log audit
        log_audit(
            db, user.id, "close_position", "portfolio_position",
            resource_id=str(position_id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return ClosePositionResponse(
            position_id=str(position.id),
            exit_price=current_price,
            realized_pnl=float(realized_pnl),
            realized_pnl_percent=float((realized_pnl / (position.average_price * position.quantity)) * 100),
            close_time=position.closed_at,
            message="Đóng vị thế thành công"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Close position error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đóng vị thế"
        )


# ========== STATISTICS ENDPOINTS ==========

@router.get("/statistics")
async def get_statistics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trading statistics - DB-based"""
    
    try:
        # Aggregate from DB
        total_orders = db.query(func.count(TradingOrder.id)).filter(
            TradingOrder.user_id == user.id
        ).scalar() or 0
        
        filled_orders = db.query(func.count(TradingOrder.id)).filter(
            and_(
                TradingOrder.user_id == user.id,
                TradingOrder.status == "filled"
            )
        ).scalar() or 0
        
        total_volume = db.query(func.sum(TradingOrder.quantity * TradingOrder.filled_price)).filter(
            and_(
                TradingOrder.user_id == user.id,
                TradingOrder.status == "filled"
            )
        ).scalar() or 0
        
        total_positions = db.query(func.count(PortfolioPosition.id)).filter(
            PortfolioPosition.user_id == user.id
        ).scalar() or 0
        
        total_pnl = db.query(func.sum(PortfolioPosition.realized_pnl)).filter(
            PortfolioPosition.user_id == user.id
        ).scalar() or 0
        
        return {
            "total_orders": total_orders,
            "filled_orders": filled_orders,
            "total_volume": float(total_volume or 0),
            "total_positions": total_positions,
            "total_pnl": float(total_pnl or 0),
            "win_rate": 0.0  # Can be calculated from positions
        }
        
    except Exception as e:
        print(f"Get statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thống kê"
        )


@router.get("/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Trading pair symbol"),
    limit: int = Query(20, ge=1, le=100)
):
    """Get orderbook - fetch from market data service"""
    # In production, fetch from exchange API
    return {
        "symbol": symbol,
        "bids": [],  # TODO: Fetch from market data service
        "asks": [],  # TODO: Fetch from market data service
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/trades")
async def get_trades(
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent trades - DB-based"""
    
    try:
        query = db.query(TradingOrder).filter(
            and_(
                TradingOrder.user_id == user.id,
                TradingOrder.status == "filled"
            )
        )
        
        if symbol:
            query = query.filter(TradingOrder.symbol == symbol)
        
        orders = query.order_by(TradingOrder.filled_at.desc()).limit(limit).all()
        
        trades = []
        for order in orders:
            trades.append({
                "id": str(order.id),
                "symbol": order.symbol,
                "side": order.side,
                "quantity": float(order.filled_quantity or 0),
                "price": float(order.filled_price or 0),
                "time": order.filled_at.isoformat() if order.filled_at else order.created_at.isoformat()
            })
        
        return {"trades": trades}
        
    except Exception as e:
        print(f"Get trades error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy lịch sử giao dịch"
        )


@router.get("/pairs")
async def get_pairs():
    """Get available trading pairs - Config-based"""
    return {
        "pairs": [
            {"symbol": "BTCUSDT", "base": "BTC", "quote": "USDT"},
            {"symbol": "ETHUSDT", "base": "ETH", "quote": "USDT"},
            {"symbol": "BNBUSDT", "base": "BNB", "quote": "USDT"},
        ]
    }


@router.get("/rules")
async def get_rules():
    """Get trading rules - Config-based"""
    return {
        "min_order_amount": 10.0,
        "max_order_amount": 1000000.0,
        "max_leverage": 100,
        "trading_fee": 0.001,  # 0.1%
        "maker_fee": 0.0005,  # 0.05%
        "taker_fee": 0.001  # 0.1%
    }


@router.get("/risk-assessment")
async def get_risk_assessment(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk assessment - Calculate from positions"""
    
    try:
        positions = db.query(PortfolioPosition).filter(
            and_(
                PortfolioPosition.user_id == user.id,
                PortfolioPosition.is_closed == False
            )
        ).all()
        
        total_exposure = sum(float(pos.quantity * pos.average_price) for pos in positions)
        total_margin = sum(float(pos.margin_used or 0) for pos in positions)
        
        # Get balance
        balance = db.query(WalletBalance).filter(
            and_(
                WalletBalance.user_id == user.id,
                WalletBalance.asset == "USDT"
            )
        ).first()
        
        available_balance = float(balance.available_balance) if balance else 0
        
        # Calculate risk metrics
        margin_ratio = (total_margin / available_balance * 100) if available_balance > 0 else 0
        exposure_ratio = (total_exposure / available_balance * 100) if available_balance > 0 else 0
        
        risk_level = "low"
        if margin_ratio > 80 or exposure_ratio > 200:
            risk_level = "high"
        elif margin_ratio > 50 or exposure_ratio > 100:
            risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "total_exposure": total_exposure,
            "total_margin": total_margin,
            "available_balance": available_balance,
            "margin_ratio": round(margin_ratio, 2),
            "exposure_ratio": round(exposure_ratio, 2),
            "open_positions": len(positions)
        }
        
    except Exception as e:
        print(f"Get risk assessment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đánh giá rủi ro"
        )

