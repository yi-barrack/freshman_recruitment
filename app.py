from flask import Flask, render_template, request, session, redirect, url_for
import numpy as np
from werkzeug.exceptions import BadRequest

# 커스텀 400 에러 예외 정의 (redirect_url 정보를 포함)
class CustomBadRequest(BadRequest):
    def __init__(self, description=None, redirect_url="/", response=None):
        super().__init__(description=description, response=response)
        self.redirect_url = redirect_url

app = Flask(__name__)
app.secret_key = 'secret_key_here'

@app.before_request
def init_session():
    if 'balance' not in session:
        session['balance'] = 1000  # 기본 자산 1000원
    if 'apples' not in session:
        session['apples'] = 0

@app.route('/')
def index():
    return render_template('index.html', balance=session['balance'], apples=session['apples'])

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if request.method == 'POST':
        try:
            quantity = int(request.form['quantity'])
        except ValueError:
            raise CustomBadRequest(
                description="잘못된 입력입니다. 숫자를 입력해주세요.",
                redirect_url="/buy"
            )
        
        if quantity <= 0:
            raise CustomBadRequest(
                description="잘못된 입력입니다. 다시 입력해주세요.",
                redirect_url="/buy"
            )
        
        cost = quantity * 100
        if session['balance'] >= cost:
            new_balance = np.int32(session['balance'] - cost)
            session['balance'] = int(new_balance)
            session['apples'] += quantity
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
            quantity = int(request.form['quantity'])
        except ValueError:
            raise CustomBadRequest(
                description="잘못된 입력입니다. 숫자를 입력해주세요.",
                redirect_url="/sell"
            )
        
        if session['apples'] >= quantity:
            gain = quantity * 100
            new_balance = np.int32(session['balance'] + gain)
            session['balance'] = int(new_balance)
            session['apples'] -= quantity
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
        if session['balance'] >= 100000000:
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
