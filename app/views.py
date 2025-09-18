from rest_framework import status, views, generics
from rest_framework.response import Response
from django.db import transaction
from .models import LogJob
from .serializers import LogJobSerializer, LogUploadSerializer
from .services.parser import parse_log_lines
from .services.llm import build_prompt, call_llm

MAX_BYTES = 1_000_000

class JobCreateView(views.APIView):
    @staticmethod
    def post(request):
        ser = LogUploadSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        f = ser.validated_data["file"]

        if f.size > MAX_BYTES:
            return Response({"detail": "File too large (max 1MB)."}, status=413)

        lines = [line.decode("utf-8", errors="ignore") for line in f.readlines()]
        parsed = parse_log_lines(lines)

        with transaction.atomic():
            job = LogJob.objects.create(
                filename=f.name, size_bytes=f.size, status="PENDING", parsed_preview=parsed
            )
            prompt = build_prompt(parsed, f.name)
            try:
                summary = call_llm(prompt)
                job.llm_summary = summary
                job.status = "DONE"
                job.save()
            except Exception as e:
                job.status = "ERROR"
                job.error_msg = str(e)
                job.save()

        return Response(LogJobSerializer(job).data, status=status.HTTP_201_CREATED)

class JobRetrieveView(generics.RetrieveAPIView):
    queryset = LogJob.objects.all()
    serializer_class = LogJobSerializer
