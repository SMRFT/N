from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Registration
from .serializers import RegistrationSerializer,PatientAssessmentSerializer
import datetime
from django.db.models import Max

@api_view(['POST'])
def create_registration(request):
    serializer = RegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()  # Automatically calls the save() method in your model to generate the registration number
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Registration
from .serializers import RegistrationSerializer
from django.db.models import Count
from datetime import datetime, time

@api_view(['GET'])
def get_patients_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str or not end_date_str:
        return Response({"error": "Start date and end date are required."}, status=400)

    # Parse dates
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Ensure time is set to the start and end of the day
    start_date = datetime.combine(start_date, time.min)  # 00:00:00
    end_date = datetime.combine(end_date, time.max)  # 23:59:59

    # Filter patients by date range
    patients = Registration.objects.filter(date__range=[start_date, end_date])

    # Calculate total patients in the selected date range
    total_patients = patients.count()

    # Calculate daily counts
    daily_counts = (
        patients.values('date')
        .annotate(total_cases=Count('id'))
        .order_by('date')
    )

    # Calculate monthly counts
    monthly_counts = (
        patients.values('date__month')
        .annotate(total_cases=Count('id'))
        .order_by('date__month')
    )

    # Serialize patient data
    serializer = RegistrationSerializer(patients, many=True)

    return Response({
        'total_patients': total_patients,  # Added total patients count
        'patients': serializer.data,
        'daily_counts': daily_counts,
        'monthly_counts': monthly_counts
    })

from .serializers import RegistrationSerializer
from .models import Registration, PatientAssessment
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
@api_view(['GET'])
def get_all_patients(request):
    # Get today's date
    today = datetime.utcnow().date()
    
    # Get all patients from the Registration model
    patients = Registration.objects.all()
    
    # Get all patient assessments
    patient_assessments = PatientAssessment.objects.all()
    
    # Filter assessments for today in Python
    assessed_patients_today = {
        assessment.registration_number
        for assessment in patient_assessments
        if assessment.created_at.date() == today
    }
    
           # Create a list of patient data without the 'disabled' field
    patient_data = []
    for patient in patients:
        # Serialize patient data using RegistrationSerializer
        patient_info = RegistrationSerializer(patient).data
                       
        # Add patient data to the list without the 'disabled' field
        patient_data.append(patient_info)
    
    # Return the patient data in the response
    return Response(patient_data)

@api_view(['POST'])
def save_assessments(request):
    if request.method == 'POST':
        serializer = PatientAssessmentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()  # Save the new patient assessment to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PatientAssessment
from .serializers import PatientAssessmentSerializer

@api_view(['GET'])
def get_assessments(request):
    # Retrieve all patient assessments
    assessments = PatientAssessment.objects.all()
    
    # Serialize all the assessments
    serializer = PatientAssessmentSerializer(assessments, many=True)
    
    # Return the serialized data as a response
    return Response(serializer.data, status=status.HTTP_200_OK)



# To get the next registration number
@api_view(['GET'])
def get_next_registration_number(request):
    last_reg = Registration.objects.all().order_by('id').last()
    if last_reg:
        last_reg_no = last_reg.registration_number.split('/')[1]
        new_reg_no = int(last_reg_no) + 1
    else:
        new_reg_no = 1  # Start with 1 if no registrations exist
    current_year = datetime.datetime.now().year
    next_registration_number = f'MDC/{new_reg_no:03}/{current_year}'
    
    return Response({'next_registration_number': next_registration_number})@api_view(['GET'])


@api_view(['GET'])
def get_latest_registration_number(request):
    # Fetch the latest registration number from the database
    latest_registration = Registration.objects.aggregate(Max('registration_number'))

    # Get the current year
    current_year = datetime.now().year

    # If there's a registration number, increment it, otherwise start with MDC/001/current_year
    if latest_registration['registration_number__max']:
        # Extract the numeric part and increment it
        reg_no = latest_registration['registration_number__max'].split('/')[1]
        current_id = int(reg_no)
        new_registration_number = f"MDC/{str(current_id + 1).zfill(3)}/{current_year}"
    else:
        # Start the numbering with MDC/001/current_year if no previous registration exists
        new_registration_number = f"MDC/001/{current_year}"

    # Return the registration number in JSON format using DRF's Response
    return Response({"registration_number": new_registration_number}, status=status.HTTP_200_OK)


from django.http import JsonResponse
from pymongo import MongoClient



