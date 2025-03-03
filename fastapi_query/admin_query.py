from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core import use_session
from fastapi_query.auth import check_jwt
from models_db.models_bd import *
from models_pydantic.validate_query_admin import *
from cloudin import delete_images

router_admin = APIRouter()

async def delete_sneaker_func(item: DeleteSneaker, session: AsyncSession):
	before_processing = await session.execute(
		select(Sneaker).where(Sneaker.product_code == item.product_code).options(selectinload(Sneaker.another_images)))
	sneaker = before_processing.scalar()
	if not sneaker:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
		                    detail=f'Sneaker with code "{item.product_code}" not found')
	delete_images(sneaker.another_images, sneaker.main_image)
	logs = Logs(operation='Delete sneaker', table='sneaker_main, size_sneaker, images',
	            product_code=sneaker.product_code)
	session.add(logs)

	await session.execute(delete(SizeSneaker).where(SizeSneaker.sneaker_id == sneaker.id))
	await session.execute(delete(ImagesSneaker).where(ImagesSneaker.sneaker_id == sneaker.id))
	await session.delete(sneaker)

	await session.commit()

	return True

@router_admin.post('/add_sneaker')
async def add_sneaker_for_db(item: AddSneaker, request: Request, session: AsyncSession = Depends(use_session)):
	token = request.cookies.get('auth_token')
	await check_jwt(token)

	product_data = item.model_dump(exclude={"size_sneaker", 'another_images'})
	product = Sneaker(**product_data)

	for size in item.size_sneaker:
		size_obj = SizeSneaker(size=size.size, count=size.count, size_in_sm=size.size_in_sm)
		product.size_list.append(size_obj)

	for image in item.another_images:
		image_url = ImagesSneaker(url_image=image)
		product.another_images.append(image_url)
	session.add(product)

	logs = Logs(operation='Add sneaker', table='sneaker_main, size_sneaker, images, season', product_code=product.product_code)
	session.add(logs)
	await session.commit()
	return True

@router_admin.patch('/change_sneaker')
async def change_sneaker(item: SneakerChange, request: Request, session: AsyncSession = Depends(use_session)):
	token = request.cookies.get('auth_token')
	await check_jwt(token)

	update_data = item.model_dump(exclude_unset=True)
	before_processing = await session.execute(select(Sneaker).where(Sneaker.product_code == item.product_code))
	preparing_product = before_processing.scalar()
	if not preparing_product:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
		                    detail=f'Sneaker with code "{item.product_code}" not found')
	product = await session.execute((update(Sneaker).where(Sneaker.product_code == item.product_code).values(**update_data)))

	logs = Logs(operation='Change sneaker', table='sneaker_main', product_code=preparing_product.product_code)
	session.add(logs)

	await session.commit()
	return True

@router_admin.delete('/delete_sneaker')
async def delete_sneaker(item: DeleteSneaker, request: Request, session: AsyncSession = Depends(use_session)):
	token = request.cookies.get('auth_token')
	await check_jwt(token)

	await delete_sneaker_func(item, session)

@router_admin.get('/all_order')
async def read_all_orders(status: Annotated[str | None, Query], request: Request, session: AsyncSession = Depends(use_session)):
	token = request.cookies.get('auth_token')
	await check_jwt(token)

	query = select(OpenOrders, Sneaker).join(Sneaker)
	if status:
		query = query.where(OpenOrders.status == status)


	orders = (await session.execute(query)).all()
	date = []
	for order_info, sneaker_info in orders:
		order_info.phone_number = str(order_info.phone_number)
		date_product = order_info.__dict__.copy()
		code_product = date_product.pop('order_code')
		date_product['price'] = sneaker_info.price
		date_product['image_url'] = sneaker_info.main_image
		date_product['code_product'] = sneaker_info.product_code
		date_product['name_product'] = sneaker_info.name

		added_in_date = False
		for y in date:
			if y['order_code'] == code_product:
				y['date'].append(date_product)
				added_in_date = True

		if not added_in_date:
			date.append({'order_code': code_product, 'date': [date_product]})

	return date

@router_admin.patch('/change_status_order')
async def change_status_order(change_order: ChangeStatusOrder, request: Request, session: AsyncSession = Depends(use_session)):
	token = request.cookies.get('auth_token')
	await check_jwt(token)

	before_processing = await session.execute(select(OpenOrders).where(OpenOrders.order_code == change_order.order_code))
	orders = before_processing.scalars().all()
	for order in orders:
		order.status = change_order.status
		if change_order.status == 'sent':
			order.date_dispatch = datetime.now(timezone.utc)
		session.add(order)

	logs = Logs(operation='Change status order |examination -> sent|', table='open_orders', product_code=change_order.order_code)
	session.add(logs)

	await session.commit()
	return True

@router_admin.delete('/delete_order')
async def delete_order(order: ChangeStatusOrder, request: Request, session: AsyncSession = Depends(use_session)):
	token = request.cookies.get('auth_token')
	await check_jwt(token)

	info_order = (await session.execute(select(OpenOrders).where(OpenOrders.order_code == order.order_code))).scalar()
	info_sizes = (await session.execute(select(SizeSneaker).where(SizeSneaker.sneaker_id == info_order.sneaker_id))).scalars().all()

	for size in info_sizes:
		if size.size == info_order.size:
			size.count -= 1
			if size.count == 0:
				await session.delete(size)
				break

	sneaker_id = info_order.sneaker_id
	await session.delete(info_order)

	logs = Logs(operation='Close order', table='open_orders',
	            product_code=f'id: {sneaker_id}')

	session.add(logs)
	await session.commit()
	info_sizes = (await session.execute(select(SizeSneaker).where(SizeSneaker.sneaker_id == info_order.sneaker_id))).scalars().all()
	if not info_sizes:
		sneaker_code = (await session.execute(select(Sneaker.product_code).where(Sneaker.id == sneaker_id))).scalar()
		item = DeleteSneaker(product_code=sneaker_code, price=1)
		await delete_sneaker_func(item, session)
	return info_sizes

@router_admin.post('/return_sneaker')
async def return_sneaker(item: ReturnSneaker, request: Request, session: AsyncSession = Depends(use_session)):
	token = request.cookies.get('auth_token')
	await check_jwt(token)

	sneaker = (await session.execute(select(Sneaker).where(Sneaker.product_code == item.product_code).options(selectinload(Sneaker.size_list)))).scalars().first()
	if not sneaker:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
		                    detail=f'Sneaker with code "{item.product_code}" not found')

	in_list = False
	for size in sneaker.size_list:
		if size.size == item.size:
			size.count += 1
			in_list = True

	if not in_list:
		new_size = SizeSneaker(size=item.size, count=1, size_in_sm=item.size_in_sm)
		sneaker.size_list.append(new_size)
	logs = Logs(operation='return sneaker', table='sneaker_main, size_sneaker',
	            product_code=sneaker.product_code)
	session.add(logs)
	await session.commit()
	return True






