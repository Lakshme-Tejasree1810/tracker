# from fastapi import FastAPI, Request, Form, HTTPException, File, UploadFile
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
# from pymongo import MongoClient
# from fastapi.middleware.cors import CORSMiddleware
# from io import BytesIO
# import re
# from bson import ObjectId
# import os
# import matplotlib.pyplot as plt
# import io
# import base64

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["localhost"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# templates = Jinja2Templates(directory="templates")

# client = MongoClient('mongodb://localhost:27017/')
# db = client['homepage']
# collection = db['users']
# tasks_collection=db['tasks']

# @app.get("/")
# async def home(request: Request):
#     return templates.TemplateResponse("home.html", {"request": request})

# @app.get("/login")
# async def login(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.get("/register")
# async def get_register(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})

# def is_valid_email(email):
#     pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
#     return re.match(pattern, email) is not None

# def create_user(username, email, password, role):
#     user = {
#         "_id": str(ObjectId()),
#         "username": username,
#         "email": email,
#         "password": password,
#         "role": role
#     }
#     collection.insert_one(user)
#     return user["_id"]

# def check_login(email, password):
#     user = collection.find_one({"email": email, "password": password})
#     return user

# @app.post("/login")
# async def login(email: str = Form(...), password: str = Form(...)):
#     user = check_login(email, password)
#     if user:
#         return JSONResponse(content={"message": "Login successful", "role": user["role"]})
#     else:
#         return JSONResponse(content={"message": "Login failed"}, status_code=401)

# @app.post("/register")
# def post_register(
#     username: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...),
#     repassword: str = Form(...),
#     role: str = Form(...)
# ):
#     if password != repassword:
#         return JSONResponse(content={"message": "Passwords do not match"}, status_code=400)
    
#     if not is_valid_email(email):
#         return JSONResponse(content={"message": "Invalid email format"}, status_code=400)
    
#     existing_user = collection.find_one({"$or": [{"username": username}, {"email": email}]})
#     if existing_user:
#         return JSONResponse(content={"message": "Username or email already taken"}, status_code=400)
    
#     if role not in ["manager", "user"]:
#         return JSONResponse(content={"message": "Invalid role"}, status_code=400)
    
#     user_id = create_user(username, email, password, role)
#     return JSONResponse(content={"message": "Registration successful", "user_id": user_id})


# @app.get("/admindashboard")
# async def admin_dashboard(request: Request):
#     return templates.TemplateResponse("admindashboard.html", {"request": request})

# @app.get("/userdashboard")
# async def user_dashboard(request: Request):
#     return templates.TemplateResponse("userdashboard.html", {"request": request})

# @app.get("/logout")
# async def logout(request: Request):
#     return RedirectResponse(url="/")

# #Report generation
# @app.post("/generate_report")
# def generate_text_report():
#     # Fetch tasks data
#     in_progress_tasks = tasks_collection.find({"status": "In Progress"})
#     completed_tasks = tasks_collection.find({"status": "Completed"})
#     print("tasks completed vs progress", completed_tasks,in_progress_tasks)
#     # Build the report
#     report = []
#     report.append("Task Report: In Progress vs Completed")
#     report.append("=" * 40)
    
#     # Add in-progress tasks
#     report.append("\nIn Progress Tasks:")
#     for task in in_progress_tasks:
#         report.append(f"- Title: {task['title']}")
#         report.append(f"  Assigned To: {task['assignedTo']}")
#         report.append(f"  Priority: {task['priority']}")
#         report.append(f"  Due Date: {task['dueDate']}")
#         report.append("")
    
#     # Add completed tasks
#     report.append("\nCompleted Tasks:")
#     for task in completed_tasks:
#         report.append(f"- Title: {task['title']}")
#         report.append(f"  Assigned To: {task['assignedTo']}")
#         report.append(f"  Priority: {task['priority']}")
#         report.append(f"  Completed Date: {task['completedDate']}")
#         report.append("")

#     report_content = "\n".join(report)
#     return JSONResponse(content={"message": "report generation completed", "report":report_content})

# @app.post("/generate_task_report")
# def generate_task_report():
#     # Fetch tasks data
#     in_progress_count = tasks_collection.count_documents({"status": "In Progress"})
#     completed_count = tasks_collection.count_documents({"status": "Completed"})
    
#     # Data for pie chart
#     labels = ['In Progress', 'Completed']
#     counts = [in_progress_count, completed_count]
#     colors = ['skyblue', 'lightgreen']
    
#     # Plot the pie chart
#     plt.figure(figsize=(6, 6))
#     plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
#     plt.title('Task Report: In Progress vs Completed')
#     plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

#     # Save the chart to a BytesIO buffer
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     buf.seek(0)
#     plt.close()

#     # Encode the image to base64
#     image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
#     buf.close()

#     # Return the image as a base64 string
#     return JSONResponse(content={
#         "message": "Task report generated successfully",
#         "chart": f"data:image/png;base64,{image_base64}"
#     })

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import re
from bson import ObjectId
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
client = MongoClient('mongodb://localhost:27017/')
db = client['homepage']
users_collection = db['users']
tasks_collection = db['tasks']

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def create_user(username, email, password, role):
    user = {
        "_id": str(ObjectId()),
        "username": username,
        "email": email,
        "password": password,
        "role": role
    }
    users_collection.insert_one(user)
    return user["_id"]

def check_login(email, password):
    user = users_collection.find_one({"email": email, "password": password})
    return user

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    user = check_login(email, password)
    if user:
        return JSONResponse(content={"message": "Login successful", "role": user["role"], "username": user["username"]})
    else:
        return JSONResponse(content={"message": "Login failed"}, status_code=401)

@app.get("/logout")
async def logout(request: Request):
    return RedirectResponse(url="/")

@app.post("/register")
def post_register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    repassword: str = Form(...),
    role: str = Form(...)
):
    if password != repassword:
        return JSONResponse(content={"message": "Passwords do not match"}, status_code=400)
    
    if not is_valid_email(email):
        return JSONResponse(content={"message": "Invalid email format"}, status_code=400)
    
    existing_user = users_collection.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        return JSONResponse(content={"message": "Username or email already taken"}, status_code=400)
    
    if role not in ["manager", "user"]:
        return JSONResponse(content={"message": "Invalid role"}, status_code=400)
    
    user_id = create_user(username, email, password, role)
    return JSONResponse(content={"message": "Registration successful", "user_id": user_id})

