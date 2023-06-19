from usu import loads


def test_quotes():
    assert ["Quoted String", "Next Quoted String", "Backtick Quoted"] == loads(
        """
    (
        "Quoted String"
        'Next Quoted String'
        `Backtick Quoted`
    )
    """
    )


def test_quoted_string():
    assert dict(quoted="We'll accept single quotes") == loads(
        """(:quoted "We'll accept single quotes")"""
    )


def test_backtick_quoted():
    assert dict(backticks='"Howdy!" - A Cowboy') == loads(
        '(:backticks `"Howdy!" - A Cowboy`)'
    )
