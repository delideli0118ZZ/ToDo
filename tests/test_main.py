# -----------------------------------------------------------
# 파일명:  test_setup.py (예시)
# 목적: FastAPI앱을 테스트할 수 있도록 설정하는 코드입니다.
# - 실제 DB를 사용하지 않고, 메모리에서만 동작하는 임시 DB를 사용합니다.
# - FastAPI 앱이 이 테스트용 DB를 사용하도록 바꿔줍니다.
# -----------------------------------------------------------

# 테스트 도구: pytest는 파이썬 테스트 프레임워크
import pytest

# 비동기 테스트 지원: pytest에서 async 함수도 테스트 가능하게 해줍니다.
import pytest_asyncio

# httpx: 코드로 HTTP 요청을 보낼 수 있는 클라이언트 (FastAPI와 잘 호환됨)
from httpx import AsyncClient, ASGITransport

# SQLAlchemy 비동기 전용 모듈
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 프로젝트 내부 코드 불러오기 (DB 세션 함수, DB 모델, FastAPI 앱)
from api.db import get_db, Base
from api.main import app

# 타입 힌트를 위한 모듈
from typing import AsyncGenerator

import starlette.status as status

# -----------------------------------------------------------
# ASYNC_DB_URL: 테스트에 사용할 임시 SQLite 데이터베이스 주소
# - ":memory:"는 실제 파일을 만들지 않고, 메모리에만 저장함
# - 테스트가 끝나면 DB 내용은 모두 사라짐
# -----------------------------------------------------------
ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


# -----------------------------------------------------------
# async_client: 테스트에서 사용할 비동기 HTTP 클라이언트를 만드는 함수
# - 이 함수는 fixture로 등록되어 여러 테스트에서 공통으로 사용 가능
# - yield를 사용하므로 AsyncGenerator로 타입 지정해야 함
# -----------------------------------------------------------
@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    # -----------------------------------------------------------
    # 1. 테스트용 비동기 DB 엔진과 세션 생성기 설정
    # - 실제 서비스용 DB와는 완전히 분리됨
    # -----------------------------------------------------------
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    # -----------------------------------------------------------
    # 2. 테스트용 DB 초기화 (테이블 전체 삭제 후 재생성)
    # -----------------------------------------------------------
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # -----------------------------------------------------------
    # 3. get_db() 함수를 테스트용 DB와 연결되도록 override
    # - 실제 앱에서 사용하는 DB 대신 테스트용 DB로 작동하게 만듦
    # -----------------------------------------------------------
    async def get_test_db():
        async with async_session() as session:
            yield session
            # yield는 session을 외부로 잠깐 넘기고, 끝나면 정리 작업 실행

    app.dependency_overrides[get_db] = get_test_db

    # -----------------------------------------------------------
    # 4. 테스트용 HTTP 클라이언트 생성
    # - FastAPI 서버를 실제로 띄우지 않아도 요청을 보낼 수 있으ㅡㅁ
    # - base_url은 내부적으로만 사용되는 테스트 주소
    # -----------------------------------------------------------
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
        # 테스트 함수에서 이 client를 사용하면, 실제 서버 없이도 앱에 요청 가능


# -----------------------------------------------------------------
# [테스트 함수] 할 일 생성 및 목록 조회 테스트
# - POST /tasks로 할 일을 하나 추가하고
# - GET /tasks로  전체 목록을 조회해 결과를 검증합니다.
# -----------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_and_read(async_client):
    # -----------------------------------------------------------------
    # 1. 새로운 할 일을 추가 (POST 요청)
    # - title이 "테스트 작업"인 할 일을 서버에 추가 요청
    # -----------------------------------------------------------------
    response = await async_client.post("/tasks", json={"title": "테스트 작업"})
    assert response.status_code == status.HTTP_200_OK

    response_obj = response.json()
    assert (
        response_obj["title"] == "테스트 작업"
    )  # 응답 JSON에 title이 잘 들어 갔는지 확인

    # -----------------------------------------------------------------
    # 2. 전체 할 일 목록 조회 (GET 요청)
    # - 방금 추가한 할 일이 목록에 포함되어 있는지 확인
    # -----------------------------------------------------------------
    response = await async_client.get("/tasks")
    assert response.status_code == status.HTTP_200_OK

    response_obj = response.json()
    assert len(response_obj) == 1  # 할 일 개수가 1개인지 확인
    assert response_obj[0]["title"] == "테스트 작업"  # 그 할 일의 제목이 정확한지 확인
    assert response_obj[0]["done"] is False  # 완료 여부가 False인지 확인 (기본값)


