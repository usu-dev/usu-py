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


def test_multiline_list():
    assert ["each line", "is it's own", "string"] == loads(
        """
        (
            each line
            is it's own
            string
        )
        """
    )


def test_multiline_unquoted_string():
    assert {"string": "this string should have all newlines removed"} == loads(
        """(
              :string >
                this string should
                have all newlines removed
           )
        """
    )


def test_unquoted_multiline_string():
    assert {
        "folded-string": "This string ignores newlines, which has various uses.",
        "unquoted-w-newlines": "This string uses its newline\nso who am I to argue?\n",
    } == loads(
        """
        (
          :folded-string >
            This string ignores newlines,
            which has various uses.

          :unquoted-w-newlines
            This string uses its newline
            so who am I to argue?
        )
        """
    )
