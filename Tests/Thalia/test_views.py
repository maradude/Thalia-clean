import pytest
from flask import session, request
from flask_login import current_user

from Thalia.models.user import User

# Status codes
OK = 200


def test_register(client):
    # test that viewing the page renders without template errors
    assert client.get("/register", follow_redirects=True).status_code == OK

    # test that successful registration redirects to the login page
    with client as c:
        c.post(
            "/register",
            data={
                "username": "new_user",
                "password": "helloworld@2",
                "confirm_password": "helloworld@2",
            },
            follow_redirects=True,
        )
        assert request.path == "/login/"

    # test that the user was inserted into the database
    assert User.query.filter_by(username="new_user").first() is not None


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", None, b"Username not recognised"), (None, "a", b"Incorrect password")),
)
def test_login_validate_input(auth, default_user, username, password, message):
    username = username or default_user["username"]
    password = password or default_user["password"]
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, default_user, auth):

    with client:  # context necessary for login
        auth.login()
        assert "_user_id" in session, "login needs to work"
        auth.logout()
        assert "_user_id" not in session, "_user_id should be forgotten on logout"


def test_register_prevent_duplicates(client, default_user):
    response = client.post(
        "/register",
        data={
            "username": default_user["username"],
            "password": default_user["password"],
            "confirm_password": default_user["password"],
        },
        follow_redirects=True,
    )
    assert b"already registered" in response.data


def test_register_validate_input(client):
    response = client.post(
        "/register",
        data={"username": "foo", "password": "bar", "confirm_password": "baz!2312313"},
        follow_redirects=True,
    )
    assert b"Passwords must match" in response.data


def test_login(client, auth, default_user):
    # test that viewing the page renders without template errors
    assert client.get("/login", follow_redirects=True).status_code == OK

    # test that successful login redirects to the index page
    response = auth.login()

    # this is a poor way to test if redirected to homepage while logged in
    # ideally it would test if path is "/" and or something more
    home_page_message = bytes(f"{default_user['username']}", "utf-8")
    assert home_page_message in response.data

    # login request set the _user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["_user_id"] == "1"
        assert current_user.username == default_user["username"]

    # test redirection of login page to home when already signed in
    response = client.get("/login", follow_redirects=True)
    assert home_page_message in response.data

    # test redirection of registration page to home when already signed in
    response = client.get("/register", follow_redirects=True)
    assert home_page_message in response.data


def test_dashboard_access(client, default_user, auth):
    with client as c:
        response = c.get("/dashboard", follow_redirects=True)

        assert response.status_code == OK

        assert (
            request.path == "/login/"
        ), "non-loggedin users should be redirected to login page"

        auth.login()

        c.get("/dashboard", follow_redirects=True)

        assert response.status_code == OK
        assert (
            request.path == "/dashboard/"
        ), "logged in users should have access to dashbaord"
