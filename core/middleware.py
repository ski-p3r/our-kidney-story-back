import logging
import traceback
from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger(__name__)

class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(f"Exception occurred: {exception}")
        logger.error(traceback.format_exc())
        
        return JsonResponse({
            'error': str(exception),
            'detail': 'An unexpected error occurred. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
