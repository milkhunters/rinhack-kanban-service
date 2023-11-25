import asyncio
import logging
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from src.config import Config

from src.db import create_psql_async_session
from src.services.auth.scheduler import update_reauth_list


async def init_db(app: FastAPI, config: Config):
    engine, session = create_psql_async_session(
        host=config.DB.POSTGRESQL.HOST,
        port=config.DB.POSTGRESQL.PORT,
        username=config.DB.POSTGRESQL.USERNAME,
        password=config.DB.POSTGRESQL.PASSWORD,
        database=config.DB.POSTGRESQL.DATABASE,
        echo=config.DEBUG,
    )
    app.state.db_session = session


async def init_reauth_checker(app: FastAPI, config: Config):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_reauth_list,
        'interval',
        seconds=5,
        args=[app, (config.UMS_GRPC.HOST, config.UMS_GRPC.PORT)]
    )
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    scheduler.start()


def create_start_app_handler(app: FastAPI, config: Config) -> Callable:
    async def start_app() -> None:
        logging.debug("Выполнение FastAPI startup event handler.")
        await init_db(app, config)

        app.state.reauth_session_dict = dict()
        await init_reauth_checker(app, config)

        logging.info("FastAPI Успешно запущен.")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        logging.debug("Выполнение FastAPI shutdown event handler.")

    return stop_app
