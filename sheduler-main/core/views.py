import datetime
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import (TeachersForm, TeachersFileForm, ClassesFileForm, SallesForm, 
	SallesFileForm, ClassesForm, CoursesForm, SchedulerForm, CoursesFileForm, 
	SchedulerTableForm, MyAuthentificationForm)
from .models import (Admin, Salle, Teacher, Classe, Courses, Plages, Specialite)
from django.db import connection
import pdfkit
from django.template.loader import get_template
import io
import os



class Emploi():
	
	nom_ens1 = ''
	nom_ens2 = ''
	classe = ''
	salle = ''
	cours = ''


class ListEnseignant():
	
	department = ''
	teachers = []


class ListClasses():
	
	filiere = ''
	name_filiere = ''
	classes = []


# connexion admin
class AuthentificationAdminView(View):
	
	template_name = "core/login.html"

	def get(self, request, *args, **kwargs):
		
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
				return render(request, 'core/home.html', {'admin':admin, 'online':online})
			form_auth = MyAuthentificationForm()
			context = {"form_auth" : form_auth, 'admin':admin, 'online':online}
			return render(request, self.template_name, context)
		else: 
			form_auth = MyAuthentificationForm()
			context = {"form_auth" : form_auth, 'admin':admin, 'online':online}
			return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		
		admin, online = False, False

		form_auth = MyAuthentificationForm(data=request.POST) 

		if form_auth.is_valid():
			username = form_auth.cleaned_data['username']
			password = form_auth.cleaned_data['password']
			if Admin.objects.filter(user__username = username).filter(user__password = password).exists():
				user = Admin.objects.filter(user__username = username).filter(user__password = password)[0].user
			else:
				user = None
			if user is not None:
				if( Admin.objects.filter(user = user).exists()):
					login(request, user)
					admin = True
					online = True
					return render(request, 'core/home.html', {'admin':admin, 'online':online})
				form_auth.msg_error = " Username or Password is not valid !"
				context = {"form_auth" : form_auth, 'admin':admin, 'online':online}
				return render(request, self.template_name, context)
			else:
				form_auth.msg_error = " Username or Password is not valid !"
				context = {"form_auth" : form_auth, 'admin':admin, 'online':online}
				return render(request, self.template_name, context)
		else:
			print(form_auth.errors)
			context = {"form_auth" : form_auth, 'admin':admin, 'online':online}
			return render(request, self.template_name, context)

# deconnexion
class LogoutView(View):

	def get(self, request, *args, **kwargs):		
		logout(request)
		return redirect("login")


# vue pour la page d'accueil du site, la premiere lorsqu'on ouvre le site.
class HomeView(TemplateView):

	template_name = 'core/home.html'

	def get(self, request, *args, **kwargs):
		
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		return render(request, 'core/home.html', {'admin':admin, 'online':online})


# Si l'admin veut modifier son profil
class EditProfilAdminView(TemplateView):

	template_name = 'core/edit_profil_admin.html'


