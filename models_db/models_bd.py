from sqlalchemy import ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime, timezone


class Base(AsyncAttrs, DeclarativeBase):
	pass

class Sneaker(Base):
	__tablename__ = 'sneaker_main'
	id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
	product_code: Mapped[str] = mapped_column(unique=True)
	name: Mapped[str]
	price: Mapped[int]
	description: Mapped[str]
	material_sneaker: Mapped[str]
	gender: Mapped[str | None] = mapped_column(nullable=True)
	size: Mapped[str | None] = mapped_column(nullable=True)
	main_image: Mapped[str | None]
	another_images: Mapped[list['ImagesSneaker']] = relationship(back_populates='product', uselist=True)
	category_id: Mapped[int] = mapped_column(ForeignKey('category_sneakermain.id'))
	category: Mapped['CategorySneakerMain'] = relationship(back_populates='sneaker_list')
	size_list: Mapped[list['SizeSneaker']] = relationship(back_populates='product_size', uselist=True)
	id_season: Mapped[int] = mapped_column(ForeignKey('season.id'))
	type_season: Mapped['Season'] = relationship(back_populates='sneaker_id')

class ImagesSneaker(Base):
	__tablename__ = 'images'
	id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
	sneaker_id: Mapped[int] = mapped_column(ForeignKey('sneaker_main.id'))
	product: Mapped[Sneaker] = relationship(back_populates='another_images')
	url_image: Mapped[str]

class Season(Base):
	__tablename__ = 'season'
	id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
	name_season: Mapped[str]
	sneaker_id: Mapped[list[Sneaker]] = relationship(back_populates='type_season', uselist=True)

class CategorySneakerMain(Base):
	__tablename__ = 'category_sneakermain'
	id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
	name: Mapped[str]
	sneaker_list: Mapped[list[Sneaker]] = relationship(back_populates='category', uselist=True)

class SizeSneaker(Base):
	__tablename__ = 'size_sneaker'
	id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
	sneaker_id: Mapped[int] = mapped_column(ForeignKey('sneaker_main.id'))
	product_size: Mapped[Sneaker] = relationship(back_populates='size_list')
	size: Mapped[int]
	count: Mapped[int]
	size_in_sm: Mapped[float]

class Logs(Base):
	__tablename__ = 'logs'
	id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
	operation: Mapped[str]
	table: Mapped[str]
	product_code: Mapped[str]
	date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True) ,default=datetime.now(timezone.utc))

class OpenOrders(Base):
	__tablename__ = 'open_orders'
	id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
	order_code: Mapped[str]
	sneaker_id: Mapped[int] = mapped_column(ForeignKey('sneaker_main.id'))
	size: Mapped[int]
	phone_number: Mapped[str]
	adress: Mapped[str]
	status: Mapped[str]
	full_name: Mapped[str]
	payment: Mapped[str]
	date_open_order: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
	date_dispatch: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), default=None)
