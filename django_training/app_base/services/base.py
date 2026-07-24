import logging
from typing import Any
from typing import Callable
from typing import Generic
from typing import TypeVar
from django.db import transaction
from django_training.app_base.repositories.base import PBBaseRepository

RepoT = TypeVar("RepoT", bound=PBBaseRepository)
ModelT = TypeVar("ModelT")


class PBBaseService(Generic[RepoT]):
    """Base class for service layer components.

    Coordinates business logic, handles exceptions, orchestrates transactions,
    and returns Go-style result/error tuples: (result, error_message).
    """

    repository_class: type[RepoT] = None
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, user: Any = None) -> None:
        self.user = user
        if self.repository_class is None:
            raise NotImplementedError("Concrete service subclasses must specify a 'repository_class' attribute.")
        self.repository = self.repository_class(user=user)

    def run_transactional(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> tuple[Any, str | None]:
        """Runs a service function wrapped inside a database transaction and exception handler."""
        try:
            with transaction.atomic():
                result = func(*args, **kwargs)
                return result, None
        except Exception as e:
            self.logger.exception("Error executing transaction in service %s: %s", self.__class__.__name__, e)
            return None, str(e)

    def run_safe(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> tuple[Any, str | None]:
        """Runs a service function wrapped in an exception handler (no transaction context)."""
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            self.logger.exception("Error executing safe operation in service %s: %s", self.__class__.__name__, e)
            return None, str(e)

    def get(self, pk: Any) -> tuple[Any | None, str | None]:
        """Fetches a single record by primary key."""
        def _get():
            return self.repository.get_by_id(pk)
        return self.run_safe(_get)

    def list(self) -> tuple[Any, str | None]:
        """Lists all records."""
        def _list():
            return self.repository.fetch_queryset()
        return self.run_safe(_list)

    def create(self, data: dict[str, Any]) -> tuple[Any | None, str | None]:
        """Creates a new record within a database transaction."""
        def _create():
            return self.repository.create(**data)
        return self.run_transactional(_create)

    def update(self, pk: Any, data: dict[str, Any]) -> tuple[Any | None, str | None]:
        """Updates an existing record within a database transaction."""
        def _update():
            instance = self.repository.get_by_id(pk)
            if not instance:
                raise ValueError("Record not found.")
            return self.repository.update(instance, **data)
        return self.run_transactional(_update)

    def delete(self, pk: Any) -> tuple[bool, str | None]:
        """Deletes a record by primary key within a database transaction."""
        def _delete():
            instance = self.repository.get_by_id(pk)
            if not instance:
                raise ValueError("Record not found.")
            self.repository.delete(instance)
            return True
        result, error = self.run_transactional(_delete)
        return bool(result), error
