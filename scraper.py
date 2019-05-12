import datetime
import urllib
import requests
import json
from collections import OrderedDict

date_format = "%Y-%m-%dT%H:%M:%SZ"


class Scraper():

    def __init__(self, url):
        self.repo_url = url if url[-1] != '/' else url[:-1]
        self.time_frame = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
        self.total_issues = None
        self.ctx = OrderedDict()
        self.past_day = 0
        self.past_week = 0
        self.more_than_a_week = 0

    def add_data_to_dict(self, time_passed):
        if time_passed == 0:
            self.past_day += 1
        elif 1 <= time_passed <= 7:
            self.past_week += 1

    def week_flag(self, issue_time):
        if (datetime.datetime.now() - issue_time).days > 7:
            return False
        return True

    def get_pull_requests_count(self):
        """
        gets count of open pull requests
        """
        repo_details = self.repo_url.strip().split('/')[-2:]
        pull_requests = 0
        i = 1
        while True:
            args = {'state': 'open', 'page': i, 'per_page': 100}
            api_url = "https://api.github.com/repos/{}/{}/pulls?{}".format(repo_details[0], repo_details[1],
                                                                           urllib.parse.urlencode(args))
            response = requests.request("GET", api_url)
            response = json.loads(response.content)
            if not response:
                return pull_requests
            else:
                pull_requests += len(response)
                i += 1

    def get_data(self):
        repo_details = self.repo_url.strip().split('/')[-2:]
        i = 0
        week = True

        """
        gets all legit open issues in the past 7 days excluding pull requests
        """
        while week:
            i += 1
            args = {'since': str(self.time_frame), 'state': 'open', 'page': i, 'per_page': 100}
            api_url = "https://api.github.com/repos/{}/{}/issues?{}".format(repo_details[0], repo_details[1],
                                                                            urllib.parse.urlencode(args))
            response = requests.request("GET", api_url)
            response = json.loads(response.content)
            if not response:
                week = False
            for issue in response:
                pull_request = issue.get('pull_request', None)
                if not pull_request:
                    issue_time = datetime.datetime.strptime(issue['created_at'], date_format)
                    self.add_data_to_dict((datetime.datetime.now() - issue_time).days)
                    week = self.week_flag(issue_time)
        api_url = "https://api.github.com/repos/{}/{}".format(repo_details[0], repo_details[1])
        response = requests.request("GET", api_url)
        response = json.loads(response.content)
        self.total_issues = response['open_issues'] - self.get_pull_requests_count()
        self.more_than_a_week = self.total_issues - (self.past_day+self.past_week)

    def send_final_data(self):

        """
        sends final data as context (to be passed into the html)
        """
        self.ctx['total'] = self.total_issues
        self.ctx['past_day'] = self.past_day
        self.ctx['past_week'] = self.past_week
        self.ctx['more_than_a_week'] = self.more_than_a_week

        return self.ctx

