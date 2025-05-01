# ------------------------------------------------------------
# 파일명: task.py
# 위치: api/routers/task.py
# 이 파일은 "할 일(To-Do)" 기능을 처리하는 API를 정의한 곳이다.
# - /tasks로 시작하는 주소들을 FastAPI의 APIRouter로 관리한다.
# - 주요 기능: 할 일 목록 조회, 할 일 추가, 수정, 삭제
# ------------------------------------------------------------

# FastAPI에서 여러 개의 URL 경로를 그룹으로 묶어 관리할 수 있게 해주는 도구
from fastapi import APIRouter, Depends, HTTPException

# - APIRouter: 기능별로 URL을 나눠 관리할 수 있게 해줌 (예: /tasks, /users 등)
# - Depends: 다른 함수(예: DB 연결)를 자동으로 실행하고 주입해주는 도구

# * SQLAlchemy의 비동기 세션을 사용하기 위한 도구
from sqlalchemy.ext.asyncio import AsyncSession

# - AsyncSession: await를 사용하는 비동기 DB 작업에 사용됨

# * 우리가 만든 CRUD 함수들을 불러온다 (파일 위치: api/cruds/task.py)
# - 여기에 create_task, update_task 같은 실제 DB 작업 함수를 정의되어 있음
import api.cruds.task as task_crud

# * DB 세션을 자동으로 가져오기 위한 함수 (파일 위치: api/db.py)
# - FastAPI에서 Depends로 연결할 수 있게 준비해둔 함수
# -  비동기 세션(AsyncSession)을 반환함
from api.db import get_db

# * 우리가 정의한 데이터 구조를 불러온다 (파일 위치: api/schemas/task.py)
# - Task: 전체 할 일 데이터를 표현
# - TaskCreate: 사용자가 보낼 입력 데이터 구조
# - TaskCreateResponse: 응답할 때 사용할 데이터 구조 (id 포함)
import api.schemas.task as task_schema

# * router 객체를 만든다.
# - task 목록과 관련된 여러 기능을 이 객체에 모두 담아서
#   나중에 main.py에서 FastAPI 앱에 등록하게 된다.
router = APIRouter()


# ----------------------------------------------------------------
# [1]할 일 목록 조회(GET 방식)
# - 클라이언트가 /tasks 주소로 요청하면 전체 할 일 목록을 반환한다.
# - 아직 DB는 연결하지 않았기 때문에 임시 데이터만 보여준다.
# ----------------------------------------------------------------
@router.get("/tasks", response_model=list[task_schema.Task])
# - response_model: 응답의 데이터 형태를 지정함
# - 여기서는 Task 모델을 여러 개 담은 리스트를 반환한다고 지정함
async def list_tasks(db: AsyncSession = Depends(get_db)):
    # * async: 이 함수는 '비동기 함수'임
    #   - 비동기 함수는 DB와 통신 같은 시간이 오래 걸리는 작업울
    #     기다리지 않고도 다른 작업을 처리할 수 있게 해줌
    #   - 덕분에 FastAPI 서버가 동시에 여러 요청을 효율적으로 처리 가능함

    # * await: 시간이 오래 걸리는 작업을 '기다렸다가' 실행을 이어감
    #   - 여기서는 DB 조회 작업을 기다리는 데 사용함
    return await task_crud.get_tasks_with_done(db)
    # * 실제 DB에서 모든 할 일을 가져오고, 각 할 일이 완료되었는지도 함께 반환함
    # * 완료여부는 'Done 테이블에 해당 할 일이 있는지'로 판단
    #   (외부 조인이라는 방식으로 처리됨 - 모든 할 일을 보여주되, 완료된 것도 함께 표시함)


