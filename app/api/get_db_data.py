import ujson

from decimal import Decimal
from datetime import date
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Response
from sqlalchemy.engine.result import Result
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.database import get_async_db


load_dotenv()

router = APIRouter(prefix="/real_data", tags=["Realestate"])


def convert_value(value):
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, date):
        return value.isoformat()
    else:
        return value


@router.get("/return_data_db")
async def return_data_db(db: AsyncSession = Depends(get_async_db)):

    query = text(
        """
            SELECT * FROM public.imoveis_jp_scrape
        """
    )

    result: Result = await db.execute(query)

    rows = result.fetchall()

    if not rows:
        return Response(content="[]", media_type="application/json")

    columns = result.keys()

    result_json = [
        {key: convert_value(value) for key, value in zip(columns, row)} for row in rows
    ]

    return Response(content=ujson.dumps(result_json), media_type="application/json")
