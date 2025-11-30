import pytest
from lol_replay_recorder.domain.errors import CustomError, HTTPError, LockfileError, ProcessError, ConfigError


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


# HTTPError tests
@pytest.mark.unit
def test_http_error_inherits_from_custom_error():
    assert issubclass(HTTPError, CustomError)


@pytest.mark.unit
def test_http_error_with_details():
    url = "https://example.com/api"
    status_code = 404
    message = "Not found"

    error = HTTPError(url, status_code, message)

    assert error.url == url
    assert error.status_code == status_code
    assert error.message == message
    assert str(error) == f"HTTP {status_code} for {url}: {message}"


@pytest.mark.unit
def test_http_error_repr():
    error = HTTPError("https://example.com", 500, "Server error")
    expected = "HTTPError(url='https://example.com', status_code=500, message='Server error')"
    assert repr(error) == expected


@pytest.mark.unit
def test_http_error_can_be_raised():
    with pytest.raises(HTTPError) as exc_info:
        raise HTTPError("https://api.example.com", 500, "Internal server error")

    error = exc_info.value
    assert error.url == "https://api.example.com"
    assert error.status_code == 500
    assert error.message == "Internal server error"


# LockfileError tests
@pytest.mark.unit
def test_lockfile_error_inherits_from_custom_error():
    assert issubclass(LockfileError, CustomError)


@pytest.mark.unit
def test_lockfile_error_default_message():
    error = LockfileError()
    assert str(error) == "Lockfile not found or invalid"


@pytest.mark.unit
def test_lockfile_error_custom_message():
    message = "Custom lockfile error"
    error = LockfileError(message)
    assert str(error) == message


@pytest.mark.unit
def test_lockfile_error_can_be_raised():
    with pytest.raises(LockfileError) as exc_info:
        raise LockfileError("Lockfile corrupted")
    assert str(exc_info.value) == "Lockfile corrupted"


# ProcessError tests
@pytest.mark.unit
def test_process_error_inherits_from_custom_error():
    assert issubclass(ProcessError, CustomError)


@pytest.mark.unit
def test_process_error_with_message():
    message = "Process failed to start"
    error = ProcessError(message)
    assert str(error) == message


@pytest.mark.unit
def test_process_error_can_be_raised():
    with pytest.raises(ProcessError) as exc_info:
        raise ProcessError("Process already running")
    assert str(exc_info.value) == "Process already running"


# ConfigError tests
@pytest.mark.unit
def test_config_error_inherits_from_custom_error():
    assert issubclass(ConfigError, CustomError)


@pytest.mark.unit
def test_config_error_with_message():
    message = "Configuration file not found"
    error = ConfigError(message)
    assert str(error) == message


@pytest.mark.unit
def test_config_error_can_be_raised():
    with pytest.raises(ConfigError) as exc_info:
        raise ConfigError("Invalid YAML syntax")
    assert str(exc_info.value) == "Invalid YAML syntax"


# Test error hierarchy
@pytest.mark.unit
def test_all_errors_inherit_from_custom_error():
    """Ensure all custom errors inherit from CustomError base class."""
    assert issubclass(HTTPError, CustomError)
    assert issubclass(LockfileError, CustomError)
    assert issubclass(ProcessError, CustomError)
    assert issubclass(ConfigError, CustomError)


@pytest.mark.unit
def test_all_errors_inherit_from_exception():
    """Ensure all custom errors can be caught as Exception."""
    assert issubclass(CustomError, Exception)
    assert issubclass(HTTPError, Exception)
    assert issubclass(LockfileError, Exception)
    assert issubclass(ProcessError, Exception)
    assert issubclass(ConfigError, Exception)