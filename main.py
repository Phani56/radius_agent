from flask import Flask, render_template, request
from scraper import Scraper

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("input.html")


@app.route('/issues', methods=['POST', 'GET'])
def result():
    """
    renders the html output based on the input url
    """
    if request.method == 'POST':
        url = request.form['repo_url']
        if not url:
            return render_template('input.html', invalid=True)
        scraper = Scraper(url)
        if not scraper.check_validity():
            return render_template('input.html', invalid=True)
        scraper.scrape()
        ctx = scraper.send_final_data()
        return render_template("output.html", ctx=ctx)


@app.route('/test')
def test():
    return render_template('test.html')


if __name__ == "__main__":
    app.run(debug=True)



