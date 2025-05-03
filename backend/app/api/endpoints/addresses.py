from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...models.user import User
from ...models.address import Address
from ...schemas.address import Address as AddressSchema, AddressCreate, AddressUpdate
from ..deps import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[AddressSchema])
async def get_user_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lấy danh sách địa chỉ của người dùng hiện tại
    """
    addresses = db.query(Address).filter(Address.user_id == current_user.id).all()
    return addresses

@router.post("/", response_model=AddressSchema, status_code=status.HTTP_201_CREATED)
async def create_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Tạo địa chỉ mới cho người dùng hiện tại
    """
    # Kiểm tra nếu đánh dấu là mặc định, cập nhật các địa chỉ khác
    if address.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Tạo đối tượng Address mới
    db_address = Address(
        user_id=current_user.id,
        address_name=address.address_name,
        address=address.address,
        latitude=address.latitude,
        longitude=address.longitude,
        is_default=address.is_default
    )
    
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

@router.get("/{address_id}", response_model=AddressSchema)
async def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lấy thông tin một địa chỉ cụ thể
    """
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy địa chỉ hoặc địa chỉ không thuộc về bạn"
        )
    
    return address

@router.put("/{address_id}", response_model=AddressSchema)
async def update_address(
    address_id: int,
    address_update: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cập nhật thông tin địa chỉ
    """
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy địa chỉ hoặc địa chỉ không thuộc về bạn"
        )
    
    # Cập nhật các trường nếu có trong request
    update_data = address_update.dict(exclude_unset=True)
    
    # Nếu đánh dấu là mặc định, cập nhật các địa chỉ khác
    if update_data.get('is_default'):
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.id != address_id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Cập nhật thông tin
    for key, value in update_data.items():
        setattr(db_address, key, value)
    
    db.commit()
    db.refresh(db_address)
    return db_address

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Xóa địa chỉ
    """
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy địa chỉ hoặc địa chỉ không thuộc về bạn"
        )
    
    db.delete(db_address)
    db.commit()
    return None 