# src/modules/admin/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date

from src.core.database import get_db
from src.shared.models.resource_models import Location, Service, Resource
from src.shared.models.schedule_models import Shift
from sqlalchemy.orm import joinedload
from src.modules.auth.security import get_current_admin_user # 2. 导入管理员依赖
from src.shared.models.user_models import User # 3. 导入 User (用于类型注解)
from . import schemas # 4. 导入我们刚创建的 schemas

# 我们创建一个专门用于管理后台的 'admin' 路由
# 它不带 prefix，我们将在 main.py 中统一添加
router = APIRouter(
    responses={
        404: {"description": "Not found"},
        403: {"description": "Operation not permitted"},
    }
)

# --- Locations CRUD ---

@router.post(
    "/locations", 
    response_model=schemas.LocationPublic, 
    status_code=status.HTTP_201_CREATED,
    summary="创建新地点"
)
async def create_location(
    location_data: schemas.LocationCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 关键：保护此接口
):
    """
    (Admin Only) 创建一个新的工作地点。
    """
    # 检查地点名称是否已存在 (可选，但推荐)
    query = select(Location).where(Location.name == location_data.name)
    existing_location = (await db.execute(query)).scalars().first()
    if existing_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已存在同名地点"
        )
        
    new_location = Location(
        name=location_data.name,
        address=location_data.address
    )
    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)
    
    return new_location

@router.get(
    "/locations", 
    response_model=List[schemas.LocationPublic],
    summary="获取所有地点列表"
)
async def get_all_locations(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 关键：保护此接口
):
    """
    (Admin Only) 获取所有工作地点的列表。
    
    (注意: 客户查看地点列表将是另一个 *公开* 接口，这个是管理后台用的)
    """
    query = select(Location).order_by(Location.name)
    result = await db.execute(query)
    locations = result.scalars().all()
    
    return locations

@router.put(
    "/locations/{location_uid}", 
    response_model=schemas.LocationPublic,
    summary="更新指定地点"
)
async def update_location(
    location_uid: str,
    location_data: schemas.LocationUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 关键：保护此接口
):
    """
    (Admin Only) 更新一个已存在地点的名称或地址。
    """
    query = select(Location).where(Location.uid == location_uid)
    result = await db.execute(query)
    db_location = result.scalars().first()
    
    if not db_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地点不存在"
        )
    
    # 使用 Pydantic 的 .model_dump() 来安全地更新字段
    # exclude_unset=True 意味着只更新客户端传入的字段
    update_data = location_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_location, key, value)
        
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    
    return db_location

