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
from httpx import AsyncClient

# SQLAlchemy 비동기 전용 모듈
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 프로젝트 내부 코드 불러오기 (DB 세션 함수, DB 모델, FastAPI 앱)
from api.db import get_db, Base
from api.main import app

# 타입 힌트를 위한 모듈
from typing import AsyncGenerator


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
    async_sessoion = sessionmaker(
        autocommit = False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession
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
        async with async_sessoion() as session:
            yield session
            # yield는 session을 외부로 잠깐 넘기고, 끝나면 정리 작업 실행
            
    app.dependency_overrides[get_db] = get_test_db
    
    # -----------------------------------------------------------
    # 4. 테스트용 HTTP 클라이언트 생성
    # - FastAPI 서버를 실제로 띄우지 않아도 요청을 보낼 수 있으ㅡㅁ
    # - base_url은 내부적으로만 사용되는 테스트 주소
    # -----------------------------------------------------------
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
        # 테스트 함수에서 이 client를 사용하면, 실제 서버 없이도 앱에 요청 가능