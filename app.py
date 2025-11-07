from flask import Flask, render_template, request
from health_checker import check_website_health

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check():
    url = request.form['url']
    results = check_website_health(url)
    return render_template('result.html', url=url, results=results)


if __name__ == '__main__':
    app.run(debug=True)
