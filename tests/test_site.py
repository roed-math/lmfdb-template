"""
Tests of the website's pages; see conftest.py for the database they need.
"""

import re
import secrets

import pytest

PAGES = [
    "/",
    "/about",
    "/health",
    "/style.css",
    "/static/lmfdb.js",
    "/static/site.css",
    "/Example/",
    "/Example/?n=1-100",
    "/Example/?is_sum=no&n=1-30",
    "/Example/65",
    "/Example/stats",
    "/Example/Source",
    "/Example/Labels",
    "/knowledge/",
    "/knowledge/show/example.r2",
    "/knowledge/history",
    "/users/",
    "/users/myself",
]


@pytest.mark.parametrize("url", PAGES)
def test_page(client, url):
    response = client.get(url)
    assert response.status_code == 200, url
    page = response.get_data(as_text=True)
    assert "ERROR in the template" not in page


def test_layout(client):
    page = client.get("/").get_data(as_text=True)
    assert "<title>Example Database" in page
    assert "Built with the" in page          # templates/homepage.html
    assert "/static/site.css" in page        # templates/base.html
    assert "Sums of two squares" in page     # sidebar.yaml


def test_colors(client):
    from website.colors import SiteColors
    css = client.get("/style.css").get_data(as_text=True)
    assert SiteColors.col_link in css
    # other schemes can be previewed
    assert SiteColors.col_link not in client.get("/style.css?color=0").get_data(as_text=True)


def test_search(client):
    page = client.get("/Example/?n=1-100&r2=8").get_data(as_text=True)
    assert "24 matches" in page
    assert 'href="/Example/5"' in page and 'href="/Example/65"' not in page  # r_2(65) = 16
    # 3, 6 and 7 are the n <= 10 that are not sums of two squares
    page = client.get("/Example/?n=1-10&is_sum=no").get_data(as_text=True)
    assert "3 matches" in page
    # both conditions on the number of representations apply together
    def matches(url):
        return int(re.search(r"(\d+) match", client.get(url).get_data(as_text=True)).group(1))
    assert matches("/Example/?num_reps=2&is_sum=yes") == matches("/Example/?num_reps=2")
    assert "No matches" in client.get("/Example/?num_reps=2&is_sum=no").get_data(as_text=True)
    assert "No matches" in client.get("/Example/?num_reps=0&is_sum=yes").get_data(as_text=True)
    # a search input error is reported on the search page
    page = client.get("/Example/?n=abc").get_data(as_text=True)
    assert "not a valid input" in page


def test_jump_and_random(client):
    assert client.get("/Example/?jump=1105").headers["Location"].endswith("/Example/1105")
    assert re.search(r"/Example/\d+$", client.get("/Example/random").headers["Location"])
    # an unknown label goes back to the search page
    assert client.get("/Example/9999999").status_code == 302


def test_object_page(client):
    page = client.get("/Example/65").get_data(as_text=True)
    assert "$1^2 + 8^2$" in page and "$4^2 + 7^2$" in page
    assert "r_2(65) = 16" in page


def test_download(client):
    response = client.get("/Example/?n=1-50&download=1&format=gp&query=%7B%27n%27%3A+%7B%27%24gte%27%3A+1%2C+%27%24lte%27%3A+50%7D%7D")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Example Database" in text  # "downloaded from the Example Database"


def test_statistics(client, app):
    page = client.get("/Example/stats").get_data(as_text=True)
    assert page.count("Distribution of") == 3
    # every integer is in one of the buckets of r_2(n)
    from website import db
    from website.sections.example.main import ExampleStats
    with app.test_request_context("/Example/stats"):
        r2 = ExampleStats().distributions[0]
    assert sum(cell["count"] for cell in r2["counts"]) == db.example_sums.count()


def test_knowls(client):
    page = client.get("/knowledge/show/example.r2").get_data(as_text=True)
    assert "Jacobi" in page
    # the external reference becomes a link
    assert "wikipedia.org/wiki/Sum_of_two_squares_theorem" in client.get("/knowledge/render/example.r2").get_data(as_text=True)
    # knowls used on pages exist
    page = client.get("/Example/").get_data(as_text=True)
    assert 'knowl="example.r2"' in page


def test_login_and_edit_knowl(app, admin):
    username, password = admin
    client = app.test_client()
    response = client.post("/users/login", data={"name": username, "password": password, "next": ""},
                           follow_redirects=True)
    assert "your login was successful" in response.get_data(as_text=True)

    kid = "test.%s" % secrets.token_hex(4)
    page = client.get("/knowledge/edit/%s" % kid).get_data(as_text=True)
    assert "Edit Knowl" in page
    with client.session_transaction() as session:
        token = session["_csrf_token"]
    response = client.post("/knowledge/save", data={
        "id": kid, "title": "A test knowl", "content": "Content of the test knowl, with $x^2$.",
        "csrf_token": token,
    }, follow_redirects=True)
    assert response.status_code == 200
    page = client.get("/knowledge/show/%s" % kid).get_data(as_text=True)
    assert "Content of the test knowl" in page

    # reviewing it, then deleting it (administrators only)
    from lmfdb_utils.knowledge.knowl import Knowl
    k = Knowl(kid)
    assert client.get("/knowledge/review/%s/%s" % (kid, k.ms_timestamp), follow_redirects=True).status_code == 200
    assert Knowl(kid).status == 1
    client.get("/knowledge/delete/%s" % kid, follow_redirects=True)
    # administrators still see deleted knowls; others do not
    assert "(DELETED)" in client.get("/knowledge/show/%s" % kid).get_data(as_text=True)
    client.get("/users/logout")
    assert client.get("/knowledge/show/%s" % kid).status_code == 404


def test_anonymous_cannot_edit(client):
    response = client.get("/knowledge/edit/example.r2")
    assert response.status_code in (302, 401)
