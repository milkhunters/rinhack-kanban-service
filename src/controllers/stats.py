from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.services import ServiceFactory
from src.views.tag_stat import TagStatResponse

router = APIRouter()


@router.get("/version", response_model=dict, status_code=http_status.HTTP_200_OK)
async def version(details: bool = False, services: ServiceFactory = Depends(get_services)):
    """
    Получить информацию о приложении

    Ограничений по доступу нет
    """
    return await services.stats.get_stats(details)


@router.get("/ping", response_model=str, status_code=http_status.HTTP_200_OK)
def ping():
    return "pong"


@router.get("/tag", response_model=TagStatResponse, status_code=http_status.HTTP_200_OK)
async def tag_stat(project_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить статистику по тегам проекта

    Требуемое состояние: Active

    Требуемые права доступа: GET_TASK
    """
    return TagStatResponse(content=await services.stats.get_tag_stat(project_id))
