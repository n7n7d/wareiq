from fastapi import FastAPI, Body
from pydantic import BaseModel, validator, Field
from notification_worker import celery_app 

app = FastAPI()

class DataModel(BaseModel):
    order_id: str = Field(..., min_length=1)
    order_status: str = Field(..., in_=["RECIEVED","PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"])
    channel: str = Field(..., min_length=1)
    template: str = Field(..., min_length=1)
    mobile_number: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)

    @validator("order_status")
    def check_order_status(cls, v):
        if v not in ["RECIEVED","PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]:
            raise ValueError("Invalid order status")
        return v


@app.post("/process_order_update")
async def process_order_update(data: DataModel = Body(...)):
    data = data.dict()
    print(data)
    channel = data.get('channel','').lower()
    if channel == 'sms':
        celery_app.send_task("send_sms", args=(data,))
    elif channel == 'email':
        celery_app.send_task("send_email", args=(data,))

    return {"message": "TASK sent to celery for processing"}