# -------------------------------------------------------------
# [2] 할 일 추가 (POST 방식)
# - 클라이언트가 Json 형식으로 보낸 데이터(title)를 받아
#   새로운 할 일을 생성하는 기능 (예: {"title": "책 읽기"})
# - 이번에는 예시 데이터가 아니라, 실제 DB에 저장하는 구조로 구현함
# -------------------------------------------------------------
@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
# - task_body: 사용자가 보낸 데이터 요청 본문
# - TaskCreate: 사용자가 보낸 데이터(title만 포함됨)
# - TaskCreateResponse: 응답할 때 포함한 데이터(id 포함)
# - db: FastAPI가 get_db() 함수를 통해 자동으로 주입하는 DB 세션 객체
async def create_task(
    task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
):
    return await task_crud.create_task(db, task_body)
    # * crud 모듈의 create_task() 함수를 호출하여 실제 DB에 저장함
    # * 저장 후 생성된 할 일 (Task)을 반환하며, 그 안에는 id가 포함됨
    #   (예: TaskCreateResponse(id=1, title="책 읽기"))
    #
    # * db: get_db() 함수를 통해 생성된 SQLAlchemy 비동기 세션이 자동으로 들어옴
    #   - FastAPI의 Depends를 사용해 '의존성 주입(Dependency Injection)' 방식으로 처리함
    #   - 함수 안에서 직접 DB 연결을 만들지 않아도 되므로 코드가 더 유연하고 테스트하기 쉬워짐
    #   - 테스트 시에는 get_db 함수를 오버라이드해서 가짜 DB나 테스트용 DB를 넣을 수 있음
    #
    # * 이 구조는 DB 작업(비즈니스 로직)은 crud.py에 따로 만들고,
    #   이 함수는 요청 받고 응답하는 역할만 담당하도록 나눠서 구성함
    #   -> 코드가 더 깔끔하고 관리하기 쉬워짐


# ----------------------------------------------------
# [3] 할 일 수정 (PUT 방식)
# - 경로에 포함된 번호(task_id)에 해당하는 할 일을 수정함
# - 클라이언트가 수정할 내용을 JSON으로 보내면 title을 바꿔주는 역할
# - 실제 DB에서 해당 Task가 존재하는지 확인한 뒤 수정 진행
# ----------------------------------------------------
@router.put("/tasks/{task_id}", response_model=task_schema.TaskCreateResponse)
# - task_id: URL 경로에 포함된 숫자 (수정 대상 할 일 번호)
# - task_body: 수정할 내용을 담은 요청 본문 (title)


async def update_task(
    task_id: int, task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
):
    task = await task_crud.get_task(db, task_id=task_id)
    # * DB에서 해당 task_id에 맞는 Task를 조회함

    # * if: 조건문 -> 특정 조건이 참(True)이면 아래 코드를 실행함
    if task is None:
        # * raise: 예외(오류)를 의도적으로 발생시킴
        #   - 여기서는 task가 존재하지 않느면 404 오류를 발생시킴
        #   - FastAPI는 raise된 HTTPException을 자동으로 처리해서
        #     클라이언트에 "할 일을 찾을 수 없음"이라는 에러 응답을 보냄
        raise HTTPException(status_code=404, detail="Task not found")

    return await task_crud.update_task(db, task_body, original=task)
    # * 기존 Task 객체(original)의 title을 수정하고, 수정된 결과를 반환함


# ---------------------------------------------------------------
# [4] 할 일 삭제 (DELETE 요청)
# - task_id: 삭제할 할 일의 번호
# - 이 함수는 아직 DB가 없기 때문에 동작은 하지 않지만 구조만 정의함
# ----------------------------------------------------------
@router.delete("/tasks/{task_id}")
# - task_id: 삭제할 일의 번호
# - response_model이 없으므로 별도 응답내용 없이 처이 가능 (204 No Content)
async def delete_task(task_id: int):
    return
    # * 실제 구현에서는 crud.py의 삭제 함수를 호출하고,
    #   성공 시 상태 코드(예: 204)니 메시지를 응답으로 보낼 수 있음
