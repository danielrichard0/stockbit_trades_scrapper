from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import service 
import uvicorn
from pydantic import BaseModel
from datetime import date


app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReqBaseBroksum(BaseModel):
    first_date: date
    second_date: date    

class ReqBrokerSummary(ReqBaseBroksum):
    broker_codes: list[str]
    stocks: list[str]

class ReqBrokerSummaryScreened(ReqBaseBroksum):
    limit: int 
    page: int    

@app.post('/broker-summary')
def get_broksum(req: ReqBrokerSummary):
    req_dict = req.model_dump()
    return service.get_broker_summary(req_dict)

@app.post('/broker-summary-screened')
def get_broksum(req: ReqBrokerSummaryScreened):
    req_dict = req.model_dump()
    print('req_dict : ', req_dict)
    return service.get_broker_summary_screened(req_dict)

@app.get('/get-all-stocks')
def get_all_stocks():
    return service.get_all_stocks()

@app.get('/get-all-brokers')
def get_all_brokers():
    return service.get_all_brokers()

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)
