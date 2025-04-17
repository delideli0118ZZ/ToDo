# FastAPI에서 여러 주소(URL 경로)를 관리하기 위한 도구를 불러온다.
from fastapi import APIRouter

# router는 여러 기능(API 주소들)을 모아두는 모움집이다.
router = APIRouter()

# ---------------------------------------------------------
# 이 함수를 어떤 할일 "완료" 상태로 표시하는 기능이다.
# 예: /tasks/3/done -> 3번 할 일을 완료 처리한다.
# ---------------------------------------------------------

# 보충설명:
# - PUT은 정보를 "설정하거나 수정"할 때 사용
# - 주소 끝에 /done 은 "완료 상태 전환"을 의미미
# - {task_id}는 할 일 번호로, 숫자가 바뀔 수 있음음
@router.put("/tasks/{task_id}/done", response_model=None)
async def mark_task_as_done(task_id: int):
    return


# ----------------------------------------------------------
# 할 일의 "완료된 상태"를 취소(해제)하는 기능
# 예: /tasks/3/done -> 3번 할 일을 완료 해제함
# ---------------------------------------------------------

# 보충 설명:
# -DELETE는 정보를 "제거"할 때 사용
# -여기선 "완료 표시"를 지운는 동작
# - PUT과 DELETE는 반대 동작 (완료 <-> 해제)
@router.delete("/tasks/{task_id}/done", response_model=None)
async def unmark_task_as_done(task_idL int):
    return
