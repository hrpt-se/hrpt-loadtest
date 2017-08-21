from urlparse import urlparse, parse_qs
from random import choice

from locust import HttpLocust, TaskSet, task
from locust.exception import StopLocust
from pyquery import PyQuery

NUM_USERS = 50

users = ['test{0}'.format(i) for i in range(NUM_USERS)]

remaining_users = len(users)


class SurveyTask(TaskSet):
    def on_start(self):
        try:
            username = users.pop()
        except IndexError:
            print('no avaliable user, continuing')
            self.interrupt(reschedule=False)

        response = self.client.get(
            '/accounts/login/',
            name='Login form load'
        )

        csrf_token = response.cookies['csrftoken']

        login_response = self.client.post(
            '/accounts/login/',
            {
                'username': username,
                'password': 'password',
                'csrfmiddlewaretoken': csrf_token
            },
            name='Login form submit'
        )

        query_string = urlparse(login_response.url).query
        self.client.gid = parse_qs(query_string)['gid'][0]

        self.load_survey()

    @task(5)
    def load_survey(self):
        with self.client.get(
            '/survey/show/test2/?gid='+self.client.gid,
            name='Survey load',
            capture=True
        ) as survey_response:

            if 'csrftoken' not in survey_response.cookies:
                print(survey_response.status_code)

            self.token = survey_response.cookies['csrftoken']

    @task(20)
    def save_draft(self):
        response = self.client.post(
            '/survey/show/test2/?gid='+self.client.gid+'&draft=save',
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
            name='Survey draft save'
        )

    # @task(1)
    def submit_survey(self):
        global remaining_users
        response = self.client.post(
            '/survey/show/test2/?gid='+self.client.gid,
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
            name='Survey submit'
        )

        remaining_users -= 1

        if not remaining_users:
            print('All done, exiting')
            raise StopLocust
        else:
            print('Remaining users: {0}'.format(remaining_users))

        self.interrupt(reschedule=False)

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


    @task(1)
    def logout(self):
        self.client.get('/accounts/logout/')
        self.history.append('logout')


class WebsiteUser(HttpLocust):
    task_set = SurveyTask
    min_wait = 1000
    max_wait = 15000
