import React, { useEffect, useState } from "react";
import { initModals } from 'flowbite'

const TodosContext = React.createContext({
  todos: [], fetchTodos: () => { }
})

function TextInput({ value = "", placeholder, onChange }: { value?: string, placeholder: string, onChange: React.ChangeEventHandler<HTMLInputElement> }) {
  return (
    <input
      type="text"
      className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      value={value}
      placeholder={placeholder}
      onChange={onChange}
    >
    </input>
  )
}

function AddTodo() {
  const [item, setItem] = React.useState("")
  const { todos, fetchTodos } = React.useContext(TodosContext)

  const handleInput = (event: React.FormEvent<HTMLInputElement>) => {
    setItem((event.target as HTMLInputElement).value)
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    fetch("http://localhost:8000/todo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "item": item
      })
    }).then(fetchTodos)
  }

  return (
    <form onSubmit={handleSubmit}>
      <TextInput
        value={item}
        placeholder="Add a todo item"
        onChange={handleInput}
      />
    </form>
  )
}

function UpdateTodo({ item, id }: { item: string, id: string }) {
  useEffect(() => {
    initModals()
  });

  const [todo, setTodo] = useState(item)
  const { fetchTodos } = React.useContext(TodosContext)

  const updateTodo = async () => {
    await fetch(`http://localhost:8000/todo/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item: todo })
    })
    await fetchTodos()
  }

  const modalId = "popup-modal-" + id

  return (
    <>
      <button
        data-modal-target={modalId}
        data-modal-toggle={modalId}
        className="bg-blue-500 hover:bg-blue-700 text-white py-1 mr-1 px-4 rounded"
      >
        Update
      </button>

      <div id={modalId}
        tabIndex={-1}
        className="fixed top-0 left-0 right-0 z-50 hidden p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-[calc(100%-1rem)] max-h-full"
      >
        <div className="relative w-full max-w-md max-h-full">
          <div className="relative bg-white rounded-lg shadow dark:bg-gray-700">
            <button type="button"
              className="absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center dark:hover:bg-gray-800 dark:hover:text-white"
              data-modal-hide={modalId}
            >
              <svg aria-hidden="true" className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>
              <span className="sr-only">Close modal</span>
            </button>
            <div className="p-6 text-center">
              <h3 className="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">Update todo</h3>
              <TextInput
                value={todo}
                placeholder="Add a todo item"
                onChange={e => setTodo(e.target.value)}
              />
            </div>
            <div className="flex items-center p-6 space-x-2 border-t border-gray-200 rounded-b dark:border-gray-600">
              <button className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-4 rounded"
                onClick={updateTodo}
                data-modal-hide={modalId}
              >
                Save
              </button>
              <button className="text-gray-500 bg-white hover:bg-gray-100 py-1 px-4 rounded border border-gray-200"
                onClick={updateTodo}
                data-modal-hide={modalId}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

function DeleteTodo({ id }: { id: string }) {
  const { fetchTodos } = React.useContext(TodosContext)

  const deleteTodo = async () => {
    await fetch(`http://localhost:8000/todo/${id}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "id": id }),
    })
    await fetchTodos()
  }

  return (
    <button className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-4 rounded"
      onClick={deleteTodo}
    >
      Delete
    </button>
  )
}

function TodoHelper({ item, id, fetchTodos }: { item: string, id: string, fetchTodos: () => {} }) {
  return (
    <li key={id} className="flex justify-between gap-x-6 py-5">
      <div className="flex gap-x-4">
        <div className="text-center text-5xl">
          👋
        </div>
        <div className="min-w-0 flex-auto">
          <p className="text-sm font-semibold leading-6 text-gray-900">{item}</p>
          <UpdateTodo item={item} id={id} />
          <DeleteTodo id={id} />
        </div>
      </div>
    </li>
  )
}

export default function Todos() {
  const [todos, setTodos] = useState([])
  const fetchTodos = async () => {
    const response = await fetch("http://localhost:8000/todo")
    const todos = await response.json()
    setTodos(todos.data)
  }
  useEffect(() => {
    fetchTodos()
  }, [])
  return (
    <TodosContext.Provider value={{ todos, fetchTodos }}>
      <AddTodo />
      <ul>
        {
          todos.map((todo: { item: string, id: string }) => (
            <TodoHelper item={todo.item} id={todo.id} key={todo.id} fetchTodos={fetchTodos} />
          ))
        }
      </ul>
    </TodosContext.Provider>
  )
}