@router.post(
    "/services", 
    response_model=schemas.ServicePublic, 
    status_code=status.HTTP_201_CREATED,
    summary="创建新服务项目"
)
async def create_service(
    service_data: schemas.ServiceCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 创建一个新的服务项目 (如 推拿, 针灸)。
    """
    # 检查名称是否唯一
    query = select(Service).where(Service.name == service_data.name)
    existing_service = (await db.execute(query)).scalars().first()
    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已存在同名服务项目"
        )
        
    new_service = Service(
        name=service_data.name,
        technician_operation_duration=service_data.technician_operation_duration,
        room_operation_duration=service_data.room_operation_duration,
        buffer_time=service_data.buffer_time
    )
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    
    return new_service

@router.get(
    "/services", 
    response_model=List[schemas.ServicePublic],
    summary="获取所有服务项目列表"
)
async def get_all_services(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 获取所有服务项目的列表。
    """
    query = select(Service).order_by(Service.name)
    result = await db.execute(query)
    services = result.scalars().all()
    
    return services

@router.put(
    "/services/{service_uid}", 
    response_model=schemas.ServicePublic,
    summary="更新指定服务项目"
)
async def update_service(
    service_uid: str,
    service_data: schemas.ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 更新一个服务项目的时长或名称。
    """
    query = select(Service).where(Service.uid == service_uid)
    result = await db.execute(query)
    db_service = result.scalars().first()
    
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务项目不存在"
        )
    
    update_data = service_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_service, key, value)
        
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    
    return db_service

@router.post(
    "/resources",
    response_model=schemas.ResourcePublic,
    status_code=status.HTTP_201_CREATED,
    summary="创建新物理资源(床位/房间)"
)
async def create_resource(
    resource_data: schemas.ResourceCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 创建一个新的物理资源 (如 1号床)，并将其分配给一个地点。
    """
    # 1. 验证 Location 是否存在
    db_location = (await db.execute(
        select(Location).where(Location.uid == resource_data.location_uid)
    )).scalars().first()
    
    if not db_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UID 为 {resource_data.location_uid} 的地点不存在"
        )
        
    # 2. 创建 Resource 并直接关联 Location 对象
    new_resource = Resource(
        name=resource_data.name,
        location=db_location  # <-- 直接关联对象
    )
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    
    # 3. 返回。因为 location 关系是在 session 中被赋的，
    # Pydantic (with from_attributes=True) 可以正确地嵌套 LocationPublic
    return new_resource

@router.get(
    "/locations/{location_uid}/resources",
    response_model=List[schemas.ResourcePublic],
    summary="获取指定地点的所有物理资源"
)
async def get_resources_for_location(
    location_uid: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 获取特定地点下的所有物理资源 (床位/房间) 列表。
    """
    query = (
        select(Resource)
        .where(Resource.location_id == location_uid)
        # 关键: 必须 Eager Load 'location' 关系
        # 否则 ResourcePublic schema 会因为缺少 location 数据而失败
        .options(joinedload(Resource.location))
        .order_by(Resource.name)
    )
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return resources

@router.put(
    "/resources/{resource_uid}",
    response_model=schemas.ResourcePublic,
    summary="更新物理资源(床位/房间)"
)
async def update_resource(
    resource_uid: str,
    resource_data: schemas.ResourceUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 更新一个物理资源的名称或其所属的地点。
    """
    query = (
        select(Resource)
        .where(Resource.uid == resource_uid)
        .options(joinedload(Resource.location)) # 预加载以便返回
    )
    result = await db.execute(query)
    db_resource = result.scalars().first()

    if not db_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    update_data = resource_data.model_dump(exclude_unset=True)
    
    # 检查是否需要更新 location_uid
    if "location_uid" in update_data:
        new_location_uid = update_data.pop("location_uid") # 从 update_data 中移除
        db_location = (await db.execute(
            select(Location).where(Location.uid == new_location_uid)
        )).scalars().first()
        
        if not db_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"UID 为 {new_location_uid} 的新地点不存在"
            )
        db_resource.location = db_location # 更新 location 关系
    
    # 更新其他字段 (例如 name)
    for key, value in update_data.items():
        setattr(db_resource, key, value)
        
    db.add(db_resource)
    await db.commit()
    await db.refresh(db_resource, ["location"]) # 确保 location 关系被刷新
    
    return db_resource

@router.get(
    "/technicians",
    response_model=List[schemas.TechnicianPublic],
    summary="获取所有技师及其技能列表"
)
async def get_all_technicians(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 获取所有角色为 'technician' 的用户列表，
    并包含他们所掌握的服务 (技能)。
    """
    query = (
        select(User)
        .where(User.role == 'technician')
        # 关键: 必须 Eager Load 'service' 多对多关系
        # 否则 TechnicianPublic schema 会因为缺少 services 数据而失败
        .options(joinedload(User.service))
        .order_by(User.nickname)
    )
    result = await db.execute(query)
    technicians = result.scalars().unique().all()
    
    return technicians

@router.post(
    "/technicians/{user_uid}/services",
    response_model=schemas.TechnicianPublic,
    summary="为技师分配一项新技能(服务)"
)
async def assign_service_to_technician(
    user_uid: str,
    skill_data: schemas.TechnicianSkillAssign,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 为指定技师添加一项他能提供的服务。
    """
    # 1. 查找技师，并预加载他已有的技能
    query = (
        select(User)
        .where(User.uid == user_uid)
        .options(joinedload(User.service)) # 必须预加载才能 .append()
    )
    result = await db.execute(query)
    db_technician = result.scalars().first()

    if not db_technician or db_technician.role != 'technician':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该技师用户不存在"
        )
        
    # 2. 查找服务
    db_service = (await db.execute(
        select(Service).where(Service.uid == skill_data.service_uid)
    )).scalars().first()
    
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该服务项目不存在"
        )
        
    # 3. 检查是否已分配
    if db_service in db_technician.service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该技师已掌握此技能，请勿重复添加"
        )
        
    # 4. 分配技能 (SQLAlchemy 会自动处理多对多关联表)
    db_technician.service.append(db_service)
    
    db.add(db_technician)
    await db.commit()
    await db.refresh(db_technician, ["service"]) # 刷新关系
    
    return db_technician

