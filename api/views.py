from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.conf import settings
import os
from .utils import crawler_data  # Import đúng đường dẫn tới hàm

class SendZaloMessageView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            zalo_file_path = request.data.get('zalo_file_path')
            phone_number = request.data.get('phone_number')
            messages = request.data.getlist('messages')  # Chỉ dùng được với form-data

            default_delta_y_search = int(request.data.get('default_delta_y_search', 0))
            wait_image_loading_time = int(request.data.get('wait_image_loading_time', 3))

            # Lấy file ảnh nếu có
            image_file = request.data.get('image_file')
            crawler_data(
                zalo_file_path=zalo_file_path,
                phone_number=phone_number,
                messages=messages,
                default_delta_y_search=default_delta_y_search,
                image_path_from_client=image_file,
                wait_image_loading_time=wait_image_loading_time
            )

            return Response({'message': 'Thành công'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)