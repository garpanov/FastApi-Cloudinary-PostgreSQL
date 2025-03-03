from pydantic import BaseModel

class AddSizeSneaker(BaseModel):
	size: int
	count: int
	size_in_sm: float

class AddSneaker(BaseModel):
	product_code: str
	name: str
	price: int
	description: str
	material_sneaker: str
	main_image: str
	another_images: list[str]
	gender: str | None = None
	size: str | None = None
	category_id: int
	id_season: int
	size_sneaker: list[AddSizeSneaker]


class DeleteSneaker(BaseModel):
	product_code: str
	price: int

class ReturnSneaker(BaseModel):
	product_code: str
	size: int
	size_in_sm: float

class SneakerChange(BaseModel):
	product_code: str | None = None
	name: str | None = None
	price: int | None = None
	gender: str | None = None
	size: str | None = None
	image_url: str | None = None
	description: str | None = None
	material_sneaker: str | None = None
	category_id: int | None = None
	id_season: int | None = None

class ChangeStatusOrder(BaseModel):
	order_code: str
	status: str