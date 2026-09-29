from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint to verify backend API operational status.
    """
    return Response({
        "status": "success",
        "message": "Placement Portal API is running"
    })
