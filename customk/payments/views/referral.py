from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.services import verify_referral_code


class ReferralView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        code = request.GET.get("code")
        data = verify_referral_code(code)

        return Response(data, status=status.HTTP_200_OK)
