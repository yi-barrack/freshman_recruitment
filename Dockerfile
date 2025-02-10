# Python 3.9-slim 이미지를 베이스로 사용
FROM python:3.9-slim

# 컨테이너 내 작업 디렉터리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY . .

# Flask 앱이 사용할 포트 노출
EXPOSE 5000

# Flask 환경 변수 설정
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# gunicorn으로 앱 실행
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
