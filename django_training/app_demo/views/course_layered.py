from django.urls import reverse_lazy
from django_training.app_base.views.base import PBBaseCreateView
from django_training.app_base.views.base import PBBaseDeleteView
from django_training.app_base.views.base import PBBaseListView
from django_training.app_base.views.base import PBBaseUpdateView
from django_training.app_demo.forms import CourseForm
from django_training.app_demo.models import Course
from django_training.app_demo.services.course import CourseService


class CourseLayeredListView(PBBaseListView):
    """Path B: Layered Architecture ListView delegating query and filtering to CourseService."""

    model = Course
    service_class = CourseService
    template_name = "app_demo/layered/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        is_active_str = self.request.GET.get("is_active")

        is_active = None
        if is_active_str == "true":
            is_active = True
        elif is_active_str == "false":
            is_active = False

        # Query logic is isolated in the service layer, keeping the view thin
        courses, error = self.get_service().list_courses(
            search_query=search_query,
            is_active=is_active,
        )
        if error:
            # Error handling has already logged the error, we display a user-friendly message
            from django.contrib import messages
            messages.error(self.request, f"Error loading courses: {error}")
            return Course.objects.none()
        return courses


class CourseLayeredCreateView(PBBaseCreateView):
    """Path B: Layered Architecture CreateView delegating creation to CourseService."""

    model = Course
    service_class = CourseService
    form_class = CourseForm
    template_name = "app_demo/layered/course_form.html"
    success_url = reverse_lazy("courses:layered_list")


class CourseLayeredUpdateView(PBBaseUpdateView):
    """Path B: Layered Architecture UpdateView delegating retrieval and update to CourseService."""

    model = Course
    service_class = CourseService
    form_class = CourseForm
    template_name = "app_demo/layered/course_form.html"
    success_url = reverse_lazy("courses:layered_list")


class CourseLayeredDeleteView(PBBaseDeleteView):
    """Path B: Layered Architecture DeleteView delegating retrieval and deletion to CourseService."""

    model = Course
    service_class = CourseService
    template_name = "app_demo/layered/course_confirm_delete.html"
    success_url = reverse_lazy("courses:layered_list")
