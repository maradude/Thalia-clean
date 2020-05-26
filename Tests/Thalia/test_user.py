from Thalia.extensions import db
from Thalia.models import user
import pytest

import sqlalchemy


def test_new_user(client):
    """
    functional test for testing user creation and storage
    """
    name = "john_smith"
    pw = "123456a"
    assert (
        user.User.query.filter_by(username=name).first() is None
    ), "username should not be db already"

    new_user = user.User(username=name)
    new_user.set_password(pw)

    assert new_user.password_hash != pw, "passwords should be hashed"
    assert new_user.check_password(pw), "checking the same pw should return true"

    assert not new_user.check_password("012938"), "checking if different pw fails"
    assert not new_user.check_password("012938A"), "checking if different pw fails"
    assert not new_user.check_password(
        "12345a6"
    ), "checking if same pw in different order fails"

    db.session.add(new_user)
    db.session.commit()

    id_ = user.User.query.filter_by(username=name).first().id
    assert (
        user.User.query.filter_by(username=name).count() == 1
    ), "user should only be inserted once"
    same_user = user.load_user(id_)
    assert same_user == new_user, "user should be accessible from database"


def test_duplicate_user(client, default_user):
    new_user = user.User(username=default_user["username"])
    new_user.set_password("test")
    db.session.add(new_user)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.commit()
        pytest.fail("should not be able to insert same username twice")


def test_creation_without_password(client):
    username = "a"
    new_user = user.User(username=username)
    db.session.add(new_user)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.commit()
        pytest.fail("exception should be raised when missing password hash")
