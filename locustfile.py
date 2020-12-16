from locust import HttpLocust, TaskSequence, task, between, seq_task, exception
from common import auth, survey, users
from urllib3 import disable_warnings, exceptions

VERIFY_SSL = True


class SurveyTask(TaskSequence):
    username = ""

    def on_start(self):
        # If users is empty we stop since we can't login
        if not users.CREDENTIALS:
            raise exception.StopLocust()

        if not VERIFY_SSL:
            disable_warnings(category=exceptions.InsecureRequestWarning)

        self.username = users.CREDENTIALS.pop(0)
        self.login(self.username)

    def login(self, username, password="password"):
        self.client.get(auth.LOGIN_URL, name="Login form load", verify=False)

        with self.client.post(
                auth.LOGIN_URL,
                headers={
                    auth.CSRF_HEADER: auth.get_token(self.client),
                },
                data={
                    "csrfmiddlewaretoken": auth.get_token(self.client),
                    "username": username,
                    "password": password,
                },
                allow_redirects=False,
                catch_response=True,
                name="Login form submit",
                verify=VERIFY_SSL,
        ) as response:
            # Any status_code != 302 means that the login failed. 200 = error hidden in the template.
            if response.status_code >= 400:
                response.failure(response.reason)
                raise exception.StopLocust()
            if not response.is_redirect:
                response.failure("Invalid credentials, <{}, {}>".format(username, password))
                raise exception.StopLocust()

    @seq_task(1)
    @task(1)
    def survey_list(self):
        self.client.get(auth.WELCOME_URL, allow_redirects=False, name='Survey list load', verify=VERIFY_SSL)

    @seq_task(2)
    @task(1)
    def survey_load(self):
        self.client.get(survey.SURVEY_URL, allow_redirects=False, name="Survey load", verify=VERIFY_SSL)

    @seq_task(3)
    @task(20)
    def survey_draft(self):
        self.client.post(
            survey.DRAFT_URL,
            headers={
                auth.CSRF_HEADER: auth.get_token(self.client),
                "Referer": self.parent.host,
            },
            json=survey.get_draft(),
            name="Survey draft save",
            verify=VERIFY_SSL,
        )

    @seq_task(4)
    def survey_submit(self):
        self.client.post(
            survey.SURVEY_URL,
            headers={
                auth.CSRF_HEADER: auth.get_token(self.client),
                "Referer": self.parent.host,
            },
            data=survey.get_data(auth.get_token(self.client)),
            name="Survey submit",
            verify=VERIFY_SSL,
        )

    @seq_task(5)
    def logout(self):
        self.client.get(
            auth.LOGOUT_URL,
            name="User logout",
            verify=VERIFY_SSL,
        )
        raise exception.StopLocust()


class WebsiteUser(HttpLocust):
    task_set = SurveyTask
    wait_time = between(1, 15)
    host = 'http://localhost:8000/'
