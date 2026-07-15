from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.site_blocks_service import get_all_site_content


class SiteBlocksView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(get_all_site_content())
