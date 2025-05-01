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

# * select:
#   - SQLAlchemy에서 SELECT 쿼리를 만들 때 사용
# * Result:
#   - 쿼리 실행 결과를 담는 객체 (fetchall() 또는 all()로 결과 추출 가능)
from sqlalchemy import select
from sqlalchemy.engine import Result

# ----------------------------------------------------------
# [ 함수: create_task ]
# 사용자가 보낸 "할 일" 정보를 받아서 실제 DB에 저장하는 함수
# ----------------------------------------------------------


# * 함수 정의: async def ... -> 비동기 DB 작업을 위해 async 사용
#   - 시간이 오래 걸리는 작업(예: DB 저장 등)에도 앱이 멈추지 않도록 도와줌
# * 매개변수:
#   - db: 비동기 DB 세션 (AsyncSession)
#   - task_create: 사용자 요청으로 받은 할 일(Task) 생성용 대이터 (Pydantic 스키마)
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

    # * 실제 DB에 저장되도록 commit 실행
    # * await: DB 작업이 끝날 때까지 기다렸다가 다음 줄을 실행함
    await db.commit()

    # * commit 이후 DB가 자동 생성한 id 값을 포함한 최신 데이터를 다시 불러옴
    await db.refresh(task)

    # * 최종적으로 저장된 Task 객체를 반환 (API 응답에서 사용됨)
    return task


# ---------------------------------------------------------
# [ 함수: get_task ]
# 특정 id에 해당하는 할 일을 하나만 가져오는 함수
# - 할 일이 존재하지 않으면 None을 반환한다
# ---------------------------------------------------------


# * 함수 정의: async def ... -> 비동기 DB 작업을 위해 async 사용
# * 매개변수:
#   - db: 비동기 DB 세션
#   - task_id: 조회할 Task의 고유 번호
# * 반환값: Task 객체 또는 None
async def get_task(db: AsyncSession, task_id: int) -> task_model.Task | None:
    result: Result = await db.execute(
        # * await: DB에 쿼리를 보낸 뒤, 결과가 올 때까지 기다림
        select(task_model.Task).filter(task_model.Task.id == task_id)
        # * SELECT 쿼리: Task 테이블에서 id가 task_id인 항목을 찾음
    )
    return result.scalars().first()
    # * result.scalars(): 결과 중 실제 모델 객체만 추출
    # * .first(): 첫 번째 결과만 반환 (없으면 None 반환됨)


# ---------------------------------------------------------
# [ 함수: update_task ]
# 기존 할 일(Task) 객체를 받아 내용을 수정하고 DB에 반영하는 함수
# ---------------------------------------------------------


# * 함수 정의: async def ... -> 비동기 DB 작업을 위해 async 사용
# * 매개변수:
#   - db: 비동기 DB 세션
#   - task_create: 수정할 내용을 담고 있는 Pydantic 스키마 (title만 포함)
#   - original: 기존 DB에서 가져온 Task 객체
# * 반환값: 수정된 Task 객체
async def update_task(
    db: AsyncSession, task_create: task_schema.TaskCreate, original: task_model.Task
) -> task_model.Task:
    original.title = task_create.title
    # * 기존 Task 객체의 title 값을 수정함

    db.add(original)
    # * 수정된 객체를 세션에 등록 (SQLAlchemy는 상태 변경을 추적함)

    await db.commit()
    # * 실제 DB에 반영함 (비동기이므로 await 필수)

    await db.refresh(original)
    # * 최신 상태의 데이터를 다시 불러옴 (예: 다른 필드가 자동 변경된 경우)

    return original
    # * 수정 완료된 Task 객체를 반환함

# ----------------------------------------------------------------
# * 매개변수:
#   - db: 비동기 DB 세션






# ----------------------------------------------------------
# [ 함수: get_tasks_with_done ]
# 모든 할 일을 불러오고, 각 할 일이 완료되었는지도 함계 알려주는 함수
# - '완료 여부'는 Done 테이블에 데이터가 있는지를 기준으로 판단함
# ----------------------------------------------------------


# * 반환값: (id, title, done) 형식의 튜플 리스트
#   - 예: [(1, "공부하기", True), (2, "청소하기", False), ...]
async def get_tasks_with_done(db: AsyncSession) -> list[tuple[int, str, bool]]:
    result: Result = await db.execute(
        select(
            task_model.Task.id,  # 할 일 번호
            task_model.Task.title,  # 할 일 제목
            (task_model.Done.id.isnot(None)).label("done"),
            # * Done 테이블에 이 할 일(Task)의 완료 기록이 없으면 -> True
            # * Done 테이블에 없으면 -> False (아직 완료 안 된 상태)
            # 이건 SQL에서 '외부 조인'이라는 방법을 써서 확인함
            #   -> 쉽게 말해, '모든 할 일'을 다 불러오고, 그 중에서 완료된 것도 표시하는 방식
        ).outerjoin(
            task_model.Done
        )  # outerjoin: 할 일이 완료됐든 안 됐든 모두 가져오기
    )

    return result.all()
    # 쿼리 결과를 리스트로 반환함
