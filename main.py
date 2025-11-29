from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from upload import router as upload_router
from ask import router as ask_router

app = FastAPI()
origins = [
    "https://lector-pdfia-81a7qh1fg-blackkengels-projects.vercel.app",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"], 
)

app.include_router(upload_router)
app.include_router(ask_router)
