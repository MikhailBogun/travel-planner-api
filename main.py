from fastapi import FastAPI

from app.routers import places, projects

app = FastAPI(
    title="Travel Planner API",
    description=(
        "Manage travel projects and places. "
        "Places are sourced from the Art Institute of Chicago API."
    ),
    version="1.0.0",
)

app.include_router(projects.router)
app.include_router(places.router)
