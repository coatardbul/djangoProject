
from django.http import HttpResponse

from rest_framework.decorators import api_view





@api_view(['POST'])
def learn(request):
    return HttpResponse("1111")
