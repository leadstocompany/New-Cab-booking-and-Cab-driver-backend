from django.db import models
from django.utils import timezone
import cloudinary
import cloudinary.uploader
import cloudinary.models

from JLP_MyRide import settings


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.localtime)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.localtime()
        super().save(*args, **kwargs)


class CloudinaryBaseModelUser(models.Model):
    class Meta:
        abstract = True  # No database table will be created for this model

    def get_cloudinary_folder(self, field_name):
        """
        Override this method in child models to define different folder structures.
        Example: return f"users/{self.id}/profile" for user profile images.
        """
        raise NotImplementedError(
            "You must implement get_cloudinary_folder(field_name) in subclasses"
        )

    def get_file_fields(self):
        """Override in child models to return a list of file fields (e.g., ['icon', 'photo', 'document'])."""
        raise NotImplementedError("You must implement get_file_fields() in subclasses")

    def save(self, *args, **kwargs):
        """Handles file upload and old file deletion."""
        if self.pk:
            old_instance = self.__class__.objects.filter(pk=self.pk).first()
            if old_instance:
                for field_name in self.get_file_fields():
                    old_file = getattr(old_instance, field_name, None)
                    new_file = getattr(self, field_name, None)

                    if old_file and old_file != new_file:
                        cloudinary.uploader.destroy(old_file)

        for field_name in self.get_file_fields():
            file_instance = getattr(self, field_name, None)

            if isinstance(file_instance, str):
                continue

            if file_instance:
                folder_path = self.get_cloudinary_folder(
                    field_name
                )  # Get dynamic folder
                # Upload the file manually to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    file_instance,
                    folder=folder_path,
                    resource_type="auto",
                    use_filename=True,
                    unique_filename=True,
                )
                print(upload_result)
                setattr(self, field_name, upload_result["secure_url"])

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete files from Cloudinary when the instance is deleted."""
        for field_name in self.get_file_fields():
            file_instance = getattr(self, field_name, None)
            if file_instance:
                cloudinary.uploader.destroy(file_instance)
        super().delete(*args, **kwargs)


class CloudinaryBaseModel(BaseModel, CloudinaryBaseModelUser):
    """Abstract model for handling Cloudinary file uploads dynamically."""

    class Meta:
        abstract = True  # No database table will be created for this model

    def get_cloudinary_folder(self, field_name):
        """
        Override this method in child models to define different folder structures.
        Example: return f"users/{self.id}/profile" for user profile images.
        """
        raise NotImplementedError(
            "You must implement get_cloudinary_folder(field_name) in subclasses"
        )

    def get_file_fields(self):
        """Override in child models to return a list of file fields (e.g., ['icon', 'photo', 'document'])."""
        raise NotImplementedError("You must implement get_file_fields() in subclasses")
