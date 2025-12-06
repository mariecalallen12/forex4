"""
Financial Endpoints - DB-based
Bao gồm: deposits, withdrawals với đầy đủ validation logic và DB integration
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import secrets
try:
    import qrcode
    import io
    import base64
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Import schemas
from ...schemas.financial import (
    CreateDepositRequest,
    DepositRecord,
    Invoice,
    DepositResponse,
    DepositsListResponse,
    CreateWithdrawalRequest,
    WithdrawalRecord,
    WithdrawalLimits,
    WithdrawalResponse,
    WithdrawalsListResponse,
    FinancialErrorResponse,
    FinancialValidationErrorResponse
)

# Import dependencies
from ...dependencies import get_current_user, get_financial_service
from ...db.session import get_db
from ...models.user import User
from ...models.financial import Transaction, WalletBalance
from ...models.audit import AuditLog
from ...services.financial_service import FinancialService
from ...middleware.auth import get_client_ip

router = APIRouter(tags=["financial"])


# ========== HELPER FUNCTIONS ==========

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
            category="financial"
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Audit logging error: {e}")


def generate_deposit_address(asset: str, user_id: int) -> str:
    """Generate deposit address - integrate with crypto service"""
    # In production, integrate with crypto wallet service
    if asset.upper() == "BTC":
        return f"bc1q{secrets.token_hex(16)}"
    elif asset.upper() == "ETH":
        return f"0x{secrets.token_hex(20)}"
    elif asset.upper() == "USDT":
        return f"0x{secrets.token_hex(20)}"  # ERC20
    return f"address_{secrets.token_hex(16)}"


def generate_qr_code(data: str) -> str:
    """Generate QR code base64 string"""
    if not QRCODE_AVAILABLE:
        # Return placeholder if qrcode not available
        return ""
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


# ========== DEPOSIT ENDPOINTS ==========

@router.post(
    "/deposits",
    response_model=DepositResponse,
    responses={
        201: {"model": DepositResponse, "description": "Tạo deposit request thành công"},
        400: {"model": FinancialValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": FinancialErrorResponse, "description": "Không tìm thấy token xác thực"},
        403: {"model": FinancialErrorResponse, "description": "Tài khoản không hoạt động"}
    }
)
async def create_deposit(
    request: Request,
    deposit_data: CreateDepositRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Tạo yêu cầu nạp tiền - DB-based"""
    
    try:
        # Check account status
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản không hoạt động"
            )
        
        client_ip = get_client_ip(request)
        asset = deposit_data.currency.value.upper()
        amount = Decimal(str(deposit_data.amount))
        
        # Validate minimum deposit
        min_deposit = Decimal("10.0")  # Can be configurable
        if amount < min_deposit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số tiền nạp tối thiểu là {min_deposit} {asset}"
            )
        
        # Handle different deposit methods
        if deposit_data.method.value == "crypto_deposit":
            # Crypto deposit
            deposit_address = generate_deposit_address(asset, user.id)
            
            # Create transaction
            transaction = financial_service.create_transaction(
                user_id=user.id,
                transaction_type="deposit",
                category="crypto_deposit",
                asset=asset,
                amount=amount,
                fee=Decimal("0"),  # No fee for crypto deposits
                description=f"Crypto deposit {amount} {asset}",
                metadata={
                    "method": "crypto",
                    "wallet_address": deposit_address,
                    "network": "mainnet"  # Can be configurable
                }
            )
            
            # Log audit
            log_audit(
                db, user.id, "create_deposit", "transaction",
                resource_id=str(transaction.id),
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent")
            )
            
            return DepositResponse(
                success=True,
                message="Tạo yêu cầu nạp tiền thành công",
                data={
                    "deposit": {
                        "id": str(transaction.id),
                        "amount": float(amount),
                        "currency": asset.lower(),
                        "method": "crypto_deposit",
                        "status": "pending",
                        "wallet_address": deposit_address,
                        "network": "mainnet",
                        "min_confirmations": 3
                    },
                    "qr_code": generate_qr_code(deposit_address),
                    "warnings": {
                        "network": "Chỉ gửi {asset} trên mạng chính (Mainnet)",
                        "minimum": f"Số tiền nạp tối thiểu: {min_deposit} {asset}",
                        "fee": "Không có phí nạp tiền"
                    }
                }
            )
        
        elif deposit_data.method.value == "bank_transfer":
            # VietQR deposit
            if not user.customer_payment_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Không tìm thấy customer_payment_id"
                )
            
            # Create transaction
            transaction = financial_service.create_transaction(
                user_id=user.id,
                transaction_type="deposit",
                category="vietqr",
                asset=asset,
                amount=amount,
                fee=Decimal("0"),
                description=f"VietQR deposit {amount} {asset}",
                metadata={
                    "method": "vietqr",
                    "customer_payment_id": user.customer_payment_id,
                    "bank_account": deposit_data.bankAccount.dict() if deposit_data.bankAccount else None
                }
            )
            
            # Generate QR code data
            qr_data = f"{user.customer_payment_id}|{amount}|{asset}"
            qr_code = generate_qr_code(qr_data)
            
            # Log audit
            log_audit(
                db, user.id, "create_deposit", "transaction",
                resource_id=str(transaction.id),
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent")
            )
            
            return DepositResponse(
                success=True,
                message="Tạo yêu cầu nạp tiền thành công",
                data={
                    "deposit": {
                        "id": str(transaction.id),
                        "amount": float(amount),
                        "currency": asset.lower(),
                        "method": "bank_transfer",
                        "status": "pending",
                        "customer_payment_id": user.customer_payment_id,
                        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
                    },
                    "qr_code": qr_code,
                    "warnings": {
                        "expiry": "QR code có hiệu lực trong 24 giờ",
                        "minimum": f"Số tiền nạp tối thiểu: {min_deposit} {asset}",
                        "fee": "Không có phí nạp tiền"
                    }
                }
            )
        
        elif deposit_data.method.value == "card":
            # Online payment - Coming soon
            return DepositResponse(
                success=True,
                message="Thanh toán online đang được phát triển",
                data={
                    "deposit": {
                        "id": None,
                        "status": "coming_soon"
                    },
                    "message": "Tính năng thanh toán online sẽ sớm được ra mắt"
                }
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phương thức thanh toán không hợp lệ"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create deposit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo yêu cầu nạp tiền"
        )


