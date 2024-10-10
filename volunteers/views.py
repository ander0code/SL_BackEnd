from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .serializers import GetVolunteersSerializer,UserAuthSerializer ,VolunteerSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.models import Volunteers ,AuthUser
from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token

class VolunteersViewSet(ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    @action(detail=False, methods=['GET'], url_path='Get_Volunteers')
    def Get_Volunteers(self, request):
        try:
            # Obtener todos los voluntarios
            volunteers = Volunteers.objects.all()

            # Serializar los voluntarios
            serializer = GetVolunteersSerializer(volunteers, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['POST'], url_path='create_volunteer')
    def create_volunteer(self, request):
        
        User = get_user_model()
        user_data = request.data.get('user')
        volunteer_data = request.data.get('volunteer')

        if not user_data or not volunteer_data:
            return Response({"error": "Se requiere tanto la información del usuario como la del voluntario."}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = UserAuthSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Hashear la contraseña si está presente
        if 'password' in user_data:
            user_data['password'] = make_password(user_data['password'])

        user_data['date_joined'] = timezone.now()
        user_data['is_active'] = user_data.get('is_active', True)

        # Crear el usuario usando el modelo auth.User
        user = User.objects.create_user(**user_data)

        # Crear el token para el nuevo usuario
        token, created = Token.objects.get_or_create(user=user)

        volunteer_data['user'] = user.id
        volunteer_serializer = VolunteerSerializer(data=volunteer_data)

        if not volunteer_serializer.is_valid():
            return Response(volunteer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Crear el voluntario
        volunteer_serializer.save()

        return Response({
            'user': user_serializer.data,
            'volunteer': volunteer_serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['PUT'], url_path='update_volunteer')
    def update_volunteer(self, request, pk=None):
        # Obtener los datos enviados por el frontend
        volunteer_id = request.data.get('volunteer_id')
        user_id = request.data.get('user_id')
        user_data = request.data.get('user')
        volunteer_data = request.data.get('volunteer')

        # Validar que los IDs y los datos estén presentes
        if not volunteer_id or not user_id or not user_data or not volunteer_data:
            return Response({"error": "Se requiere el id del usuario, id del voluntario, y la información de ambos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el voluntario basado en el `volunteer_id`
            volunteer = Volunteers.objects.get(pk=volunteer_id)
        except Volunteers.DoesNotExist:
            return Response({"error": "El voluntario no existe."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Obtener el usuario basado en el `user_id`
            user = AuthUser.objects.get(id=user_id)
        except AuthUser.DoesNotExist:
            return Response({"error": "El usuario no existe."}, status=status.HTTP_404_NOT_FOUND)

        # Serializar los datos del usuario para actualizarlos
        user_serializer = UserAuthSerializer(user, data=user_data, partial=True)  # Partial permite actualizar campos individuales
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Si la contraseña está presente, hashearla
        if 'password' in user_data:
            user_data['password'] = make_password(user_data['password'])

        # Actualizar los datos del usuario
        user_serializer.save()

        # Serializar los datos del voluntario para actualizarlos
        volunteer_serializer = VolunteerSerializer(volunteer, data=volunteer_data, partial=True)
        if not volunteer_serializer.is_valid():
            return Response(volunteer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar los datos del voluntario
        volunteer_serializer.save()

        return Response({
            'user': user_serializer.data,
            'volunteer': volunteer_serializer.data
        }, status=status.HTTP_200_OK)
        
        
    @action(detail=False, methods=['DELETE'], url_path='delete_volunteer')
    def delete_volunteer(self, request):
        # Obtener los IDs enviados por el frontend
        User = get_user_model()
        volunteer_id = request.data.get('volunteer_id')
        user_id = request.data.get('user_id')

        # Validar que ambos IDs estén presentes
        if not volunteer_id or not user_id:
            return Response({"error": "Se requiere el ID del voluntario y el ID del usuario."}, status=status.HTTP_400_BAD_REQUEST)

        # Intentar eliminar el voluntario
        try:
            volunteer = Volunteers.objects.get(pk=volunteer_id)
        except Volunteers.DoesNotExist:
            return Response({"error": "El voluntario no existe."}, status=status.HTTP_404_NOT_FOUND)

        # Intentar obtener y eliminar el usuario
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "El usuario no existe."}, status=status.HTTP_404_NOT_FOUND)

        # Eliminar el token asociado al usuario
        Token.objects.filter(user=user).delete()

        # Eliminar el voluntario
        volunteer.delete()

        # Eliminar el usuario
        user.delete()

        return Response({"message": "Voluntario y usuario eliminados correctamente."}, status=status.HTTP_204_NO_CONTENT)