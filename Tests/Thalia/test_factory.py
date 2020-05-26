from Thalia import create_app


def test_config():
    assert not create_app().testing, "testing should not be on by default"
    assert create_app({"TESTING": True}).testing, "testing should be possible to enable"