def get_all_assessments(request):
    client = MongoClient('mongodb://3.109.210.34:27017/')
    db = client['Milestone']  # Replace with your MongoDB database name
    try:
        # Fetch all documents from the milestone_backend_Billing collection
        billing_data = list(db['milestone_backend_Billing'].find({}, {'_id': 0}))

        # Initialize the response data with empty lists
        response_data = {
            "psychological_assessments": [],
            "speech_assessments": [],
            "ot_assessments": [],
            "physio_therapy_assessments": [],
            "drs_consulting": []
        }

        # Loop through each document and collect assessments
        for document in billing_data:
            response_data["psychological_assessments"].extend(document.get("psychological_assessments", []))
            response_data["speech_assessments"].extend(document.get("speech_assessments", []))
            response_data["ot_assessments"].extend(document.get("ot_assessments", []))
            response_data["physio_therapy_assessments"].extend(document.get("physio_therapy_assessments", []))
            response_data["drs_consulting"].extend(document.get("drs_consulting", []))

        # Return the combined data as JSON
        return JsonResponse(response_data, safe=False, json_dumps_params={'indent': 2})

    except Exception as e:      
        return JsonResponse({"error": str(e)}, status=500)


#Login check through email and password
from django.contrib.auth.hashers import check_password
from .models import EmployeeRegistration
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@api_view(['POST'])
def LoginView(request):
    email = request.data.get('email')
    password = request.data.get('password')
    try:
        # Find the user by email
        user = EmployeeRegistration.objects.get(email=email)
        # Check if the password matches
        if check_password(password, user.password):
            # If password matches, login is successful
            return JsonResponse({'message': 'Login successful!', 'name': user.name}, status=status.HTTP_200_OK)
        else:
            # If password doesn't match
            return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except EmployeeRegistration.DoesNotExist:
        # If user with given email does not exist
        return JsonResponse({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from pymongo import MongoClient
from urllib.parse import quote_plus
from django.views.decorators.http import require_GET
    
@require_GET
def DevelopmentalTask(request):
    # URL-encode the password
    password = quote_plus('Smrft@2024')
    # Use f-string to inject the encoded password into the connection string
    client = MongoClient(f'mongodb://3.109.210.34:27017/')
    db = client['Milestone']  # Access the 'Lab' database
    collection = db['milestone_developmental_screening']  # Access the 'Testdetails' collection
    # Fetch all test details from the collection
    test_details = list(collection.find({}, {"_id": 0}))  # Exclude '_id' field if not needed
    return JsonResponse(test_details, safe=False)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PediatricAssessment
from .serializers import PediatricAssessmentSerializer

@api_view(['GET', 'POST'])
def PediatricAssessmentView(request):
    if request.method == 'POST':
        serializer = PediatricAssessmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PediatricAssessment
from .serializers import PediatricAssessmentSerializer

# GET method to retrieve all pediatric assessments
@api_view(['GET'])
def pediatric_assessment_list(request):
    if request.method == 'GET':
        assessments = PediatricAssessment.objects.all()  # Fetch all records
        serializer = PediatricAssessmentSerializer(assessments, many=True)  # Serialize list of assessments
        return Response(serializer.data)




import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import SkillTestResult
logger = logging.getLogger(__name__)
@csrf_exempt
@require_http_methods(["POST", "GET"])
def save_patient_skilltest(request):
    if request.method == "POST":
        # POST code as provided
        try:
            data = json.loads(request.body)
            logger.debug(f"Received data: {data}")
            registration_number = data.get('registration_number')
            patient_name = data.get('patient_name')
            age = data.get('age')
            sex = data.get('sex')
            status = data.get('data', {}).get('status')
            category = data.get('data', {}).get('category')
            selected_questions = data.get('data', {}).get('selected_questions', [])
            comment = data.get('data', {}).get('comment', '')
            date = data.get('date')
            data_dict = {
                "status": status,
                "category": category,
                "selected_questions": selected_questions,
                "comment": comment,
            }
            skill_test_result = SkillTestResult(
                registration_number=registration_number,
                patient_name=patient_name,
                age=age,
                sex=sex,
                date=date,
                data=data_dict
            )
            skill_test_result.save()
            return JsonResponse({'message': 'Data saved successfully!'}, status=201)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    elif request.method == "GET":
        try:
            # Retrieve patient_id and date from the query parameters
            patient_id = request.GET.get('patient_id')
            date = request.GET.get('date')
            # Build the filter query based on the parameters
            filters = {}
            if patient_id:
                filters['registration_number'] = patient_id  # Assuming patient ID corresponds to registration_number
            if date:
                filters['date'] = date
            # Retrieve reports with the applied filters
            reports = SkillTestResult.objects.filter(**filters).values(
                'registration_number', 'patient_name', 'age', 'sex', 'date', 'data'
            )
            report_list = list(reports)  # Convert QuerySet to a list of dictionaries
            return JsonResponse(report_list, safe=False, status=200)
        except Exception as e:
            logger.error(f"Error retrieving reports: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        



from django.shortcuts import render
from django.http import JsonResponse
from .models import Registration
def get_patient_by_registration(request, prefix, id, year):
    try:
        registration_number = f"{prefix}/{id}/{year}"
        patient = Registration.objects.get(registration_number=registration_number)
        return JsonResponse({
            "name_of_child": patient.name_of_child,
            "age": patient.age,
            "sex": patient.sex,
            # other fields...
        })
    except Registration.DoesNotExist:
        return JsonResponse({"error": "Patient not found"}, status=404)
    



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TherapyBilling
from .serializers import TherapyBillingSerializer

@csrf_exempt
@api_view(['POST'])
def therapy_billing(request):
    serializer = TherapyBillingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Automatically calls the save() method in your model to generate the registration number
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TherapyBilling
from .serializers import TherapyBillingSerializer

@api_view(['GET'])
def pendingPayment(request):
    # Get all the data for the specified patient
    data = TherapyBilling.objects.all()
    serializer = TherapyBillingSerializer(data, many=True)
    return Response(serializer.data)

from .models import TherapyBilling

from django.http import JsonResponse
from .models import TherapyBilling

def get_latest_billing_no(request):
    latest_billing = TherapyBilling.objects.all().order_by('billing_no').last()
    
    if latest_billing:
        # Increment the latest billing number by 1
        latest_billing_no = int(latest_billing.billing_no)
        new_billing_no = str(latest_billing_no + 1).zfill(3)  # Increment and zero-fill to 3 digits
        return JsonResponse({'billing_no': new_billing_no})
    else:
        # If no records exist, start with "001"
        return JsonResponse({'billing_no': '001'})


from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import PatientAssessment
from .serializers import PatientAssessmentSerializer

def therapybillinggetall(request):
    try:
        # Get the current date range
        today = datetime.utcnow().date()  # UTC date
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today + timedelta(days=1), datetime.min.time())

        # Fetch records created today using Django ORM
        assessments = PatientAssessment.objects.filter(
            created_at__gte=start_of_day,
            created_at__lt=end_of_day
        )

        # Serialize the queryset
        serializer = PatientAssessmentSerializer(assessments, many=True)

        # Get the total count of today's patients
        total_count = assessments.count()

        return JsonResponse({
            'status': 'success',
            'data': serializer.data,
            'total_count': total_count
        }, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})





from django.http import JsonResponse
from rest_framework.decorators import api_view
from pymongo import MongoClient
from urllib.parse import quote_plus
import json

@csrf_exempt
@api_view(['PATCH'])
def update_payment(request):
    # MongoDB connection setup
    password = quote_plus('Smrft@2024')
    client = MongoClient(f'mongodb://3.109.210.34:27017/')
    db = client['Milestone']
    collection = db['milestone_backend_therapybilling']

    if request.method == 'PATCH':
        data = json.loads(request.body)
        billing_no = data.get('billing_no')
        pending_amt_paid_date = data.get('pending_amt_paid_date')  # Get the date from the frontend

        if not billing_no:
            return JsonResponse({'error': 'Billing number is required.'}, status=400)

        # Fetch the document by billing_no
        patient = collection.find_one({'billing_no': billing_no})
        if not patient:
            return JsonResponse({'error': 'Patient not found.'}, status=404)

        remaining_amount = patient.get('remaining_amount', 0)
        amount_paid = patient.get('amount_paid', 0)

        # Update fields
        updated_data = {
            'remaining_amount': 0,
            'amount_paid': amount_paid + remaining_amount,
        }

        # Add the pending_amt_paid_date if it's provided
        if pending_amt_paid_date:
            updated_data['pending_amt_paid_date'] = pending_amt_paid_date

        # Update the record in the database
        collection.update_one({'billing_no': billing_no}, {'$set': updated_data})

        return JsonResponse({'message': 'Payment updated successfully.'}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmployeeRegistrationSerializer
from django.contrib.auth.hashers import make_password

@api_view(['POST'])
def employeeregistration(request):
    serializer = EmployeeRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        # Hash the password before saving
        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        serializer.save()
        return Response({'message': 'Registration successful!'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





from django.http import JsonResponse
from django.shortcuts import render
from .models import PatientAssessment
from .serializers import PatientAssessmentSerializer
from datetime import datetime, timedelta
import pytz

# Function to convert string to UTC datetime object
def str_to_date_utc(date_str, is_end_of_day=False):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        if is_end_of_day:
            # Set to end of the day (23:59:59)
            date_obj += timedelta(days=1) - timedelta(seconds=1)
        # Convert to UTC timezone
        return pytz.utc.localize(date_obj)
    except ValueError:
        return None

# Fetch patient assessments using Django ORM with date filtering
def get_patient_assessments(request):
    from_date_str = request.GET.get('from_date')  # Get the 'from_date' query parameter
    to_date_str = request.GET.get('to_date')  # Get the 'to_date' query parameter

    # Convert to UTC datetime objects
    from_date = str_to_date_utc(from_date_str) if from_date_str else None
    to_date = str_to_date_utc(to_date_str, is_end_of_day=True) if to_date_str else None

    try:
        # Prepare the query filter
        query_filter = {}

        # Apply date filtering if both from_date and to_date are provided
        if from_date and to_date:
            query_filter["created_at__range"] = (from_date, to_date)
        elif from_date:
            query_filter["created_at__gte"] = from_date
        elif to_date:
            query_filter["created_at__lte"] = to_date

        # Fetch records using Django ORM
        assessments = PatientAssessment.objects.filter(**query_filter)

        # Serialize the data
        serializer = PatientAssessmentSerializer(assessments, many=True)

        # Get the total count of patients (number of records)
        total_count = assessments.count()

        return JsonResponse({
            'status': 'success',
            'data': serializer.data,
            'total_count': total_count
        }, safe=False)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime
from .models import Registration
from .serializers import RegistrationSerializer

@api_view(['GET'])
def get_referrals(request):
    try:
        # Get the date range from query parameters
        from_date_str = request.GET.get('fromDate', '')
        to_date_str = request.GET.get('toDate', '')
        
        # Convert strings to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None
        
        # Filter registrations based on the date range
        queryset = Registration.objects.all()

        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        # Serialize the data
        serializer = RegistrationSerializer(queryset, many=True)

        return Response(serializer.data, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from .models import TherapyBilling
from .serializers import TherapyBillingSerializer

@api_view(['GET'])
def get_therapy_reports(request):
    """
    Fetch all TherapyBilling data from the database and return it as JSON,
    filtered by date range if provided, using the TherapyBillingSerializer.
    """
    # Get the from_date and to_date from query params
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    # Convert date strings to datetime objects
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

    # Filter data using Django ORM
    if from_date and to_date:
        therapy_billing_data = TherapyBilling.objects.filter(date__gte=from_date, date__lte=to_date)
    else:
        therapy_billing_data = TherapyBilling.objects.all()

    # Serialize the data
    serializer = TherapyBillingSerializer(therapy_billing_data, many=True)

    # Return the serialized data as a JSON response
    return Response(serializer.data)

#storing m-chart 

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MCHATResponse
from .serializers import MCHATResponseSerializer

@api_view(['POST'])
def saveMCHATResponses(request):
    """
    Save M-CHAT responses for a patient, including the calculated risk level and total score.
    """
    data = request.data

    # Extract patient details
    registration_number= data.get('patient', {}).get('registration_number', 'Unknown')
    patient_name = data.get('patient', {}).get('name', 'Unknown')
    age = data.get('patient', {}).get('age', 'Unknown')
    sex = data.get('patient', {}).get('sex', 'Unknown')

    # Extract responses
    responses = data.get('responses', [])
    
    if not responses:
        return Response({"error": "No responses provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Create the question list with all responses
    question_list = [
        {
            "question_no": response_data["question_no"],
            "question_text": response_data["question_text"],
            "answer": response_data["answer"],
            "score": response_data.get("score", 0)
        }
        for response_data in responses
    ]

    # Extract total score and risk level from the payload
    total_score = data.get('totalScore', 0)
    risk_level = data.get('riskLevel', 'Unknown')

    # Prepare the complete data object to save
    data_to_save = {
        'registration_number': registration_number,
        'patient_name': patient_name,
        'age': age,
        'sex': sex,
        'question': question_list,  # List of all questions and answers
        'score': total_score,  # Store the provided total score
        'riskLevel': risk_level  # Store the provided risk level
    }

    # Serialize and save
    serializer = MCHATResponseSerializer(data=data_to_save)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "All responses saved successfully"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Failed to save responses", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MCHATResponse
from .serializers import MCHATResponseSerializer

@api_view(['GET'])
def getMCHATResponse(request, registration_number):
    """
    Fetch M-CHAT-R responses for a given patient using their registration number.
    """
    try:
        response = MCHATResponse.objects.get(registration_number=registration_number)
        serializer = MCHATResponseSerializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except MCHATResponse.DoesNotExist:
        return Response({"error": "No data found for this registration number"}, status=status.HTTP_404_NOT_FOUND)
    

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ReferralDoctor
from .serializers import ReferralDoctorSerializer

@api_view(['POST'])
def register_referral_doctor(request):
    if request.method == 'POST':
        serializer = ReferralDoctorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Referral Doctor registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_referral_doctors(request):
    if request.method == 'GET':
        doctors = ReferralDoctor.objects.all()
        serializer = ReferralDoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

from django.shortcuts import render
from django.http import JsonResponse
from .models import DevelopmentalScreeningTask
from django import forms
from django.views.decorators.csrf import csrf_exempt

# Define a form class directly in views.py (since you don't have a forms.py)
class DevelopmentalScreeningTaskForm(forms.Form):
    patient_name = forms.CharField(max_length=255)
    gender = forms.CharField(max_length=20)
    age = forms.IntegerField()
    age_in_month = forms.IntegerField()
    tasks = forms.JSONField()  # Expecting a JSON object for tasks
    total_value = forms.IntegerField(initial=0)
    dq_value = forms.DecimalField(max_digits=5, decimal_places=2, initial=0.0)

# View to create a new Developmental Screening Task
@csrf_exempt
def create_developmental_screening_task(request):
    if request.method == 'POST':
        form = DevelopmentalScreeningTaskForm(request.POST)
        if form.is_valid():
            patient_name = form.cleaned_data['patient_name']
            gender = form.cleaned_data['gender']
            age = form.cleaned_data['age']
            age_in_month = form.cleaned_data['age_in_month']
            tasks = form.cleaned_data['tasks']
            total_value = form.cleaned_data['total_value']
            dq_value = form.cleaned_data['dq_value']

            # Create and save the DevelopmentalScreeningTask instance
            developmental_task = DevelopmentalScreeningTask(
                patient_name=patient_name,
                gender=gender,
                age=age,
                age_in_month=age_in_month,
                tasks=tasks,
                total_value=total_value,
                dq_value=dq_value,
            )
            developmental_task.save()

            # Return a success response
            return JsonResponse({'message': 'Data saved successfully'}, status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = DevelopmentalScreeningTaskForm()  # Render the empty form for GET requests

    return render(request, 'your_template.html', {'form': form})

# View to list all DevelopmentalScreeningTask records
def list_developmental_screening_tasks(request):
    tasks = DevelopmentalScreeningTask.objects.all()
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'patient_name': task.patient_name,
            'gender': task.gender,
            'age': task.age,
            'age_in_month': task.age_in_month,
            'tasks': task.tasks,
            'total_value': task.total_value,
            'dq_value': task.dq_value,
        })
    return JsonResponse({'tasks': tasks_data}, safe=False)


from django.db.models import Sum  # Add this import
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from bson.decimal128 import Decimal128
from django.http import JsonResponse
from .models import TherapyBilling, PatientAssessment
import logging
from datetime import timedelta


def parse_iso_date(date_string):
    try:
        # Handle ISO 8601 format
        return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    except ValueError:
        # Fallback for other formats (if needed)
        return None

def therapy_total(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:
        from_date = parse_iso_date(from_date)
        to_date = parse_iso_date(to_date)
        if from_date and to_date:
            total = TherapyBilling.objects.filter(
                date__range=[from_date, to_date]
            ).aggregate(grand_total=Sum('amount_paid'))['grand_total'] or 0.0
            return JsonResponse({'grand_total': total})

    return JsonResponse({'error': 'Invalid date range'}, status=400)

# Create a logger instance
logger = logging.getLogger(__name__)

def op_assessment_total(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:
        from_date = parse_iso_date(from_date)
        to_date = parse_iso_date(to_date)
        if from_date and to_date:
            # Make `from_date` and `to_date` aware
            from_date = timezone.make_aware(from_date, timezone.utc)
            to_date = timezone.make_aware(to_date, timezone.utc)

            # Set the time to the last moment of the day for `to_date`
            to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Fetching assessments between the provided date range
            assessments = PatientAssessment.objects.filter(
                created_at__range=[from_date, to_date]
            ).values_list('finalAmount', flat=True)

            # Calculate the total, ensuring proper decimal handling
            total = sum(
                Decimal(str(amount)) if isinstance(amount, Decimal128) else amount
                for amount in assessments
                if amount is not None
            )

            return JsonResponse({'grand_total': float(total)})

    return JsonResponse({'error': 'Invalid date range'}, status=400)