@app.get("/admindashboard")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admindashboard.html", {"request": request})

@app.get("/userdashboard")
async def user_dashboard(request: Request):
    return templates.TemplateResponse("userdashboard.html", {"request": request})

@app.post("/create_task")
async def create_task(
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...),
    status: str = Form(...),
    due_date: str = Form(...),
    assigned_to: str = Form(...)
):
    assigned_to_list = [user.strip() for user in assigned_to.split(',')]
    task = {
        "_id": str(ObjectId()),
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "dueDate": due_date,
        "assignedTo": assigned_to_list,
        "created_at": datetime.now().isoformat()
    }
    tasks_collection.insert_one(task)
    return JSONResponse(content={"message": "Task created successfully", "task_id": task["_id"]})

@app.get("/get_tasks")
async def get_tasks(assigned_to: str = None, priority: str = None, due_date: str = None):
    query = {}
    if assigned_to:
        query["assignedTo"] = assigned_to
    if priority:
        query["priority"] = priority
    if due_date:
        query["due_date"] = due_date
    
    tasks = list(tasks_collection.find(query))
    for task in tasks:
        task["_id"] = str(task["_id"])
    print("tasks",tasks)
    return JSONResponse(content=tasks)

@app.put("/update_task/{task_id}")
async def update_task(
    task_id: str,
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...),
    status: str = Form(...),
    due_date: str = Form(...),
    assigned_to: str = Form(...)
):
    assigned_to_list = [user.strip() for user in assigned_to.split(',')]
    updated_task = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "dueDate": due_date,
        "assignedTo": assigned_to_list
    }
    result = tasks_collection.update_one({"_id": task_id}, {"$set": updated_task})
    if result.modified_count > 0:
        return JSONResponse(content={"message": "Task updated successfully"})
    else:
        return JSONResponse(content={"message": "Task not found"}, status_code=404)

@app.delete("/delete_task/{task_id}")
async def delete_task(task_id: str):
    result = tasks_collection.delete_one({"_id": task_id})
    if result.deleted_count > 0:
        return JSONResponse(content={"message": "Task deleted successfully"})
    else:
        return JSONResponse(content={"message": "Task not found"}, status_code=404)

@app.get("/get_users")
async def get_users():
    users = list(users_collection.find({}, {"_id": 1, "username": 1}))
    for user in users:
        user["_id"] = str(user["_id"])
    return JSONResponse(content=users)
# class Task(BaseModel):
#     title: str
#     description: str
#     priority: str  # 'High', 'Medium', 'Low'
#     status: str  # 'Pending', 'In Progress', 'Completed'
#     due_date: str  # 'YYYY-MM-DDTHH:MM:SS' format (ISO 8601), e.g., '2024-03-15T12:00:00'
#     assignee: Optional[str] = None  # Optional assignee

# # Task model for returning tasks to the client (with id as string)
# class TaskInDB(Task):
#     id: str  # 'id' will be the string version of MongoDB's _id

# # Helper function to convert MongoDB ObjectId to string
# def task_to_dict(task) -> dict:
#     task_dict = task.copy()
#     task_dict["id"] = str(task["_id"])  # Convert MongoDB ObjectId to string
#     if isinstance(task["due_date"], datetime):
#         task_dict["due_date"] = task["due_date"].isoformat()  # Ensure due_date is ISO 8601 string
#     del task_dict["_id"]  # Remove MongoDB-specific _id field
#     return task_dict

