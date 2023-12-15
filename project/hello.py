from fastapi import FastAPI

app = FastAPI()

@app.get('/hi')
def greet(who, status_code=200):
    return f"Hello? {who}?"