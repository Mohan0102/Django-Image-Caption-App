from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from . import ml_service

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
MAX_BYTES = 10 * 1024 * 1024


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class CaptionView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        image = request.FILES.get("image")
        if image is None:
            return Response({"error": "Upload an image in the 'image' field."}, status=400)
        if image.content_type not in ALLOWED_TYPES:
            return Response({"error": "Unsupported file type. Use JPG, PNG, WEBP or BMP."}, status=400)
        if image.size > MAX_BYTES:
            return Response({"error": "Image too large (max 10 MB)."}, status=400)
        try:
            caption = ml_service.generate_caption(image)
        except FileNotFoundError as e:
            return Response({"error": str(e)}, status=503)
        except Exception as e:  # unreadable image, model problems, etc.
            return Response({"error": f"Could not generate caption: {e}"}, status=500)
        return Response({"caption": caption})
