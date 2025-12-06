"""
Client Endpoints - DB-based
Bao gồm: dashboard, wallet-balances, transactions, exchange-rates, crypto-deposit-address, generate-vietqr
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.schemas.client import (
    DashboardResponse,
    WalletBalanceResponse,
    TransactionsResponse,
    ExchangeRatesResponse,
    CryptoDepositAddressRequest,
    CryptoDepositAddressResponse,
    GenerateVietQRRequest,
    VietQRResponse,
    ClientErrorResponse,
    ValidationErrorResponse,
    TransactionHistory,
    WalletBalance,
    ExchangeRate as ExchangeRateSchema,
)
from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.financial import WalletBalance as WalletBalanceModel, Transaction, ExchangeRate
from app.models.audit import AuditLog

router = APIRouter(tags=["client"])


def map_wallet_balances(user: User, db: Session) -> List[WalletBalance]:
    balances: List[WalletBalance] = []
    records = (
        db.query(WalletBalanceModel)
        .filter(WalletBalanceModel.user_id == user.id)
        .order_by(WalletBalanceModel.asset.asc())
        .all()
    )
    for rec in records:
        total = rec.total_balance
        balances.append(
            WalletBalance(
                userId=str(user.id),
                asset=rec.asset.upper(),
                totalBalance=float(total),
                availableBalance=float(rec.available_balance or 0),
                lockedBalance=float(rec.locked_balance or 0),
                pendingBalance=float(rec.pending_balance or 0),
                reservedBalance=float(rec.reserved_balance or 0),
                lastUpdated=rec.updated_at or rec.created_at or datetime.utcnow(),
            )
        )
    return balances


def map_transactions(user: User, db: Session, limit: int = 50) -> List[TransactionHistory]:
    txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
    result: List[TransactionHistory] = []
    for tx in txs:
        amount = float(tx.amount or 0)
        fee = float(tx.fee or 0)
        net_amount = float(tx.net_amount or (tx.amount or 0) - (tx.fee or 0))
        result.append(
            TransactionHistory(
                id=str(tx.id),
                userId=str(tx.user_id),
                type=tx.transaction_type,
                category=tx.category or "",
                status=tx.status,
                amount=amount,
                currency=tx.asset.upper(),
                fee=fee,
                netAmount=net_amount,
                description=tx.description,
                reference=tx.reference_id,
                externalReference=tx.external_id,
                paymentMethod=tx.transaction_metadata.get("method") if tx.transaction_metadata else None,
                fromAddress=tx.from_address,
                toAddress=tx.to_address,
                bankDetails={
                    "bank_name": tx.bank_name,
                    "bank_account": tx.bank_account,
                }
                if tx.bank_name or tx.bank_account
                else None,
                blockchainNetwork=tx.network,
                confirmations=tx.confirmations,
                requiredConfirmations=None,
                metadata=tx.transaction_metadata or {},
                relatedId=None,
                adminNotes=None,
                createdAt=tx.created_at or datetime.utcnow(),
                updatedAt=tx.updated_at,
                completedAt=tx.completed_at,
            )
        )
    return result


def get_usd_equivalent(asset: str, amount: Decimal, db: Session) -> float:
    """Ước lượng giá trị USD dựa trên bảng exchange_rates (nếu có)"""
    asset = asset.upper()
    if asset == "USD":
        return float(amount)

    rate = (
        db.query(ExchangeRate)
        .filter(
            and_(
                ExchangeRate.base_asset == asset,
                ExchangeRate.target_asset == "USD",
                ExchangeRate.is_active == True,
            )
        )
        .order_by(ExchangeRate.priority.desc())
        .first()
    )
    if rate:
        return float(amount * rate.rate)
    return float(amount)


# ========== DASHBOARD ENDPOINT ==========

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    responses={
        200: {"model": DashboardResponse, "description": "Lấy dữ liệu dashboard thành công"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
        404: {"model": ClientErrorResponse, "description": "Không tìm thấy thông tin người dùng"},
        500: {"model": ClientErrorResponse, "description": "Lỗi hệ thống"},
    },
)
async def get_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy dữ liệu dashboard từ dữ liệu thực trong DB
    """
    try:
        user = (
            db.query(User)
            .filter(User.id == current_user.id)
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin người dùng",
            )

        # Balances
        balances = map_wallet_balances(user, db)

        # Recent transactions
        recent_transactions = map_transactions(user, db, limit=20)

        # Tổng quan (tính dựa trên availableBalance quy đổi USD)
        total_balance_usd = 0.0
        available_balance_usd = 0.0
        locked_balance_usd = 0.0
        pending_deposits = 0.0
        pending_withdrawals = 0.0

        for b in balances:
            asset_amount = Decimal(str(b.availableBalance))
            total_amount = Decimal(str(b.totalBalance))
            locked_amount = Decimal(str(b.lockedBalance))

            total_balance_usd += get_usd_equivalent(b.asset, total_amount, db)
            available_balance_usd += get_usd_equivalent(b.asset, asset_amount, db)
            locked_balance_usd += get_usd_equivalent(b.asset, locked_amount, db)

        pending_deposits = sum(
            t.amount
            for t in recent_transactions
            if t.type == "deposit" and t.status == "pending"
        )
        pending_withdrawals = sum(
            t.amount
            for t in recent_transactions
            if t.type == "withdrawal" and t.status == "pending"
        )

        # Stats
        deposits = [t for t in recent_transactions if t.type == "deposit"]
        withdrawals = [t for t in recent_transactions if t.type == "withdrawal"]

        total_deposits = sum(t.amount for t in deposits)
        total_withdrawals = sum(t.amount for t in withdrawals)
        deposit_count = len(deposits)
        withdrawal_count = len(withdrawals)

        largest_deposit = max((t.amount for t in deposits), default=0.0)
        largest_withdrawal = max((t.amount for t in withdrawals), default=0.0)

        average_deposit = total_deposits / deposit_count if deposit_count > 0 else 0.0
        average_withdrawal = (
            total_withdrawals / withdrawal_count if withdrawal_count > 0 else 0.0
        )

        last_deposit_at = deposits[0].createdAt if deposits else None
        last_withdrawal_at = withdrawals[0].createdAt if withdrawals else None

        # Risk & compliance (sơ bộ dựa trên trạng thái KYC)
        kyc_status = user.kyc_status or "pending"
        risk_score = 50
        if kyc_status == "verified":
            risk_score += 20
        if len(recent_transactions) > 10:
            risk_score += 10

        # Exchange rates (lấy từ bảng exchange_rates)
        rate_records = (
            db.query(ExchangeRate)
            .filter(ExchangeRate.is_active == True)
            .order_by(ExchangeRate.priority.desc())
            .all()
        )
        exchange_rates: Dict[str, float] = {}
        for r in rate_records:
            key = f"{r.base_asset}_{r.target_asset}"
            exchange_rates[key] = float(r.rate)

        dashboard_data = {
            "userId": str(user.id),
            "overview": {
                "totalBalance": total_balance_usd,
                "availableBalance": available_balance_usd,
                "lockedBalance": locked_balance_usd,
                "pendingDeposits": pending_deposits,
                "pendingWithdrawals": pending_withdrawals,
                "recentActivity": recent_transactions,
            },
            "balances": balances,
            "recentTransactions": recent_transactions,
            "stats": {
                "totalDeposits": total_deposits,
                "totalWithdrawals": total_withdrawals,
                "netFlow": total_deposits - total_withdrawals,
                "activeAssets": len(balances),
                "largestDeposit": largest_deposit,
                "largestWithdrawal": largest_withdrawal,
                "averageDeposit": average_deposit,
                "averageWithdrawal": average_withdrawal,
                "depositCount": deposit_count,
                "withdrawalCount": withdrawal_count,
                "lastDepositAt": last_deposit_at,
                "lastWithdrawalAt": last_withdrawal_at,
            },
            "riskScore": risk_score,
            "complianceStatus": kyc_status,
            "lastUpdated": datetime.utcnow(),
        }

        return DashboardResponse(
            success=True,
            data=dashboard_data,
            exchangeRates=exchange_rates,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy dữ liệu dashboard",
        )


