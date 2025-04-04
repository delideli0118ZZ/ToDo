# FastAPI에서 여러 주소(URL 경로)를 관리하기 위한 도구를 불러온다.
from fastapi import APIRouter

# router는 여러 기능(API 주소들)을 모아두는 모움집이다.
router = APIRouter()

# ---------------------------------------------------------
# 이 함수를 어떤 할일 "완료" 상태로 표시하는 기능이다.
# 예: /tasks/3/done -> 3번 할 일을 완료 처리한다.


# 보충설명:
# - put은 기존 정보를 바꾸거나 설정할 때 사용한다.
# - 주소 끝에 /done 이 붙은 건 "완료 상태"를 나타낸다.
# - {task_id}는 바뀌는 숫자다. 할 일 번호를 뜻한다.
@router.put("/tasks/{task_id}/done")
async def mark_task_as_done():
    pass  # 아직 기능은 만들지 않았고, 나중에 실제 동작을 추가할 예정이다.


# ----------------------------------------------------------
# 이 함수는 "완료된 상태"를 다시 취소(해)제)하는 기능이다.
# 예: /tasks/3/done -> 3번 할 일의 완료 표시를 해제한다.


# 보충 설명:
# -delete는 어떤 상태나 정보를 없앨 때 사용한다.
# -여기선 "완료된 상태 표시"를 지운다고 생각하면 된다.
# - put과 delete는 반대되는 행동을 한다.
@router.delete("/tasks/{task_id}/done")
async def unmark_task_as_done():
    pass  # 여기도 나중에 실제 코드가 들어갈 예정
