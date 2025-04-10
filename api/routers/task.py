# ------------------------------------------------------------
# 할 일 기능을 담당하는 파일 (task.py)
# 이 파일은 /task 관련 주소 (GET, POST, PUT, DELETE)를 처리한다.
# ------------------------------------------------------------

# FastAPI에서 URL 주소를 모아 관리할 수 있는 도구를 불러온다.
from fastapi import APIRouter

# 우리가 만든 Task 데이터 구조를 불러온다.
# Task 모델은 api/schemas/task.py 파일에 있으며,
# 어떤 정보(id, title, done)를 담는지 정의되어 있다.
import api.schemas.task as task_schema

# router는 여러 기능(API 주소를)을 모아서 저장해두는 상자(모음집) 같은 역할을 한다.
router = APIRouter()


# ----------------------------------------------------------------
# 할 일 목록 보기 기능 (GET 방식)
# 예: /tasks 주소로 접속하면 전체 할일 목록을 보여준다.
# ----------------------------------------------------------------
@router.get("/tasks", response_model=list[task_schema.Task])
# response_model -> 응답의 데이터 모양을 정해주는 옵션
# 여기서는 여러 개의 Task 모델을 리스트 형태로 응답함
async def list_tasks():
    return [task_schema.Task(id=1, title="첫 번째 ToDo 작업", done=False)]
    # 실제 DB가 없으므로 예시 데이터를 직접 만들어 응답으로 보낸다.
    # task_schema.Task(...) 형태로 모델에 맞춰 값을 채운다.


# -------------------------------------------------------------
# 새로운 할 일 추가 기능 (POST 방식)
# 예: 사용자가 할 일을 작성해서 보내면 서버에 저장하도록 준비
# -------------------------------------------------------------
@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
# task_body: 클라이언트가 보낸 할 일 데이터 (title만 있음)
# TaskCreateResponse: 저장된 결과로 id를 포함해 응답
async def create_task(task_body: task_schema.TaskCreate):
    return task_schema.TaskCreateResponse(id=1, **task_body.dict())
    # DB가 없으므로 임시로 id=1을 부여하고, 받은 데이터를 그대로 반환

    # ----------------------------------------------------
    # 할 일 수정 기능 (PUT 방식)
    # 예ㅣ /task/3 -> 번호가 3인 할 일의 내용을 바꾼다.
    # ----------------------------------------------------
    @router.put("/tasks/{task_id}")
    async def update_task():
        pass  # 추후 구현 예정


# ---------------------------------------------------------------
# 할 일 삭제 기능 (DELETE 방식)
# 예: /task/3 -> 번호가 3인 할 일을 삭제한다.
# ------------------------------------------------------
@router.delete("/tasks/{task_id}")
async def delete_task():
    pass
