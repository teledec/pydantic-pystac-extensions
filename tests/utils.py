"""Utils module."""


def should_fail(func, args, exception_cls):
    """Helper with intended failing tests."""
    try:
        if isinstance(args, list):
            func(*args)
        else:
            func(**args)

        raise AssertionError("This test should fail!")
    except exception_cls:
        print("Failing as expected :)")
