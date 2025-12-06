"""
Admin Endpoints - DB-based
Bao gồm: users, customers, deposits, withdrawals, platform stats, analytics, logs, settings
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal

# Import schemas
from ...schemas.admin import (
    GetUsersRequest,
    UpdateUserRequest,
    UsersResponse,
    UserResponse,
    AdminUser,
    GetCustomersRequest,
    CustomersResponse,
    AdminCustomer,
    DepositDetailRequest,
    DepositDetailResponse,
    AdminDeposit,
    PlatformStatsResponse,
    PlatformStats,
    AdminErrorResponse,
    AdminValidationErrorResponse,
    UserRole,
    UserStatus,
    KYCStatus
)

# Import dependencies
from ...dependencies import get_current_user, require_role, get_financial_service, get_user_service
from ...db.session import get_db
from ...models.user import User, UserProfile, Role
from ...models.financial import Transaction, WalletBalance
from ...models.trading import TradingOrder, PortfolioPosition
from ...models.audit import AuditLog
from ...services.user_service import UserService
from ...services.financial_service import FinancialService
from ...middleware.auth import get_client_ip, require_admin_role

router = APIRouter(tags=["admin"])


# ========== HELPER FUNCTIONS ==========

def format_admin_user(user: User, db: Session) -> Dict[str, Any]:
    """Format User to AdminUser response"""
    # Get balances
    balances = db.query(WalletBalance).filter(WalletBalance.user_id == user.id).all()
    balance_dict = {}
    for bal in balances:
        balance_dict[bal.asset.lower()] = float(bal.total_balance)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "displayName": user.profile.display_name if user.profile else None,
        "role": user.role.name if user.role else "customer",
        "status": user.status,
        "kycStatus": user.kyc_status,
        "isActive": user.status == "active",
        "phoneNumber": user.profile.phone if user.profile else None,
        "emailVerified": user.email_verified,
        "phoneVerified": user.phone_verified,
        "balance": balance_dict,
        "lastLoginAt": user.last_login_at.isoformat() if user.last_login_at else None,
        "createdAt": user.created_at.isoformat(),
        "updatedAt": user.updated_at.isoformat()
    }


def log_audit(
    db: Session,
    admin_user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    result: str = "success"
):
    """Log admin audit trail"""
    try:
        audit_log = AuditLog(
            user_id=admin_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            category="admin"
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Audit logging error: {e}")


# ========== USER MANAGEMENT ENDPOINTS ==========

@router.get(
    "/users",
    response_model=UsersResponse,
    responses={
        200: {"model": UsersResponse, "description": "Lấy danh sách users thành công"},
        401: {"model": AdminErrorResponse, "description": "Không có quyền truy cập"},
        403: {"model": AdminErrorResponse, "description": "Cần quyền admin"}
    }
)
async def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    kyc_status: Optional[str] = Query(None, alias="kycStatus"),
    sort_by: str = Query("createdAt", alias="sortBy"),
    sort_order: str = Query("desc", alias="sortOrder"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách users - DB-based"""
    
    try:
        # Build query
        query = db.query(User).join(UserProfile, User.id == UserProfile.user_id, isouter=True)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    UserProfile.full_name.ilike(f"%{search}%"),
                    UserProfile.display_name.ilike(f"%{search}%")
                )
            )
        
        if role:
            role_obj = db.query(Role).filter(Role.name == role).first()
            if role_obj:
                query = query.filter(User.role_id == role_obj.id)
        
        if status_filter:
            query = query.filter(User.status == status_filter)
        
        if kyc_status:
            query = query.filter(User.kyc_status == kyc_status)
        
        # Get total count
        total_count = query.count()
        
        # Sort
        if sort_by == "email":
            order_by = User.email
        elif sort_by == "createdAt":
            order_by = User.created_at
        elif sort_by == "lastLoginAt":
            order_by = User.last_login_at
        else:
            order_by = User.created_at
        
        if sort_order.lower() == "desc":
            query = query.order_by(desc(order_by))
        else:
            query = query.order_by(order_by)
        
        # Pagination
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
        
        # Format response
        users_data = [format_admin_user(user, db) for user in users]
        
        log_audit(
            db, admin_user.id, "get_users", "admin",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return UsersResponse(
            success=True,
            data={
                "users": users_data
            },
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "totalPages": (total_count + limit - 1) // limit
            }
        )
        
    except Exception as e:
        print(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách người dùng"
        )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={
        200: {"model": UserResponse, "description": "Lấy thông tin user thành công"},
        404: {"model": AdminErrorResponse, "description": "Không tìm thấy user"}
    }
)
async def get_user_by_id(
    request: Request,
    user_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy thông tin chi tiết user - DB-based"""
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Get statistics
        total_deposits = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_orders = db.query(func.count(TradingOrder.id)).filter(
            TradingOrder.user_id == user_id
        ).scalar() or 0
        
        total_positions = db.query(func.count(PortfolioPosition.id)).filter(
            PortfolioPosition.user_id == user_id
        ).scalar() or 0
        
        user_data = format_admin_user(user, db)
        user_data.update({
            "statistics": {
                "totalDeposits": float(total_deposits),
                "totalWithdrawals": float(total_withdrawals),
                "totalOrders": total_orders,
                "totalPositions": total_positions
            }
        })
        
        return UserResponse(
            success=True,
            data=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get user by id error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thông tin người dùng"
        )


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={
        200: {"model": UserResponse, "description": "Cập nhật user thành công"},
        404: {"model": AdminErrorResponse, "description": "Không tìm thấy user"}
    }
)
async def update_user(
    request: Request,
    user_id: int = Path(...),
    update_data: UpdateUserRequest = None,
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Cập nhật thông tin user - DB-based"""
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        updated_fields = []
        
        # Update role
        if update_data.role:
            role_obj = db.query(Role).filter(Role.name == update_data.role.value).first()
            if role_obj:
                user.role_id = role_obj.id
                updated_fields.append("role")
        
        # Update status
        if update_data.status:
            user.status = update_data.status.value
            updated_fields.append("status")
        
        # Update KYC status
        if update_data.kycStatus:
            user.kyc_status = update_data.kycStatus.value
            updated_fields.append("kycStatus")
        
        # Update isActive (via status)
        if update_data.isActive is not None:
            if update_data.isActive:
                user.status = "active"
            else:
                user.status = "suspended"
            updated_fields.append("isActive")
        
        db.commit()
        db.refresh(user)
        
        # Log audit
        log_audit(
            db, admin_user.id, "update_user", "user",
            resource_id=str(user_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return UserResponse(
            success=True,
            message="Cập nhật thông tin người dùng thành công",
            data=format_admin_user(user, db),
            updatedFields=updated_fields
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật thông tin người dùng"
        )


@router.get(
    "/customers",
    response_model=CustomersResponse,
    responses={
        200: {"model": CustomersResponse, "description": "Lấy danh sách customers thành công"}
    }
)
async def get_customers(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    kyc_status: Optional[str] = Query(None, alias="kycStatus"),
    is_active: Optional[bool] = Query(None, alias="isActive"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách customers - DB-based"""
    
    try:
        # Get customer role
        customer_role = db.query(Role).filter(Role.name == "customer").first()
        if not customer_role:
            return CustomersResponse(
                success=True,
                data=[],
                pagination={"page": 1, "limit": limit, "total": 0, "totalPages": 0}
            )
        
        # Build query
        query = db.query(User).filter(User.role_id == customer_role.id)
        
        # Apply filters
        if search:
            query = query.join(UserProfile).filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    UserProfile.full_name.ilike(f"%{search}%")
                )
            )
        
        if kyc_status:
            query = query.filter(User.kyc_status == kyc_status)
        
        if is_active is not None:
            query = query.filter(User.status == "active" if is_active else User.status != "active")
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
        
        # Format response with statistics
        customers_data = []
        for user in users:
            # Get deposit/withdrawal totals
            total_deposits = db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.user_id == user.id,
                    Transaction.transaction_type == "deposit",
                    Transaction.status == "completed"
                )
            ).scalar() or Decimal("0")
            
            total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.user_id == user.id,
                    Transaction.transaction_type == "withdrawal",
                    Transaction.status == "completed"
                )
            ).scalar() or Decimal("0")
            
            customers_data.append({
                "id": str(user.id),
                "userId": str(user.id),
                "email": user.email,
                "displayName": user.profile.display_name if user.profile else None,
                "phoneNumber": user.profile.phone if user.profile else None,
                "registrationDate": user.created_at,
                "totalDeposits": float(total_deposits),
                "totalWithdrawals": float(total_withdrawals),
                "kycStatus": user.kyc_status,
                "isActive": user.status == "active",
                "lastActivity": user.last_login_at
            })
        
        return CustomersResponse(
            success=True,
            data=customers_data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "totalPages": (total_count + limit - 1) // limit
            }
        )
        
    except Exception as e:
        print(f"Get customers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách khách hàng"
        )


# ========== DASHBOARD ENDPOINT ==========

@router.get("/dashboard")
async def get_dashboard(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy thống kê dashboard - DB-based"""
    
    try:
        # Total users
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar() or 0
        
        # Total deposits/withdrawals
        total_deposits = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        # Trading volume
        trading_volume = db.query(func.sum(TradingOrder.quantity * TradingOrder.filled_price)).filter(
            TradingOrder.status == "filled"
        ).scalar() or Decimal("0")
        
        # KYC pending
        kyc_pending = db.query(func.count(User.id)).filter(User.kyc_status == "pending").scalar() or 0
        
        # Recent activities (last 10 audit logs)
        recent_activities = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(10).all()
        
        activities_data = []
        for log in recent_activities:
            activities_data.append({
                "id": str(log.id),
                "action": log.action,
                "user_id": log.user_id,
                "resource_type": log.resource_type,
                "created_at": log.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "stats": {
                    "totalUsers": total_users,
                    "activeUsers": active_users,
                    "totalDeposits": float(total_deposits),
                    "totalWithdrawals": float(total_withdrawals),
                    "tradingVolume": float(trading_volume),
                    "kycPending": kyc_pending
                },
                "recentActivities": activities_data
            }
        }
        
    except Exception as e:
        print(f"Get dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thống kê dashboard"
        )


# ========== PLATFORM STATS ENDPOINT ==========

@router.get("/platform-stats", response_model=PlatformStatsResponse)
async def get_platform_stats(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy thống kê platform - DB-based"""
    
    try:
        # Aggregate stats from DB
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar() or 0
        
        total_deposits = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        # Average deposits/withdrawals
        deposit_count = db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or 0
        
        withdrawal_count = db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or 0
        
        avg_deposit = float(total_deposits / deposit_count) if deposit_count > 0 else 0
        avg_withdrawal = float(total_withdrawals / withdrawal_count) if withdrawal_count > 0 else 0
        
        # New users
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today.replace(day=1)
        
        new_users_today = db.query(func.count(User.id)).filter(
            User.created_at >= today
        ).scalar() or 0
        
        new_users_month = db.query(func.count(User.id)).filter(
            User.created_at >= month_start
        ).scalar() or 0
        
        # KYC stats
        verified_kyc = db.query(func.count(User.id)).filter(User.kyc_status == "verified").scalar() or 0
        pending_kyc = db.query(func.count(User.id)).filter(User.kyc_status == "pending").scalar() or 0
        
        # Trading volume
        transaction_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.status == "completed"
        ).scalar() or Decimal("0")
        
        stats = PlatformStats(
            totalUsers=total_users,
            activeUsers=active_users,
            totalDeposits=float(total_deposits),
            totalWithdrawals=float(total_withdrawals),
            averageDeposit=avg_deposit,
            averageWithdrawal=avg_withdrawal,
            newUsersToday=new_users_today,
            newUsersThisMonth=new_users_month,
            verifiedKycUsers=verified_kyc,
            pendingKycUsers=pending_kyc,
            totalRevenue=float(total_deposits - total_withdrawals),  # Simplified
            transactionVolume=float(transaction_volume)
        )
        
        return PlatformStatsResponse(
            success=True,
            data=stats
        )
        
    except Exception as e:
        print(f"Get platform stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thống kê platform"
        )


# ========== DEPOSITS MANAGEMENT ENDPOINTS ==========

@router.get("/deposits")
async def get_deposits(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách deposits - DB-based"""
    
    try:
        query = db.query(Transaction).filter(Transaction.transaction_type == "deposit")
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if currency:
            query = query.filter(Transaction.asset == currency.upper())
        
        total_count = query.count()
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        deposits_data = []
        for tx in transactions:
            user = db.query(User).filter(User.id == tx.user_id).first()
            deposits_data.append({
                "id": str(tx.id),
                "userId": str(tx.user_id),
                "customerEmail": user.email if user else "",
                "amount": float(tx.amount),
                "currency": tx.asset.lower(),
                "status": tx.status,
                "paymentMethod": tx.category or "unknown",
                "transactionHash": tx.transaction_hash,
                "createdAt": tx.created_at.isoformat(),
                "processedAt": tx.completed_at.isoformat() if tx.completed_at else None
            })
        
        return {
            "success": True,
            "data": {
                "deposits": deposits_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get deposits error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách nạp tiền"
        )


@router.get("/deposits/{deposit_id}")
async def get_deposit_detail(
    request: Request,
    deposit_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết deposit - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == deposit_id,
                Transaction.transaction_type == "deposit"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch nạp tiền"
            )
        
        user = db.query(User).filter(User.id == transaction.user_id).first()
        
        deposit_data = {
            "id": str(transaction.id),
            "userId": str(transaction.user_id),
            "customerEmail": user.email if user else "",
            "amount": float(transaction.amount),
            "currency": transaction.asset.lower(),
            "status": transaction.status,
            "paymentMethod": transaction.category or "unknown",
            "transactionHash": transaction.transaction_hash,
            "bankReference": transaction.reference_id,
            "adminNotes": transaction.description,
            "processedAt": transaction.completed_at.isoformat() if transaction.completed_at else None,
            "createdAt": transaction.created_at.isoformat()
        }
        
        return DepositDetailResponse(
            success=True,
            data=deposit_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get deposit detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy chi tiết giao dịch nạp tiền"
        )


@router.post("/deposits/{deposit_id}/approve")
async def approve_deposit(
    request: Request,
    deposit_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Duyệt deposit - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == deposit_id,
                Transaction.transaction_type == "deposit",
                Transaction.status == "pending"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch nạp tiền hoặc đã được xử lý"
            )
        
        # Complete transaction (updates balance)
        completed_tx = financial_service.complete_transaction(deposit_id)
        
        if not completed_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hoàn tất giao dịch"
            )
        
        # Log audit
        log_audit(
            db, admin_user.id, "approve_deposit", "transaction",
            resource_id=str(deposit_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Duyệt nạp tiền thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Approve deposit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể duyệt nạp tiền"
        )


@router.post("/deposits/{deposit_id}/reject")
async def reject_deposit(
    request: Request,
    deposit_id: int = Path(...),
    reason: str = Query(..., description="Lý do từ chối"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Từ chối deposit - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == deposit_id,
                Transaction.transaction_type == "deposit",
                Transaction.status == "pending"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch nạp tiền hoặc đã được xử lý"
            )
        
        # Cancel transaction
        cancelled_tx = financial_service.cancel_transaction(deposit_id, reason)
        
        if not cancelled_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hủy giao dịch"
            )
        
        # Log audit
        log_audit(
            db, admin_user.id, "reject_deposit", "transaction",
            resource_id=str(deposit_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Từ chối nạp tiền thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject deposit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể từ chối nạp tiền"
        )


# ========== WITHDRAWALS MANAGEMENT ENDPOINTS ==========

@router.get("/withdrawals")
async def get_withdrawals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách withdrawals - DB-based"""
    
    try:
        query = db.query(Transaction).filter(Transaction.transaction_type == "withdrawal")
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if currency:
            query = query.filter(Transaction.asset == currency.upper())
        
        total_count = query.count()
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        withdrawals_data = []
        for tx in transactions:
            user = db.query(User).filter(User.id == tx.user_id).first()
            withdrawals_data.append({
                "id": str(tx.id),
                "userId": str(tx.user_id),
                "customerEmail": user.email if user else "",
                "amount": float(tx.amount),
                "currency": tx.asset.lower(),
                "fee": float(tx.fee or 0),
                "netAmount": float(tx.net_amount),
                "status": tx.status,
                "createdAt": tx.created_at.isoformat(),
                "processedAt": tx.completed_at.isoformat() if tx.completed_at else None,
                "rejectReason": tx.failed_reason
            })
        
        return {
            "success": True,
            "data": {
                "withdrawals": withdrawals_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get withdrawals error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách rút tiền"
        )


@router.get("/withdrawals/{withdrawal_id}")
async def get_withdrawal_detail(
    request: Request,
    withdrawal_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết withdrawal - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == withdrawal_id,
                Transaction.transaction_type == "withdrawal"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch rút tiền"
            )
        
        user = db.query(User).filter(User.id == transaction.user_id).first()
        
        withdrawal_data = {
            "id": str(transaction.id),
            "userId": str(transaction.user_id),
            "customerEmail": user.email if user else "",
            "amount": float(transaction.amount),
            "currency": transaction.asset.lower(),
            "fee": float(transaction.fee or 0),
            "netAmount": float(transaction.net_amount),
            "status": transaction.status,
            "bankAccount": transaction.transaction_metadata.get("bank_account") if transaction.transaction_metadata else None,
            "walletAddress": transaction.to_address,
            "createdAt": transaction.created_at.isoformat(),
            "processedAt": transaction.completed_at.isoformat() if transaction.completed_at else None,
            "rejectReason": transaction.failed_reason
        }
        
        return {
            "success": True,
            "data": withdrawal_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get withdrawal detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy chi tiết giao dịch rút tiền"
        )


@router.post("/withdrawals/{withdrawal_id}/approve")
async def approve_withdrawal(
    request: Request,
    withdrawal_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Duyệt withdrawal - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == withdrawal_id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "pending"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch rút tiền hoặc đã được xử lý"
            )
        
        # Complete transaction (deducts from locked balance)
        completed_tx = financial_service.complete_transaction(withdrawal_id)
        
        if not completed_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hoàn tất giao dịch"
            )
        
        # Log audit
        log_audit(
            db, admin_user.id, "approve_withdrawal", "transaction",
            resource_id=str(withdrawal_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Duyệt rút tiền thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Approve withdrawal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể duyệt rút tiền"
        )


@router.post("/withdrawals/{withdrawal_id}/reject")
async def reject_withdrawal(
    request: Request,
    withdrawal_id: int = Path(...),
    reason: str = Query(..., description="Lý do từ chối"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Từ chối withdrawal - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == withdrawal_id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "pending"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch rút tiền hoặc đã được xử lý"
            )
        
        # Cancel transaction (unlocks balance)
        cancelled_tx = financial_service.cancel_transaction(withdrawal_id, reason)
        
        if not cancelled_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hủy giao dịch"
            )
        
        # Log audit
        log_audit(
            db, admin_user.id, "reject_withdrawal", "transaction",
            resource_id=str(withdrawal_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Từ chối rút tiền thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject withdrawal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể từ chối rút tiền"
        )


# ========== ANALYTICS ENDPOINT ==========

@router.get("/analytics")
async def get_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy analytics data - DB-based"""
    
    try:
        # Default to last 30 days
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Trading volume by day
        trading_volume_query = db.query(
            func.date(TradingOrder.created_at).label("date"),
            func.sum(TradingOrder.quantity * TradingOrder.filled_price).label("volume")
        ).filter(
            and_(
                TradingOrder.status == "filled",
                TradingOrder.created_at >= start_date,
                TradingOrder.created_at <= end_date
            )
        ).group_by(func.date(TradingOrder.created_at)).all()
        
        trading_volume_data = [
            {"date": date.isoformat(), "volume": float(volume or 0)}
            for date, volume in trading_volume_query
        ]
        
        return {
            "success": True,
            "data": {
                "tradingVolume": trading_volume_data,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
        }
        
    except Exception as e:
        print(f"Get analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy analytics"
        )


# ========== REPORTS ENDPOINT ==========

@router.get("/reports")
async def get_reports(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách reports - DB-based"""
    
    try:
        # Generate reports from DB
        # This is a simplified version - can be expanded
        return {
            "success": True,
            "data": {
                "reports": [
                    {
                        "id": "daily_report",
                        "name": "Báo cáo hàng ngày",
                        "status": "available"
                    },
                    {
                        "id": "monthly_report",
                        "name": "Báo cáo hàng tháng",
                        "status": "available"
                    }
                ]
            }
        }
        
    except Exception as e:
        print(f"Get reports error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách báo cáo"
        )


# ========== LOGS ENDPOINT ==========

@router.get("/logs")
async def get_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy audit logs - DB-based"""
    
    try:
        query = db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        if category:
            query = query.filter(AuditLog.category == category)
        
        total_count = query.count()
        offset = (page - 1) * limit
        logs = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
        
        logs_data = []
        for log in logs:
            logs_data.append({
                "id": str(log.id),
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "category": log.category,
                "result": log.result,
                "ip_address": str(log.ip_address) if log.ip_address else None,
                "created_at": log.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "logs": logs_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy audit logs"
        )


# ========== SETTINGS ENDPOINT ==========

@router.get("/settings")
async def get_settings(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy system settings - Config-based"""
    
    try:
        # In production, can be stored in DB
        return {
            "success": True,
            "data": {
                "maintenanceMode": False,
                "tradingFee": 0.001,  # 0.1%
                "minDeposit": 10.0,
                "maxDeposit": 1000000.0,
                "minWithdraw": 20.0,
                "maxWithdraw": 100000.0,
                "dailyWithdrawLimit": 10000.0,
                "monthlyWithdrawLimit": 100000.0
            }
        }
        
    except Exception as e:
        print(f"Get settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy cài đặt hệ thống"
        )


@router.put("/settings")
async def update_settings(
    request: Request,
    settings_data: Dict[str, Any],
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Cập nhật system settings - Config-based"""
    
    try:
        # Validate settings
        if "maintenanceMode" in settings_data:
            maintenance_mode = settings_data["maintenanceMode"]
            # Can update in DB or config file
        
        if "tradingFee" in settings_data:
            fee = settings_data["tradingFee"]
            if fee < 0 or fee > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Trading fee phải trong khoảng 0-1"
                )
        
        # Log audit
        log_audit(
            db, admin_user.id, "update_settings", "system",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Cập nhật cài đặt hệ thống thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cài đặt hệ thống"
        )
