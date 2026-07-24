from django.conf import settings
from django.db import models


class Course(models.Model):
    """Represents a Course in the educational system.

    Includes standard informational fields and audit fields for tracking.
    """

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=255)
    credits = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_courses",
    )

    class Meta:
        verbose_name = "course"
        verbose_name_plural = "courses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} - {self.title}"