# vue qui liste la liste des enseignants, ensuite l'on clique pour voir son emploi de temps
class ListTeachersView(TemplateView):

	template_name = 'core/list_teachers.html'

	def get(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		departments = list(set([teacher.department for teacher in Teacher.objects.all()]))
		list_teachers = []
		departments = sorted(departments)
		print(departments)
		for department in departments:
			instance = ListEnseignant()
			instance.department = department
			instance.teachers = Teacher.objects.filter(department = department)
			list_teachers.append(instance)
	

		return render(request, self.template_name, {'admin':admin, 'online':online, 'list_teachers':list_teachers, 'admin':admin, 'online':online})

# vue qui liste la liste des salles, ensuite l'on clique pour voir son emploi de temps
class ListSallesView(TemplateView):

	template_name = 'core/list_salles.html'

	def get(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		salles = Salle.objects.all()

		return render(request, self.template_name, {"salles":salles, 'admin':admin, 'online':online})


# vue qui liste la liste des classes, ensuite l'on clique pour voir son emploi de temps
class ListClassesView(TemplateView):

	template_name = 'core/list_classes.html'

	def get(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		filieres = list(set([classe.complete_name_filiere for classe in Classe.objects.all()]))
		list_classes = []
		filieres = sorted(filieres)
		print(filieres)
		for filiere in filieres:
			instance = ListClasses()
			instance.filiere = filiere
			instance.classes = Classe.objects.filter(complete_name_filiere = filiere)
			for classe in instance.classes:
				if classe.groupe != None and classe.groupe != "" :
					classe.groupe = "Group "+str(classe.groupe)+""
				else:
					classe.groupe = ""

				if classe.specialite != None: # juste pour l'affichage
					s = Specialite()
					s.nom_specialite = "/ "+str(classe.specialite)+""
					classe.specialite = s
				else: # ici je veux juste preciser que pour les niveaux 3 et 4 dont la specialité n'est pas precisee qu'en fait cest tronc commun
					if classe.niveau == 'L3' or classe.niveau == 'M1':
						s = Specialite()
						s.nom_specialite = "(tronc commun)"
						classe.specialite = s

			list_classes.append(instance)
		print(list_classes[0].classes)

		return render(request, self.template_name, {'list_classes':list_classes, 'admin':admin, 'online':online})


# vue permettant à l'admin d'enregistrer l'ensemble des enseignants sur la plate forme
class RegisterTeachersView(TemplateView):

	template_name = 'core/register_teachers.html'

	def get(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		return render(request, self.template_name, {'admin':admin, 'online':online})

	def post(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		form = TeachersForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('list/teachers')
		print(form.errors)
		return render(request, self.template_name, {'admin':admin, 'online':online, 'form':form})


# vue permettant à l'admin d'enregistrer l'ensemble des salles sur la plate forme
class RegisterSallesView(TemplateView):

	template_name = 'core/register_salles.html'

	def get(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		return render(request, self.template_name, {'admin':admin, 'online':online})

	def post(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		form = SallesForm(request.POST, request.FILES)
		if form.is_valid():
			res = form.save()
			print(res)
			return redirect('list/salles')
		print(form.errors)
		return render(request, self.template_name, {'admin':admin, 'online':online, 'form':form})


# vue permettant à l'admin d'enregistrer l'ensemble des cours de la fac sur la plate forme
class RegisterCoursesView(TemplateView):

	template_name = 'core/register_courses.html'

	def get(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		teachers = Teacher.objects.all()
		classes = Classe.objects.all()

		return render(request, self.template_name, {'admin':admin, 'online':online, "teachers":teachers, "classes":classes})

	def post(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		form = CoursesForm(request.POST, request.FILES)
		if form.is_valid():
			res = form.save()
			print(res)
			return redirect('list/classes')
		print(form.errors)
		teachers = Teacher.objects.all()
		classes = Classe.objects.all()
		return render(request, self.template_name, {'admin':admin, 'online':online, 'form':form, "teachers":teachers, "classes":classes})


# vue permettant à l'admin d'enregistrer l'ensemble des classes sur la plate forme
class RegisterClassesView(TemplateView):

	template_name = 'core/register_classes.html'

	def get(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		return render(request, self.template_name, {'admin':admin, 'online':online})

	def post(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		form = ClassesForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('list/classes')
		print(form.errors)
		return render(request, self.template_name, {'admin':admin, 'online':online, 'form':form})


# vue qui affiche un emploi de temps quelconque, que ce soit pour un enseignant, pour une salle ou pour une classe
class PrintShedulerView(TemplateView):

	template_name = 'core/show_sheduler.html'


# vue qui affiche l'emploi de temps d'une salle de classe
class PrintShedulerSallesView(TemplateView):

	template_name = 'core/show_sheduler_salles.html'

	def get(self, request, slug, *args, **kwargs):
		salle_id = Salle.objects.get(slug = slug).id
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		context = {'admin':admin, 'online':online}
		with connection.cursor() as cursor:

			# je recupere la salle en question
			query = """select * from core_salle where id = %s"""
			# set variable in query
			cursor.execute(query, (salle_id,))
			salle = cursor.fetchall()[0]
			id_salle = salle[0]
			nom_salle = salle[1]

			# je recupere tous les cours programmés dans cette salle
			query = """select teacher1_id, teacher2_id, course_id, plage_id from core_schedulers where salle_id = %s"""
			# set variable in query
			cursor.execute(query, (id_salle,))
			programmations = cursor.fetchall()			

			#chargeons les emplois à afficher
			for i in programmations:

				# on recupere l'enseignant1
				query = """select full_name, degree from core_teacher where id = %s"""
				cursor.execute(query, (i[0],))
				teacher1 = cursor.fetchall()[0]
				if teacher1[1][0] == 'P' or teacher1[1][0] == 'c' or teacher1[1][0] == 'C':
					nom_ens1 = 'Pr '+teacher1[0]
				if teacher1[1][0] == 'A' or teacher1[1][0] == 'S':
					nom_ens1 = 'Dr '+teacher1[0]
				if teacher1[1][0] == 'V':
					nom_ens1 = 'M. '+teacher1[0]

				# on recupere l'enseignant2
				if not i[1] == None:
					query = """select full_name, degree from core_teacher where id = %s"""
					cursor.execute(query, (i[1],))
					teacher2 = cursor.fetchall()[0]
					if teacher2[1][0] == 'P' or teacher2[1][0] == 'c' or teacher2[1][0] == 'C':
						nom_ens2 = 'Pr '+teacher2[0]
					if teacher2[1][0] == 'A' or teacher2[1][0] == 'S':
						nom_ens2 = 'Dr '+teacher2[0]
					if teacher1[1][0] == 'V':
						nom_ens2 = 'M. '+teacher2[0]
				else:
					nom_ens2 = ""

				# on recupere le cours 
				query = """select code_ue from core_courses where id = %s"""
				cursor.execute(query, (i[2],))
				course = cursor.fetchall()[0][0]
				course = str(course)

				# on recupere la classe
				query = """select classe_id from core_courses where id = %s"""
				print(i[2], ".....................")
				cursor.execute(query, (i[2],))
				classe_id = cursor.fetchall()[0][0]

				query = """select filiere, niveau, specialite_id, groupe from core_classe where id = %s"""
				cursor.execute(query, (classe_id,))
				classe = cursor.fetchall()[0]

				if not classe[2] == None:
					query = """select nom_specialite from core_specialite where id = %s"""
					cursor.execute(query, (classe[2],))
					specialite = cursor.fetchall()[0][0]
				else:
					specialite = ""
				
				if not specialite == "": 
					if classe[3] == None or classe[3] == "":
						classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") "
					else:
						classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") groupe "+ str(classe[3])
				else:
					if classe[1] == 'L3' or classe[1] == 'M1':
						if classe[3] == None or classe[3] == "":
							classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) "
						else:
							classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) groupe "+ str(classe[3])
					else:
						if classe[3] == None or classe[3] == "":
							classe = str(classe[0])+" "+str(classe[1])
						else:
							classe = str(classe[0])+" "+str(classe[1])+" groupe "+ str(classe[3])
				
				globals()['emploi%s' % i[-1]] = Emploi() 
				globals()['emploi%s' % i[-1]].nom_ens1 = nom_ens1
				globals()['emploi%s' % i[-1]].nom_ens2 = nom_ens2
				globals()['emploi%s' % i[-1]].classe = classe
				globals()['emploi%s' % i[-1]].cours = course

				# formation du context 
				context['emploi%s' % i[-1]] = globals()['emploi%s' % i[-1]]


			context['nom_salle'] = nom_salle 
			print(context)
			return render(request, self.template_name, context)


# vue qui affiche l'emploi de temps d'une classe
class PrintShedulerClassesView(TemplateView):

	template_name = 'core/show_sheduler_classes.html'
	classe = 0

	def get(self, request, slug, *args, **kwargs):

		classe_id = Classe.objects.get(slug=slug).id
		courses = Courses.objects.filter(classe_id = classe_id)
		teachers = Teacher.objects.all()
		classrooms = Salle.objects.filter(capacity__gt = Classe.objects.get(id=classe_id).effectif)

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		context = {'admin':admin, 'online':online, 'courses':courses, 'teachers':teachers, 'classrooms':classrooms}
		with connection.cursor() as cursor:

			# je recupere la classe en question
			query = """select filiere, niveau, specialite_id, groupe from core_classe where id = %s"""
			cursor.execute(query, (classe_id,))
			classe = cursor.fetchall()[0]

			if not classe[2] == None:
				query = """select nom_specialite from core_specialite where id = %s"""
				cursor.execute(query, (classe[2],))
				specialite = cursor.fetchall()[0][0]
			else:
				specialite = ""	
				
			print(specialite, 'specialite.....')
			if not specialite == "": 
				# si la classe a une specialite je recupere aussi l'id des cours de la classe sans la specialite (un peu comme ci en prenant l'emploi de temps de infl3 datasciences, je prends aussi l'emploi de temps de infol3 tronc commun)
				query = """select id, specialite_id from core_classe where filiere = %s and niveau = %s"""
				# set variable in query
				cursor.execute(query, (classe[0], classe[1]))
				res = cursor.fetchall()
				print(res, "res")
				keep = []
				for i in res:
					if i[1] == None:
						keep.append(i)
				print(keep, 'keeeep')
				if len(keep) != 0:
					classe_id_also = [k[0] for k in keep]
					print(classe_id_also,  '000')
				else :
					classe_id_also = None 				
				
				if classe[3] == None or classe[3] == "":
					classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") "		
				else:	
					classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") groupe "+ str(classe[3])
			else:
				classe_id_also = None
				if classe[1] == 'L3' or classe[1] == 'M1':
					if classe[3] == None or classe[3] == "":
						classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) "
					else:
						classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) groupe "+ str(classe[3])
				else:
					if classe[3] == None or classe[3] == "":
						classe = str(classe[0])+" "+str(classe[1])
					else:
						classe = str(classe[0])+" "+str(classe[1])+" groupe "+ str(classe[3])

			# je recupere tous les cours de cette classe
			query = """select id from core_courses where classe_id = %s"""
			# set variable in query
			cursor.execute(query, (classe_id,))
			all_courses = cursor.fetchall()
			all_id_courses = [i[0] for i in all_courses]
			print(all_id_courses, 'all_id_courses')

			# j'joute l'id des cours de la classe tronc commun
			if not classe_id_also == None:
				# je recupere tous les cours de cette classe
				#query = """select id from core_courses where classe_id = %s"""
				# set variable in query
				#cursor.execute(query, (classe_id_also,))
				#also_courses = cursor.fetchall()
				also_courses = Courses.objects.filter(classe_id = classe_id_also[0])
				print("also_courses", also_courses)
				to_add = [i.id for i in also_courses]
				print(to_add, 'toadd')
				all_id_courses = all_id_courses + to_add

			programmations = []
			# je recupere tous les cours programmés de cette classe la.
			for id_courses in all_id_courses:
				query = """select teacher1_id, teacher2_id, course_id, salle_id, plage_id from core_schedulers where course_id = %s"""
				# set variable in query
				cursor.execute(query, (id_courses,))
				scheduler_instance = cursor.fetchall()
				if len(scheduler_instance)>0:
					for i in scheduler_instance:
						programmations.append(i)			

			#chargeons les emplois à afficher
			print(programmations, "programmations....")
			for i in programmations:

				# on recupere l'enseignant1
				query = """select full_name, degree from core_teacher where id = %s"""
				cursor.execute(query, (i[0],))
				teacher1 = cursor.fetchall()[0]
				if teacher1[1][0] == 'P' or teacher1[1][0] == 'c' or teacher1[1][0] == 'C':
					nom_ens1 = 'Pr '+teacher1[0]
				if teacher1[1][0] == 'A' or teacher1[1][0] == 'S':
					nom_ens1 = 'Dr '+teacher1[0]
				if teacher1[1][0] == 'V':
					nom_ens1 = 'M. '+teacher1[0]

				# on recupere l'enseignant2
				print("dis nous !!")
				if not i[1] == None:
					print("dis nous !! in")
					query = """select full_name, degree from core_teacher where id = %s"""
					cursor.execute(query, (i[1],))
					teacher2 = cursor.fetchall()[0]
					print(teacher2, teacher2[1], 'toujours')
					if teacher2[1][0] == 'P' or teacher2[1][0] == 'c' or teacher2[1][0] == 'C':
						nom_ens2 = 'Pr '+teacher2[0]
					if teacher2[1][0] == 'A' or teacher2[1][0] == 'S':
						nom_ens2 = 'Dr '+teacher2[0]
					if teacher2[1][0] == 'V':
						nom_ens2 = 'M. '+teacher2[0]
				else:
					print("dis nous !! 2")
					nom_ens2 = ""

				# on recupere le cours 
				query = """select code_ue from core_courses where id = %s"""
				cursor.execute(query, (i[2],))
				course = cursor.fetchall()[0][0]
				course = str(course)

				# on recupere la salle
				query = """select nom_salle from core_salle where id = %s"""
				cursor.execute(query, (i[3],))
				salle = cursor.fetchall()[0][0]
				salle = str(salle)
				
				globals()['emploi%s' % i[-1]] = Emploi() 
				globals()['emploi%s' % i[-1]].nom_ens1 = nom_ens1
				globals()['emploi%s' % i[-1]].nom_ens2 = nom_ens2
				globals()['emploi%s' % i[-1]].cours = course
				globals()['emploi%s' % i[-1]].salle = salle

				# formation du context 
				context['emploi%s' % i[-1]] = globals()['emploi%s' % i[-1]]


			context['classe'] = classe
			context['classe_id'] = classe_id
			if online == True and admin == True:
				return render(request, self.template_name, context)
			else :
				return render(request, 'core/show_sheduler_classes_offline.html', context)	
			

	def post(self, request, slug, *args, **kwargs):
		print("posttttt")
		classe_id = Classe.objects.get(slug=slug).id
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		form = SchedulerTableForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('../../../sheduler/classes/'+str(slug))
		print(form.errors)
		id_plage = form.id_plage
		#------------------------------------------
		courses = Courses.objects.filter(classe_id = classe_id)
		teachers = Teacher.objects.all()
		classrooms = Salle.objects.filter(capacity__gt = Classe.objects.get(id=classe_id).effectif)

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		context = {'id_plage':id_plage, 'admin':admin, 'online':online, 'courses':courses, 'teachers':teachers, 'classrooms':classrooms}
		with connection.cursor() as cursor:

			# je recupere la classe en question
			query = """select filiere, niveau, specialite_id, groupe from core_classe where id = %s"""
			cursor.execute(query, (classe_id,))
			classe = cursor.fetchall()[0]

			if not classe[2] == None:
				query = """select nom_specialite from core_specialite where id = %s"""
				cursor.execute(query, (classe[2],))
				specialite = cursor.fetchall()[0][0]
			else:
				specialite = ""	
			
			print(specialite, 'specialite.....')
			if not specialite == "": 
				# si la classe a une specialite je recupere aussi l'id des cours de la classe sans la specialite (un peu comme ci en prenant l'emploi de temps de infl3 datasciences, je prends aussi l'emploi de temps de infol3 tronc commun)
				query = """select id, specialite_id from core_classe where filiere = %s and niveau = %s"""
				# set variable in query
				cursor.execute(query, (classe[0], classe[1]))
				res = cursor.fetchall()
				print(res, "res")
				keep = []
				for i in res:
					if i[1] == None:
						keep.append(i)
				print(keep, 'keeeep')
				if len(keep) != 0:
					classe_id_also = [k[0] for k in keep]
					print(classe_id_also,  '000')
				else :
					classe_id_also = None 				
				
				if classe[3] == None or classe[3] == "":
					classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") "		
				else:	
					classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") groupe "+ str(classe[3])
			else:
				classe_id_also = None
				if classe[1] == 'L3' or classe[1] == 'M1':
					if classe[3] == None or classe[3] == "":
						classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) "
					else:
						classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) groupe "+ str(classe[3])
				else:
					if classe[3] == None or classe[3] == "":
						classe = str(classe[0])+" "+str(classe[1])
					else:
						classe = str(classe[0])+" "+str(classe[1])+" groupe "+ str(classe[3])

			# je recupere tous les cours de cette classe
			query = """select id from core_courses where classe_id = %s"""
			# set variable in query
			cursor.execute(query, (classe_id,))
			all_courses = cursor.fetchall()
			all_id_courses = [i[0] for i in all_courses]

			'''
			# j'joute l'id des cours de la classe tronc commun
			if not classe_id_also == None:
				# je recupere tous les cours de cette classe
				query = """select id from core_courses where classe_id = %s"""
				# set variable in query
				cursor.execute(query, (classe_id_also,))
				also_courses = cursor.fetchall()
				all_also_courses = [i[0] for i in all_courses]
				print(all_also_courses, "donc queeeeee", classe_id_also)
			'''

			programmations = []
			# je recupere tous les cours programmés de cette classe la.
			for id_courses in all_id_courses:
				query = """select teacher1_id, teacher2_id, course_id, salle_id, plage_id from core_schedulers where course_id = %s"""
				# set variable in query
				cursor.execute(query, (id_courses,))
				scheduler_instance = cursor.fetchall()
				if len(scheduler_instance)>0:
					for i in scheduler_instance:
						programmations.append(i)			

			#chargeons les emplois à afficher
			print(programmations, "programmations....")
			for i in programmations:

				# on recupere l'enseignant1
				query = """select full_name, degree from core_teacher where id = %s"""
				cursor.execute(query, (i[0],))
				teacher1 = cursor.fetchall()[0]
				if teacher1[1][0] == 'P' or teacher1[1][0] == 'c' or teacher1[1][0] == 'C':
					nom_ens1 = 'Pr '+teacher1[0]
				if teacher1[1][0] == 'A' or teacher1[1][0] == 'S':
					nom_ens1 = 'Dr '+teacher1[0]
				if teacher1[1][0] == 'V':
					nom_ens1 = 'M. '+teacher1[0]

				# on recupere l'enseignant2
				print("dis nous !!")
				if not i[1] == None:
					print("dis nous !! in")
					query = """select full_name, degree from core_teacher where id = %s"""
					cursor.execute(query, (i[1],))
					teacher2 = cursor.fetchall()[0]
					if teacher2[1][0] == 'P' or teacher2[1][0] == 'c' or teacher2[1][0] == 'C':
						nom_ens2 = 'Pr '+teacher2[0]
					if teacher2[1][0] == 'A' or teacher2[1][0] == 'S':
						nom_ens2 = 'Dr '+teacher2[0]
					if teacher2[1][0] == 'V':
						nom_ens2 = 'M. '+teacher2[0]
				else:
					print("else..")
					nom_ens2 = ""

				# on recupere le cours 
				query = """select code_ue from core_courses where id = %s"""
				cursor.execute(query, (i[2],))
				course = cursor.fetchall()[0][0]
				course = str(course)

				# on recupere la salle
				query = """select nom_salle from core_salle where id = %s"""
				cursor.execute(query, (i[3],))
				salle = cursor.fetchall()[0][0]
				salle = str(salle)
				
				globals()['emploi%s' % i[-1]] = Emploi() 
				globals()['emploi%s' % i[-1]].nom_ens1 = nom_ens1
				globals()['emploi%s' % i[-1]].nom_ens2 = nom_ens2
				globals()['emploi%s' % i[-1]].cours = course
				globals()['emploi%s' % i[-1]].salle = salle

				# formation du context 
				context['emploi%s' % i[-1]] = globals()['emploi%s' % i[-1]]


			context['classe'] = classe
			context['classe_id'] = classe_id
			context['form'] = form
		return render(request, self.template_name, context)


# vue qui affiche l'emploi de temps d'un enseignant
class PrintShedulerTeachersView(TemplateView):

	template_name = 'core/show_sheduler_teachers.html'

	def get(self, request, slug, *args, **kwargs):
		teacher_id = Teacher.objects.get(slug = slug).id
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		context = {'admin':admin, 'online':online}
		with connection.cursor() as cursor:

			# je recupere l'enseignant en question'
			query = """select degree, full_name from core_teacher where id = %s"""
			# set variable in query
			cursor.execute(query, (teacher_id,))
			teacher = cursor.fetchall()[0]
			degree = teacher[0]
			full_name = teacher[1]

			# je recupere tous les cours programmés avec cet enseignant
			query = """select salle_id, course_id, plage_id from core_schedulers where teacher1_id = %s or teacher2_id=%s"""
			# set variable in query
			cursor.execute(query, (teacher_id,teacher_id))
			programmations = cursor.fetchall()		
			print(programmations, "programmations")	

			#chargeons les emplois à afficher
			for i in programmations:

				# on recupere le cours 
				query = """select code_ue from core_courses where id = %s"""
				cursor.execute(query, (i[1],))
				course = cursor.fetchall()[0][0]
				course = str(course)

				# on recupere la salle
				query = """select nom_salle from core_salle where id = %s"""
				cursor.execute(query, (i[0],))
				salle = cursor.fetchall()[0][0]
				salle = str(salle)

				# on recupere la classe
				query = """select classe_id from core_courses where id = %s"""
				print(i[1], ".....................")
				cursor.execute(query, (i[1],))
				classe_id = cursor.fetchall()[0][0]

				query = """select filiere, niveau, specialite_id, groupe from core_classe where id = %s"""
				cursor.execute(query, (classe_id,))
				classe = cursor.fetchall()[0]

				if not classe[2] == None:
					query = """select nom_specialite from core_specialite where id = %s"""
					cursor.execute(query, (classe[2],))
					specialite = cursor.fetchall()[0][0]
				else:
					specialite = ""
				
				if not specialite == "": 
					if classe[3] == None or classe[3] == "":
						classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") "
					else:
						classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") groupe "+ str(classe[3])
				else:
					if classe[1] == 'L3' or classe[1] == 'M1':
						if classe[3] == None or classe[3] == "": 
							classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) "
						else:
							classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) groupe "+ str(classe[3])
					else:
						if classe[3] == None or classe[3] == "": 
							classe = str(classe[0])+" "+str(classe[1])
						else:
							classe = str(classe[0])+" "+str(classe[1])+" groupe "+ str(classe[3])
				
				globals()['emploi%s' % i[-1]] = Emploi() 
				globals()['emploi%s' % i[-1]].classe = classe
				globals()['emploi%s' % i[-1]].salle = salle
				globals()['emploi%s' % i[-1]].cours = course

				# formation du context 
				context['emploi%s' % i[-1]] = globals()['emploi%s' % i[-1]]

			if degree[0] == 'P' or degree[0] == 'c' or degree[0] == 'C':
				full_name = 'Pr '+full_name
			if degree[0] == 'A' or degree[0] == 'S':
				full_name = 'Dr '+full_name
			if degree[0] == 'V':
				full_name = 'M. '+full_name	
			context['full_name_degree'] = full_name
			print(context)
			return render(request, self.template_name, context)


# si jamais l'on veut modifier l'emploi de temps direct, celle qui s'affiche dans __PrintShedulerView__
class EditShedulerView(TemplateView):

	template_name = 'core/edit_sheduler.html'

	def get(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		teachers = Teacher.objects.all()
		courses = Courses.objects.all()
		classrooms = Salle.objects.all()
		plages = Plages.objects.all()

		return render(request, self.template_name, {'admin':admin, 'online':online, "plages":plages, "teachers":teachers, "courses":courses, "classrooms":classrooms})

	def post(self, request, *args, **kwargs):

		teachers = Teacher.objects.all()
		courses = Courses.objects.all()
		classrooms = Salle.objects.all()
		plages = Plages.objects.all()

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		form = SchedulerForm(request.POST, request.FILES)
		if form.is_valid():
			rturn = form.save()			
			return redirect('../../../sheduler/classes/'+str(rturn))
		print(form.errors)
		return render(request, self.template_name, {'admin':admin, 'online':online, "plages":plages, "teachers":teachers, "courses":courses, "classrooms":classrooms, 'form':form})


class SchedulerFormView(TemplateView):

	template_name = 'core/scheduler_form.html'

class GenerateCvView(TemplateView):

	def get(self, request, classe_id, *args, **kwargs):
		
		courses = Courses.objects.filter(classe_id = classe_id)
		teachers = Teacher.objects.all()
		classrooms = Salle.objects.filter(capacity__gt = Classe.objects.get(id=classe_id).effectif)

		context = {'courses':courses, 'teachers':teachers, 'classrooms':classrooms}
		with connection.cursor() as cursor:

			# je recupere la classe en question
			query = """select filiere, niveau, specialite_id, groupe from core_classe where id = %s"""
			cursor.execute(query, (classe_id,))
			classe = cursor.fetchall()[0]

			if not classe[2] == None:
				query = """select nom_specialite from core_specialite where id = %s"""
				cursor.execute(query, (classe[2],))
				specialite = cursor.fetchall()[0][0]
			else:
				specialite = ""	
			
			if not specialite == "": 
				''' je reviendrais de ssus
				# si la classe a une specialite je recupere aussi l'id des cours de la classe sans la specialite (un peu comme ci en prenant l'emploi de temps de infl3 datasciences, je prends aussi l'emploi de temps de infol3 tronc commun)
				query = """select specialite_id from core_classe where filiere = %s and niveau = %s"""
				# set variable in query
				cursor.execute(query, (classe[0], classe[1]))
				res = cursor.fetchall()
				print(res, "res")
				if len(res[0]) != 0:
					classe_id_also = res[1][0]
					print(len(classe_id_also),  '000')
				else :
					classe_id_also = None 				
				'''
				if classe[3] == "":
					classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") "		
				else:	
					classe = str(classe[0])+" "+str(classe[1])+" ("+str(specialite)+") groupe "+ str(classe[3])
			else:
				#classe_id_also = None
				if classe[1] == 'L3' or classe[1] == 'M1':
					if classe[3] == "" :
						classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) "
					else:
						classe = str(classe[0])+" "+str(classe[1])+" (tronc commun) groupe "+ str(classe[3])
				else:
					if classe[3] == "" :
						classe = str(classe[0])+" "+str(classe[1])
					else:
						classe = str(classe[0])+" "+str(classe[1])+" groupe "+ str(classe[3])

			# je recupere tous les cours de cette classe
			query = """select id from core_courses where classe_id = %s"""
			# set variable in query
			cursor.execute(query, (classe_id,))
			all_courses = cursor.fetchall()
			all_id_courses = [i[0] for i in all_courses]

			'''
			# j'joute l'id des cours de la classe tronc commun
			if not classe_id_also == None:
				# je recupere tous les cours de cette classe
				query = """select id from core_courses where classe_id = %s"""
				# set variable in query
				cursor.execute(query, (classe_id_also,))
				also_courses = cursor.fetchall()
				all_also_courses = [i[0] for i in all_courses]
				print(all_also_courses, "donc queeeeee", classe_id_also)
			'''

			programmations = []
			# je recupere tous les cours programmés de cette classe la.
			for id_courses in all_id_courses:
				query = """select teacher1_id, teacher2_id, course_id, salle_id, plage_id from core_schedulers where course_id = %s"""
				# set variable in query
				cursor.execute(query, (id_courses,))
				scheduler_instance = cursor.fetchall()
				if len(scheduler_instance)>0:
					for i in scheduler_instance:
						programmations.append(i)			

			#chargeons les emplois à afficher
			print(programmations, "programmations....")
			for i in programmations:

				# on recupere l'enseignant1
				query = """select full_name, degree from core_teacher where id = %s"""
				cursor.execute(query, (i[0],))
				teacher1 = cursor.fetchall()[0]
				if teacher1[1][0] == 'P' or teacher1[1][0] == 'c' or teacher1[1][0] == 'C':
					nom_ens1 = 'Pr '+teacher1[0]
				if teacher1[1][0] == 'A' or teacher1[1][0] == 'S':
					nom_ens1 = 'Dr '+teacher1[0]
				if teacher1[1][0] == 'V':
					nom_ens1 = 'M. '+teacher1[0]

				# on recupere l'enseignant2
				if not i[1] == None:
					query = """select full_name, degree from core_teacher where id = %s"""
					cursor.execute(query, (i[1],))
					teacher2 = cursor.fetchall()[0]
					if teacher2[1][0] == 'P' or teacher2[1][0] == 'c' or teacher2[1][0] == 'C':
						nom_ens2 = 'Pr '+teacher2[0]
					if teacher2[1][0] == 'A' or teacher2[1][0] == 'S':
						nom_ens2 = 'Dr '+teacher2[0]
					if teacher1[1][0] == 'V':
						nom_ens2 = 'M. '+teacher2[0]
				else:
					nom_ens2 = ""

				# on recupere le cours 
				query = """select code_ue from core_courses where id = %s"""
				cursor.execute(query, (i[2],))
				course = cursor.fetchall()[0][0]
				course = str(course)

				# on recupere la salle
				query = """select nom_salle from core_salle where id = %s"""
				cursor.execute(query, (i[3],))
				salle = cursor.fetchall()[0][0]
				salle = str(salle)
				
				globals()['emploi%s' % i[-1]] = Emploi() 
				globals()['emploi%s' % i[-1]].nom_ens1 = nom_ens1
				globals()['emploi%s' % i[-1]].nom_ens2 = nom_ens2
				globals()['emploi%s' % i[-1]].cours = course
				globals()['emploi%s' % i[-1]].salle = salle

				# formation du context 
				context['emploi%s' % i[-1]] = globals()['emploi%s' % i[-1]]


			context['classe'] = classe
			template = get_template('core/generator_classe.html')
			html = template.render(context)
			options = {
				'page-size':'Letter',
				'encoding':'UTF-8',
			}
			pdf = pdfkit.from_string(html, False, options)

			reponse = HttpResponse(pdf, content_type='application/pdf')
			reponse['Content-Disposition']="attachement"
			return reponse


class SchedulerPlannView(TemplateView):

	template_name = 'core/scheduler_plann.html'	

	def get(self, request, *args, **kwargs):
		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')
		filieres = list(set([classe.filiere for classe in Classe.objects.all()]))
		list_classes = []
		filieres = sorted(filieres)
		print(filieres)
		for filiere in filieres:
			instance = ListClasses()
			instance.filiere = filiere
			instance.classes = Classe.objects.filter(filiere = filiere)
			for classe in instance.classes:
				if classe.groupe != "":
					classe.groupe = "Group "+str(classe.groupe)+""
				if classe.specialite != None: # juste pour l'affichage
					s = Specialite()
					s.nom_specialite = "/ "+str(classe.specialite)+""
					classe.specialite = s
				else: # ici je veux juste preciser que pour les niveaux 3 et 4 dont la specialité n'est pas precisee qu'en fait cest tronc commun
					if classe.niveau == 'L3' or classe.niveau == 'M1':
						s = Specialite()
						s.nom_specialite = "(tronc commun)"
						classe.specialite = s

			list_classes.append(instance)
		print(list_classes[0].classes)

		return render(request, self.template_name, {'admin':admin, 'online':online, 'list_classes':list_classes})

# enregistrement d'un ensemble d'enseignants
class UploadTeachersView(View):

	template_name = 'core/list_teachers.html'

	def post(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		file = request.POST['file']
		form = TeachersFileForm()
		with open(file, "r") as fic:
			for line in fic.readlines():
				instance = line.split(",")
				print(instance, "instance")
				form.save(instance)
		return redirect('list/teachers')


# enregistrement d'un ensemble de classes
class UploadClassesView(View):

	template_name = 'core/list_classes.html'

	def post(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		file = request.POST['file']
		form = ClassesFileForm()
		with open(file, "r") as fic:
			for line in fic.readlines():
				instance = line.split(",")
				print(instance, "instance")
				form.save(instance)
		return redirect('list/classes')

# enregistrement d'un ensemble de salles
class UploadSallesView(View):

	template_name = 'core/list_salles.html'

	def post(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		file = request.POST['file']
		form = SallesFileForm()
		with open(file, "r") as fic:
			for line in fic.readlines():
				instance = line.split(",")
				print(instance, "instance")
				form.save(instance)
		return redirect('list/salles')

# enregistrement d'un ensemble de cours
class UploadCoursesView(View):

	template_name = 'core/list_classes.html'

	def post(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		file = request.POST['file']
		form = CoursesFileForm()
		with open(file, "r") as fic:
			for line in fic.readlines():
				instance = line.split(",")
				print(instance, "instance")
				form.save(instance)
		return redirect('list/classes')


#recherche d'une salle particuliere
class SearchSallesView(View):

	def post(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		searched = request.POST['searched']
		salles = Salle.objects.filter(Q(nom_salle__icontains=searched) | Q(type__icontains=searched) )
		number  = len(salles) 
		context = {'searched':searched, 'salles': salles, 'number': number, "admin":admin, "online":online}
		return render(request, "core/searchsalles.html", context)

#recherche d'un enseignant particulier
class SearchTeachersView(View):

	def post(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		searched = request.POST['searched']
		# je recupere tous les enseignants qui respectent la condition
		all_teachers = Teacher.objects.filter(Q(full_name__icontains=searched) | Q(department__icontains=searched) )
		departments = list(set([teacher.department for teacher in all_teachers]))
		list_teachers = []
		departments = sorted(departments)
		for department in departments:
			instance = ListEnseignant()
			instance.department = department
			# pour prendre ceux qui corresponent a la recherche et qui sont du departement actuel
			not_in = Teacher.objects.filter(department = department).intersection(all_teachers)
			instance.teachers = not_in
			list_teachers.append(instance)
		number  = len(list_teachers) 	
		context = {'searched':searched, 'list_teachers': list_teachers, 'number': number, "admin":admin, "online":online}
		return render(request, "core/searchteachers.html", context)



#recherche d'une classe particuliere
class SearchClassesView(View):

	def post(self, request, *args, **kwargs):

		admin, online = False, False
		if request.user.is_authenticated :
			if Admin.objects.filter(user = request.user).exists():
				admin = True
				online = True
			print('')

		searched = request.POST['searched']
		all_correspondances = Classe.objects.filter(Q(filiere__icontains=searched) | Q(niveau__icontains=searched))
		print(all_correspondances, "all")
		filieres = list(set([classe.complete_name_filiere for classe in all_correspondances]))
		list_classes = []
		filieres = sorted(filieres)
		print(filieres)
		for filiere in filieres:
			instance = ListClasses()
			instance.filiere = filiere
			instance.classes = Classe.objects.filter(complete_name_filiere = filiere)
			for classe in instance.classes:
				if classe.groupe != None and classe.groupe != "" :
					classe.groupe = "Group "+str(classe.groupe)+""
				else:
					classe.groupe = ""

				if classe.specialite != None: # juste pour l'affichage
					s = Specialite()
					s.nom_specialite = "/ "+str(classe.specialite)+""
					classe.specialite = s
				else: # ici je veux juste preciser que pour les niveaux 3 et 4 dont la specialité n'est pas precisee qu'en fait cest tronc commun
					if classe.niveau == 'L3' or classe.niveau == 'M1':
						s = Specialite()
						s.nom_specialite = "(tronc commun)"
						classe.specialite = s

			list_classes.append(instance)
			print(list_classes[0],"popo")
		
		number  = len(list_classes) 
		context = {'searched':searched, 'list_classes': list_classes, 'number': number, "admin":admin, "online":online}
		return render(request, "core/searchclasses.html", context)

