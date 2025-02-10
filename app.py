from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.exceptions import BadRequest
import ctypes

# 커스텀 400 에러 예외 정의 (redirect_url 정보를 포함)
class CustomBadRequest(BadRequest):
    def __init__(self, description=None, redirect_url="/", response=None):
        super().__init__(description=description, response=response)
        self.redirect_url = redirect_url

app = Flask(__name__)
app.secret_key = 'secret_key_here'

@app.before_request
def init_session():
    # 세션에 balance, apples가 없다면 c_int32(초기값)으로 초기화
    if 'balance' not in session:
        session['balance'] = ctypes.c_int32(1000).value  # 기본 자산 1000원
    if 'apples' not in session:
        session['apples'] = ctypes.c_int32(0).value

@app.route('/')
def index():
    return render_template('index.html',
                           balance=session['balance'],
                           apples=session['apples'])

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if request.method == 'POST':
        # 입력값을 정수로 변환
        try:
            quantity_input = int(request.form['quantity'])
        except ValueError:
            raise CustomBadRequest(
                description="잘못된 입력입니다. 숫자를 입력해주세요.",
                redirect_url="/buy"
            )

        # c_int32로 변환하여 32비트 정수 범위로 강제
        quantity = ctypes.c_int32(quantity_input)

        # 수량 검증 (음수나 0 이하를 허용하고 싶다면 이 로직을 조정)
        if quantity.value <= 0:
            raise CustomBadRequest(
                description="잘못된 입력입니다. 다시 입력해주세요.",
                redirect_url="/buy"
            )
        
        # 사과 한 개당 100원
        cost = ctypes.c_int32(quantity.value * 100)

        # 현재 balance를 c_int32로 가져오기
        current_balance = ctypes.c_int32(session['balance'])

        # 잔액 확인
        if current_balance.value >= cost.value:
            new_balance = ctypes.c_int32(current_balance.value - cost.value)
            session['balance'] = new_balance.value

            current_apples = ctypes.c_int32(session['apples'])
            new_apples = ctypes.c_int32(current_apples.value + quantity.value)
            session['apples'] = new_apples.value

            return redirect(url_for('index'))
        else:
            raise CustomBadRequest(
                description="잔액이 부족합니다!",
                redirect_url="/buy"
            )
    return render_template('buy.html')

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        try:
            quantity_input = int(request.form['quantity'])
        except ValueError:
            raise CustomBadRequest(
                description="잘못된 입력입니다. 숫자를 입력해주세요.",
                redirect_url="/sell"
            )

        quantity = ctypes.c_int32(quantity_input)
        current_apples = ctypes.c_int32(session['apples'])

        # 사과가 충분한지, 그리고 판매량이 0 이상인지 확인
        if current_apples.value >= quantity.value:
            gain = ctypes.c_int32(quantity.value * 100)
            current_balance = ctypes.c_int32(session['balance'])
            new_balance = ctypes.c_int32(current_balance.value + gain.value)

            session['balance'] = new_balance.value
            new_apples = ctypes.c_int32(current_apples.value - quantity.value)
            session['apples'] = new_apples.value

            return redirect(url_for('index'))
        else:
            raise CustomBadRequest(
                description="사과가 부족합니다!",
                redirect_url="/sell"
            )
    return render_template('sell.html')

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if request.method == 'POST':
        balance = ctypes.c_int32(session['balance'])
        # 1억(100,000,000)은 int32 범위 이내이므로 비교 가능
        if balance.value >= 100000000:
            flag = "FLAG{overflow_harvest}"
            return render_template('shop.html', flag=flag)
        else:
            raise CustomBadRequest(
                description="플래그 구매에 필요한 잔액이 부족합니다!",
                redirect_url="/shop"
            )
    return render_template('shop.html', flag=None)

@app.errorhandler(CustomBadRequest)
def handle_custom_bad_request(e):
    # 전달된 description과 redirect_url 사용
    message = e.description if e.description else "잘못된 요청입니다!"
    redirect_url = e.redirect_url if hasattr(e, "redirect_url") else "/"
    return f'''
    <html>
      <head>
        <meta charset="UTF-8">
        <title>400 Bad Request</title>
      </head>
      <body>
        <script>
          alert("{message}");
          window.location.href = "{redirect_url}";
        </script>
      </body>
    </html>
    ''', 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
