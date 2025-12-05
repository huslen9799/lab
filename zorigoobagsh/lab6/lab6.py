from flask import Flask, render_template, redirect, url_for, abort

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/go-to-help')
def go_to_help():
   
    return redirect(url_for('help_page'))

@app.route('/user/<username>')
def user_profile(username):
    if username.lower() == 'admin':
        return render_template('user.html', username=username)
    elif username.lower() == 'guest':
        abort(403)
    else:
        abort(404)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Page Not Found"), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, message="Access Forbidden"), 403

@app.route('/check-error')
def check_error():
    abort(404)

if __name__ == '__main__':
    app.run(debug=True)
