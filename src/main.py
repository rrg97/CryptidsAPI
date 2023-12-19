from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from web import explorer, creature, user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ui.cryptids.com"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)
app.include_router(explorer.router)
app.include_router(creature.router)
app.include_router(user.router)

@app.get('/')
def top():
    return "top here"

@app.get("/echo/{thing}")
def echo(thing):
    return f"echoing {thing}"

@app.get("/test_cors")
def test_cors(request: Request):
    print(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        reload=True
    )