from flask import *
from func import sms

# 基于Python和LeanCloud的短信验证
app = Flask(__name__)


@app.route("/login", methods=['POST', 'GET'])
def do_login():
    error_msg = None
    if request.method == 'GET':
        phone_number = request.args.get('mobile_phone_number')
		#input phone_number
        if phone_number is not None:
            if sms.send_message(phone_number):
                return render_template('login.html')
            else:
                error_msg = 'Failed to get the verification code!'
    elif request.method == 'POST':
        phone_number = request.form['phone']
        code = request.form['code']
        if code == '':
            error_msg = 'Please input the verification code!'
        elif sms.verify(phone_number, code):
            return redirect(url_for('success'))
        else:
            error_msg = 'Your code is wrong, please check again!'
    return render_template('login.html', error_msg=error_msg)


@app.route("/success")
def success():
    return render_template('success.html')


if __name__ == "__main__":
    app.run(debug=True)
