import pytest
import json
from pyquery import PyQuery
from django.core.urlresolvers import reverse

from records.models import Record, OUTCOME, INCOME


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
class TestIncomeNoRecurring:
    @pytest.fixture
    def income_new(self, user_client, income, current_date, user):
        record = Record.objects.create(
            category=income, amount=1, start_date=current_date, user=user)
        return record

    def test_create_returns_new_id(
            self, income, current_date, user_client):
        post_data = {
            'description': 'income',
            'category': income.id,
            'new_category': '',
            'amount': 1,
            'start_date': current_date.strftime("%Y/%m/%d"),
        }
        create_income_url = reverse("create_record", kwargs={"type": INCOME})
        response = user_client.post(create_income_url, post_data)
        assert response.status_code == 200
        try:
            new_id = json.loads(response.content)
        except ValueError:
            raise Exception("Form is invalid or content is not a json")
        assert new_id > 0

    def test_update_changes_value_in_db(
            self, income_new, income, user, user_client,
            current_date):
        new_description = "changed income"
        new_amount = 9999
        update_record_url = reverse(
            "update_record", kwargs={"pk": income_new.id})
        post_data = {
            'description': new_description,
            'category': income.id,
            'new_category': '',
            'amount': new_amount,
            'start_date': current_date.strftime("%Y/%m/%d"),
        }
        response = user_client.post(update_record_url, post_data)
        assert response.status_code == 200
        updated = json.loads(response.content)
        assert updated['id'] == income_new.id
        instance = Record.objects.get(pk=updated['id'])
        assert instance.amount == new_amount
        assert instance.description == new_description

    def test_delete_returns_no_id(
            self, income_new, user_client):
        delete_record_url = reverse(
            "delete_record", kwargs={"pk": income_new.id})
        response = user_client.post(delete_record_url)
        assert response.status_code == 200
        deleted = json.loads(response.content)
        assert deleted['id'] is None


@pytest.mark.django_db
class TestOutcomeNoRecurring:
    @pytest.fixture
    def outcome_new(self, user_client, outcome, current_date, user):
        record = Record.objects.create(
            category=outcome, amount=1, start_date=current_date, user=user)
        return record

    def test_create_returns_new_id(
            self, outcome, current_date, user_client):
        post_data = {
            'description': 'outcome',
            'category': outcome.id,
            'new_category': '',
            'amount': 1,
            'start_date': current_date.strftime("%Y/%m/%d"),
        }
        create_outcome_url = reverse("create_record", kwargs={"type": OUTCOME})
        response = user_client.post(create_outcome_url, post_data)
        assert response.status_code == 200
        try:
            new_id = json.loads(response.content)
        except ValueError:
            raise Exception("Form is invalid or content is not a json")
        assert new_id > 0

    def test_update_changes_value_in_db(
            self, outcome_new, outcome, user, user_client,
            current_date):
        new_description = "changed outcome"
        new_amount = 9999
        update_record_url = reverse(
            "update_record", kwargs={"pk": outcome_new.id})
        post_data = {
            'description': new_description,
            'category': outcome.id,
            'new_category': '',
            'amount': new_amount,
            'start_date': current_date.strftime("%Y/%m/%d"),
        }
        response = user_client.post(update_record_url, post_data)
        assert response.status_code == 200
        updated = json.loads(response.content)
        assert updated['id'] == outcome_new.id
        instance = Record.objects.get(pk=updated['id'])
        assert instance.amount == new_amount
        assert instance.description == new_description

    def test_delete_returns_no_id(
            self, outcome_new, user_client):
        delete_record_url = reverse(
            "delete_record", kwargs={"pk": outcome_new.id})
        response = user_client.post(delete_record_url)
        assert response.status_code == 200
        deleted = json.loads(response.content)
        assert deleted['id'] is None