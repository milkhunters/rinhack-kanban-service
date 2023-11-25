from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory
from src.views import ColumnResponse, ColumnsResponse

router = APIRouter()


@router.get("/list", response_model=ColumnsResponse, status_code=http_status.HTTP_200_OK)
async def column_list(project_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить список колонок проекта

    Требуемое состояние: Active

    Требуемые права доступа: GET_COLUMN

    """
    return ColumnsResponse(
        content=await services.kanban.column_list(project_id)
    )


@router.post("/new", response_model=ColumnResponse, status_code=http_status.HTTP_201_CREATED)
async def new_column(project_id: UUID, column: schemas.ColumnCreate, services: ServiceFactory = Depends(get_services)):
    """
    Создать колонку

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_COLUMN

    """
    return ColumnResponse(content=await services.kanban.create_column(project_id, column))


@router.get("/{column_id}", response_model=ColumnResponse, status_code=http_status.HTTP_200_OK)
async def get_column(column_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить колонку по id

    Требуемое состояние: Active

    Требуемые права доступа: GET_COLUMN
    """
    return ColumnResponse(content=await services.kanban.get_column(column_id))


@router.put("/{column_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_column(
        column_id: UUID,
        data: schemas.ColumnUpdate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Обновить колонку по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_COLUMN

    """
    await services.kanban.update_column(column_id, data)


@router.delete("/{column_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_column(column_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить колонку по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_COLUMN
    """
    await services.kanban.delete_column(column_id)
