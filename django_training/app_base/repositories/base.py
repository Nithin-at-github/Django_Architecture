from django.db import models


class PBBaseRepository:
    """Base repository class wrapping standard Django ORM queries and CRUD mutations."""

    model = None

    def __init__(self, user=None):
        self.user = user
        if self.model is None:
            raise NotImplementedError("Concrete repository subclasses must specify a 'model' attribute.")

    def fetch_queryset(self):
        """Returns the base QuerySet for the model.

        Concrete repositories should override or extend this to prefetch or filter queries.
        """
        return self.model.objects.all()

    def get_by_id(self, pk):
        """Fetches a single model instance by primary key.

        Returns None if the instance does not exist.
        """
        try:
            return self.fetch_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def create(self, **kwargs):
        """Creates and saves a new model instance."""
        return self.model.objects.create(**kwargs)

    def update(self, instance, **kwargs):
        """Updates and saves an existing model instance with specified fields."""
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Deletes a model instance from the database."""
        instance.delete()

    def delete_multiple(self, queryset):
        """Deletes all instances in the provided queryset.

        Returns the number of deleted records.
        """
        count, _ = queryset.delete()
        return count

    def bulk_create(self, instances, **kwargs):
        """Creates multiple model instances in bulk."""
        return self.model.objects.bulk_create(instances, **kwargs)
