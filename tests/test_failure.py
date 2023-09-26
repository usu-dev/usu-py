import pytest
from usu import UsuDecodeError, loads


def test_duplicate_keys():
    with pytest.raises(UsuDecodeError):
        loads("{:key value :key value}")


def test_key_in_list():
    with pytest.raises(UsuDecodeError):
        loads(
            """
        [
          entry 1
          entry 2
          :a-key
        ]
        """
        )
