from fastapi import  APIRouter, Depends, Response
from external_api.client import image_tmdb_client


router = APIRouter(prefix="/proxy")


@router.get("/image/{size}/{poster_path}")
async def get_image(result = Depends(image_tmdb_client.get_image)):
    response = Response(content=result["image_data"], media_type=result["content_type"])
    return response


@router.get("/index/image/{size}/{poster_path}")
async def get_main_page_poster(result = Depends(image_tmdb_client.get_main_page_image)):
    response = Response(content=result["image_data"], media_type=result["content_type"])
    return response
