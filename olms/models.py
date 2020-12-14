import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator, RegexValidator


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, unique=True, related_name='profile', on_delete=models.CASCADE)
    id = models.CharField(max_length=7, primary_key=True)
    usertypes = [('student', 'Student'), ('admin', 'Admin'),
                 ('security', 'Security')]
    usertype = models.CharField(
        max_length=8, choices=usertypes, default='student')
    branches = [('puc', 'PUC'), ('cse', 'CSE'), ('mech', 'MECH'),
                ('chem', 'CHEM'), ('ece', 'ECE'), ('mme', 'MME'), ('civil', 'CIVIL')]
    branch = models.CharField(max_length=5, choices=branches, default='puc')
    years = [('p1', 'P1'), ('p2', 'P2'), ('e1', 'E1'),
             ('e2', 'E2'), ('e3', 'E3'), ('e4', 'E4')]
    year = models.CharField(max_length=2, choices=years, default='p1')
    gender = models.CharField(choices=[(
        'male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=6, default='male')
    hostels = [('i1', 'I1'), ('i2', 'I2'), ('i3', 'I3'),
               ('k1', 'K1'), ('k2', 'K2'), ('k3', 'K3'), ('k4', 'K4')]
    hostel = models.CharField(max_length=2, choices=hostels, default='i2')
    room_no = models.CharField(
        max_length=7, blank=True, null=True, default=None)
    in_campus = models.BooleanField(default=True)


class LeaveCount(models.Model):
    count = models.IntegerField(default=0)
    user = models.OneToOneField(
        UserProfile, on_delete=models.SET_NULL, null=True)


class Leaves(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, related_name='leaveuser', blank=True, null=True)
    reason = models.CharField(max_length=50, default=None)
    description = models.CharField(max_length=999, default=None)
    proof = models.FileField(default=None, blank=True,
                             null=True, upload_to='proofs/', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png', 'xlsx', 'xls', 'jpeg', 'img'])])
    out_date = models.DateField(default=None, blank=True, null=True)
    in_date = models.DateField(default=None,  blank=True, null=True)
    actual_out_date = models.DateTimeField(default=None, blank=True, null=True)
    actual_in_date = models.DateTimeField(default=None, blank=True, null=True)
    statuses = [('pending', 'pending'), ('granted',
                                         'granted'), ('rejected', 'rejected'), ('on_leave', 'On Leave'), ('delayed', 'Delayed'), ('completed', 'Completed'), ('expired', 'Expired')]
    status = models.CharField(
        max_length=9, choices=statuses, default='pending')
    is_emergency = models.BooleanField(default=False)
    remark = models.CharField(max_length=100, default='No remark')


def rename_and_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.userprofile.id, ext)
    return os.path.join('photos/', filename)


class Personal_info(models.Model):
    full_name = models.CharField(
        max_length=50)
    photo = models.ImageField(default=None, blank=True, null=True, upload_to=rename_and_upload, validators=[
                              FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'img'])])
    aadhar_regex = RegexValidator(
        regex=r'^\d{12}$', message='Aadhar number should only contain numbers and should have exactly 12 digits')
    aadhar_no = models.CharField(primary_key=True, validators=[
                                 aadhar_regex], max_length=12)
    userprofile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name='personal_info')
    phone_regex = RegexValidator(
        regex=r'^\d{10}$', message='Phone number should only contain numbers and should have exactly 10 digits')
    phone_no = models.CharField(validators=[phone_regex], max_length=10)
    Parent_name = models.CharField(max_length=50)
    Parent_phn_no = models.CharField(validators=[phone_regex], max_length=10)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=20)
    district = models.CharField(max_length=30)


class Outing(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, related_name='outinguser', blank=True, null=True)
    reason = models.CharField(max_length=50, default=None)
    date = models.DateField(default=None, blank=True, null=True)
    out_time = models.TimeField(default=None, blank=True, null=True)
    in_time = models.TimeField(default=None, blank=True, null=True)
    actual_in_time = models.TimeField(default=None, blank=True, null=True)
    actual_out_time = models.TimeField(default=None, blank=True, null=True)
    statuses = [('pending', 'pending'), ('granted',
                                         'granted'), ('rejected', 'rejected'), ('on_outing', 'On Outing'),
                ('completed', 'Completed'), ('expired', 'Expired')]
    status = models.CharField(
        max_length=9, choices=statuses, default='pending')


class Counts(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, related_name='user_count', blank=True, null=True)
    leaves_this_month = models.IntegerField(default=0)
    total_leaves = models.IntegerField(default=0)
    outings_this_month = models.IntegerField(default=0)
    total_outings = models.IntegerField(default=0)
    month = models.IntegerField(default=datetime.datetime.now().month)
