from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django_training.app_demo.forms import CourseForm
from django_training.app_demo.models import Course


class CourseStandardListView(ListView):
    """Path A: Traditional Django ListView querying models directly."""

    model = Course
    template_name = "app_demo/standard/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        qs = super().get_queryset()
        search_query = self.request.GET.get("search")
        is_active = self.request.GET.get("is_active")

        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query)
                | Q(code__icontains=search_query)
                | Q(instructor__icontains=search_query),
            )

        if is_active == "true":
            qs = qs.filter(is_active=True)
        elif is_active == "false":
            qs = qs.filter(is_active=False)

        return qs.order_by("-created_at")


class CourseStandardCreateView(CreateView):
    """Path A: Traditional Django CreateView performing form.save() in the view."""

    model = Course
    form_class = CourseForm
    template_name = "app_demo/standard/course_form.html"
    success_url = reverse_lazy("courses:standard_list")

    def form_valid(self, form):
        # In Standard Django, logic like setting audit fields is done directly in the view
        form.instance.created_by = self.request.user
        messages.success(self.request, "Course created successfully (Standard Style).")
        return super().form_valid(form)


class CourseStandardUpdateView(UpdateView):
    """Path A: Traditional Django UpdateView updating model directly."""

    model = Course
    form_class = CourseForm
    template_name = "app_demo/standard/course_form.html"
    success_url = reverse_lazy("courses:standard_list")

    def form_valid(self, form):
        messages.success(self.request, "Course updated successfully (Standard Style).")
        return super().form_valid(form)


class CourseStandardDeleteView(DeleteView):
    """Path A: Traditional Django DeleteView deleting model directly."""

    model = Course
    template_name = "app_demo/standard/course_confirm_delete.html"
    success_url = reverse_lazy("courses:standard_list")

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Course deleted successfully (Standard Style).")
        return super().post(request, *args, **kwargs)
