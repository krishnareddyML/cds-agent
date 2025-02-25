from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app import cds_agent_router

import os
import base64
import logfire

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# Example route
@app.get("/")
async def say_hello_to_project():
    return {"message": "Welcome to CDS AGENT FAST API!"}

# Roter files inclusion
app.include_router(cds_agent_router.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    