from django.db.models import Q
from django_training.app_base.services.base import PBBaseService
from django_training.app_demo.repositories.course import CourseRepository


class CourseService(PBBaseService):
    """Service layer orchestrating business logic and filtering for Course objects."""

    repository_class = CourseRepository

    def list_courses(
        self,
        search_query=None,
        is_active=None,
        sort_by=None,
    ):
        """Lists courses with optional search terms and activity filters."""
        def _list():
            qs = self.repository.fetch_queryset()
            if search_query:
                qs = qs.filter(
                    Q(title__icontains=search_query)
                    | Q(code__icontains=search_query)
                    | Q(instructor__icontains=search_query),
                )
            if is_active is not None:
                qs = qs.filter(is_active=is_active)
            if sort_by:
                qs = qs.order_by(sort_by)
            else:
                # Default sorting
                qs = qs.order_by("-created_at")
            return qs

        return self.run_safe(_list)
