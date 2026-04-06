from uuid import UUID


class DomainException(Exception):
    """Base exception for domain errors."""

    pass


class ResourceNotFoundException(DomainException):
    """Raised when a resource is not found."""

    def __init__(self, resource_name: str, resource_id: UUID):
        self.resource_name = resource_name
        self.resource_id = resource_id
        super().__init__(f"{resource_name} com id {resource_id} não encontrado")


class ResourceAlreadyExistsException(DomainException):
    """Raised when trying to create a duplicate resource."""

    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        super().__init__(f"{resource_name} já existe")


class ValidationException(DomainException):
    """Raised when validation fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundException(DomainException):
    """Raised when a resource is not found."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BadRequestException(DomainException):
    """Raised when a bad request is made."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnauthorizedException(DomainException):
    """Raised when authentication fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
