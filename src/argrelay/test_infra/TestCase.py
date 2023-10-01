class TestCase:
    """
    1.
    The input data provided by the `TestCase` (and its derived classes)
    parameterizes test scenario code and allows multiple test cases (e.g. via `TestCase.subTest`)
    run without changing that test scenario code.
    2.
    For test scenarios with variable input parameters, `TestCase` works as a builder pattern to provide:
    *   flexibility by omitting some parameters
        (assuming some defaults)
    *   flexibility by reordering parameters
        (e.g. instead of tuple with positional args, use named args or set them via func)
    *   flexibility by separating:
        *   partial input specification (e.g. common defaults)
        *   final input specification (e.g. individual overrides)
    3.
    Also, `TestCase` drives settings for any other `test_infra` classes, for example:
    *   Select specific `ServerActionVerifier` based on `CompType`.
    *   Init `EnvMockBuilder` mock the test input.
    *   Ensure input makes sense within given `*TestClass`.
    *   Ensure there is no missing or conflicting combination of input parameters.
    """

    def __init__(
        self,
        line_no: int,
        case_comment: str,
    ):
        self.line_no: int = line_no
        self.case_comment: str = case_comment

    def __str__(
        self,
    ):
        return f"line:{self.line_no}: {self.case_comment}"
