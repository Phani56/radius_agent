from flask import Flask, render_template, request
from scraper import main

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("input.html")


@app.route('/issues', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        url = request.form
        ctx = main(url)
        return render_template("output.html", ctx=ctx)


if __name__ == "__main__":
    app.run(debug=True)