# ========== WALLET BALANCES ENDPOINT ==========

@router.get(
    "/wallet-balances",
    response_model=WalletBalanceResponse,
    responses={
        200: {"model": WalletBalanceResponse, "description": "Lấy số dư ví thành công"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
    },
)
async def get_wallet_balances(
    request: Request,
    user_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy số dư ví từ bảng wallet_balances
    """
    try:
        target_user_id = int(user_id) if user_id is not None else current_user.id
        user = db.query(User).filter(User.id == target_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )

        balances = map_wallet_balances(user, db)

        return WalletBalanceResponse(success=True, data=balances)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Wallet balances error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy số dư ví",
        )


# ========== TRANSACTIONS ENDPOINT ==========

@router.get(
    "/transactions",
    response_model=TransactionsResponse,
    responses={
        200: {"model": TransactionsResponse, "description": "Lấy danh sách giao dịch thành công"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
    },
)
async def get_transactions(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    transaction_type: Optional[str] = Query(None, alias="type"),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None, alias="currency"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách giao dịch từ bảng transactions
    """
    try:
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)

        if status_filter:
            query = query.filter(Transaction.status == status_filter)

        if currency:
            query = query.filter(Transaction.asset == currency.upper())

        total_items = query.count()
        offset = (page - 1) * limit
        items = (
            query.order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        history = []
        for tx in items:
            amount = float(tx.amount or 0)
            fee = float(tx.fee or 0)
            net_amount = float(tx.net_amount or (tx.amount or 0) - (tx.fee or 0))
            history.append(
                TransactionHistory(
                    id=str(tx.id),
                    userId=str(tx.user_id),
                    type=tx.transaction_type,
                    category=tx.category or "",
                    status=tx.status,
                    amount=amount,
                    currency=tx.asset.upper(),
                    fee=fee,
                    netAmount=net_amount,
                    description=tx.description,
                    reference=tx.reference_id,
                    externalReference=tx.external_id,
                    paymentMethod=tx.transaction_metadata.get("method") if tx.transaction_metadata else None,
                    fromAddress=tx.from_address,
                    toAddress=tx.to_address,
                    bankDetails={
                        "bank_name": tx.bank_name,
                        "bank_account": tx.bank_account,
                    }
                    if tx.bank_name or tx.bank_account
                    else None,
                    blockchainNetwork=tx.network,
                    confirmations=tx.confirmations,
                    requiredConfirmations=None,
                    metadata=tx.transaction_metadata or {},
                    relatedId=None,
                    adminNotes=None,
                    createdAt=tx.created_at or datetime.utcnow(),
                    updatedAt=tx.updated_at,
                    completedAt=tx.completed_at,
                )
            )

        pagination = {
            "page": page,
            "limit": limit,
            "total": total_items,
            "pages": (total_items + limit - 1) // limit,
            "hasNext": offset + limit < total_items,
            "hasPrev": page > 1,
        }

        return TransactionsResponse(
            success=True,
            data=history,
            pagination=pagination,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Transactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách giao dịch",
        )


# ========== EXCHANGE RATES ENDPOINT ==========

@router.get(
    "/exchange-rates",
    response_model=ExchangeRatesResponse,
    responses={
        200: {"model": ExchangeRatesResponse, "description": "Lấy tỷ giá hối đoái thành công"}
    },
)
async def get_exchange_rates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy tỷ giá hối đoái từ bảng exchange_rates
    """
    try:
        rate_records = (
            db.query(ExchangeRate)
            .filter(ExchangeRate.is_active == True)
            .order_by(ExchangeRate.priority.desc())
            .all()
        )

        exchange_rates: List[ExchangeRateSchema] = [
            ExchangeRateSchema(
                id=str(r.id),
                baseAsset=r.base_asset,
                targetAsset=r.target_asset,
                rate=float(r.rate),
                isActive=r.is_active,
                priority=r.priority,
                lastUpdated=r.updated_at or r.created_at or datetime.utcnow(),
                metadata={"source": r.source} if r.source else {},
            )
            for r in rate_records
        ]

        return ExchangeRatesResponse(success=True, data=exchange_rates)

    except Exception as e:
        print(f"Exchange rates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy tỷ giá hối đoái",
        )


# ========== CRYPTO DEPOSIT ADDRESS & VIETQR ==========

@router.post(
    "/crypto-deposit-address",
    response_model=CryptoDepositAddressResponse,
    responses={
        200: {
            "model": CryptoDepositAddressResponse,
            "description": "Tạo địa chỉ nạp crypto thành công",
        },
        400: {"model": ValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
    },
)
async def create_crypto_deposit_address(
    request: Request,
    crypto_request: CryptoDepositAddressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tạo địa chỉ nạp crypto
    Endpoint này chỉ làm nhiệm vụ sinh địa chỉ và QR, ghi transaction do module financial xử lý.
    """
    try:
        # Tạo địa chỉ giả lập nhưng duy nhất (ở production sẽ tích hợp ví thực)
        import secrets

        currency = crypto_request.currency.upper()
        if currency == "BTC":
            address = f"bc1q{secrets.token_hex(16)}"
        elif currency in ("ETH", "USDT"):
            address = f"0x{secrets.token_hex(20)}"
        else:
            address = f"addr_{secrets.token_hex(16)}"

        from base64 import b64encode

        qr_content = f"{currency}:{address}"
        qr_code = b64encode(qr_content.encode()).decode()

        expires_at = datetime.utcnow() + timedelta(hours=24)

        return CryptoDepositAddressResponse(
            success=True,
            data={
                "address": address,
                "currency": currency,
                "network": crypto_request.network or "mainnet",
                "qrCode": qr_code,
                "memo": None,
                "createdAt": datetime.utcnow(),
                "expiresAt": expires_at,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Crypto deposit address error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo địa chỉ nạp crypto",
        )


@router.post(
    "/generate-vietqr",
    response_model=VietQRResponse,
    responses={
        200: {"model": VietQRResponse, "description": "Tạo VietQR thành công"},
        400: {"model": ValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
    },
)
async def generate_vietqr(
    request: Request,
    qr_request: GenerateVietQRRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tạo QR code thanh toán VietQR
    (ở production sẽ tích hợp với VietQR API, ở đây chỉ encode dữ liệu cơ bản)
    """
    try:
        from base64 import b64encode
        import json

        payment_id = f"VQR{current_user.id}{int(datetime.utcnow().timestamp())}"

        qr_data = {
            "paymentId": payment_id,
            "amount": qr_request.amount,
            "description": qr_request.description,
            "orderId": qr_request.orderId,
            "bankCode": "970436",
            "accountNumber": current_user.customer_payment_id or "0000000000",
            "accountName": "DIGITAL UTOPIA",
        }

        qr_content = json.dumps(qr_data, separators=(",", ":"))
        qr_code = b64encode(qr_content.encode()).decode()
        payment_url = f"https://vietqr.net/pay/{payment_id}"

        return VietQRResponse(
            success=True,
            data={
                **qr_data,
                "qrCode": qr_code,
                "paymentUrl": payment_url,
                "createdAt": datetime.utcnow().isoformat(),
                "expiresAt": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            },
            qrCode=qr_code,
            paymentUrl=payment_url,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"VietQR generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo VietQR",
        )
