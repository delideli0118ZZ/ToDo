# ----------------------------------------------------------
# 파일명: task.py
# 위치: api/cruds/task.py
# 이 파일은 "할 일(Task)" 관련 데이터 처리 기능(CRUD)을 정의한 곳이다.
# - FastAPI에서 API 요청이 들어오면,
#   실제 DB에 데이터를 저장하거나 불러오는 작업을 수행한다.
# - 이 파일에서는 SQLAlchemy의 비동기 세션(AsyncSession)을 사용한다.
# ----------------------------------------------------------

# ----------------------------------------------------------
# [ import 구문 ]
# 비동기 DB 세션과 Task 모델, Task 스키마를 불러온다.
# ----------------------------------------------------------

# * AsyncSession:
#   - SQLAlchemy에서 DB 작업을 비동기(async)방식으로 수행할 수 있게 해주는 세션 객체
#   - FastAPI에서 async def 함수와 함께 사용하며, commit/refresh 같은 작업 앞에는 await를 붙여야 한다.
from sqlalchemy.ext.asyncio import AsyncSession

# * task_model:
#   - 실제 DB에 저장될 Task 테이블 클래스가 정의되어 있음
# * task_schema:
#   - 사용자의 요청/응답 데이터를 정의한 Pydantic 스키마 클래스
import api.models.task as task_model
import api.schemas.task as task_schema

# ----------------------------------------------------------
# [ 함수: create_task ]
# 사용자가 보낸 "할 일" 정보를 받아서 실제 DB에 저장하는 함수
# ----------------------------------------------------------


# * 함수 정의: async def ... -> 비동기 DB 작업을 위해 async 사용
# * 변환값: 저장된 Task 객체 자체 (id가 포함된 상태로 변환됨)
async def create_task(
    db: AsyncSession, task_create: task_schema.TaskCreate
) -> task_model.Task:
    # * task_create.model_dump():
    #   - Pydantic v2 기준: 스키마 객체를 딕셔너리로 변환하는 메서드
    #   - 예: {"title":"공부하기", "done":False}

    # * Task(**dict): 파이썬의 ** 문법으로 딕셔너리를 key=value 형식으로 풀어서 전달함
    #   - 예: Task(title="공부하기", done=False)
    task = task_model.Task(**task_create.model_dump())

    # * DB에 새 Task 객체를 추가함 (add만 해서는 실제 저장되지 않음)
    db.add(task)

    # * 실제 DB에 저장되도록 commit 실행 (비동기이므로 await 필수)
    await db.commit()

    # * commit 이후 DB가 자동 생성한 id 값을 포함한 최신 데이터를 다시 불러옴
    #   - 예: task.id가 None이었다면, refresh 이후 실제 숫자가 들어오게 됨
    await db.refresh(task)

    # * 최종적으로 저장된 Task 객체를 반환 (API 응답에서 사용됨)
    return task
