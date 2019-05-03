import requests
from bs4 import BeautifulSoup
from datetime import datetime

# data extraction classes in the html
issues_entity = ['div', 'js-navigation-container js-active-navigation-container']
issue_box = ['div', 'Box-row Box-row--focus-gray p-0 mt-0 js-navigation-item js-issue-row']
data_box = ['span', 'opened-by']
date_format = "%Y-%m-%dT%H:%M:%SZ"



def scraper(url):

    """
    scrapes all the issues until the last page and returns list of all the issue blocks(html)
    """

    issues = []
    issues_data = True
    i = 1

    while issues_data:
        print (i)
        response = requests.get(url + "/issues?page={}&q=is%3Aissue+is%3Aopen".format(i))
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            issues_data = soup.find( issues_entity[0], {'class': issues_entity[1]})
            if issues_data:
                issues.extend(issues_data.find_all(issue_box[0], {'class': issue_box[1]}))
                i += 1

    return issues


def get_datetime(s):
    s = str(s)
    index = s.find("datetime=") + len("datetime=") + 1
    return datetime.strptime(s[index:index + 20], date_format)


def parse_and_render(issues):
    ctx = {}
    ctx['total'] = len(issues)
    past_day = 0
    past_week = 0
    more_than_a_week = 0
    now = datetime.now()
    for issue in issues:
        issue_time_stamp = get_datetime(issue.find(data_box[0], {'class': data_box[1]}))
        time_passed = (now - issue_time_stamp).days
        if time_passed == 0:
            past_day += 1
        elif 1 <= time_passed <= 7:
            past_week += 1
        elif time_passed > 7:
            more_than_a_week += 1
    ctx['past_day'] = past_day
    ctx['past_week'] = past_week
    ctx['more_than_a_week'] = more_than_a_week
    print (ctx)


def main(url):
    issues = scraper(url)
    parse_and_render(issues)
