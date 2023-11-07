from rest_framework import serializers
from .models import CsvFile


class CsvFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvFile
        fields = '__all__'
