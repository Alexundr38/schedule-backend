from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.routers import user_router, global_group_router, teacher_router, group_router, subject_router

app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(global_group_router.router)
app.include_router(teacher_router.router)
app.include_router(group_router.router)
app.include_router(subject_router.router)

@app.get("/")
def root():
    return {"message": "API работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)