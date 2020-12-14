from django import forms
from .models import UserProfile, Leaves, Personal_info, Outing
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput
from datetime import datetime
import re


class newLeave(forms.ModelForm):
    class Meta:
        model = Leaves
        fields = ('reason', 'description', 'proof',
                  'out_date', 'in_date', 'is_emergency')
        widgets = {
            'out_date': DatePickerInput,
            'in_date': DatePickerInput,
        }
        labels = {
            'proof': "Proof ( Allowed file types => 'pdf', 'doc', 'docx', 'jpg', 'png', 'xlsx', 'xls' )",
            'is_emergency': 'a          Emergency(Only check this if it is really an emergency)'
        }

    def clean(self):
        cd = super().clean()

        if cd.get('out_date') < datetime.now().date():
            self.add_error('out_date', 'Out date cannot be a past date')

        if cd.get('out_date') > cd.get('in_date'):
            self.add_error('out_date',
                           'Out date should be lower than in date')
        if cd.get('proof'):
            if cd.get('proof').size > settings.MAX_UPLOAD_SIZE:
                self.add_error('proof', ('Please keep filesize under %s. Current filesize %s') % (
                    filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(cd.get('proof').size)))

        if cd.get('out_date') == cd.get('in_date'):
            self.add_error('out_date', 'Out date and In date can\'t be same')


class student(UserCreationForm):
    uid = forms.CharField(max_length=7, label='Id', widget=forms.TextInput(
        attrs={}))
    branch = forms.ChoiceField(
        choices=UserProfile.branches, label='Branch')
    year = forms.ChoiceField(choices=UserProfile.years, label='Year',
                             widget=forms.Select(attrs={'class': 'form-control'}))
    hostel = forms.ChoiceField(choices=UserProfile.hostels, label='Hostel')
    room_no = forms.CharField(
        max_length=7, label='Room Number (Format ex: TF-21A)')

    class Meta:
        model = User
        fields = ['uid', 'username', 'password1', 'password2']

    def clean(self):
        cd = super().clean()

        if UserProfile.objects.filter(id=cd.get('uid').capitalize()).first() is not None:
            self.add_error('uid',
                           'Account with this Id no. already exists\nIf this Id no. belongs to you, report to the olms admin')

        if not re.match(r'[s,S][0-9]{6}', cd.get('uid')):
            self.add_error('uid', 'Invalid id no')

        if (cd.get('branch') == 'puc' and (cd.get('year') != ('p1' or 'p2'))) or (cd.get('branch') != 'puc' and (cd.get('year') == ('p1' or 'p2'))):
            self.add_error('branch', 'Invalid year and branch combination ')

        if not re.match(r'[GFST]{1}F[-][0-9]{2,3}[AB]', cd.get('room_no')):
            self.add_error('room_no', 'Invalid room number')


class pform(forms.ModelForm):

    class Meta:
        model = Personal_info
        fields = ['aadhar_no', 'full_name', 'photo', 'phone_no',
                  'Parent_name', 'Parent_phn_no', 'address', 'city', 'district']
        widgets = {
            'address': forms.Textarea()
        }

        labels = {
            'parent_phn_no': 'Parent phone number',
        }

    def clean(self):
        cd = super().clean()
        if not re.match(r'^\d{12}$', str(cd.get('aadhar_no'))):
            self.add_error('aadhar_no', 'Invalid aadhar number')

        if not re.match(r'^\d{10}$', str(cd.get('phone_no'))):
            self.add_error('phone_no', 'Invalid phone number')

        if not re.match(r'^\d{10}$', str(cd.get('Parent_phn_no'))):
            self.add_error('Parent_phn_no', 'Invalid parent phone number')

        if not re.match(r'^[a-zA-Z, ]+$', str(cd.get('parent_name'))):
            self.add_error(
                'Parent_name', 'Unsupported characters in parent name')


class OutingForm(forms.ModelForm):
    class Meta:
        model = Outing
        fields = ['reason', 'out_time', 'in_time']
        widgets = {'out_time': TimePickerInput(
        ), 'in_time': TimePickerInput(), }

    def clean(self):
        clean_data = super().clean()
        if clean_data.get('out_time') > clean_data.get('in_time'):
            self.add_error(
                'out_time', 'Out Time must be lower than In Time.')


class PublicHoliday(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[('all', 'All'), ('male', 'Only Boys'), ('female', 'Only Girls')], label='Grant to')

    class Meta:
        model = Leaves
        fields = ['reason', 'description', 'out_date', 'in_date', 'gender']
        widgets = {
            'out_date': DatePickerInput,
            'in_date': DatePickerInput,
        }
        labels = {
            'out_date': 'Start date',
            'in_date': 'End date'
        }

    def clean(self):
        cd = super().clean()

        if cd.get('out_date') < datetime.now().date():
            self.add_error('out_date', 'Out date cannot be a past date')

        if cd.get('out_date') > cd.get('in_date'):
            self.add_error('out_date',
                           'Out date should be lower than in date')

        if cd.get('out_date') == cd.get('in_date'):
            self.add_error('out_time', 'Out time and In time can\'t be same')
            raise forms.ValidationError('Out time and In time can\'t be same')


class SetNewPassword(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        if cd.get('password') != cd.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords didn\'t match')


def validate_password_form(password):
    return validate_password(password)
