from django.urls import path
from django.views.generic import TemplateView
from django_training.app_demo.views import course_layered
from django_training.app_demo.views import course_standard

app_name = "courses"

urlpatterns = [
    # Dashboard / comparison guide landing page
    path(
        "",
        TemplateView.as_view(template_name="app_demo/dashboard.html"),
        name="dashboard",
    ),
    # Path A: Standard Django
    path("standard/", course_standard.CourseStandardListView.as_view(), name="standard_list"),
    path("standard/create/", course_standard.CourseStandardCreateView.as_view(), name="standard_create"),
    path("standard/<int:pk>/update/", course_standard.CourseStandardUpdateView.as_view(), name="standard_update"),
    path("standard/<int:pk>/delete/", course_standard.CourseStandardDeleteView.as_view(), name="standard_delete"),
    # Path B: Layered Architecture
    path("layered/", course_layered.CourseLayeredListView.as_view(), name="layered_list"),
    path("layered/create/", course_layered.CourseLayeredCreateView.as_view(), name="layered_create"),
    path("layered/<int:pk>/update/", course_layered.CourseLayeredUpdateView.as_view(), name="layered_update"),
    path("layered/<int:pk>/delete/", course_layered.CourseLayeredDeleteView.as_view(), name="layered_delete"),
]
