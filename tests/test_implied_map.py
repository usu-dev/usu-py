from usu import loads


def test_implied_map():
    assert dict(key="value") == loads(":key value")
