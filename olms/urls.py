from django.urls import path, include
from . import views
from django.conf.urls import url
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static
import django

urlpatterns = [
    path('newleave', views.newLeave, name='newLeave'),
    path('', views.main, name='main_page'),
    path('home', views.home, name='home'),
    path('register', views.register, name='register'),
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}),
    path('admin_home', views.admin_home, name='admin_home'),
    path('approve/<str:loro>/<int:id>', views.approve, name='approve'),
    path('approve/<str:loro>/<int:id>/<str:remark>',
         views.approve, name='approve'),
    path('reject/<str:loro>/<int:id>', views.reject, name='reject'),
    path('out/<str:loro>/<int:id>', views.out, name='out'),
    path('in/<str:loro>/<int:id>', views.inn, name='in'),
    path('sec_home/', views.sec_home, name='sec_home'),
    path('sec_home/<int:aadhar>', views.sec_home, name='sec_home_aadhar'),
    path('nic', views.nic, name='nic'),  # not in campus site url
    path('del/<str:loro>/<int:id>', views.delete, name='del'),
    path('newouting', views.outing, name='outing'),
    path('publicholiday', views.public_holiday, name='publicholiday'),
    path('leave/<int:lid>', views.leave_view, name='leaveview'),
    path('personal_info', views.pinfo, name='personal_info'),
    path('forgotpassword', views.forgotPassword, name='forgotpassword'),
    path('forgotpassword/<int:otp>', views.forgotPassword, name='forgotpassword'),
    path('setnewpassword', views.setNewPassword, name='setnewpassword'),
    path('changepassword', views.change_password, name='changepassword'),
    path('logoutrequired', views.logoutreq, name='logoutrequired'),
    path('sec_home/<str:manual>', views.sec_home, name='sec_home'),
    path('undo/<str:obj>', views.undo, name='undo'),
    path('profile', views.profile, name='profile'),
] + static(settings.STATIC_URL, doucument_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
