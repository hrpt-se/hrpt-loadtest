

# TODO: Remove after test
# import pydevd_pycharm
# Remove above

from urllib.parse import urlparse, parse_qs
from random import choice

from locust import HttpLocust, TaskSet, task, between
from locust.exception import StopLocust
from pyquery import PyQuery
from bs4 import BeautifulSoup


NUM_USERS = 10

users = ['test{0}'.format(i) for i in range(0, NUM_USERS)]

remaining_users = len(users)


class SurveyTask(TaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.token = ''
        self.sessionid = ''
        self.mwtoken = ''

    def on_start(self):
        try:
            username = users.pop()
        except IndexError:
            print('no avaliable user, continuing')
            self.interrupt(reschedule=False)
        # TODO: remove after test
        # pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
        # Remove above
        print("user: " + username)
        response = self.client.get(
            '/accounts/login/',
            name='Login form load'
        )
        print(response.cookies)
        self.token = response.cookies['csrftoken']
        # Get the csrfmiddlewaretoken from the HMTL response
        soup = BeautifulSoup(response.content, features="lxml")
        self.mwtoken = soup.find('input', {'name':'csrfmiddlewaretoken'}).get('value')
        print(self.mwtoken)
        # TODO: remove after test
        # import pdb;
        # pdb.set_trace()
        login_response = self.client.post(
            '/accounts/login/',
            headers={'X-CSRFToken': self.token},
            data={"csrfmiddlewaretoken": self.mwtoken,
                'username': username,
                'password': 'password'},
            cookies={'csrftoken': self.token},
            allow_redirects=False,
            name='Login form submit'
        )

        # query_string = urlparse(login_response.url).query
        # print("query_string:" + query_string)
        # self.sessionid = login_response.cookies['sessionid']
        print(login_response.is_redirect)
        print(login_response.content)
        try:
            self.sessionid = login_response.cookies['sessionid']
        except KeyError:
            print('No sessionid cookie')
        try:
            self.token = login_response.cookies['csrftoken']
        except KeyError:
            print('No csrftoken cookie')
        # self.client.gid = parse_qs(query_string)['gid'][0]

        self.load_survey()

    @task(5)
    def load_survey(self):
        with self.client.get(
            '/survey/show/test2/',
            # capture=True,
            cookies={'csrftoken': self.token, 'sessionid': self.sessionid},
            allow_redirects=False,
            name='Survey load',
        ) as survey_response:

            if 'csrftoken' not in survey_response.cookies:
                print(survey_response.status_code)
            try:
                self.token = survey_response.cookies['csrftoken']
            except KeyError:
                print('No csrftoken cookie')
            # self.sessionid = survey_response.cookies['sessionid']

    @task(20)
    def save_draft(self):
        print('SaveDraft_sessionid:', self.sessionid)
        print('SaveDraft_token:', self.token)
        response = self.client.post(
            '/survey/show/test2/?draft=save',
            # data={"csrfmiddlewaretoken": self.token},
            headers={'X-CSRFToken': self.token},
            json={
                "survey_id": 3,
                "form_data": {
                    "PREFIL_BIRTHYEAR": "1950",
                    "TestRegEx": "",
                    "testChild": "NULL",
                    "OpenDate": "",
                    "OpenNumeric": "",
                    "TestMatrixEntries_multi_row1_col1": "",
                    "TestMatrixEntries_multi_row1_col2": "",
                    "TestMatrixEntries_multi_row2_col1": "",
                    "TestMatrixEntries_multi_row2_col2": "",
                    "TestMatrixEntries_multi_row3_col1": "",
                    "TestMatrixEntries_multi_row3_col2": ""
                }
            },
            cookies={'csrftoken': self.token, 'sessionid': self.sessionid},
            name='Survey draft save'
        )
        print('Save draft cookies: ', response.cookies)
        print('Save draft response: ', response)
        # self.token = response.cookies['csrftoken']

    @task(5)
    def submit_survey(self):
        global remaining_users
        response = self.client.post(
            '/survey/show/test2/',
            data={
                'csrfmiddlewaretoken': self.token,
                'PREFIL_BIRTHYEAR': '1950',
                'TestRegEx': '',
                'TestSC': 'N',
                'testChild': 'NULL',
                'TestAdult': 'Y',
                'OpenDate': '22/08/2017',
                'OpenNumeric': '765',
                'TestMC_B': '1',
                'TestMC_M': '1',
                'TestSufficient': 'Y',
                'TestSuff2': 'Y',
                'UncheckTest': 'REMOPT',
                'TestQ': 'T',
                'TestFill': 'FILL',
                'TestMatrixEntries_multi_row1_col1': '',
                'TestMatrixEntries_multi_row1_col2': '',
                'TestMatrixEntries_multi_row2_col1': 'Banana!',
                'TestMatrixEntries_multi_row2_col2': '',
                'TestMatrixEntries_multi_row3_col1': '',
                'TestMatrixEntries_multi_row3_col2': ''
            },
            cookies={'crftoken': self.token, 'sessionid': self.sessionid},
            name='Survey submit'
        )

        remaining_users -= 1

        if not remaining_users:
            print('All done, exiting')
            raise StopLocust
        else:
            print('Remaining users: {0}'.format(remaining_users))

        # self.interrupt(reschedule=False)

class LoginUser(TaskSet):
    @task(1)
    def login(self):
        username = choice(users)
        response = self.client.get(
            '/accounts/login/',
            name='Login form load'
        )
        csrf_token = response.cookies['csrftoken']

        with self.client.post(
            '/accounts/login/',
            {
                'username': username,
                'password': 'password',
                'csrfmiddlewaretoken': csrf_token
            },
            name='Login form submit',
            catch_response=True
        ) as login_response:

            if not '/sv/valkommen' in login_response.url:
                print('BOOM')
                login_response.failure('Double login!')
            print(login_response.cookies)
            self.sessionid = login_response.cookies['sessionid']
            self.token = login_response.cookies['csrftoken']


    @task(1)
    def logout(self):
        self.client.get('/accounts/logout/')
        self.history.append('logout')


class WebsiteUser(HttpLocust):
    task_set = SurveyTask
    wait_time = between(1, 15)
    # min_wait = 1000
    # max_wait = 15000
    host = 'http://127.0.0.1:8000/'


if __name__ == '__main__':
    WebsiteUser().run()
