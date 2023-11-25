from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory
from src.views import TaskResponse, TasksResponse
from src.views.task import TagResponse, TagsResponse

router = APIRouter()


@router.get("/list", response_model=TasksResponse, status_code=http_status.HTTP_200_OK)
async def task_list(column_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить список задач колонки

    Требуемое состояние: Active

    Требуемые права доступа: GET_TASK

    """
    return TasksResponse(
        content=await services.kanban.task_list(column_id)
    )


@router.post("/new", response_model=TaskResponse, status_code=http_status.HTTP_201_CREATED)
async def new_task(column_id: UUID, task: schemas.TaskCreate, services: ServiceFactory = Depends(get_services)):
    """
    Создать задачу

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_TASK

    """
    return TaskResponse(content=await services.kanban.create_task(column_id, task))


@router.get("/{task_id}", response_model=TaskResponse, status_code=http_status.HTTP_200_OK)
async def get_task(task_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить задачу по id

    Требуемое состояние: Active

    Требуемые права доступа: GET_TASK
    """
    return TaskResponse(content=await services.kanban.get_task(task_id))


@router.put("/{task_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_task(
        task_id: UUID,
        data: schemas.TaskUpdate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Обновить задачу по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TASK

    """
    await services.kanban.update_task(task_id, data)


@router.delete("/{task_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить задачу по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_TASK
    """
    await services.kanban.delete_task(task_id)


@router.post("/tag", response_model=TagResponse, status_code=http_status.HTTP_201_CREATED)
async def create_tag(project_id: UUID, data: schemas.TagCreate, services: ServiceFactory = Depends(get_services)):
    """
    Создать тег

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TASK
    """
    return TagResponse(content=await services.kanban.create_tag(project_id, data))


@router.delete("/tag/{tag_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить тег по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TASK
    """
    await services.kanban.delete_tag(tag_id)


@router.get("/tag/list", response_model=TagsResponse, status_code=http_status.HTTP_200_OK)
async def tag_list(project_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить список тегов

    Требуемое состояние: Active

    Требуемые права доступа: GET_TASK
    """
    return TagsResponse(content=await services.kanban.tag_list(project_id))


@router.post("/{task_id}/tag/{tag_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def set_tag(task_id: UUID, tag_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Установить тег по id

    Требуемое состояние: Active

    Требуемые права доступа: UPDATE_TASK
    """
    await services.kanban.set_tag(task_id, tag_id)


@router.delete("/{task_id}/tag/{tag_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def unset_tag(task_id: UUID, tag_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить связь тега по id

    Требуемое состояние: Active

    Требуемые права доступа: UPDATE_TASK
    """
    await services.kanban.unset_tag(task_id, tag_id)
