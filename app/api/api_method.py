import ujson
import joblib
import numpy as np
import pandas as pd

from decimal import Decimal
from datetime import date
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Response
from sqlalchemy.engine.result import Result
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.predict_model import ModelStructure
from app.api.database import get_async_db
from pathlib import Path


PATH_FILE = Path(__file__)
load_dotenv()

router = APIRouter(prefix="/real_data", tags=["Realestate"])


@router.post("predict")
def predict_house_price(data: ModelStructure):
    body = data.model_dump()

    file_model = "app/api/model.pkl"
    model = joblib.load(file_model)

    create_df = pd.DataFrame(body)

    predicted = model.predict(create_df)
    return np.expm1(predicted)


@router.get("/return_data_db")
async def return_data_db(db: AsyncSession = Depends(get_async_db)):

    def convert_value(value):
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, date):
            return value.isoformat()
        else:
            return value

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
