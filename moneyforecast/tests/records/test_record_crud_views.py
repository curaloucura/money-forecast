import pytest
from pyquery import PyQuery
from django.core.urlresolvers import reverse

from records.models import OUTCOME


@pytest.fixture
def user_client(user, client):
    result = client.login(username=user.username, password=user.raw_password)
    assert result
    return client


@pytest.fixture
def html_parser():
    return HtmlParserUtil()


class HtmlParserUtil:
    def set(self, html):
        self.parser = PyQuery(html)

    def select(self, css_selector):
        return self.parser(css_selector)


@pytest.mark.django_db
def test_create_outcome_no_recurring(
        user_client, outcome, current_date, html_parser):
    post_data = {
        'description': 'outcome',
        'category': "5",
        'new_category': '',
        'amount': 1,
        'start_date': current_date.strftime("%Y/%m/%d"),
    }
    create_outcome_url = reverse("create_record", kwargs={"type": OUTCOME})
    response = user_client.post(create_outcome_url, post_data)
    assert response.status_code == 200
    assert response.content == "successfully-sent!"
