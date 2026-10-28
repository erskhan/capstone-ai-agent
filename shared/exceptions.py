"""Custom exceptions for the application."""


class LoanApprovalException(Exception):
    """Base exception for loan approval system."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        """Initialize exception."""
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationException(LoanApprovalException):
    """Raised when data validation fails."""

    def __init__(self, message: str, field: str = None):
        """Initialize validation exception."""
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class ApplicationNotFoundException(LoanApprovalException):
    """Raised when application is not found."""

    def __init__(self, application_id: str):
        """Initialize not found exception."""
        super().__init__(
            f"Application {application_id} not found", "NOT_FOUND"
        )
        self.application_id = application_id


class AgentException(LoanApprovalException):
    """Raised when agent execution fails."""

    def __init__(self, message: str, agent_name: str = None):
        """Initialize agent exception."""
        super().__init__(message, "AGENT_ERROR")
        self.agent_name = agent_name


class WorkflowException(LoanApprovalException):
    """Raised when workflow execution fails."""

    def __init__(self, message: str, workflow_id: str = None):
        """Initialize workflow exception."""
        super().__init__(message, "WORKFLOW_ERROR")
        self.workflow_id = workflow_id


class DatabaseException(LoanApprovalException):
    """Raised when database operation fails."""

    def __init__(self, message: str):
        """Initialize database exception."""
        super().__init__(message, "DATABASE_ERROR")


class AuthenticationException(LoanApprovalException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        """Initialize auth exception."""
        super().__init__(message, "AUTH_ERROR")


class AuthorizationException(LoanApprovalException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Authorization failed"):
        """Initialize authorization exception."""
        super().__init__(message, "AUTHZ_ERROR")
