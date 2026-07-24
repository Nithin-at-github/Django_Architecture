from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView


class PermissionServiceMixin:
    """Mixin to dynamically instantiate and bind request.user to a Service class."""

    service_class = None

    def get_service(self):
        if self.service_class is None:
            raise NotImplementedError("View subclass must specify a 'service_class' attribute.")
        # Bind the request's user context to the service
        return self.service_class(user=self.request.user)


class PBBaseListView(PermissionServiceMixin, ListView):
    """Base list view that retrieves querysets via a Service layer."""

    def get_queryset(self):
        service = self.get_service()
        # Subclasses can override lists by specifying custom service calls
        if hasattr(service, "list_items"):
            queryset, error = service.list_items()
        else:
            queryset, error = service.list()

        if error:
            messages.error(self.request, f"Failed to retrieve data: {error}")
            return self.model.objects.none() if self.model else []
        return queryset


class PBBaseCreateView(PermissionServiceMixin, CreateView):
    """Base create view that delegates record creation to the Service layer."""

    def form_valid(self, form):
        service = self.get_service()
        instance, error = service.create(form.cleaned_data)
        if error:
            form.add_error(None, error)
            return self.form_invalid(form)

        self.object = instance
        messages.success(self.request, f"{self.model._meta.verbose_name.capitalize()} created successfully.")
        return redirect(self.get_success_url())


class PBBaseUpdateView(PermissionServiceMixin, UpdateView):
    """Base update view that retrieves object and performs update via the Service layer."""

    def get_object(self, queryset=None):
        service = self.get_service()
        pk = self.kwargs.get(self.pk_url_kwarg or "pk")
        instance, error = service.get(pk)
        if error or not instance:
            raise Http404(f"Object not found: {error}")
        return instance

    def form_valid(self, form):
        service = self.get_service()
        instance, error = service.update(self.object.pk, form.cleaned_data)
        if error:
            form.add_error(None, error)
            return self.form_invalid(form)

        self.object = instance
        messages.success(self.request, f"{self.model._meta.verbose_name.capitalize()} updated successfully.")
        return redirect(self.get_success_url())


class PBBaseDeleteView(PermissionServiceMixin, DeleteView):
    """Base delete view that retrieves object and performs delete via the Service layer."""

    def get_object(self, queryset=None):
        service = self.get_service()
        pk = self.kwargs.get(self.pk_url_kwarg or "pk")
        instance, error = service.get(pk)
        if error or not instance:
            raise Http404(f"Object not found: {error}")
        return instance

    def form_valid(self, form):
        service = self.get_service()
        success, error = service.delete(self.object.pk)
        if error or not success:
            messages.error(self.request, f"Failed to delete: {error}")
            return redirect(self.get_success_url())

        messages.success(self.request, f"{self.model._meta.verbose_name.capitalize()} deleted successfully.")
        return redirect(self.get_success_url())
