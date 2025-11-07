from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():

    return render_template('hello.html')


@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/help')
def help_page():
    
    return render_template('help.html')


if __name__ == '__main__':
  
    app.run(debug=True)
