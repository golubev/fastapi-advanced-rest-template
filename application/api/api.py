from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


todos = [
    {"id": 1, "item": "Read a book."},
    {"id": 2, "item": "Cycle around town."},
]

id_sequence = max(todo_item["id"] for todo_item in todos) + 1

application = FastAPI()

origins = ["http://localhost:3000", "localhost:3000"]


application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@application.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}


@application.get("/todo", tags=["todos"])
async def get_todos() -> dict:
    return {"data": todos}


@application.post("/todo", tags=["todos"])
async def add_todo(todo: dict) -> dict:
    global id_sequence
    todo["id"] = id_sequence
    id_sequence += 1
    todos.append(todo)
    return {"data": {"Todo added."}}


@application.put("/todo/{id}", tags=["todos"])
async def update_todo(id: int, body: dict) -> dict:
    for todo in todos:
        if todo["id"] == id:
            todo["item"] = body["item"]
            return {"data": f"Todo with id {id} has been updated."}

    return {"data": f"Todo with id {id} not found."}


@application.delete("/todo/{id}", tags=["todos"])
async def delete_todo(id: int) -> dict:
    for todo in todos:
        if todo["id"] == id:
            todos.remove(todo)
            return {"data": f"Todo with id {id} has been removed."}

    return {"data": f"Todo with id {id} not found."}
