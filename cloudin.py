from dotenv import load_dotenv
load_dotenv()

import threading
import cloudinary
import cloudinary.uploader
import cloudinary.api


from fastapi import HTTPException, status

config = cloudinary.config(secure=True)


def delete_images_sync(ready_images: list):
	try:
		result = cloudinary.api.delete_resources(ready_images, invalidate=True, resource_type="image")
		print(result)  # Логируем результат, если нужно
	except Exception as e:
		print(f"Error during image deletion: {e}")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Error deleting images: {str(e)}')


def delete_images(images: list, main_image: str):
	ready_images = [image.url_image.split('/')[1] for image in images]
	ready_images.append(main_image.split('/')[1])

	# Создаем поток для выполнения операции в фоне
	thread = threading.Thread(target=delete_images_sync, args=(ready_images,))
	thread.start()

	# Возвращаем ответ немедленно, не дожидаясь завершения потока
	return {"message": "Image deletion started"}
