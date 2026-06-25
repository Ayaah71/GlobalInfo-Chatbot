from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "GlobalInfo Chatbot API Running"}

@app.get("/country/{country_name}")
def get_country(country_name: str):

    url = f"https://restcountries.com/v3.1/name/{country_name}"

    response = requests.get(url)

    if response.status_code != 200:
        return {"message": "Country not found"}

    data = response.json()[0]

    return {
        "country": data["name"]["common"],
        "capital": data["capital"][0],
        "population": data["population"],
        "currency": list(data["currencies"].keys())[0]
    }