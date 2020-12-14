from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from . import forms
from .models import UserProfile, Leaves, Personal_info, Outing, Counts
from django.utils.timezone import localtime, now
import traceback
from datetime import timedelta, datetime
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import time
import random
import threading

date = None

max_leave = 4
max_outing = 4
dean_mail = 'S160142@rguktkslm.ac.in'

print('='*30, date)


def expobs(leave):
    print('expiring leave', leave)
    leave.status = 'expired'
    leave.save()


def delayobs(leave):
    print('delaying leave', leave)
    leave.status = 'delayed'
    leave.save()


def resetCount():
    counts = Counts.objects.all()
    month = datetime.now().month
    if counts[0].month == counts.reverse()[0].month == month:
        return
    print('resetting counts')
    for c in counts:
        if c.month != month:
            c.leaves_this_month = 0
            c.outings_this_month = 0
            c.save()


def expireObjects():
    print('in expireobjects ')
    global date
    print(date)
    if date:
        if date == datetime.now().date():
            print('Done')
    else:
        print('epiringObjects')
        try:
            print('I am working')
            date = datetime.now().date()
            leaves = Leaves.objects.filter(
                in_date__lt=date, status__in=['pending', 'granted'])
            [expobs(o) for o in Outing.objects.filter(
                date__lt=date, status__in=['pending', 'granted'])]
            print(leaves)
            [expobs(l) for l in leaves]
            [delayobs(l) for l in Leaves.objects.filter(
                in_date__lt=date, status='on_leave')]
        except:
            traceback.print_exc()
    threading.Thread(target=resetCount).start()


# Create your views here.


def main(response):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    return redirect('/home')


def register(response):
    if response.method == 'POST':
        form = forms.student(response.POST)

        if form.is_valid():
            cd = form.cleaned_data
            email = f'{cd["uid"]}@rguktsklm.ac.in'
            user = User.objects.get_or_create(
                username=cd["username"], email=email)[0]
            user.set_password(cd["password1"])
            user.save()
            up = UserProfile(user=user)
            up.id = cd['uid'].capitalize()
            up.branch = cd['branch']
            up.year = cd['year']
            up.room_no = cd['room_no']
            up.save()
            response.session['uid'] = up.id
            return redirect('personal_info')
        return render(response, 'register.html', {'form': form, 'button': '+ Add personal Info', 'i': 1, 'action': 'register'})
    return render(response, 'register.html', {'form': forms.student(), 'button': '+ Add personal Info', 'i': 1, 'action': 'register'})


def pinfo(response):
    try:
        response.session['uid']
    except:
        return redirect('register')
    if response.method == 'POST':
        form = forms.pform(response.POST)

        if form.is_valid():
            up = UserProfile.objects.get(
                id=response.session['uid'])
            print(up)
            form = form.save(commit=False)
            form.userprofile = up
            form.save()
            return redirect('/')
        return render(response, 'register.html', {'form': form,  'button': 'Register', 'i': 2,  'action': 'personal_info'})
    return render(response, 'register.html', {'form': forms.pform(), 'button': 'Register', 'i': 2,  'action': 'personal_info'})


def userhome(response):
    print('schedule')
    threading.Thread(target=expireObjects).start()
    if response.user.profile.usertype == 'admin':
        return redirect('admin_home')
    elif response.user.profile.usertype == 'security':
        return redirect('sec_home')
    return


def usertype(response):
    print('schedule')
    threading.Thread(target=expireObjects).start()
    if response.user.profile.usertype == 'admin':
        return 'admin'
    elif response.user.profile.usertype == 'security':
        return 'security'
    return 'student'


