from rest_framework import generics, status, viewsets
from .models import Certificate, VerificationLog
from .serializers import CertificateSerializer, VerificationSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response


class SoftDeletedCertificateView(generics.ListAPIView):
    queryset = Certificate.objects.filter(deleted=True).order_by('certificate_id')  # Order by certificate_id (or another field)
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]  # Adjust permission as required

    def get(self, request, *args, **kwargs):
        certificates = self.get_queryset()
        serializer = self.get_serializer(certificates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CertificateCreateView(viewsets.ModelViewSet):
    queryset = Certificate.objects.filter(deleted=False).order_by('id')
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        print(f"POST request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print(f"Serializer errors: {serializer.errors}")  # Logs serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CertificateVerificationView(generics.GenericAPIView):
    serializer_class = VerificationSerializer

    def post(self, request, *args, **kwargs):
        certificate_id = request.data.get('certificate_id')
        certificate = Certificate.objects.filter(certificate_id=certificate_id, deleted=False).first()  # Exclude deleted
        if certificate:
            VerificationLog.objects.create(certificate=certificate, verifier_ip=request.META.get('REMOTE_ADDR'))
            certificate.verification_count += 1
            certificate.save()
            return Response({"status": "valid"}, status=status.HTTP_200_OK)
        return Response({"status": "invalid"}, status=status.HTTP_404_NOT_FOUND)


class CertificateSoftDeleteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, certificate_id, *args, **kwargs):
        certificate = Certificate.objects.filter(certificate_id=certificate_id).first()
        if certificate and not certificate.deleted:
            certificate.soft_delete()
            return Response({"status": "certificate deleted"}, status=status.HTTP_200_OK)
        return Response({"error": "Certificate not found or already deleted"}, status=status.HTTP_404_NOT_FOUND)



class CertificateRestoreView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, certificate_id, *args, **kwargs):
        certificate = Certificate.objects.filter(certificate_id=certificate_id).first()
        if certificate and certificate.deleted:
            certificate.restore()
            return Response({"status": "certificate restored"}, status=status.HTTP_200_OK)
        return Response({"error": "Certificate not found or not deleted"}, status=status.HTTP_404_NOT_FOUND)

