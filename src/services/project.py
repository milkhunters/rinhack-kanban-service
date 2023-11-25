import logging
import uuid

import grpc
from src.protos.project_control import project_control_pb2
from src.protos.project_control import project_control_pb2_grpc


async def is_user_in_project(
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        project_service_conn: tuple[str, int]
) -> bool:
    try:
        async with grpc.aio.insecure_channel(f"{project_service_conn[0]}:{project_service_conn[1]}") as channel:
            stub = project_control_pb2_grpc.ProjectServiceStub(channel)
            response = await stub.IsUserInProject(project_control_pb2.ProjectRequest(
                project_id=str(project_id),
                user_id=str(user_id)
            ))
        return response.result
    except grpc.aio.AioRpcError as error:
        logging.error(error)
        return False