@router.delete(
    "/technicians/{user_uid}/services/{service_uid}",
    response_model=schemas.TechnicianPublic,
    summary="移除技师的某项技能(服务)"
)
async def remove_service_from_technician(
    user_uid: str,
    service_uid: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 移除技师的一项服务技能。
    """
    # 1. 查找技师，并预加载他已有的技能
    query = (
        select(User)
        .where(User.uid == user_uid)
        .options(joinedload(User.service))
    )
    result = await db.execute(query)
    db_technician = result.scalars().first()

    if not db_technician or db_technician.role != 'technician':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该技师用户不存在"
        )
        
    # 2. 查找服务
    db_service = (await db.execute(
        select(Service).where(Service.uid == service_uid)
    )).scalars().first()
    
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该服务项目不存在"
        )
        
    # 3. 检查技师是否真的掌握该技能
    if db_service not in db_technician.service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该技师并未掌握此技能"
        )
        
    # 4. 移除技能 (SQLAlchemy 会自动处理多对多关联表)
    db_technician.service.remove(db_service)
    
    db.add(db_technician)
    await db.commit()
    await db.refresh(db_technician, ["service"])
    
    return db_technician

@router.post(
    "/shifts",
    response_model=schemas.ShiftPublic,
    status_code=status.HTTP_201_CREATED,
    summary="创建新排班 (V6)"
)
async def create_shift(
    shift_data: schemas.ShiftCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 为技师在指定地点创建排班。
    - 包含技师排班防重叠检查。
    """
    # 1. 验证技师是否存在
    db_technician = (await db.execute(
        select(User).where(User.uid == shift_data.technician_uid)
    )).scalars().first()
    if not db_technician or db_technician.role != 'technician':
        raise HTTPException(status_code=404, detail="技师用户不存在")

    # 2. 验证地点是否存在
    db_location = (await db.execute(
        select(Location).where(Location.uid == shift_data.location_uid)
    )).scalars().first()
    if not db_location:
        raise HTTPException(status_code=404, detail="地点不存在")

    # 3. (关键) 检查该技师的排班是否重叠
    # 查找该技师已有的、与新排班时间 [start, end] 有任何重叠的排班
    # 重叠条件: (existing.start < new.end) AND (existing.end > new.start)
    overlap_query = select(Shift).where(
        Shift.technician_id == shift_data.technician_uid,
        Shift.start_time < shift_data.end_time, # 已有排班的开始 < 新排班的结束
        Shift.end_time > shift_data.start_time   # 已有排班的结束 > 新排班的开始
    )
    existing_shift = (await db.execute(overlap_query)).scalars().first()
    
    if existing_shift:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict 冲突
            detail=f"该技师在 {existing_shift.start_time} - {existing_shift.end_time} 已有排班，无法创建重叠排班"
        )

    # 4. 创建新排班
    new_shift = Shift(
        technician_id=shift_data.technician_uid,
        location_id=shift_data.location_uid,
        start_time=shift_data.start_time,
        end_time=shift_data.end_time,
        # 手动关联对象以便 Pydantic 返回时能正确嵌套
        technician=db_technician, 
        location=db_location
    )
    db.add(new_shift)
    await db.commit()
    # refresh 不是必须的，因为我们已经手动关联了
    # await db.refresh(new_shift, ["technician", "location"]) 
    
    return new_shift

@router.get(
    "/shifts",
    response_model=List[schemas.ShiftPublic],
    summary="查询排班 (V6)"
)
async def get_shifts(
    location_uid: Optional[str] = None,
    technician_uid: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 查询排班表，可按地点、技师、日期范围过滤。
    """
    query = (
        select(Shift)
        .options(
            joinedload(Shift.technician), # 预加载技师信息
            joinedload(Shift.location)    # 预加载地点信息
        )
        .order_by(Shift.start_time)
    )

    if location_uid:
        query = query.where(Shift.location_id == location_uid)
    if technician_uid:
        query = query.where(Shift.technician_id == technician_uid)
    if start_date:
        # 查询排班结束时间 >= start_date
        query = query.where(Shift.end_time >= start_date) 
    if end_date:
        # 查询排班开始时间 <= end_date
        query = query.where(Shift.start_time <= end_date)

    result = await db.execute(query)
    shifts = result.scalars().unique().all()
    
    return shifts

@router.delete(
    "/shifts/{shift_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除排班 (V6)"
)
async def delete_shift(
    shift_uid: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user) # <-- 保护接口
):
    """
    (Admin Only) 删除一个排班记录。
    """
    query = select(Shift).where(Shift.uid == shift_uid)
    result = await db.execute(query)
    db_shift = result.scalars().first()

    if not db_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="排班记录不存在"
        )
        
    await db.delete(db_shift)
    await db.commit()
    
    return None # 204 状态码不应返回任何内容