def newLeave(response):
    if not isinstance(response.user, User):
        return redirect('login')
    if not usertype(response) == 'student':
        return redirect('home')
    if not response.user.profile.in_campus:
        return redirect('nic')
    try:
        Personal_info.objects.get(userprofile=response.user.profile)
    except:
        response.session['uid'] = response.user.profile.id
        return redirect('personal_info')
    print(Counts.objects.get(user=response.user.profile), max_leave)
    if Counts.objects.get(user=response.user.profile).leaves_this_month == max_leave:

        messages.error(
            response, 'Maximum number of  leaves per month reached')
        return redirect('home')
    form = forms.newLeave()
    if response.method == 'POST':
        form = forms.newLeave(response.POST,  response.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = response.user.profile
            form.status = 'pending'
            form.save()
        else:
            return render(response, 'newLeave.html', {'form': form, 'counts': Counts.objects.get(user=response.user.profile)})
        return redirect('home')
    return render(response, 'newLeave.html', {'form': form, 'counts': Counts.objects.get(user=response.user.profile)})


def home(response):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if userhome(response):
        return redirect(userhome(response).url)
    if not response.user.profile.in_campus:
        return redirect('nic')
    leaves = Leaves.objects.filter(user=response.user.profile).order_by('-id')
    outings = Outing.objects.filter(
        user=response.user.profile).order_by('-id')
    counts = Counts.objects.get(user=response.user.profile)
    return render(response, 'home.html', {'leaves': leaves, 'outings': outings, 'id': response.user.profile.id, 'counts': counts})


def admin_home(response):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'admin':
        return redirect('home')
    g = 'pending'
    try:
        g = response.GET['featured']
    except:
        pass
    if g == 'on leave':
        g = 'on_leave'
    leaves = Leaves.objects.filter(
        user__year=response.user.profile.year, status=g).order_by('-is_emergency', '-id')
    # if g == 'delayed':
    pinfos = [Personal_info.objects.get(userprofile=l.user) for l in leaves]
    pnb = []
    ppnb = []
    for p in pinfos:
        pnb.append(p.phone_no)
        ppnb.append(p.Parent_phn_no)

    outings = Outing.objects.filter(
        user__year=response.user.profile.year, status='pending')
    filters = ['pending', 'granted', 'delayed',
               'completed', 'rejected', 'expired', 'on leave']
    context = {'leaves': leaves, 'outings': outings, 'username': response.user.username,
               'filters': filters, 'pnb': pnb, 'ppnb': ppnb, 'g': g}
    return render(response, 'admin_home.html', context=context)


def approve(response, loro, id, remark=None):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'admin':
        return redirect('home')
    if loro == 'l':
        leave = Leaves.objects.get(id=id)
        if response.user.profile.year != leave.user.year or response.user.profile.branch != leave.user.branch or (leave.status not in ['pending', 'rejected']):
            return redirect('admin_home')
        leave.status = 'granted'
        print(remark)
        if remark:
            leave.remark = remark
        leave.save()
        if leave.is_emergency == True:
            threading.Thread(target=sendMail, args=(
                dean_mail, f'Emergency leave for {leave.user.id}', f'Sir, This is to inform you that an emergency leave is granted to {leave.user.id} \n Leave Details:  \n \n Reason : {leave.reason} \n \n Description : {leave.description} \n \n Out date : {leave.out_date} \n \n In date : {leave.in_date}  \n \n Is Emergency : {leave.is_emergency}  \n \n Remark : {leave.remark}'))
        threading.Thread(target=sendMail, args=(leave.user.user.email,
                                                f'Your leave is granted, Out date:{leave.out_date}',
                                                f'Dear student your leave regarding {leave.reason} is granted  \n \n You can leave the campus starting {leave.out_date} and have to return to the campus by {leave.in_date}  \n \n Hoping you will reach your destination safely \n \n OLMS IIIT Srikakulam \n \n Have a safe journey \n \n Leave Details:  \n \n Reason : {leave.reason} \n \n Description : {leave.description} \n \n Out date : {leave.out_date} \n \n In date : {leave.in_date}  \n \n Is Emergency : {leave.is_emergency}  \n \n Remark : {leave.remark}')
                         ).start()
    elif loro == 'o':
        outing = Outing.objects.get(id=id)
        if response.user.profile.year != outing.user.year or response.user.profile.branch != outing.user.branch or leave.status != 'pending':
            return redirect('admin_home')
        outing.status = 'granted'
        outing.save()
        threading.Thread(target=sendMail, args=(outing.user.user.email,
                                                f'Your outing is granted, Date:{outing.date}',
                                                f'Dear student your outing regarding {outing.reason} is granted  \n \n You have to return to the campus by 7:00 pm ,{outing.date}  \n \n OLMS IIIT Srikakulam')
                         ).start()
    return redirect('admin_home')


def reject(response, loro, id):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'admin':
        return redirect('home')
    if loro == 'l':
        leave = Leaves.objects.get(id=id)
        if response.user.profile.year != leave.user.year or response.user.profile.branch != leave.user.branch or (leave.status not in ['pending', 'granted']):
            return redirect('home')
        leave.status = 'rejected'
        leave.save()
        threading.Thread(target=sendMail, args=(leave.user.user.email,
                                                f'Your leave is rejected, remark:{leave.remark}',
                                                f'Dear student your leave regarding {leave.reason} is rejected  \n \n OLMS IIIT Srikakulam \n \n Leave Details:  \n \n Reason : {leave.reason} \n \n Description : {leave.description} \n \n Out date : {leave.out_date} \n \n In date : {leave.in_date}  \n \n Is Emergency : {leave.is_emergency}  \n \n Remark : {leave.remark}')
                         ).start()
    elif loro == 'o':
        outing = Outing.objects.get(id=id)
        if response.user.profile.year != outing.user.year or response.user.profile.branch != outing.user.branch or leave.status != 'pending':
            return redirect('home')
        outing.status = 'rejected'
        outing.save()
        threading.Thread(target=sendMail, args=(outing.user.user.email,
                                                f'Your outing is rejected, Date:{outing.date}',
                                                f'Dear student your outing regarding {outing.reason} is rejected]  \n \n OLMS IIIT Srikakulam')
                         ).start()
    return redirect('admin_home')


def sec_home(response, aadhar=None, manual=None):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'security':
        return redirect('home')
    leaves = None
    outings = None
    if aadhar == 0 or manual:
        date = datetime.now().date()
        leaves = list(Leaves.objects.filter(
            status='granted', out_date__lte=date, in_date__gt=date))
        outings = Outing.objects.filter(status__in=['granted', 'on_outing'])
        # outings = [o for o in outings if o.out_time.replace(tzinfo=None) <
        #            datetime.now().time() and o.in_time.replace(tzinfo=None) > datetime.now().time()]
        leaves.extend(Leaves.objects.filter(
            status__in=['on_leave', 'delayed']))
        print(leaves, outings)
        # leaves = Leaves.objects.all()
        # outings = Outing.objects.all()
        pinfos = [Personal_info.objects.get(
            userprofile=x.user) for x in leaves]
        print(pinfos)
    try:
        user = Personal_info.objects.get(aadhar_no=int(aadhar)).userprofile
        try:
            outing = Outing.objects.get(
                user=user, date=datetime.now().date(), status='granted')
            outing.status = 'on_outing'
            outing.actual_out_time = datetime.now().time()
            outing.save()
            user.in_campus = False
            user.save()

            # 1. User checking out with a granted outing
            messages.success(response, f'{user.id} can go for outing')
            messages.info(response, f'o{outing.id}')
            messages.info(response, f'id:{outing.user.id}')
            return redirect('sec_home')

        except:
            traceback.print_exc()
            try:
                outing = Outing.objects.get(
                    user=user, status__in=['on_outing'], date=datetime.now().date())
                if (datetime.combine(datetime.today(), outing.actual_out_time.replace(tzinfo=None)) + timedelta(minutes=1)) > datetime.now():
                    messages.warning(
                        response, f'Can only check in the user after {(datetime.combine(datetime.today(), outing.actual_out_time.replace(tzinfo=None)) + timedelta(minutes=1))}')
                    return redirect('sec_outings')
                outing.status = 'completed'
                outing.actual_in_time = datetime.now().time()
                outing.save()
                user.in_campus = True
                user.save()
                messages.success(response, f'{user.id} is checked in')
                messages.info(response, f'id:{outing.user.id}')

                # 2. User checking in after outing
                return redirect('sec_home')

            except:
                try:
                    leave = Leaves.objects.get(
                        user=user, status__in=['granted'])
                    leave.status = 'on_leave'
                    leave.actual_out_date = datetime.now()
                    leave.save()
                    user.in_campus = False
                    user.save()
                    # 1. User checking out with a granted leave
                    messages.success(
                        response, f'{user.id} can go for leave')
                    messages.info(response, f'l{leave.id}')
                    messages.info(response, f'id:{leave.user.id}')

                    return redirect('sec_home')

                except:
                    try:
                        leave = Leaves.objects.get(
                            user=user, status__in=['on_leave'])
                        if leave.actual_out_date.replace(tzinfo=None)+timedelta(minutes=2) > datetime.now():
                            messages.warning(
                                response, f'Can only check in the user after {(datetime.combine(datetime.today(), leave.actual_out_date.replace(tzinfo=None)) + timedelta(minutes=2))}')
                            return redirect('sec_home')
                        leave.status = 'completed'
                        leave.actual_in_date = datetime.now()
                        leave.save()
                        user.in_campus = True
                        user.save()
                        messages.success(
                            response, f'{user.id} is checked in')
                        # 2. User checking in after leave
                        pinfo = Personal_info.objects.get(
                            userprofile=leave.user)
                        return redirect('sec_home')

                    except:
                        traceback.print_exc()
                        try:
                            leave = Leaves.objects.get(
                                user=user, status__in=['completed'])
                            messages.warning(
                                response, f'No leave or outing for {user.id}')
                            # 3. User's leave already completed
                            return redirect('sec_home')
                        except:
                            traceback.print_exc()
                            # 4. No leaves and outings for that user
                            messages.warning(
                                response, f'No leave or outing for {user.id}')
                            return redirect('sec_home')
                if leave.out_date.replace(tzinfo=None) < datetime.now() or leave.in_date.replace(tzinfo=None) > datetime.now():
                    print('in hereee')
                    messages.warning(
                        response, f'No leave or outing for {user.id}')
                    return redirect('sec_home')
    except:
        traceback.print_exc()
        #  Displaying all leaves
        if aadhar:
            messages.error(response,
                           f'No student account is registered with aadhar no.{aadhar}')
        if not manual:
            return render(response, 'sec_home.html', {'leaves': leaves, 'outings': outings})

        return render(response, 'sec_home.html', {'leaves': leaves, 'outings': outings, 'pinfos': pinfos})

        return render(response, 'sec_home.html', {'leaves': leaves, 'outings': outings, 'pinfos': pinfos})


def out(response, loro, id):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'security':
        return redirect('home')
    if loro == 'l':
        leave = Leaves.objects.get(pk=id)
        leave.status = 'on_leave'
        leave.actual_out_date = datetime.now().date()
        leave.save()
        user = UserProfile.objects.get(id=leave.user.id)
        user.in_campus = False
        user.save()
        messages.success(response, f'{user.id} can go for leave')
    elif loro == 'o':
        outing = Outing.objects.get(pk=id)
        outing.status = 'on_outing'
        outing.actual_out_time = datetime.now()
        outing.save()
        user = UserProfile.objects.get(id=outing.user.id)
        user.in_campus = False
        user.save()
        messages.success(response, f'{user.id} can go for outing')
    return redirect('/sec_home/manual')


def inn(response, loro, id):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'security':
        return redirect('home')
    if loro == 'l':
        leave = Leaves.objects.get(pk=id)
        leave.status = 'completed'
        leave.actual_in_date = datetime.now()
        leave.save()
        user = UserProfile.objects.get(id=leave.user.id)
        user.in_campus = True
        user.save()
        messages.success(response, f'{user.id} is checked in')
    elif loro == 'o':
        outing = Outing.objects.get(pk=id)
        outing.status = 'completed'
        outing.actual_in_time = datetime.now().time()
        outing.save()
        user = UserProfile.objects.get(id=outing.user.id)
        user.in_campus = True
        user.save()
        messages.success(response, f'{user.id} is checked in')
    return redirect('/sec_home/manual')


def leave_view(response, lid):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'admin':
        return redirect('home')
    leave = Leaves.objects.get(pk=lid)
    pi = Personal_info.objects.get(userprofile=leave.user)
    count = Counts.objects.get(user=leave.user)
    return render(response, 'leave_view.html', {'leave': leave, 'pi': pi, 'count': count})


def nic(response):
    return render(response, 'nic.html', {})


def delete(response, loro, id):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'student':
        return redirect('home')
    if loro == 'l':
        leave = Leaves.objects.get(pk=id)
        if response.user.profile != leave.user:
            return redirect('home')
        leave.delete()
    elif loro == 'o':
        outing = Outing.objects.get(pk=id)
        if response.user.profile != outing.user:
            return redirect('home')
        outing.delete()
    return redirect('home')


def outing(response):
    if not isinstance(response.user, User):
        return redirect('login')
    if not usertype(response) == 'student':
        return redirect('home')
    if not response.user.profile.in_campus:
        return redirect('nic')
    try:
        Personal_info.objects.get(userprofile=response.user.profile)
    except:
        response.session['uid'] = response.user.profile.id
        return redirect('personal_info')
    if response.method == 'GET':
        form = forms.OutingForm()
        if not response.user.profile.in_campus:
            return redirect('home')
        try:
            leave = Leaves.objects.filter(user=response.user.profile,
                                          out_date=datetime.now().date()).last()
            print(leave)
            messages.warning(
                response, f'cannot apply a outing when there is a leave pending => Leave({leave.out_date} to {leave.in_date})')
            return redirect('home')
        except:
            pass
        return render(response, 'outing.html', {'form': form, 'counts': Counts.objects.get(user=response.user.profile)})
    else:
        form = forms.OutingForm(response.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = response.user.profile
            form.status = 'pending'
            form.date = datetime.now().date()
            form.save()
        else:
            return render(response, 'outing.html', {'form': form, 'counts': Counts.objects.get(user=response.user.profile)})
        return redirect('home')


def public_holiday(response):
    if response.user.is_superuser or not isinstance(response.user, User):
        return redirect('logout')
    if usertype(response) != 'admin':
        return redirect('home')
    if response.method == 'POST':
        form = forms.PublicHoliday(response.POST)
        if form.is_valid():
            users = UserProfile.objects.filter(
                year=response.user.profile.year, branch=response.user.profile.branch, usertype='student', gender=form.cleaned_data['gender'])
            for u in users:
                leave = Leaves()
                leave.out_date = form.cleaned_data['out_date']
                leave.in_date = form.cleaned_data['in_date']
                leave.reason = form.cleaned_data['reason']
                leave.description = form.cleaned_data['description']
                leave.status = 'granted'
                leave.user = u
                leave.save()
            return redirect('home')
        return render(response, 'public_holiday.html', {'form': form})
    return render(response, 'public_holiday.html', {'form': forms.PublicHoliday()})


def forgotPassword(response, otp=None):
    if isinstance(response.user, User):
        return redirect('logoutrequired')
    if not otp:
        try:
            response.GET['email']
        except:
            return render(response, 'forpass.html', {})
        if response.method in ('GET', 'POST'):
            ootp = random.randrange(100000, 999999)
            response.session['otp'] = ootp
            print(ootp)
            print('sending mail')
            email = f"{response.GET['email'].capitalize()}@rguktsklm.ac.in"
            try:
                User.objects.get(email=email)
            except:
                return render(response, 'forpass.html', {'error': f'No olms account is registered with id {email}'})
            response.session['email'] = email
            threading.Thread(target=sendMail, name='sendmail', args=(email, f'Your otp for olms IIIT sklm is {ootp}',  f'Your otp for olms IIIT sklm is {ootp} \n \n If you didn\'t  \n \n . This otp will expire with in 10 mins \
                             \n \n And remember do not share your collage mail id and password with anyone')).start()
            messages.success(response, 'OTP')
            return redirect('forgotpassword')
    if otp:
        ootp = response.session['otp']
        print(otp, otp.__class__, ootp)
        if ootp != otp:
            print('wrong otp')
            messages.warning(response, 'Wrong otp')
            return redirect('forgotpassword')
        return redirect('setnewpassword')
    return redirect('home')


def setNewPassword(response):
    try:
        response.session['email']
    except:
        return redirect('changepassword')
    if response.method == 'POST':
        form = forms.SetNewPassword(response.POST)
        user = User.objects.get(email=response.session['email'])

        if form.is_valid():
            cd = form.cleaned_data
            try:
                validate_password(cd['password'])
            except Exception as e:
                print(e)
                for err in e:
                    print(err)
                    form.add_error('password', err)
                return render(response, 'setnewpass.html', {'form': form})
            user.set_password(cd['password'])
            user.save()
            return redirect('logout')
        print('not valid')
        return render(response, 'setnewpass.html', {'form': form})
    return render(response, 'setnewpass.html', {'form': forms.SetNewPassword()})


def change_password(response):
    if not isinstance(response.user, User):
        return redirect('login')
    if response.method == 'POST':
        form = PasswordChangeForm(response.user, response.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(response, user)  # Important!
            messages.success(
                response, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(response, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(response.user)
    return render(response, 'changepass.html', {
        'form': form,
    })


def sendMail(email, sub, msg):
    EmailMessage(sub, msg, to=[email]).send()


def logoutreq(response):
    if isinstance(response.user, User):
        return render(response, 'logoutreq.html', {})
    return redirect('login')


def undo(res, obj):
    if usertype(res) != 'security':
        return redirect('home')
    if obj[0] == 'o':
        try:
            outing = Outing.objects.get(
                id=int(obj[1:]), status='on_outing')
            outing.status = 'granted'
            outing.save()
            outing.user.in_campus = True
            outing.user.save()
        except:
            traceback.print_exc()
    elif obj[0] == 'l':
        try:
            leave = Leaves.objects.get(
                id=int(obj[1:]), status='on_leave')
            leave.status = 'granted'
            leave.save()
            leave.user.in_campus = True
            leave.user.save()
        except:
            traceback.print_exc()
    return redirect('sec_home')


def profile(res):
    if usertype(res) != 'student':
        return redirect("home")
    pi = Personal_info.objects.get(userprofile=res.user.profile)
    return render(res, 'profilepage.html', {'pi': pi, 'user': res.user.profile})