@router.get(
    "/deposits",
    response_model=DepositsListResponse,
    responses={
        200: {"model": DepositsListResponse, "description": "Lấy danh sách deposits thành công"},
        401: {"model": FinancialErrorResponse, "description": "Không tìm thấy token xác thực"}
    }
)
async def get_deposits(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Lấy danh sách deposits - DB-based"""
    
    try:
        # Get transactions from DB
        query = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == "deposit"
            )
        )
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if currency:
            query = query.filter(Transaction.asset == currency.upper())
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        # Format response
        deposits_data = []
        for tx in transactions:
            deposits_data.append({
                "id": str(tx.id),
                "userId": str(tx.user_id),
                "userEmail": user.email,
                "amount": float(tx.amount),
                "currency": tx.asset.lower(),
                "method": tx.category or "unknown",
                "status": tx.status,
                "fees": float(tx.fee or 0),
                "netAmount": float(tx.net_amount),
                "walletAddress": tx.to_address,
                "transactionId": tx.transaction_hash,
                "createdAt": tx.created_at.isoformat(),
                "updatedAt": tx.updated_at.isoformat(),
                "processedAt": tx.completed_at.isoformat() if tx.completed_at else None
            })
        
        return DepositsListResponse(
            success=True,
            data={
                "deposits": deposits_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        )
        
    except Exception as e:
        print(f"Get deposits error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách nạp tiền"
        )


# ========== WITHDRAWAL ENDPOINTS ==========

@router.post(
    "/withdrawals",
    response_model=WithdrawalResponse,
    responses={
        201: {"model": WithdrawalResponse, "description": "Tạo withdrawal request thành công"},
        400: {"model": FinancialValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": FinancialErrorResponse, "description": "Không tìm thấy token xác thực"},
        403: {"model": FinancialErrorResponse, "description": "Cần xác minh KYC hoặc tài khoản không hoạt động"}
    }
)
async def create_withdrawal(
    request: Request,
    withdrawal_data: CreateWithdrawalRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Tạo yêu cầu rút tiền - DB-based"""
    
    try:
        # Check account status
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản không hoạt động"
            )
        
        # Check KYC status
        if user.kyc_status != "verified":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vui lòng xác minh KYC trước khi rút tiền"
            )
        
        client_ip = get_client_ip(request)
        asset = withdrawal_data.currency.value.upper()
        amount = Decimal(str(withdrawal_data.amount))
        
        # Get balance
        balance = financial_service.get_balance(user.id, asset)
        if not balance or balance.available_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số dư {asset} không đủ để rút tiền"
            )
        
        # Calculate fee (2% for withdrawals)
        fee_rate = Decimal("0.02")
        fee = amount * fee_rate
        required_amount = amount + fee
        
        if balance.available_balance < required_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số dư {asset} không đủ (cần {required_amount} bao gồm phí {fee})"
            )
        
        # Check withdrawal limits
        withdrawal_limits = WithdrawalLimits(daily=10000, monthly=100000)
        
        # Get withdrawals for current period
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        monthly_total = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed",
                Transaction.asset == asset,
                Transaction.completed_at >= start_of_month
            )
        ).scalar() or Decimal("0")
        
        daily_total = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed",
                Transaction.asset == asset,
                Transaction.completed_at >= start_of_day
            )
        ).scalar() or Decimal("0")
        
        if monthly_total + amount > Decimal(str(withdrawal_limits.monthly)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vượt quá hạn mức rút tiền hàng tháng"
            )
        
        if daily_total + amount > Decimal(str(withdrawal_limits.daily)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vượt quá hạn mức rút tiền hàng ngày"
            )
        
        # Lock balance
        if not financial_service.lock_balance(user.id, asset, required_amount):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể khóa số dư"
            )
        
        # Create transaction
        transaction = financial_service.create_transaction(
            user_id=user.id,
            transaction_type="withdrawal",
            category=withdrawal_data.method.value,
            asset=asset,
            amount=amount,
            fee=fee,
            description=f"Withdrawal {amount} {asset}",
            metadata={
                "method": withdrawal_data.method.value,
                "bank_account": withdrawal_data.bankAccount.dict() if withdrawal_data.bankAccount else None,
                "wallet_address": withdrawal_data.walletAddress
            }
        )
        
        # Log audit
        log_audit(
            db, user.id, "create_withdrawal", "transaction",
            resource_id=str(transaction.id),
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent")
        )
        
        return WithdrawalResponse(
            success=True,
            message="Tạo yêu cầu rút tiền thành công. Đang chờ phê duyệt từ quản trị viên.",
            data={
                "withdrawal": {
                    "id": str(transaction.id),
                    "amount": float(amount),
                    "currency": asset.lower(),
                    "fee": float(fee),
                    "netAmount": float(amount),
                    "status": "pending"
                },
                "limits": {
                    "remainingDaily": float(withdrawal_limits.daily - (daily_total + amount)),
                    "remainingMonthly": float(withdrawal_limits.monthly - (monthly_total + amount))
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create withdrawal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo yêu cầu rút tiền"
        )


@router.get(
    "/withdrawals",
    response_model=WithdrawalsListResponse,
    responses={
        200: {"model": WithdrawalsListResponse, "description": "Lấy danh sách withdrawals thành công"},
        401: {"model": FinancialErrorResponse, "description": "Không tìm thấy token xác thực"}
    }
)
async def get_withdrawals(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Lấy danh sách withdrawals - DB-based"""
    
    try:
        # Get transactions from DB
        query = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == "withdrawal"
            )
        )
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if currency:
            query = query.filter(Transaction.asset == currency.upper())
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        # Format response
        withdrawals_data = []
        for tx in transactions:
            withdrawals_data.append({
                "id": str(tx.id),
                "userId": str(tx.user_id),
                "userEmail": user.email,
                "amount": float(tx.amount),
                "currency": tx.asset.lower(),
                "method": tx.category or "unknown",
                "fee": float(tx.fee or 0),
                "netAmount": float(tx.net_amount),
                "status": tx.status,
                "bankAccount": tx.transaction_metadata.get("bank_account") if tx.transaction_metadata else None,
                "walletAddress": tx.to_address,
                "createdAt": tx.created_at.isoformat(),
                "updatedAt": tx.updated_at.isoformat(),
                "processedAt": tx.completed_at.isoformat() if tx.completed_at else None,
                "rejectReason": tx.failed_reason
            })
        
        return WithdrawalsListResponse(
            success=True,
            data={
                "withdrawals": withdrawals_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        )
        
    except Exception as e:
        print(f"Get withdrawals error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách rút tiền"
        )


# ========== BALANCE ENDPOINT ==========

@router.get("/balance")
async def get_balance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Lấy số dư ví - DB-based"""
    
    try:
        balances = financial_service.get_all_balances(user.id)
        
        balance_dict = {}
        for balance in balances:
            balance_dict[balance.asset.lower()] = {
                "available": float(balance.available_balance),
                "locked": float(balance.locked_balance),
                "pending": float(balance.pending_balance),
                "total": float(balance.total_balance)
            }
        
        return {
            "success": True,
            "data": {
                "balances": balance_dict,
                "currencies": list(balance_dict.keys())
            }
        }
        
    except Exception as e:
        print(f"Get balance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy số dư"
        )


# ========== TRANSACTIONS ENDPOINT ==========

@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type_filter: Optional[str] = Query(None, alias="type"),
    status_filter: Optional[str] = Query(None, alias="status"),
    asset: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Lấy lịch sử giao dịch - DB-based"""
    
    try:
        query = db.query(Transaction).filter(
            Transaction.user_id == user.id
        )
        
        if type_filter:
            query = query.filter(Transaction.transaction_type == type_filter)
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if asset:
            query = query.filter(Transaction.asset == asset.upper())
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        # Format response
        transactions_data = []
        for tx in transactions:
            transactions_data.append({
                "id": str(tx.id),
                "type": tx.transaction_type,
                "category": tx.category,
                "asset": tx.asset,
                "amount": float(tx.amount),
                "fee": float(tx.fee or 0),
                "net_amount": float(tx.net_amount),
                "status": tx.status,
                "description": tx.description,
                "reference_id": tx.reference_id,
                "created_at": tx.created_at.isoformat(),
                "completed_at": tx.completed_at.isoformat() if tx.completed_at else None
            })
        
        return {
            "success": True,
            "data": {
                "transactions": transactions_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get transactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy lịch sử giao dịch"
        )
