import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django_training.app_demo.models import Course
from django_training.app_demo.repositories.course import CourseRepository
from django_training.app_demo.services.course import CourseService

User = get_user_model()


@pytest.mark.django_db
class TestCourseRepository:
    """Tests the CourseRepository functionality and ORM abstractions."""

    def test_create_without_user(self) -> None:
        repo = CourseRepository()
        course = repo.create(
            title="Introduction to Programming",
            code="CS-101",
            instructor="Prof. Turing",
            credits=3,
        )
        assert course.pk is not None
        assert course.code == "CS-101"
        assert course.created_by is None

    def test_create_with_user_context(self) -> None:
        user = User.objects.create_user(username="testteacher", password="password123")
        repo = CourseRepository(user=user)
        course = repo.create(
            title="Introduction to Programming",
            code="CS-101",
            instructor="Prof. Turing",
            credits=3,
        )
        assert course.pk is not None
        assert course.created_by == user

    def test_get_by_id(self) -> None:
        repo = CourseRepository()
        course = repo.create(
            title="Algorithms",
            code="CS-201",
            instructor="Prof. Knuth",
            credits=4,
        )
        fetched = repo.get_by_id(course.pk)
        assert fetched == course

        assert repo.get_by_id(9999) is None

    def test_update_and_delete(self) -> None:
        repo = CourseRepository()
        course = repo.create(
            title="Algorithms",
            code="CS-201",
            instructor="Prof. Knuth",
            credits=4,
        )

        repo.update(course, title="Advanced Algorithms", credits=5)
        course.refresh_from_db()
        assert course.title == "Advanced Algorithms"
        assert course.credits == 5

        repo.delete(course)
        assert repo.get_by_id(course.pk) is None


@pytest.mark.django_db
class TestCourseService:
    """Tests the CourseService layer, business logic orchestration, and Go-style error handling."""

    def test_create_success(self) -> None:
        service = CourseService()
        course, error = service.create(
            {
                "title": "Machine Learning",
                "code": "CS-401",
                "instructor": "Prof. Ng",
                "credits": 4,
            },
        )
        assert error is None
        assert course is not None
        assert course.code == "CS-401"

    def test_create_failure_uniqueness_constraint(self) -> None:
        # Create initial record
        service = CourseService()
        service.create(
            {
                "title": "Database Systems",
                "code": "CS-301",
                "instructor": "Prof. Codd",
                "credits": 3,
            },
        )

        # Attempt to create duplicate code
        course, error = service.create(
            {
                "title": "Another Database Systems Course",
                "code": "CS-301",
                "instructor": "Prof. Stonebraker",
                "credits": 4,
            },
        )
        # Verify that the service layer caught the database IntegrityError and returned a clean tuple
        assert course is None
        assert error is not None
        assert "UNIQUE constraint failed" in error or "duplicate key" in error or "CS-301" in error

    def test_list_courses_filters(self) -> None:
        service = CourseService()
        service.create(
            {
                "title": "Operating Systems",
                "code": "CS-302",
                "instructor": "Prof. Tanenbaum",
                "credits": 4,
                "is_active": True,
            },
        )
        service.create(
            {
                "title": "Computer Networks",
                "code": "CS-303",
                "instructor": "Prof. Kurose",
                "credits": 3,
                "is_active": False,
            },
        )

        # Filter by active status
        active_courses, error = service.list_courses(is_active=True)
        assert error is None
        assert active_courses.count() == 1
        assert active_courses.first().code == "CS-302"

        # Search matching title
        found_courses, error = service.list_courses(search_query="networks")
        assert error is None
        assert found_courses.count() == 1
        assert found_courses.first().code == "CS-303"

        # Search matching instructor
        found_courses, error = service.list_courses(search_query="Tanenbaum")
        assert error is None
        assert found_courses.count() == 1
        assert found_courses.first().code == "CS-302"
