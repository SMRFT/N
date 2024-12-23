from django.db import models,transaction
import datetime

class Registration(models.Model):
    name_of_child = models.CharField(max_length=100)
    age = models.CharField(max_length=100)
    age_in_month = models.CharField(max_length=100)
    sex = models.CharField(max_length=10)
    date = models.DateField(auto_now_add=True)
    mother_name = models.CharField(max_length=100, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    guardian_name= models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
   
    REASON_CHOICES = [
        ('language_delay', 'Language Delay'),
        ('development_delay', 'Development Delay'),
        ('learning_disability', 'Learning Disability'),
        ('genetic_disorder', 'Genetic Disorder'),
        ('inattention', 'Inattention'),
        ('screening', 'Screening Of Development'),
        ('others', 'Others'),
    ]
    reason_for_visit = models.CharField(max_length=50, choices=REASON_CHOICES)
    duration_of_symptoms = models.TextField(blank=True, null=True)
    previous_treatment_done = models.TextField(blank=True, null=True)
    source_of_referral = models.JSONField(blank=True)  # Stores source of referral data as JSON
    registration_number = models.CharField(max_length=20, unique=True, blank=True)
    

    def save(self, *args, **kwargs):
        # Check if registration number is not already set
        if not self.registration_number:
            current_year = datetime.datetime.now().year

            # Use a database transaction to ensure atomicity
            with transaction.atomic():
                # Fetch the last registration object, lock the row, and ensure no other transaction can modify it
                last_reg = Registration.objects.select_for_update().order_by('id').last()

                if last_reg:
                    # Extract and increment the number from the last registration
                    reg_no = last_reg.registration_number.split('/')[1]
                    new_reg_no = int(reg_no) + 1
                else:
                    # If no registrations exist, start numbering from 1
                    new_reg_no = 1

                # Generate the new registration number in the format MDC/xxx/current_year
                self.registration_number = f'MDC/{new_reg_no:03}/{current_year}'

        # Call the parent class's save method to save the object in the database
        super(Registration, self).save(*args, **kwargs)


from django.db import models

class PatientAssessment(models.Model):
    registration_number = models.CharField(max_length=255)
    patient_name = models.CharField(max_length=255)
    age = models.CharField(max_length=100)
    age_in_month = models.CharField(max_length=100)
    sex = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    assessments = models.JSONField()  # Store selected assessments in a JSON field
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,blank=True)
    finalAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    paymentMethod = models.CharField(max_length=255,blank=True)

    def __str__(self):
        return f"Assessment for {self.patient_name}"

    

#login
class Login(models.Model):
    email = models.EmailField(unique=True) 
    password = models.CharField(max_length=255) 




from django.db import models

class EmployeeRegistration(models.Model):
    empid= models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed password in production
    confirmpassword = models.CharField(max_length=255) 
    def __str__(self):
        return self.name
 


from django.db import models

class DevelopmentalTask(models.Model):
    age = models.CharField(max_length=10)
    task = models.CharField(max_length=255)
    value = models.IntegerField()

    def __str__(self):
        return f"{self.age} - {self.task}"
    



from django.db import models
from django.contrib.postgres.fields import JSONField

class PediatricAssessment(models.Model):
    name = models.CharField(max_length=100)
    age =  models.CharField(max_length=100)
    dob = models.DateField()
    concerns = models.TextField()
    antenatalHistory = models.TextField()  # Match with frontend
    antenatalComplications = models.TextField()  # Match with frontend
    birthDetails = models.TextField()  # Match with frontend
    neonatalDetails = models.TextField()  # Match with frontend
    familyHistory = models.TextField()  # Match with frontend
    developmentalHistory = models.JSONField()  # Store the array from frontend
    regression = models.TextField()
    generalExamination = models.TextField()
    builtNourishment = models.TextField()
    previousMedications = models.TextField()
    neonatalReflexes = models.TextField()
    cnsExamination = models.TextField()
    hearingVision = models.TextField()
    toneReflex = models.TextField()
    bowelBladder = models.TextField()
    specificConcerns = models.TextField()
    threeItems = models.TextField()
    threePoints = models.TextField()
    threeActivity = models.TextField()
    interpretationRecommendation = models.TextField()

    def __str__(self):
        return self.name



class SkillTestResult(models.Model):
    registration_number = models.CharField(max_length=50)
    patient_name = models.CharField(max_length=100)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    data = models.JSONField()  # Store JSON data in this field (for relational DB)
    date = models.DateField()
    def __str__(self):
        return f"Skill Test for {self.patient_name} ({self.registration_number})"
    


from django.db import models


class TherapyBilling(models.Model):
    billing_no = models.CharField(max_length=10, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)  # Name of the child
    nameoftherapy = models.CharField(max_length=100, blank=True)
    therapy_charge = models.FloatField(blank=True, default=0.0)
    discount = models.FloatField(blank=True, default=0.0)
    adjusted_charge = models.FloatField(blank=True, default=0.0)
    amount_paid = models.FloatField(blank=True, default=0.0)
    remaining_amount = models.FloatField(blank=True, default=0.0)
    payment_type = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    consultant_doctor = models.CharField(max_length=100, blank=True)  # Name of the consultant doctor
    age = models.CharField(max_length=100)
    sex = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    pending_amt_paid_date = models.DateField(blank=True, null=True)  # New field to store the date
    date = models.DateField(auto_now_add=True)  # Date of billing
    def save(self, *args, **kwargs):
        # Automatically generate billing number if not provided
        if not self.billing_no:
            last_billing = TherapyBilling.objects.all().order_by('billing_no').last()
            if last_billing and last_billing.billing_no.isdigit():
                # Increment the last billing number by 1 and ensure it's zero-padded to 3 digits
                last_billing_no = int(last_billing.billing_no)
                self.billing_no = str(last_billing_no + 1).zfill(3)  # Increment by 1 and pad with zeros to 3 digits
            else:
                # Start with "001" if no previous records exist
                self.billing_no = "001"
        
        # Automatically calculate adjusted charge and remaining amount
        if self.therapy_charge and self.discount:
            self.adjusted_charge = float(self.therapy_charge) - float(self.discount)
            self.remaining_amount = max(self.adjusted_charge - float(self.amount_paid), 0.00)
    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Billing No: {self.billing_no} - {self.name}"
    


from django.db import models

class MCHATResponse(models.Model):
    registration_number= models.CharField(max_length=255)
    patient_name = models.CharField(max_length=255)
    age = models.CharField(max_length=255)
    sex = models.CharField(max_length=255)
    question = models.JSONField()  # Store responses as JSON
    score = models.IntegerField()
    riskLevel = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.patient_name} - {self.age} - {self.sex}"


class ReferralDoctor(models.Model):
    doctor_name = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.doctor_name


class DevelopmentalScreeningTask(models.Model):
    TASK_CHOICES = [
        ('task1', 'Task 1'),
        ('task2', 'Task 2'),
        ('task3', 'Task 3'),
    ]
    
    patient_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=20)
    age = models.PositiveIntegerField()  # Age in years
    age_in_month = models.PositiveIntegerField()  # Age in months
    tasks = models.JSONField()  # Store tasks as JSON
    total_value = models.PositiveIntegerField(default=0)
    dq_value = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Developmental Task for {self.patient_name}"
    
   

