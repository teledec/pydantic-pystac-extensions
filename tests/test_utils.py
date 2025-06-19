"""Utils module."""

from tests.utils import should_fail


def test_should_fail():
    """Test should_fail function."""

    def no_error():
        print("yo")

    try:
        should_fail(no_error, [], ValueError)
    except AssertionError:
        # Message "this test should fail"
        pass
