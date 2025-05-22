# ---------------------------------------------------------
# 파일명: task,py
# 위치: api/models/task.py
# 이 파일은 데이터베이스의 'tasks'와 'dones' 테이블에
# 대응되는 SQLAlchemy 모델 클래스(Task, Done)를 정의한다.
# ---------------------------------------------------------

# ---------------------------------------------------------
# SQLAlchemy에서 테이블을 정의할 때 필요한 기능들을 불러온다
# ---------------------------------------------------------
from sqlalchemy import Column, Integer, String, ForeignKey, Date

# Column:테이블의 각 열(컬럼)을 정의할 때 사용
# Integer: 정수형 데이터 타입 (예: ID)
# String: 문자열 데이터 타입 (예: 제목)
# ForeignKey: 다른 테이블의 값을 참조할 때 사용 (외래키 설정)

from sqlalchemy.orm import relationship

# 테이블 간의 관계(1:1, 1N 등)를 정의할 때 사용하는 도구
# 예: Task와 Done이 서로 연결되도록 설정할 수 있음

from api.db import Base  # SQLAlchemy에서 사용하는 모델의 기반 클래스


# ---------------------------------------------------------
# [1]Task 모델 -> tasks 테이블과 매핑됨
# ---------------------------------------------------------
class Task(Base):
    __tablename__ = "tasks"  # 이 클래스는 'tasks' 테이블과 연결됨

    id = Column(Integer, primary_key=True)
    # -> Db 컬럼: task.id
    # SQLAlchemy: Integer + primary_key=True
    # PostgreSQL: SERIAL PRIMARY KEY(자동 증가 정수, 기본키)

    title = Column(String(1024))
    # -> DB 컬럼: tasks.title
    # SQLAlchemy: String(1024)
    # PostgreSQL: VARCHAR(1024)

    due_date = Column(Date)
    # -> DB 컬럼: tasks.due_date
    # * SQLAlchemy: Date
    # * PostgreSQL: DATE 형식

    done = relationship("Done", back_populates="task", cascade="all, delete")
    # Task <-> Done: 1:1 관계
    # done: 연결된 Done 객체 (완료 여부)를 참조함
    # cascade="all, delete"->Task삭제 시 연결된 Done도 함께 삭제됨


# ---------------------------------------------------------
# [2] Done 모델 -> dones 테이블과 매핑됨
# ---------------------------------------------------------
class Done(Base):
    __tablename__ = "dones"  # 이 클래스는 'dones' 테이블과 연결됨

    id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    # -> DB 컬럼: dones.id (외래키: tasks.id)
    # SQLAlchemy: Integer + Foreignkey + primary_key=True
    # postgreSQL: INTEGER + FOREIGN KEY + PRIMARY KEY
    # 1:1 관계 유지: dones.id = tasks.id 인 상태
    # 완료된 작업만 이 테이블에 기록됨

    task = relationship("Task", back_populates="done")
    # 연결된 Task 객체를 참조할 수 있음
    # task: Done-> Task 방향 참조