@pytest.mark.asyncio
async def test_done_flag(async_client):
    # ---------------------------------------------------------------
    # [1] 새로운 할 일을 추가 (POST 요청)
    # - title이 "테스트 작업2"인 할 일을 서버에 추가 요청
    # ---------------------------------------------------------------
    response = await async_client.post("/tasks", json={"title": "테스트 작업2"})
    assert response.status_code == status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "테스트 작업2"

    # ---------------------------------------------------------------
    # [2] 할 일을 완료 처리 (PUT 요청)
    # - 이 테스트에서는 PUT /tasks 라는 주소에 요청을 보냄
    # - 실제 구현에서는 가장 마지막에 추가된 작업을 완료 처리하는 방식일 수 있음
    # - 즉, 우리가 방금 추가한 "테스트 작업2"가 완료 처리됨
    # ---------------------------------------------------------------
    response = await async_client.put("/tasks/1/done")
    assert response.status_code == status.HTTP_200_OK

    # ---------------------------------------------------------------
    # [3] 이미 완료된 할 일을 다시 완료 처리 시도 (PUT 요청)
    # - /tasks/1/done 주소로 요청을 보내어 id=1인 작업을 완료 처리하려고 시도함
    # - 하지만 이미 완료된 작업이므로 서버가 400 Bad Request를 반환해야 함
    # ---------------------------------------------------------------
    response = await async_client.put("/tasks/1/done")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # ---------------------------------------------------------------
    # [4] 완료 처리된 작업을 완료 해제 (DELETE 요청)
    # -/tasks/1/done 주소로 요청을 보내면 완료 상태가 해제됨 (False로 변경됨)
    # ---------------------------------------------------------------
    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == status.HTTP_200_OK

    # ---------------------------------------------------------------
    # [5] 이미 완료 해제된 작업을 다시 해제하려고 시도
    # - 더 이상 완료 상태가 아니므로 서버는 해당 작업이 존재하지 않는다고 판단
    # - 따라서 404 Not Found 응답을 보내는 것이 올바름
    # ---------------------------------------------------------------
    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------
