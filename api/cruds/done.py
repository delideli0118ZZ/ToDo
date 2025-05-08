# -----------------------------------------------------------------
# 파일명: done.py
# 목적: 할 일이 완료되었는지(Done 상태)를 데이터베이스에서
#       조회, 생성, 삭제하는 기능을 정의합니다.
# 사용 기술: SQLAlchemy (비동기 방식), FastAPI에서 사용됨
# -----------------------------------------------------------------

from sqlalchemy import select  # DB에서 데이터 조회할 때 사용
from sqlalchemy.engine import Result  # 조회 결과 타입
from sqlalchemy.ext.asyncio import AsyncSession  # 비동기 DB 접속을 위한 세션

# task_model 안에 정의된 Done 모델을 불러옵니다
import api.models.task as task_model


# -----------------------------------------------------------------
# [1] 완료된 할 일을 조회하는 함수
# - 특정 task_id에 해당하는 Done 데이터를 DB에서 찾습니다.
# - 없으면 None을 반환합니다.
# -----------------------------------------------------------------
async def get_done(db: AsyncSession, task_id: int) -> task_model.Done | None:
    # Done 테이블에서 id가 task_id인 데이터를 선택합니다
    result: Result = await db.execute(
        select(task_model.Done).filter(task_model.Done.id == task_id)
    )

    # 결과 중 첫 번째 값을 가져옵니다. 없으면 None이 됩니다.
    return result.scalars().first()


# -----------------------------------------------------------------
# [2] 새로운 Done 데이터를 생성하는 함수
# - 어떤 할 일을 완료했을 때 호출됩니다.
# - task_id만 저장하면 완료로 간주됩니다.
# -----------------------------------------------------------------
async def create_done(db: AsyncSession, task_id: int) -> task_model.Done:
    # task_id를 사용해 Done 객체를 생성합니다
    done = task_model.Done(id=task_id)

    # DB에 저장될 항목으로 추가합니다
    db.add(done)

    # 실제로 DB로 저장합니다 (commit)
    await db.commit()

    # 방금 저장한 객체를 다시 불러와 최신 상태로 만듭니다
    await db.refresh(done)

    # 최종적으로 생성된 객체를 반환합니다
    return done


# -----------------------------------------------------------------
# [3] Done 데이터를 삭제하는 함수
# - 사용자가 완료를 취소하고 싶을 때 사용합니다.
# - 기존에 존재하던 Done 객체를 인자로 받아 삭제합니다.
# -----------------------------------------------------------------
async def delete_done(db: AsyncSession, original: task_model.Done) -> None:
    # 전달받은 객체를 삭제 대상으로 지정합니다
    await db.delete(original)

    # 삭제 내용을 DB에 반영합니다
    await db.commit()
