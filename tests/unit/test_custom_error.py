import pytest
from lol_replay_recorder.models.custom_error import CustomError


@pytest.mark.unit
def test_custom_error_inherits_from_exception():
    assert issubclass(CustomError, Exception)


@pytest.mark.unit
def test_custom_error_with_message():
    error = CustomError("Test error message")
    assert str(error) == "Test error message"


@pytest.mark.unit
def test_custom_error_with_multiple_args():
    error = CustomError("Error", "arg1", "arg2")
    assert str(error) == "Error"
    assert error.args == ("Error", "arg1", "arg2")


@pytest.mark.unit
def test_custom_error_can_be_raised():
    with pytest.raises(CustomError) as exc_info:
        raise CustomError("Test error")
    assert str(exc_info.value) == "Test error"