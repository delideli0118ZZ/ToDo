# ---------------------------------------------------------------
# FastAPI로 웹 서비스를 만들기 위한 기본 웹 파일 (main.py)
# 이 파일에서 모든 기능을 모아서 최종 실행 가능한 웹 앱으로 만든다.
# -------------------------------------------------------------

# FastAPI 앱을 만들기 위한 도구를 불러온다.
from fastapi import FastAPI

# 우리가 만든 기능 코드들을 불러온다.
# task -> 할 일 만들기, 수정, 삭제
# done -> 완료 표시와 취소
from api.routers import task, done

# 보충 설명:
# 'api/routers/task.py', 'api/routers/done.py' 파일을 불러온 것이다.
# 기능별로 파일을 나눠서 코드가 복잡하지 않도록 관리하는 방식이다.

# FastAPI 앱을 만든다. 이앱이 웹 서버의 본체가 된다.
app = FastAPI()

# 수업 흐름 연결 설명:
# 우리가 만든 여러 기능을 'router'라는 방식으로 모아서 관리했는데,
# 여기서 그것들을 하나씩 연결해줘야만 실제로 동작한다.

# 기능 설명: task 기능들을 앱에 연결한다
# 예: /tasks 주소에서 할 일 목록을 보여주거나 추가하는 기능
app.include_router(task.router)

# 기능 설명: done 기능들을 앱에 연결한다
# 예: /tasks/3/done 주소에서 할 일을 완료 처리하거나 완료 취소하는 기능
app.include_router(done.router)

# 보충 설명:
# include_router는 말 그대로 기능(router)을 앱(app)에 포함시킨다는 뜻이다.
# 기능을 각각 파일에 나눠 만든 후, 이 main.py에서 전부 연결해줘야 FastAPI 서버가 완성된다.
