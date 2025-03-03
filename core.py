import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
import os
from dotenv import load_dotenv
load_dotenv()

from models_db.models_bd import *

engine = create_async_engine(os.getenv('DATABASE_URL'), echo=True)

SessionMaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def use_session() -> AsyncGenerator[AsyncSession, None]:
	session = SessionMaker()
	try:
		yield session  # ✅ Отдаем сессию в FastAPI
	except Exception as e:
		raise e
	finally:
		await session.close()  # ✅ Корректное закрытие сессии

async def initialization_bd():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)


	async with SessionMaker() as session:
		category1 = CategorySneakerMain(name='шльопанці')
		category2 = CategorySneakerMain(name="в'єтнамки")
		category3 = CategorySneakerMain(name='крокси')
		category4 = CategorySneakerMain(name='босоніжки')
		category5 = CategorySneakerMain(name='капці')
		category6 = CategorySneakerMain(name='чешки')
		category7 = CategorySneakerMain(name='мокасини')
		category8 = CategorySneakerMain(name='кросівки')
		category9 = CategorySneakerMain(name='туфлі')
		category10 = CategorySneakerMain(name='чобітки')

		season1 = Season(name_season='Зима')
		season2 = Season(name_season='Весна')
		season3 = Season(name_season='Літо')
		season4 = Season(name_season='Осінь')

		session.add_all([category1, category2, category3, category4, category5, category6, category7, category8, category9, category10,
		                 season1, season2, season3, season4])

		await session.commit()


if __name__ == '__main__':
	asyncio.run(initialization_bd())
