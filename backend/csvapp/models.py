from django.db import models

from django.db import models
import uuid


class CsvFile(models.Model):
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='csvs/')

    def __str__(self):
        return self.name