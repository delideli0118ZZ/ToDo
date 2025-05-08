# -----------------------------------------------------------------
# 파일명: done.py
# 위치: api/routers/done.py
# 이 파일을 할 일(Task)을 완료 처리하거나 완료를 취소하는 기능을 정의합니다.
# - 기능 1: 완료 처리 (PUT 요청)
# - 기능 2: 완료 취소 (DELETE 요청)
# - 요청 주소: /tasks/{할 일 번호}/done
# -----------------------------------------------------------------

# FastAPI 기능들을 불러옵니다
from fastapi import APIRouter, HTTPException, Depends

# - APIRouter: 여러 API 경로(URL)를 그룹으로 묶는 데 사용
# - HTTPException: 오류가 발생했을 때 사용저에게 에러 응답을 보내는 데 사용
# - Depends: 다른 함수(DB 접속 등)에 자동으로 연결해주는 도구

# SQLAlchemy의 비동기 DB 세션을 불러옵니다
from sqlalchemy.ext.asyncio import AsyncSession

# - DB와 연결할 때 비동기 방식으로 작업하기 위해 필요

# 완료 기능에 필요한 스키마(입출력 형식)를 불러옵니다
import api.schemas.done as done_schema

# 완료 기능을 처리하는 CRUD 함수들을 불러옵니다
import api.cruds.done as done_crud

# DB 접속에 필요한 함수 (FastAPI에서 의존성 주입에 사용)
from api.db import get_db


# -----------------------------------------------------------------
# router 객체 생성
# - 여러 API 경로를 하나로 묶어서 관리할 수 있게 도와줍니다
# - main.py에서 이 router를 FastAPI 앱에 등록해서 사용합니다
# -----------------------------------------------------------------
router = APIRouter()


# -----------------------------------------------------------------
# [1] 할 일을 "완료" 상태로 표시하는 API
# - 요청 방식: PUT
# - 요청 주소: /tasks/3/done
#   (3번 할 일을 완료로 표시한다는 의미)
# -----------------------------------------------------------------
@router.put("/tasks/{task_id}/done", response_model=done_schema.DoneResponse)
# task_id는 URL에서 전달받은 숫자 (예: 3번 할 일)
# db는 비동기 DB세션, Depends를 통해 자동으로 주입됨
async def mark_task_as_done(task_id: int, db: AsyncSession = Depends(get_db)):
    # 먼저 해당 할 일이 이미 완료되었는지 확인합니다
    done = await done_crud.get_done(db, task_id=task_id)
    if done is not None:
        raise HTTPException(status_code=400, detail="Done already exists")

    # 완료되지 않았다면 새로 완료로 저장합니다
    return await done_crud.create_done(db, task_id)


# -----------------------------------------------------------------
# [2] 할 일의 완료 상태를 해제하는 API
# - 요청 방식: DELETE
# - 요청 주소: /tasks/3/done
#   (3번 할 일을 완료 취소한다는 의미)
# -----------------------------------------------------------------
@router.delete("/tasks/{task_id}/done", response_model=None)
async def remove_task_as_done(task_id: int, db: AsyncSession = Depends(get_db)):
    # 먼저 완료 상태인지 확인합니다
    done = await done_crud.get_done(db, task_id=task_id)
    if done is None:
        # 완료 상태가 아니라면 삭제할 것이 없으므로 예외 발생
        raise HTTPException(status_code=404, detail="Done not found")

    # 완료 상태라면 삭제 (완료 해제)
    return await done_crud.delete_done(db, original=done)
