from fastapi import FastAPI

app = FastAPI(
    title="Travel Planner API",
    description=(
        "Manage travel projects and places. "
        "Places are sourced from the Art Institute of Chicago API."
    ),
    version="1.0.0",
)
