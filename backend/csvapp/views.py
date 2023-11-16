import csv
import json

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import CsvFile
from .serializers import CsvFileSerializer
from .utils import create_enriched_csv_file


class CsvFileViewSet(viewsets.ModelViewSet):
    queryset = CsvFile.objects.all()
    serializer_class = CsvFileSerializer
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'])
    def upload(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        file_name = csv_file.name

        csv_file_instance = CsvFile.objects.create(
            name=file_name,
            csv_file=csv_file
        )

        response_data = {
            'id': csv_file_instance.id,
            'name': csv_file_instance.name,
            'uploaded_at': csv_file_instance.uploaded_at,
            'content': []
        }
        with open(csv_file_instance.csv_file.path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                response_data["content"].append(dict(row))

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def enrich(self, request, *args, **kwargs):
        selected_column = request.data.get('selectedColumn')
        api_response_column = request.data.get('apiResponseColumn')
        file_id = request.data.get('fileId')
        external_file_str = request.POST.get('file')
        if external_file_str is None:
            return Response({'error': 'externalFile not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            external_file_data = json.loads(external_file_str)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON.'}, status=status.HTTP_400_BAD_REQUEST)

        if not external_file_data:
            return Response({'error': 'No external file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            csv_file_instance = CsvFile.objects.get(pk=file_id)
        except CsvFile.DoesNotExist:
            return Response({'error': 'CSV file not found.'}, status=status.HTTP_404_NOT_FOUND)

        with open(csv_file_instance.csv_file.path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            csv_data = [row for row in csv_reader]

        # Enrich the CSV data
        enriched_csv_data = []
        for csv_row in csv_data:
            for external_row in external_file_data[0]:
                if str(csv_row.get(selected_column)) == str(external_row.get(api_response_column)):
                    enriched_row = {**csv_row, **external_row}
                    enriched_csv_data.append(enriched_row)
                    break
            else:
                enriched_csv_data.append(csv_row)

        create_enriched_csv_file(csv_file_instance, enriched_csv_data)

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def review(self, request):
        files = CsvFile.objects.all()
        response_data = []

        for file in files:
            file_data = {
                "file_id": file.id,
                "file_name": file.name,
                "uploaded_at": file.uploaded_at,
                "content": []
            }

            with open(file.csv_file.path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    file_data["content"].append(dict(row))

            response_data.append(file_data)

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def retrieve_csv_file(self, request, pk=None):
        try:
            csv_file = CsvFile.objects.get(pk=pk)
        except CsvFile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        file_data = {
            "file_id": csv_file.id,
            "file_name": csv_file.name,
            "uploaded_at": csv_file.uploaded_at,
            "content": []
        }

        with open(csv_file.csv_file.path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                file_data["content"].append(dict(row))

        return Response(file_data, status=status.HTTP_200_OK)
