import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import OrderedDict

# Data extraction classes from html
issues_entity = ['div', 'js-navigation-container js-active-navigation-container']
issue_box = ['div', 'Box-row Box-row--focus-gray p-0 mt-0 js-navigation-item js-issue-row']
data_box = ['span', 'opened-by']
date_format = "%Y-%m-%dT%H:%M:%SZ"


class Scraper():

    def __init__(self, url):
        self.url = url
        self.scrape_all = False
        self.total_issues = None
        self.issues = []
        self.ctx = OrderedDict()
        self.past_day = 0
        self.past_week = 0
        self.more_than_a_week = 0

    def check_validity(self):
        if 'github.com' not in self.url:
            return False
        return True

    def add_data_to_dict(self, time_passed):
        if time_passed == 0:
            self.past_day += 1
        elif 1 <= time_passed <= 7:
            self.past_week += 1
        elif time_passed > 7:
            self.more_than_a_week += 1

    def get_last_page(self):

        """
        gets total number of open issues in the repo if pagination is present
        """
        i = 1
        response = requests.get(self.url + "/issues?page={}&q=is%3Aissue+is%3Aopen".format(i))
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            pages_data = soup.find('div', {'class': 'pagination'})
            if pages_data:
                pages = pages_data.find_all('a', href=True)
                last_page = int(pages[-2].get_text())
                response = requests.get(self.url + "/issues?page={}&q=is%3Aissue+is%3Aopen".format(last_page))
                soup = BeautifulSoup(response.content, 'html.parser')
                issues_data = soup.find(issues_entity[0], {'class': issues_entity[1]})
                issues = issues_data.find_all(issue_box[0], {'class': issue_box[1]})
                self.total_issues = (last_page-1)*25 + len(issues)
                self.scrape_all = False
            else:
                self.scrape_all = True


    def get_datetime(self, s):
        s = str(s)
        index = s.find("datetime=") + len("datetime=") + 1
        return datetime.strptime(s[index:index + 20], date_format)

    def week_flag(self, issue):

        """
        keeps on adding data to the final dict until an issue is passed with time stamp more than 7 days. Makes the
        scrape function to stop by sending a page that is not present
        """
        now = datetime.now()
        issue_time_stamp = self.get_datetime(issue.find(data_box[0], {'class': data_box[1]}))
        time_passed = (now - issue_time_stamp).days
        if time_passed > 7:
            if self.scrape_all:
                self.add_data_to_dict(time_passed)
                return True
            else:
                if self.total_issues:
                    self.more_than_a_week = self.total_issues - (self.past_day + self.past_week)
                    return False
                else:
                    self.add_data_to_dict(time_passed)
                    return True
        else:
            self.add_data_to_dict(time_passed)
            return True

    def scrape(self):

        """
        scrapes all the issues if pagination is not present. If pagination, pages with issues opened less than 7 days
        ago are scraped
        """
        self.get_last_page()
        issues_data = True
        i = 1
        while issues_data:
            response = requests.get(self.url + "/issues?page={}&q=is%3Aissue+is%3Aopen".format(i))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                issues_data = soup.find( issues_entity[0], {'class': issues_entity[1]})
                if issues_data:
                    for issue in issues_data.find_all(issue_box[0], {'class': issue_box[1]}):
                        x = self.week_flag(issue)
                        if x:
                            continue
                        else:
                            i = self.total_issues + 1
                    i += 1

    def send_final_data(self):

        """
        sends final data as context (to be passed into the html)
        """
        if self.total_issues:
            self.ctx['total'] = self.total_issues
        else:
            self.ctx['total'] = self.past_day + self.past_week + self.more_than_a_week
        self.ctx['past_day'] = self.past_day
        self.ctx['past_week'] = self.past_week
        self.ctx['more_than_a_week'] = self.more_than_a_week

        return self.ctx

