from usu import loads


def test_basic_map():
    assert {"key": "value"} == loads("{:key value}")


def test_basic_list():
    assert [1, 2, 3, 4, 5] == loads("[1 2 3 4 5]")


def test_bool():
    assert dict(key=True) == loads("{:key true}")
    assert dict(key=False) == loads("{:key False}")


def test_nested_map():
    assert {"level-one": {"level-two": "value"}} == loads(
        "{:level-one {:level-two value}}"
    )


def test_list_of_maps():
    assert [{"id": "foo", "value": "bar"}, {"id": "bar", "value": "foo"}] == loads(
        """
        [
          {:id foo :value bar}
          {:id bar :value foo}
        ]
        """
    )


def test_map_of_lists():
    assert {"list-1": [1, 2, 3, 4, 5], "list-2": ["red", "orange", "yellow"]} == loads(
        """
        {
          :list-1 [1 2 3 4 5]
          :list-2 [red orange yellow]
        }
        """
    )


def test_empty_list():
    assert {"empty-list": []} == loads("{:empty-list []}")


def test_empty_map():
    assert {"empty-map": {}} == loads("{:empty-map {}}")


def test_comments():
    assert (dict(key="value")) == loads(
        """
        # A comment that will be ignored
        {
            :key value
            # :commented-key commented-value
        }
        """
    )


def test_comment_block():
    assert [dict(key="value")] == loads(
        """
        # A comment that will be ignored
        [
            {:key value}
            #(
                :commented-key
                    commented-value
            )#
        ]
        """
    )
