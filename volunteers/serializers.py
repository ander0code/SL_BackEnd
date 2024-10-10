from rest_framework import serializers
from api.models import Volunteers , Volunteers , AuthUser

class GetVolunteersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Volunteers
        fields = '__all__'
          
class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

class VolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volunteers
        fields = ['name', 'last_name', 'org_email', 'photo', 'phone', 'nationality', 'document_type', 'document_id', 'birthdate', 'gender', 'status', 'user']

        