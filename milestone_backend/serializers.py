from rest_framework import serializers
from .models import Registration,PatientAssessment,Login
from bson import ObjectId

class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        return ObjectId(data)
    
class RegistrationSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    class Meta:
        model = Registration
        fields = '__all__'

from rest_framework import serializers
from .models import EmployeeRegistration

class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRegistration
        fields = '__all__'


class PatientAssessmentSerializer(serializers.ModelSerializer):
 # Nested serializer for assessments
    id = ObjectIdField(read_only=True)
    class Meta:
        model = PatientAssessment
        fields = '__all__'



class LoginSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    class Meta:
        model = Login
        fields = '__all__'



from rest_framework import serializers
from .models import DevelopmentalTask

class DevelopmentalTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevelopmentalTask
        fields = ['age', 'task', 'value']




from rest_framework import serializers
from .models import PediatricAssessment

class PediatricAssessmentSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    class Meta:
       
        model = PediatricAssessment
        fields = '__all__'


from rest_framework import serializers
from .models import TherapyBilling

class TherapyBillingSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    class Meta:
        model = TherapyBilling
        fields = '__all__'

from rest_framework import serializers
from .models import MCHATResponse

class MCHATResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCHATResponse
        fields = ['registration_number','patient_name', 'age', 'sex', 'question', 'score','riskLevel']

from rest_framework import serializers
from .models import ReferralDoctor

class ReferralDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralDoctor
        fields = "__all__"


from django import forms
from .models import DevelopmentalScreeningTask

class DevelopmentalTaskForm(forms.ModelForm):
    class Meta:
        model = DevelopmentalScreeningTask
        fields = ['patient_name', 'age', 'gender', 'age_in_month', 'tasks', 'total_value', 'dq_value']


