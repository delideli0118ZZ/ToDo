# ----------------------------------------------------
# 할 일(Task)을 표현하는 데이터 구조 정의
# 이 구조는 서버에서 주고받을 할 일 데이터의 모양을 정하는 것이다.
# -------------------------------------------------------

import datetime  # 데이터를 깔끔하게 다루기 위한 도구를 불러온다.

# pydantic: 우리가 정의한 자료가 숫자인지 글자인지 자동으로 확인해주는 도구다.
from pydantic import BaseModel, Field, ConfigDict


# ----------------------------------------------------
# 공통 속성 정의 (제목만 포함)
# TaskCreate, TaskCreateResponse, Task가  공통으로 사용하는 부분을 따로 묶은 클래스
# ----------------------------------------------------
class TaskBase(BaseModel):  # '할 일'을 표현할 수 있는 Task라는 틀을 만든다.
    title: str | None = Field(
        default=None,  # 아무 값이 없을 수도 있으니 기본값을 None으로 둔다.
        examples=["세탁소에 맡긴 것을 찾으러 가기"],  # 예시 제목을 보여준다.
    )

    # title: 할 일의 제목
    due_date: datetime.date | None = Field(None, example="2025-05-15")
    # * due_date: 할 일의 마감일(언제까지 해야 하는지)
    # * datetime.date | None: 날짜 형식이거나 없을 수도 있음
    #   예) 2025-05-15처럼 연-월-일 형식의 문자열을 입력
    # * 마감일은 선택사항이므로 입력하지 않아도 에러가 나지 않음


# ----------------------------------------------------
# [2] 할 일 생성 요청용 모델: TaskCreate
# - 사용자가 할 일을 새로 만들 때 사용하는 요청 구조
# - title만 필요하므로 TaskBase를 그대로 상속해서 사용함
# ----------------------------------------------------
class TaskCreate(TaskBase):
    pass  # TaskBase에 정의된 내용을 그대로 사용함


# ----------------------------------------------------
# [3] 할 일 생성 응답용 모델:  TaskCreateResponse
# - 서버가 클라이언트에게 응답할 때 사용하는 구조
# - 새로 만들어진 할 일의 번호(id)를 포함함
# ----------------------------------------------------
class TaskCreateResponse(TaskCreate):
    id: int  # 새로 만들어진 할 일의 고유 번호

    model_config = ConfigDict(
        from_attributes=True
    )  # Orm 모델(SQLAlchemy 등)을 사용할 수 있도록 설정


# ----------------------------------------------------
# 할 일을 조회하거나 응답할 때 사용하는 구조
# id, done 정보가 포함되며, 전체 할 일 목록 조회 등에 사용됨
# ----------------------------------------------------
class Task(TaskBase):  # '할 일'을 표현할 수 있는 Task라는 틀을 만든다.

    id: int  # 할 일 번호 (정수)

    done: bool = Field(
        default=False,  # 처음에는 '완료되지 않음(False)'으로 시작한다.
        description="완료 플래그",  # True면 완료, False면 미완료를 나타냄
    )

    # done: 이 할 일이 끝났는지를 표시하는 값 (True또는 False만 가능함)

    model_config = ConfigDict(
        from_attributes=True
    )  # Orm 모델(SQLAlchemy 등)을 사용할 수 있도록 설정