# # CRUD Operations

# # Create a task
# @app.post("/tasks/", response_model=TaskInDB)
# async def create_task(task: Task):
#     # Convert the due_date string to a datetime object
#     task_dict = task.model_dump()
#     try:
#         task_dict["due_date"] = datetime.fromisoformat(task_dict["due_date"])  # Convert string to datetime
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid due_date format. Please use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)")

#     # Insert task into MongoDB
#     result = tasks_collection.insert_one(task_dict)

#     # Fetch the inserted task and return it
#     inserted_task = tasks_collection.find_one({"_id": result.inserted_id})
    
#     # Trigger task update
#     from fastapi.responses import JSONResponse
#     response = JSONResponse(content=task_to_dict(inserted_task))
#     response.headers["X-Task-Updated"] = "true"
#     return response

# # Get all tasks
# @app.get("/tasks/", response_model=List[TaskInDB])
# async def get_all_tasks():
#     tasks = tasks_collection.find()  # Fetch all tasks from MongoDB
#     return [task_to_dict(task) for task in tasks]

# # Get task by ID
# @app.get("/tasks/{task_id}", response_model=TaskInDB)
# async def get_task_by_id(task_id: str):
#     task = tasks_collection.find_one({"_id": ObjectId(task_id)})
#     if task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return task_to_dict(task)

# # Update a task by ID
# @app.put("/tasks/{task_id}", response_model=TaskInDB)
# async def update_task(task_id: str, task: Task):
#     update_data = task.dict(exclude_unset=True)  # Convert Pydantic model to dict
    
#     # Fetch the existing task
#     existing_task = tasks_collection.find_one({"_id": ObjectId(task_id)})
#     if existing_task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     # If due_date is not provided in update_data, use the existing due_date
#     if "due_date" not in update_data:
#         if isinstance(existing_task["due_date"], datetime):
#             update_data["due_date"] = existing_task["due_date"]
#         else:
#             update_data["due_date"] = existing_task["due_date"]
#     else:
#         try:
#             update_data["due_date"] = datetime.fromisoformat(update_data["due_date"])
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid due_date format. Please use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)")
    
#     # Update the task in MongoDB
#     result = tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": update_data})
    
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     updated_task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    
#     # Trigger task update
#     from fastapi.responses import JSONResponse
#     response = JSONResponse(content=task_to_dict(updated_task))
#     response.headers["X-Task-Updated"] = "true"
#     return response

# # Delete a task by ID
# @app.delete("/tasks/{task_id}", response_model=TaskInDB)
# async def delete_task(task_id: str):
#     task = tasks_collection.find_one({"_id": ObjectId(task_id)})
#     if task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     task_to_return = task_to_dict(task)
#     tasks_collection.delete_one({"_id": ObjectId(task_id)})
#     return task_to_return
 #Report generation
@app.post("/generate_report")
def generate_text_report():
    # Fetch tasks data
    in_progress_tasks = tasks_collection.find({"status": "In Progress"})
    completed_tasks = tasks_collection.find({"status": "Completed"})
    print("tasks completed vs progress", completed_tasks,in_progress_tasks)
    # Build the report
    report = []
    report.append("Task Report: In Progress vs Completed")
    report.append("=" * 40)
    
    # Add in-progress tasks
    report.append("\nIn Progress Tasks:")
    for task in in_progress_tasks:
        report.append(f"- Title: {task['title']}")
        report.append(f"  Assigned To: {task['assignedTo']}")
        report.append(f"  Priority: {task['priority']}")
        report.append(f"  Due Date: {task['dueDate']}")
        report.append("")
    
    # Add completed tasks
    report.append("\nCompleted Tasks:")
    for task in completed_tasks:
        report.append(f"- Title: {task['title']}")
        report.append(f"  Assigned To: {task['assignedTo']}")
        report.append(f"  Priority: {task['priority']}")
        report.append(f"  Completed Date: {task['completedDate']}")
        report.append("")

    report_content = "\n".join(report)
    return JSONResponse(content={"message": "report generation completed", "report":report_content})

@app.post("/generate_task_report")
def generate_task_report():
    # Fetch tasks data
    in_progress_count = tasks_collection.count_documents({"status": "In Progress"})
    completed_count = tasks_collection.count_documents({"status": "Completed"})
    
    # Data for pie chart
    labels = ['In Progress', 'Completed']
    counts = [in_progress_count, completed_count]
    colors = ['skyblue', 'lightgreen']
    
    # Plot the pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    plt.title('Task Report: In Progress vs Completed')
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

    # Save the chart to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Encode the image to base64
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    # Return the image as a base64 string
    return JSONResponse(content={
        "message": "Task report generated successfully",
        "chart": f"data:image/png;base64,{image_base64}"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

