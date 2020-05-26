import os
import tempfile

import pandas as pd
import pytest

from Thalia import create_app
from Thalia.extensions import db
from Thalia.models.user import User
from decimal import Decimal

NAME = "test_default"
PW = "test_mypw@2"


class MockFdConnection:
    def __init__(self, *args, **kwargs):
        self.read = MockFdReader()


class MockFdReader:
    def __init__(self):
        pass

    def read_assets(self):
        return pd.DataFrame({"Name": []})

    def read_asset_values(self, *args, **kwargs):
        cols = ["ADate", "AssetTicker", "AOpen", "AClose", "ALow", "AHigh"]
        data = [
            [pd.Timestamp(2020, 1, 1,), "RCK", "2", "2", "2", "2"],
            [pd.Timestamp(2000, 3, 9), "RCK", "4", "6", "4", "6"],
            [pd.Timestamp(2000, 3, 9), "OVF", "40", "40", "40", "40"],
            [pd.Timestamp(2000, 3, 10), "OVF", "30", "30", "30", "30"],
            [pd.Timestamp(2000, 3, 11), "OVF", "40", "40", "40", "40"],
            [pd.Timestamp(2000, 3, 12), "OVF", "30", "30", "30", "30"],
            [pd.Timestamp(2000, 3, 13), "OVF", "40", "40", "40", "40"],
            [pd.Timestamp(2000, 3, 14), "OVF", "30", "30", "30", "30"],
            [pd.Timestamp(2000, 3, 15), "OVF", "40", "40", "40", "40"],
            [pd.Timestamp(2000, 3, 16), "OVF", "35", "35", "35", "35"],
            [pd.Timestamp(2000, 3, 17), "OVF", "25", "25", "25", "25"],
            [pd.Timestamp(2000, 3, 18), "OVF", "15", "15", "15", "15"],
            [pd.Timestamp(2000, 3, 9), "NOVF", "1", "1", "1", "1"],
            [pd.Timestamp(2000, 3, 10), "NOVF", "3", "3", "3", "3"],
            [pd.Timestamp(2000, 3, 11), "NOVF", "4", "4", "4", "4"],
            [pd.Timestamp(2000, 3, 12), "NOVF", "3", "3", "3", "3"],
            [pd.Timestamp(2000, 3, 13), "NOVF", "4", "4", "4", "4"],
            [pd.Timestamp(2000, 3, 14), "NOVF", "4", "9", "9", "9"],
            [pd.Timestamp(2000, 3, 15), "NOVF", "3", "3", "3", "3"],
            [pd.Timestamp(2000, 3, 16), "NOVF", "4", "4", "4", "4"],
            [pd.Timestamp(2000, 3, 17), "NOVF", "3", "3", "3", "3"],
            [pd.Timestamp(2000, 3, 18), "NOVF", "4", "4", "4", "4"],
        ]
        # Note OVF data has 1 large increase to simulate overfitting on
        df = pd.DataFrame(data=data, columns=cols)
        # fix types for anda input
        df["AOpen"] = df["AOpen"].map(float)
        df["AClose"] = df["AClose"].map(float)
        df["ALow"] = df["ALow"].map(float)
        df["AHigh"] = df["AHigh"].map(float)
        # return df.set_index(["ADate", "AssetTicker"])
        return df

    def read_asset_div_payout(self, *args, **kwargs):
        return pd.DataFrame({"Name": []})


@pytest.fixture(autouse=True)
def mock_finda(monkeypatch):
    import Finda
    from Thalia.dashboard import util

    monkeypatch.setattr(
        Finda.fd_manager.FdMultiController, "fd_connect", lambda *_: MockFdConnection()
    )
    monkeypatch.setattr(util, "findb", MockFdConnection())


@pytest.fixture
def app():
    """
    replaces the Thalia.__init__-file for the tests
    """

    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "WTF_CSRF_ENABLED": False,  # I think necessary for testing forms
        }
    )
    ctx = app.app_context()  # makes current_app point to this app
    ctx.push()

    db.create_all()  # I think only inits the ORM stuff

    yield app

    ctx.pop()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def default_user():
    new_user = User(username=NAME)
    new_user.set_password(PW)
    db.session.add(new_user)
    db.session.commit()

    yield {"username": NAME, "password": PW}

    db.session.delete(new_user)


@pytest.fixture
def client(app):
    """
    Allows test to make requests to the application without running the server
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    # stolen from official docs
    def __init__(self, client):
        self._client = client

    def login(self, username=NAME, password=PW):
        return self._client.post(
            "/login",
            follow_redirects=True,
            data={"username": username, "password": password},
        )

    def logout(self):
        return self._client.get("/logout", follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)