# [테스트 함수] 마감일(due_date)이 포함된 할 일 생성 테스트
# - 사용자가 title과 함께 due_date를 보낼 수 있는지 확인
# - 예: {"title": "테스트 작업", "due_date": "2024-12-01"}
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_due_date(async_client):
    # ---------------------------------------------------------------
    # 1. POST 요청을 보냄
    # - /tasks 주소에 JSON 데이터로 할 일을 하나 추가함
    # - title과 due_date를 함께 전송
    # ---------------------------------------------------------------
    response = await async_client.post(
        "/tasks", json={"title": "테스트 작업", "due_date": "2024-12-01"}
    )
    assert response.status_code == status.HTTP_200_OK  # [>] 정상 처리 여부 확인

    # ---------------------------------------------------------------
    # [2] 존재하지 않는 날짜 전송 (예: 12월 32일)
    # ---------------------------------------------------------------
    # - 날짜 형식은 맞지만, 실제로  존재하지 않는 날짜입니다.
    # - Pydantic의 date 타입은 이 경우 오류를 발생시킵니다.
    # - 서버는 422 Unprocessable Entity 응답을 반환해야 합니다.
    # ---------------------------------------------------------------
    response = await async_client.post(
        "/tasks", json={"title": "테스트 작업", "due_date": "2024-12-32"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # ---------------------------------------------------------------
    # [3] 날짜 구분 기호가 잘못된 형식 (슬래시 사용)
    # ---------------------------------------------------------------
    # - "YYYY/MM/DD" 형식은 ISO 8601 표준 형식이 아닙니다.
    # - FastAPI + Pydantic은 기본적으로 "YYYY-MM-DD" 형식만 허용합니다.
    # ---------------------------------------------------------------
    response = await async_client.post(
        "/tasks", json={"title": "테스트 작업", "due_date": "2024-12-01"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # ---------------------------------------------------------------
    # [4] 날짜 형식이 너무 뭉쳐 있음 (YYYYMMDD)
    # ---------------------------------------------------------------
    # - 구분자 없이 숫자만 연속된 형식은 날짜로 해석되지 않습니다.
    # - 이 경우도 422 오류가 발생해야 정상입니다.
    # ---------------------------------------------------------------
    response = await async_client.post(
        "/tasks", json={"title": "테스트 작업", "due_date": "20241201"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------
# 테스트 목적: 마감일(due_date)의 유효성 검사
# ---------------------------------------------------------------
# 이 테스트 함수는 사용자가 할 일을 등록할 때 입력하는 `due_date` 값이
# 유효하지 않은 날짜이거나 올바른 혁이 아닐 경우 서버가 어떻게 반응하는지 확인합니다.
#
# [겁사 항목]
# (1) 올바른 날짜 입력 시 정상 처리 (200 OK)
# (2) 존재하지 않는 날짜 (예: 12월 32일) -> 오류 반환 (422)
# (3) 잘못된 구분자 사용 (예: 2024/12/01) -> 오류 반환 (422)
# (4) 구분자 없이 숫자만 나열 (예: 20241202) -> 오류 반환 (422)
#
# 이 검사를 통해 FastAPI + Pydantic이 날짜 형식을 어떻게 겁사하는지 이해할 수 있습니다.
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_due_date(async_client):
    input_list = ["2024-12-01", "20024-12-32", "2024/12/01", "20241201"]
    expectation_list = [
        status.HTTP_200_OK,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]
    # ---------------------------------------------------------------
    # [1] 유효한 날짜 형식 전송
    # ---------------------------------------------------------------
    # - 정상적인 날짜 형식 (YYYY-MM-DD) 사용 -> 12월 1일
    # - 이 경우 서버는 요청을 정상적으로 처리해야 합니다.
    # - 따라서 상태코드는 200 OK가 나와야 합니다.
    # ---------------------------------------------------------------
    response = await async_client.post(
        "/tasks", json={"title": "테스트 작업", "due_date": input_param}
    )
    assert response.status_code == expectation

    # ---------------------------------------------------------------
    # [2] 존재하지 않는 날짜 전송 (예: 12월 32일)
    # ---------------------------------------------------------------
    # - 날짜 형식은 맞지만, 실제로 존재하지 않는 날짜입니다.
    # - Pydantic의 date 타입은 이 경우 오류를 발생시킵니다.
    # - 서버는 422 Unprocessable Entity 응답을 반환해야 합니다.
    # ---------------------------------------------------------------
    expectation_list = [
        status.HTTP_200_OK,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]

    # ---------------------------------------------------------------
    # [3] 반복문을 통해 모든 케이스 테스트
    # ---------------------------------------------------------------
    # - zip()을 사용해 input과 기대값을 함께 가져옵니다.
    # - 각 케이스에 대해 POST 요청을 보내고 상태 코드가 예상과 일치하는지 확인합니다.
    # ---------------------------------------------------------------
    for input_param, expectation in zip(input_list, expectation_list):
        response = await async_client.post(
            "/tasks", json={"title": "테스트 작업", "due_date": input_param}
        )
        # 결과 검증: 응답 상태 코드가 기대값과 일치해야 통과
        assert response.status_code == expectation
