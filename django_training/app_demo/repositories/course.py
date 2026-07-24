from typing import Any
from django_training.app_base.repositories.base import PBBaseRepository
from django_training.app_demo.models import Course


class CourseRepository(PBBaseRepository[Course]):
    """Repository handling database operations for the Course model."""

    model = Course

    def create(self, **kwargs: Any) -> Course:
        """Overrides base create to inject current user as 'created_by'."""
        if self.user and self.user.is_authenticated:
            kwargs["created_by"] = self.user
        return super().create(**kwargs)
