from flask import Flask, render_template, request
from scraper import Scraper

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("input.html")


@app.route('/issues', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        url = request.form['repo_url']
        scraper = Scraper(url)
        if not scraper.check_validity():
            return
        scraper.scrape()
        ctx = scraper.parse_and_render()
        return render_template("output.html", ctx=ctx)


@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(debug=True)



