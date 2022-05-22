import os
from decimal import Decimal
from datetime import datetime

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_utils.tasks import repeat_every

from sqlalchemy.orm import Session

from starlette import status
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

import models
from database import engine, SessionLocal, get_db
from utils import get_google_sheet, get_quotes, send_message_to_telegram

google_sheet_name = os.environ.get('GOOGLE_SHEET_NAME')

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db)):
    """Панель администрирования"""
    records = db.query(models.Record).all()

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "records": records}
    )


@app.get("/update", response_class=HTMLResponse)
async def update():
    """Обновление из панели администрирования"""
    await update_backgound()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)


@app.on_event("startup")
@repeat_every(seconds=60*60)
async def update_backgound():
    """Фоновое обновление из таблицы на google sheets"""
    with SessionLocal() as session:
        usd_quote = get_quotes()
        print(usd_quote)

        records_from_db = session.query(models.Record) \
            .with_entities(models.Record.order).all()

        records_from_db = [record[0] for record in records_from_db]

        records = get_google_sheet(google_sheet_name)
        records_from_sheet = []

        for record in records[1:]:

            order = int(record[1])
            price_usd = Decimal(record[2])
            delivery_time = datetime.strptime(record[3], '%d.%m.%Y').date()
            price_rub = price_usd * usd_quote

            records_from_sheet.append(order)

            if order not in records_from_db:
                record_model = models.Record()
                record_model.order = order
                record_model.delivery_time = delivery_time
                record_model.price_usd = price_usd
                record_model.price_rub = price_rub
            else:
                record_model = session.query(models.Record) \
                    .filter(models.Record.order == order).first()
                record_model.delivery_time = delivery_time

            session.add(record_model)

        records_to_delete = set(records_from_db) - set(records_from_sheet)

        if records_to_delete:
            session.query(models.Record) \
                .filter(models.Record.order.in_(records_to_delete)).delete()

        session.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)


@app.on_event("startup")
@repeat_every(seconds=60*60*24)
async def notify():
    """Проверка срока поставки"""
    with SessionLocal() as session:
        today = datetime.today().date()
        records = session.query(models.Record) \
            .filter(models.Record.delivery_time < today) \
            .filter(models.Record.notify == False).all()

        for record in records:
            if send_message_to_telegram(record.order):
                record.notify = True
                session.add(record)

        session.commit()
