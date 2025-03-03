import math
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models_db.models_bd import *
from models_pydantic.validate_query_client import *
from core import use_session

router_client = APIRouter()

@router_client.get('/date/{offset_s}')
async def sneaker_sort(offset_s: int, sort: str | None = None, sort_min_price: int | None = None, sort_max_price: int | None = None,
                 in_name: str | None = None, sort_type: Annotated[list[str] | None, Query()] = None, season: Annotated[list[int] | None, Query()] = None,
                 sort_gender: Annotated[list[str] | None, Query()] = None, size: Annotated[list[str] | None, Query()] = None, session: AsyncSession = Depends(use_session)):
    # Базовий запит
    date = select(Sneaker).join(CategorySneakerMain)

    # Фільтри
    if sort_type:
        date = date.where(CategorySneakerMain.name.in_(sort_type))
    if season:
        date = date.where(Sneaker.id_season.in_(season))
    if in_name:
        date = date.where(Sneaker.name.ilike(f"%{in_name}%"))
    if sort_gender:
        date = date.where(or_(Sneaker.gender.in_(sort_gender), Sneaker.gender == None))
    if size:
        date = date.where(or_(Sneaker.size.in_(size), Sneaker.size == None))

    # Сортування
    if sort:
        if sort == "price":
            date = date.order_by(Sneaker.price.asc())
        elif sort == "!price":
            date = date.order_by(Sneaker.price.desc())
    if sort_min_price:
        date = date.where(Sneaker.price >= sort_min_price)
    if sort_max_price:
        date = date.where(Sneaker.price <= sort_max_price)

    result = await session.execute(date)
    result_for_offset = result.scalars().all()
    #Перемикання сторінок

    offset_s -= 1
    if offset_s != 0:
        offset_s = 20 * (offset_s)

    date = date.offset(offset_s).limit(20)
    date = date.options(selectinload(Sneaker.size_list))

    # Виконання запиту
    one_res = await session.execute(date)
    result = one_res.scalars().all()

    result_for_offset1 = int(math.ceil(len(result_for_offset) / 20))
    new_date_sneaker = {'date': [], 'about_offest': result_for_offset1}

    # /////// add column list sizes sneakers for "information sneaker" on client //////////
    for product in result:
        new_list_size = {'list_size': []}
        for size in product.size_list:
            new_list_size['list_size'].append(size.size)

        new_poduct = product.__dict__.copy()
        new_poduct.pop("size_list", None)
        date = new_poduct | new_list_size
        new_date_sneaker['date'].append(date)


    return new_date_sneaker

@router_client.post('/buy_sneakers')
async def buy_sneaker(items:BuySneakers, session: AsyncSession = Depends(use_session)):
    order_code = str(uuid.uuid4())[:8] + str(datetime.now(timezone.utc).microsecond)
    product_codes = ''
    sneaker = (await session.execute(select(Sneaker).where(Sneaker.id.in_(items.sneaker_id)))).scalars().all()
    if not sneaker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Sneaker with code {items.sneaker_id} not found')

    for id_sneaker, size_sneaker in zip(items.sneaker_id, items.size):
        order = OpenOrders(order_code=order_code, sneaker_id=id_sneaker, size=size_sneaker,
                           phone_number=items.phone_number, adress=items.adress, status='examination',
                           full_name=items.full_name, payment=items.payment)
        session.add(order)

    for code in sneaker:
        product_codes += f'{code.product_code},'
    product_codes += f' order_code: {order_code}'
    log = Logs(operation='Create order', table='open_orders',
               product_code=product_codes)
    session.add(log)
    await session.commit()

    return True

@router_client.get('/read_sneaker/{sneaker_code}')
async def read_sneaker(sneaker_code: str, session: AsyncSession = Depends(use_session)):
    data = (await session.execute(select(Sneaker, SizeSneaker).join(SizeSneaker).where(Sneaker.product_code == sneaker_code).options(selectinload(Sneaker.another_images)))).all()
    sneaker = []
    size = []
    images = []
    for sneaker_info, size_info in data:
        sneaker = sneaker_info
        size.append({'size': size_info.size, 'size_in_sm': size_info.size_in_sm})

    for image in sneaker.another_images:
        images.append(image.url_image)
    sneaker = sneaker.__dict__
    sneaker.pop('another_images')

    return {'sneaker_info': sneaker, 'size_info': size, 'images': images}