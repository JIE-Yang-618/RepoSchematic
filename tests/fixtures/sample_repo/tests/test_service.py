from sample.service import UserService

def test_run():
    assert UserService().run() == []
