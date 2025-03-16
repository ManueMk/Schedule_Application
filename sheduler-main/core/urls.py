from core.views import (AuthentificationAdminView, EditProfilAdminView, EditShedulerView, HomeView, PrintShedulerClassesView,
					LogoutView, ListClassesView, ListSallesView, ListTeachersView, PrintShedulerSallesView,
					RegisterClassesView, RegisterCoursesView, RegisterSallesView, RegisterTeachersView, PrintShedulerTeachersView, SchedulerPlannView,
					GenerateCvView, UploadTeachersView, UploadClassesView, UploadSallesView,
					UploadCoursesView, SearchSallesView, SearchTeachersView, SearchClassesView)
from django.urls import path
from django.conf.urls.static import static
from Sheduler import settings

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
	path('',HomeView.as_view(),name='home'),
	path('edit_profil',EditProfilAdminView.as_view(),name='edit_profil'),
	path('list/teachers',ListTeachersView.as_view(),name='list/teachers'),
	path('list/salles',ListSallesView.as_view(),name='list/salles'),
	path('list/classes',ListClassesView.as_view(),name='list/classes'),
	path('register/teachers',RegisterTeachersView.as_view(),name='register/teachers'),
	path('register/salles',RegisterSallesView.as_view(),name='register/salles'),
	path('register/classes',RegisterClassesView.as_view(),name='register/classes'),
	path('register/courses',RegisterCoursesView.as_view(),name='register/courses'),
	path('searchsalles',SearchSallesView.as_view(),name='searchsalles'),
	path('searchteachers',SearchTeachersView.as_view(),name='searchteachers'),
	path('searchclasses',SearchClassesView.as_view(),name='searchclasses'),
	path('sheduler/salles/<slug:slug>/',PrintShedulerSallesView.as_view(),name='sheduler/salle'),
	path('uploadteachers',UploadTeachersView.as_view(),name='uploadteachers'),
	path('uploadclasses',UploadClassesView.as_view(),name='uploadclasses'),
	path('uploadsalles',UploadSallesView.as_view(),name='uploadsalles'),
	path('uploadcourses',UploadCoursesView.as_view(),name='uploadcourses'),
	#path('generate/<slug:slug>/',GenerateCvView.as_view(),name='generate'),
	path('sheduler/classes/<slug:slug>/',PrintShedulerClassesView.as_view(),name='sheduler/classe'),
	path('sheduler/teachers/<slug:slug>/',PrintShedulerTeachersView.as_view(),name='sheduler/teacher'),
	path('edit/sheduler',EditShedulerView.as_view(),name='edit/sheduler'),
	#path('scheduler_form',SchedulerFormView.as_view(),name='scheduler_form'),
	path('scheduler_plann',SchedulerPlannView.as_view(),name='scheduler_plann'),
	path('login', AuthentificationAdminView.as_view(), name="login"),
	path('logout',LogoutView.as_view(),name='logout'),
	
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()