from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .storage import MinioStorage
import uuid

class FileUploadView(APIView):
    """
    View to get a presigned URL for file upload to MinIO.
    """
    def post(self, request, *args, **kwargs):
        file_type = request.data.get('file_type', '')
        
        if not file_type:
            return Response(
                {'error': 'File type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Generate a unique filename
        file_extension = file_type.split('/')[-1]
        object_name = f"{uuid.uuid4()}.{file_extension}"
        
        # Get the presigned URL
        storage = MinioStorage()
        presigned_url = storage.get_presigned_put_url(object_name)
        
        # Get the public URL for the object
        public_url = storage.get_object_url(object_name)
        
        return Response({
            'presigned_url': presigned_url,
            'public_url': public_url
        })
