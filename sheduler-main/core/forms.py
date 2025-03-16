from re import fullmatch
from threading import main_thread
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.deletion import RestrictedError
from django.db import connection
import os

from .models import (Salle, Teacher, Classe, Courses, Plages, Specialite)
from django.forms import Form, ValidationError



# for authentification of admin
class MyAuthentificationForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField()
	msg_error = ""


# pour creer un nouvele enseignant
class TeachersForm(forms.Form):

	matricule = forms.CharField()
	full_name = forms.CharField()
	email = forms.EmailField()
	degree = forms.CharField()
	department = forms.CharField()
	pp = forms.ImageField(required = False)

	def clean_matricule(self):
		
		matricule = self.data["matricule"]
		if Teacher.objects.filter(matricule=matricule).exists():
			raise forms.ValidationError("Matricule already exists")
		if '@' in matricule:
			raise forms.ValidationError('Matricule must not contain the @ character')
		if ' ' in matricule:
			raise forms.ValidationError('Matricule must not contain spaces')
		return matricule

	def clean_email(self):
		
		email = self.data['email']
		if Teacher.objects.filter(email=email).exists():
			raise forms.ValidationError("Email address already exists")
		return email

	def save(self):
		
		matricule = self.cleaned_data["matricule"]
		print(type(matricule))
		email = self.cleaned_data["email"]
		full_name = self.cleaned_data['full_name']
		degree = self.cleaned_data["degree"]
		department = self.cleaned_data["department"]
		pp = self.cleaned_data['pp']

		if pp == None:
			pp = 'teachers/profil_gris.png'

		with connection.cursor() as cursor:

			"""
			#requéte SQL
			sql = "INSERT INTO core_teacher (matricule, email, full_name, degree, department, pp)\
					VALUES( %s, %s, %s, %s, %s, %s)"

			#les valeurs de la requéte SQL
			value = (matricule, email, full_name, degree, department, pp)

			#exécuter le curseur avec la méthode execute() et transmis la requéte SQL
			return cursor.execute(sql, value)
			"""
			return Teacher.objects.create(matricule = matricule, department = department,
					email = email, full_name=full_name, degree = degree, pp = pp)


# pour creer une salle de classe
class SallesForm(forms.Form):

	nom_salle = forms.CharField()
	type = forms.CharField()
	capacity = forms.CharField()

	def clean_nom_salle(self):
		
		nom_salle = self.data["nom_salle"]
		if Salle.objects.filter(nom_salle=nom_salle).exists():
			raise forms.ValidationError("This name of classroom already exists.")
		return nom_salle

	def clean_capacity(self):
		
		capacity = self.data['capacity']
		if int(capacity) <= 0:
			raise forms.ValidationError("Enter a valid capacity")
		return capacity

	def save(self):
		
		nom_salle = self.cleaned_data["nom_salle"]
		type = self.cleaned_data["type"]
		capacity = self.cleaned_data['capacity']

		with connection.cursor() as cursor:

			"""
			#requéte SQL
			sql = "INSERT INTO core_salle (nom_salle, type, capacity)\
					VALUES( %s, %s, %s)"

			#les valeurs de la requéte SQL
			value = (nom_salle, type, capacity)

			#exécuter le curseur avec la méthode execute() et transmis la requéte SQL
			return cursor.execute(sql, value)"""
			return Salle.objects.create(nom_salle = nom_salle, type = type, capacity = capacity)


# pour creer un cours
class CoursesForm(forms.Form):

	code_ue = forms.CharField()
	libele = forms.CharField()
	credit = forms.IntegerField()
	classe = forms.CharField()

	def clean_code_ue(self):
		
		code_ue = self.data['code_ue']
		if Courses.objects.filter(code_ue=code_ue).exists():
			raise forms.ValidationError("Code_ue already in use...")
		return code_ue

	def save(self):
		
		code_ue = self.cleaned_data["code_ue"]
		libele = self.cleaned_data["libele"]
		credit = self.cleaned_data['credit']
		classe = self.cleaned_data["classe"]

		with connection.cursor() as cursor:

			cursor = connection.cursor()

			classe = classe.split(' - ') # classe
			"""print("list_classe", classe)
				query = ///select * from core_specialite where nom_specialite = %s///
				# set variable in query
				cursor.execute(query, (classe[2],))
				# fetch result
				id_specialite = cursor.fetchall()[0][0] # pour ne prendre que l'id de la specialite
				print("specialite", id_specialite)
			"""
			if len(classe) == 4 : # si la classe a la specialite et le groupe je la recupere en me servant des 04 attributs
				
				# je recupere donc d'abord la specialite, son id quoi !!
				query = """select * from core_specialite where nom_specialite = %s """
				# set variable in query
				cursor.execute(query, (classe[2],))
				id_speciality = cursor.fetchall()[0][0] # pour ne prendre que l'id de la classe

				query = """select * from core_classe where filiere = %s and niveau = %s and specialite_id = %s and groupe = %s """
				# set variable in query
				cursor.execute(query, (classe[0], classe[1], id_speciality, classe[3]))
			elif len(classe) == 2 : # si la clsse n'a que la filiere et le niveau
				query = """select * from core_classe where filiere = %s and niveau = %s"""
				# set variable in query
				cursor.execute(query, (classe[0], classe[1]))
			else : 
				if classe[2] == 'A' or classe[2] == 'B' or classe[2] == 'C' or classe[2] == 'D' or classe[2] == 'E' : # si la classe est filiere niveau et groupe
					query = """select * from core_classe where filiere = %s and niveau = %s and groupe = %s"""
					# set variable in query
					cursor.execute(query, (classe[0], classe[1], classe[2]))
				else:	# si la classe est filiere niveau et specialite
					# je recupere donc d'abord la specialite, son id quoi !!
					query = """select * from core_specialite where nom_specialite = %s """
					# set variable in query
					cursor.execute(query, (classe[2],))
					id_speciality = cursor.fetchall()[0][0] # pour ne prendre que l'id de la classe

					query = """select * from core_classe where filiere = %s and niveau = %s and specialite_id = %s"""
					# set variable in query
					cursor.execute(query, (classe[0], classe[1], id_speciality))
			# fetch result
			id_class = cursor.fetchall()[0][0] # pour ne prendre que l'id de la classe
			print("class", id_class)	

			#requéte SQL
			sql = "INSERT INTO core_courses (code_ue, libele, credit, classe_id)\
					VALUES( %s, %s, %s, %s)"

			#les valeurs de la requéte SQL
			value = (code_ue, libele, credit, id_class)

			#exécuter le curseur avec la méthode execute() et transmis la requéte SQL
			return cursor.execute(sql, value)


# pour programmer un cours methode classique
class SchedulerForm(forms.Form):

	course = forms.CharField()
	salle = forms.CharField()
	teacher1 = forms.CharField()
	teacher2 = forms.CharField(required=False)
	plage = forms.CharField()
	is_td= forms.BooleanField(required = False)

	def clean_teacher1(self):

		teacher1 = self.data['teacher1']
		plage = self.data['plage']

		with connection.cursor() as cursor:

			teacher = teacher1.split(' - ') # first enseignant
			query = """select id from core_teacher where degree = %s and full_name = %s and department = %s"""
			# set variable in query
			cursor.execute(query, (teacher[0], teacher[1], teacher[2]))
			# fetch result
			self.id_teacher1 = cursor.fetchall()[0][0] # pour ne prendre que l'id de l'enseignant 1

			plage = plage.split(' - ') # pour la plage
			start_hour = plage[0].split(' : ')[1]
			day = plage[0].split(' : ')[0]
			end_hour = plage[1]
			print(day, start_hour, end_hour)
			query = """select * from core_plages where start_hour = %s and end_hour = %s and day = %s"""
			# set variable in query
			cursor.execute(query, (start_hour, end_hour, day))
			# fetch result
			self.id_plage = cursor.fetchall()[0][0] # pour ne prendre que l'id de la plage
			print("first", self.id_plage)

			query = """select teacher1_id, plage_id from core_schedulers"""
			query2 = """select teacher2_id, plage_id from core_schedulers""" # pour m'assurer aussi que l'enseignant 1 la n'est meem pas encore pris comme enseignant 2 dans cette plage
			# set variable in query
			cursor.execute(query)
			also_exist = cursor.fetchall()
			if (self.id_teacher1, self.id_plage) in also_exist:
				raise forms.ValidationError("This teacher is already scheduled for another course at this time")
			cursor.execute(query2)
			also_exist = cursor.fetchall()
			if (self.id_teacher1, self.id_plage) in also_exist:
				raise forms.ValidationError("This teacher is already scheduled for another course at this time")
		return teacher1

	def clean_course(self):

		course = self.data['course']
		plage = self.data['plage']

		with connection.cursor() as cursor:

			plage = plage.split(' - ') # pour la plage
			start_hour = plage[0].split(' : ')[1]
			day = plage[0].split(' : ')[0]
			end_hour = plage[1]
			print(day, start_hour, end_hour)
			query = """select * from core_plages where start_hour = %s and end_hour = %s and day = %s"""
			# set variable in query
			cursor.execute(query, (start_hour, end_hour, day))
			# fetch result
			self.id_plage = cursor.fetchall()[0][0] # pour ne prendre que l'id de la plage
			print("first", self.id_plage)

			# pour verifier si le cours est deja programmé
			course = course.split(' (') # course
			print("code_ue", course[0]) # j'accede direct a l'ue code

			query = """select id from core_courses where code_ue = %s """
			# set variable in query
			cursor.execute(query, (course[0],))
			# fetch result
			self.id_course = cursor.fetchall()[0][0] # pour ne prendre que l'id du cours en question
			print("id_course", self.id_course)
			print(cursor.fetchall(), "cursoooooooooooooor")

			query = """select course_id, plage_id from core_schedulers"""
			# set variable in query
			cursor.execute(query)
			also_exist = cursor.fetchall()
			if (self.id_course, self.id_plage) in also_exist:
				raise forms.ValidationError("This course is already scheduled in this time slot")

			# pour verifier si la classe a deja un cours programmé à cette heure la

			# je recupere d'abord l'id de la classe concernee par le cours que l'on est entain de vouloir programmer
			query = """select classe_id from core_courses where id = %s """
			# set variable in query
			cursor.execute(query, (self.id_course,))
			# fetch result
			self.id_classe = cursor.fetchall()[0][0] # j'ai ici l'id de la classe 
			print("id_classe", self.id_classe)

			# je recupere tous les cours qui passent a cette plage horaire; pour recuperer leurs classes et comparer à celle du cours que l'on veut nouvellement programmer
			query = """select course_id from core_schedulers where plage_id = %s""" 
			# set variable in query
			cursor.execute(query, (self.id_plage,))
			courses_plage = [i[0] for i in cursor.fetchall()]
			for course in courses_plage:
				# je recupere les id des classes concernee par le cours
				query = """select classe_id from core_courses where id = %s""" 
				# set variable in query
				cursor.execute(query, (course,))
				id_classe = cursor.fetchall()[0][0]
				if id_classe == self.id_classe: # si la classe du cours que l'on veut programmer a deja un cours a cette heure
					raise forms.ValidationError("The class involved in this course already has a class scheduled at this time slot.")
		return course

	def clean_teacher2(self):

		teacher2 = self.data['teacher2']
		plage = self.data['plage']

		with connection.cursor() as cursor:

			if not teacher2 == "": # pour le deuxieme enseignant
				teacher = teacher2.split(' - ') # first enseignant
				query = """select id from core_teacher where degree = %s and full_name = %s and department = %s"""
				# set variable in query
				cursor.execute(query, (teacher[0], teacher[1], teacher[2]))
				# fetch result
				self.id_teacher2 = cursor.fetchall()[0][0] # pour ne prendre que l'id de l'enseignant 1
			else:
				self.id_teacher2 = None

			plage = plage.split(' - ') # pour la plage
			start_hour = plage[0].split(' : ')[1]
			day = plage[0].split(' : ')[0]
			end_hour = plage[1]
			print(day, start_hour, end_hour)
			query = """select * from core_plages where start_hour = %s and end_hour = %s and day = %s"""
			# set variable in query
			cursor.execute(query, (start_hour, end_hour, day))
			# fetch result
			self.id_plage = cursor.fetchall()[0][0] # pour ne prendre que l'id de la plage
			print("first", self.id_plage)

			query = """select teacher1_id, plage_id from core_schedulers"""
			query2 = """select teacher2_id, plage_id from core_schedulers""" # pour m'assurer aussi que l'enseignant 1 la n'est meem pas encore pris comme enseignant 2 dans cette plage
			# set variable in query
			cursor.execute(query)
			also_exist = cursor.fetchall()
			#if (self.id_teacher2, self.id_plage) in also_exist and self.id_teacher2 != None: # je verifie s'il est deja pri comme enseignant 2 ou enseignant 1
			#	raise forms.ValidationError("This teacher is already scheduled for another course at this time")
			cursor.execute(query2)
			also_exist = cursor.fetchall()
			#if (self.id_teacher2, self.id_plage) in also_exist and self.id_teacher2 != None: # je verifie s'il est deja pri comme enseignant 2 ou enseignant 1
			#	raise forms.ValidationError("This teacher is already scheduled for another course at this time")
		return teacher2		

	def clean_salle(self):

		salle = self.data['salle']
		plage = self.data['plage']
		print("nom_salle", salle)

		with connection.cursor() as cursor:

			query = """select * from core_salle where nom_salle = %s """
			# set variable in query
			cursor.execute(query, (salle,))
			# fetch result
			self.id_salle= cursor.fetchall()[0][0] # pour ne prendre que l'id de la salle
			print("id_salle", self.id_salle)

			plage = plage.split(' - ') # pour la plage
			start_hour = plage[0].split(' : ')[1]
			day = plage[0].split(' : ')[0]
			end_hour = plage[1]
			print(day, start_hour, end_hour)
			query = """select * from core_plages where start_hour = %s and end_hour = %s and day = %s"""
			# set variable in query
			cursor.execute(query, (start_hour, end_hour, day))
			# fetch result
			self.id_plage = cursor.fetchall()[0][0] # pour ne prendre que l'id de la plage
			print("first", self.id_plage)

			query = """select salle_id, plage_id from core_schedulers"""
			# set variable in query
			cursor.execute(query)
			also_exist = cursor.fetchall()
			if (self.id_salle, self.id_plage) in also_exist:
				raise forms.ValidationError("Another course already scheduled in this classroom")


	def save(self):
		
		course = self.cleaned_data["course"]
		salle = self.cleaned_data["salle"]
		teacher1 = self.cleaned_data['teacher1']
		teacher2 = self.cleaned_data["teacher2"]
		plage = self.cleaned_data["plage"]
		is_td = self.cleaned_data["is_td"]

		
		with connection.cursor() as cursor:

			cursor = connection.cursor()

			#requéte SQL
			sql = "INSERT INTO core_schedulers (is_td, course_id, plage_id, salle_id, teacher1_id, teacher2_id)\
					VALUES( %s, %s, %s, %s, %s, %s)"

			#les valeurs de la requéte SQL
			value = (is_td, self.id_course, self.id_plage, self.id_salle, self.id_teacher1, self.id_teacher2)

			#exécuter le curseur avec la méthode execute() et transmis la requéte SQL
			cursor.execute(sql, value)

			# je recupere la salle, que je vais retourner
			query = """select classe_id from core_courses where id = %s"""
			# set variable in query
			cursor.execute(query, (self.id_course,))
			return cursor.fetchall()[0][0]



# pour programmer un cours methode tokooos
class SchedulerTableForm(forms.Form):

	course = forms.CharField()
	salle = forms.CharField()
	teacher1 = forms.CharField()
	teacher2 = forms.CharField()
	plage = forms.CharField()
	is_td= forms.BooleanField(required = False)

	def clean_teacher1(self):

		teacher1 = self.data['teacher1']
		plage = self.data['plage']
		print(plage, "lllll")

		with connection.cursor() as cursor:

			teacher = teacher1.split(' - ') # first enseignant
			query = """select id from core_teacher where degree = %s and full_name = %s and department = %s"""
			# set variable in query
			cursor.execute(query, (teacher[0], teacher[1], teacher[2]))
			# fetch result
			self.id_teacher1 = cursor.fetchall()[0][0] # pour ne prendre que l'id de l'enseignant 1

			self.id_plage = int(plage) # j'ai deja l'id de la plage en question

			query = """select teacher1_id, plage_id from core_schedulers"""
			query2 = """select teacher2_id, plage_id from core_schedulers""" # pour m'assurer aussi que l'enseignant 1 la n'est meem pas encore pris comme enseignant 2 dans cette plage
			# set variable in query
			cursor.execute(query)
			also_exist = cursor.fetchall()
			if (self.id_teacher1, self.id_plage) in also_exist:
				raise forms.ValidationError("This teacher is already scheduled for another course at this time")
			cursor.execute(query2)
			also_exist = cursor.fetchall()
			if (self.id_teacher1, self.id_plage) in also_exist:
				raise forms.ValidationError("This teacher is already scheduled for another course at this time")
		return teacher1

	def clean_teacher2(self):

		teacher2 = self.data['teacher2']
		plage = self.data['plage']

		with connection.cursor() as cursor:

			if not teacher2 == "": # pour le deuxieme enseignant
				teacher = teacher2.split(' - ') # first enseignant
				query = """select id from core_teacher where degree = %s and full_name = %s and department = %s"""
				# set variable in query
				#cursor.execute(query, (teacher[0], teacher[1], teacher[2]))
				# fetch result
				#print(Teacher.objects.filter(degree = teacher[1]), "mkmkmkmkmkkall")
				#self.id_teacher2 = cursor.fetchall()[0][0] # pour ne prendre que l'id de l'enseignant 1
				self.id_teacher2 = Teacher.objects.filter(degree = teacher[0]).filter(full_name = teacher[1]).filter(department = teacher[2])[0].id
			else:
				self.id_teacher2 = None

			self.id_plage = int(plage)

			query = """select teacher1_id, plage_id from core_schedulers"""
			query2 = """select teacher2_id, plage_id from core_schedulers""" # pour m'assurer aussi que l'enseignant 1 la n'est meem pas encore pris comme enseignant 2 dans cette plage
			# set variable in query
			cursor.execute(query)
			also_exist = cursor.fetchall()
			#if (self.id_teacher2, self.id_plage) in also_exist: # je verifie s'il est deja pri comme enseignant 2 ou enseignant 1
			#	raise forms.ValidationError("This teacher is already scheduled for another course at this time")
			cursor.execute(query2)
			also_exist = cursor.fetchall()
			#if (self.id_teacher2, self.id_plage) in also_exist: # je verifie s'il est deja pri comme enseignant 2 ou enseignant 1
			#	raise forms.ValidationError("This teacher is already scheduled for another course at this time")
		return teacher2
			
	def clean_course(self):

		course = self.data['course']
		plage = self.data['plage']
		print(plage, "lllll")

		with connection.cursor() as cursor:

			print(type(plage), plage, 'renseignes moi')
			self.id_plage = int(plage)

			# pour verifier si le cours est deja programmé
			course = course.split(' (') # course
			print("code_ue", course[0]) # j'accede direct a l'ue code

			query = """select id from core_courses where code_ue = %s """
			# set variable in query
			cursor.execute(query, (course[0],))
			# fetch result
			self.id_course = cursor.fetchall()[0][0] # pour ne prendre que l'id du cours en question
			print("id_course", self.id_course)
			print(cursor.fetchall(), "cursoooooooooooooor")

			query = """select course_id, plage_id from core_schedulers"""
			# set variable in query
			cursor.execute(query)
			also_exist = cursor.fetchall()
			if (self.id_course, self.id_plage) in also_exist:
				raise forms.ValidationError("This course is already scheduled in this time slot")

			# pour verifier si la classe a deja un cours programmé à cette heure la

			# je recupere d'abord l'id de la classe concernee par le cours que l'on est entain de vouloir programmer
			query = """select classe_id from core_courses where id = %s """
			# set variable in query
			cursor.execute(query, (self.id_course,))
			# fetch result
			self.id_classe = cursor.fetchall()[0][0] # j'ai ici l'id de la classe 
			print("id_classe", self.id_classe)

			# je recupere tous les cours qui passent a cette plage horaire; pour recuperer leurs classes et comparer à celle du cours que l'on veut nouvellement programmer
			query = """select course_id from core_schedulers where plage_id = %s""" 
			# set variable in query
			cursor.execute(query, (self.id_plage,))
			courses_plage = [i[0] for i in cursor.fetchall()]
			for course in courses_plage:
				# je recupere les id des classes concernee par le cours
				query = """select classe_id from core_courses where id = %s""" 
				# set variable in query
				cursor.execute(query, (course,))
				id_classe = cursor.fetchall()[0][0]
				if id_classe == self.id_classe: # si la classe du cours que l'on veut programmer a deja un cours a cette heure
					raise forms.ValidationError("The class involved in this course already has a class scheduled at this time slot.")
		return course


	
	def clean_salle(self):

		salle = self.data['salle']
		plage = self.data['plage']
		print("nom_salle", salle)

		with connection.cursor() as cursor:

			query = """select * from core_salle where nom_salle = %s """
			# set variable in query
			cursor.execute(query, (salle,))
			# fetch result
			self.id_salle= cursor.fetchall()[0][0] # pour ne prendre que l'id de la salle
			print("id_salle", self.id_salle)

			self.id_plage = int(plage)

			query = """select salle_id, plage_id from core_schedulers"""
			# set variable in query
			cursor.execute(query)
			also_exist = cursor.fetchall()
			if (self.id_salle, self.id_plage) in also_exist:
				raise forms.ValidationError("Another course already scheduled in this classroom")


	def save(self):

		
		with connection.cursor() as cursor:

			cursor = connection.cursor()

			#requéte SQL
			sql = "INSERT INTO core_schedulers (is_td, course_id, plage_id, salle_id, teacher1_id, teacher2_id)\
					VALUES( %s, %s, %s, %s, %s, %s)"

			#les valeurs de la requéte SQL
			value = (self.cleaned_data['is_td'], self.id_course, self.id_plage, self.id_salle, self.id_teacher1, self.id_teacher2)

			#exécuter le curseur avec la méthode execute() et transmis la requéte SQL
			return cursor.execute(sql, value)


# pour creer une classe
class ClassesForm(forms.Form):

	filiere = forms.CharField()
	niveau = forms.CharField()
	groupe = forms.CharField(required = False)
	effectif = forms.CharField()
	specialite = forms.CharField(required = False)

	def clean_effectif(self):
		
		effectif = self.data['effectif']
		if int(effectif) <= 0:
			raise forms.ValidationError("Enter a valid class size")
		return effectif

	def save(self):
		
		filiere = self.cleaned_data["filiere"]
		niveau = self.cleaned_data["niveau"]
		groupe = self.cleaned_data['groupe']
		effectif = self.cleaned_data["effectif"]
		nom_specialite = self.cleaned_data["specialite"]

		with connection.cursor() as cursor:

			# creation de la row specialite
			# si la specialite entree n'existait pas encore, je la cree d'abord
			if not Specialite.objects.filter(nom_specialite = nom_specialite).exists() and nom_specialite != "":

				#requéte SQL
				sql = """INSERT INTO core_specialite (nom_specialite)
					VALUES( %s )"""

				#les valeurs de la requéte SQL
				value = (nom_specialite,)

				#exécuter le curseur avec la méthode execute() et transmettre la requéte SQL
				cursor.execute(sql, value)

			# creation de la row classe

			#requéte SQL
			# je recupere d'abord l'id de la specialite que je viens de creer
			print(type(nom_specialite))
			if not nom_specialite == "":
				cursor = connection.cursor()
				query = """select * from core_specialite where nom_specialite = %s"""
				# set variable in query
				cursor.execute(query, (nom_specialite,))
				# fetch result
				id_specialite = cursor.fetchall()[0][0] # pour ne prendre que l'id de la specialite
			else:
				id_specialite = None

			"""		
			# maintenant je cree la classe en question
			sql = "INSERT INTO core_classe (filiere, niveau, groupe, effectif, specialite_id)\
					VALUES( %s, %s, %s, %s, %s)"

			#les valeurs de la requéte SQL
			value = (filiere, niveau, groupe, effectif, id_specialite)

			#exécuter le curseur avec la méthode execute() et transmettre la requéte SQL
			return cursor.execute(sql, value)
			"""
			return Classe.objects.create(filiere = filiere, niveau = niveau, 
					groupe = groupe, effectif = effectif, specialite_id = id_specialite)


# pour creer un ensemble d'enseignant, avec le fichier
class TeachersFileForm(forms.Form):

	def save(self, objects):
		
		full_name = objects[0]
		email = objects[1]
		degree = objects[2]
		department = objects[3]
		pp = objects[4]
		
		if pp == None or pp == "":
			pp = 'teachers/profil_gris.png'

		return Teacher.objects.create(department = department,
					email = email, full_name=full_name, degree = degree, pp = pp)


# pour creer un ensemble de salles, avec le fichier
class SallesFileForm(forms.Form):

	def save(self, objects):
		
		nom_salle = objects[0]
		type = objects[1]
		capacity = objects[2]

		return Salle.objects.create(nom_salle = nom_salle, type = type, capacity = capacity)


# pour creer un ensemble de classes, avec le fichier
class ClassesFileForm(forms.Form):

	def save(self, objects):
		
		filiere = objects[0]
		niveau = objects[1]
		groupe = objects[2]
		effectif = objects[3]
		nom_specialite = objects[4]

		with connection.cursor() as cursor:
			# si la specialite entree n'existait pas encore, je la cree d'abord
			if not Specialite.objects.filter(nom_specialite = nom_specialite).exists() and nom_specialite != "":

				#requéte SQL
				sql = """INSERT INTO core_specialite (nom_specialite)
					VALUES( %s )"""

				#les valeurs de la requéte SQL
				value = (nom_specialite,)

				#exécuter le curseur avec la méthode execute() et transmettre la requéte SQL
				cursor.execute(sql, value)

			# creation de la row classe

			#requéte SQL
			# je recupere d'abord l'id de la specialite que je viens de creer
			print(type(nom_specialite))
			if not nom_specialite == "":
				cursor = connection.cursor()
				query = """select * from core_specialite where nom_specialite = %s"""
				# set variable in query
				cursor.execute(query, (nom_specialite,))
				# fetch result
				id_specialite = cursor.fetchall()[0][0] # pour ne prendre que l'id de la specialite
			else:
				id_specialite = None
		
			return Classe.objects.create(filiere = filiere, niveau = niveau,
						groupe = groupe, effectif=effectif, specialite_id = id_specialite)



class CoursesFileForm(forms.Form):

	def save(self, objects):

		code_ue = objects[0]
		libele = objects[1]
		classe = objects[2]

		with connection.cursor() as cursor:

			cursor = connection.cursor()

			classe = classe.split('-') # classe
			"""print("list_classe", classe)
				query = ///select * from core_specialite where nom_specialite = %s///
				# set variable in query
				cursor.execute(query, (classe[2],))
				# fetch result
				id_specialite = cursor.fetchall()[0][0] # pour ne prendre que l'id de la specialite
				print("specialite", id_specialite)
			"""
			if len(classe) == 4 : # si la classe a la specialite et le groupe je la recupere en me servant des 04 attributs
				
				# je recupere donc d'abord la specialite, son id quoi !!
				query = """select * from core_specialite where nom_specialite = %s """
				# set variable in query
				cursor.execute(query, (classe[2],))
				id_speciality = cursor.fetchall()[0][0] # pour ne prendre que l'id de la classe

				query = """select * from core_classe where filiere = %s and niveau = %s and specialite_id = %s and groupe = %s """
				# set variable in query
				cursor.execute(query, (classe[0], classe[1], id_speciality, classe[3]))
			elif len(classe) == 2 : # si la clsse n'a que la filiere et le niveau
				query = """select * from core_classe where filiere = %s and niveau = %s"""
				# set variable in query
				cursor.execute(query, (classe[0], classe[1]))
			else : 
				if classe[2] == 'A' or classe[2] == 'B' or classe[2] == 'C' or classe[2] == 'D' or classe[2] == 'E' : # si la classe est filiere niveau et groupe
					query = """select * from core_classe where filiere = %s and niveau = %s and groupe = %s"""
					# set variable in query
					cursor.execute(query, (classe[0], classe[1], classe[2]))
				else:	# si la classe est filiere niveau et specialite
					# je recupere donc d'abord la specialite, son id quoi !!
					query = """select * from core_specialite where nom_specialite = %s """
					# set variable in query
					cursor.execute(query, (classe[2],))
					id_speciality = cursor.fetchall()[0][0] # pour ne prendre que l'id de la classe

					query = """select * from core_classe where filiere = %s and niveau = %s and specialite_id = %s"""
					# set variable in query
					cursor.execute(query, (classe[0], classe[1], id_speciality))
			# fetch result
			id_class = cursor.fetchall()[0][0] # pour ne prendre que l'id de la classe
			print("class", id_class)	

			#requéte SQL
			sql = "INSERT INTO core_courses (code_ue, libele, classe_id)\
					VALUES( %s, %s, %s)"

			#les valeurs de la requéte SQL
			value = (code_ue, libele, id_class)

			#exécuter le curseur avec la méthode execute() et transmis la requéte SQL
			return cursor.execute(sql, value)

"""
class SpecialiteForm(forms.Form):

	nom_specialite = forms.CharField()

	def clean_nom_specialite(self):
		
		nom_specialite = self.data["nom_specialite"]
		if Salle.objects.filter(nom_specialite=nom_specialite).exists():
			raise forms.ValidationError("This name of speciaity already exists.")
		return nom_specialite

	def save(self):
		
		nom_specialite = self.cleaned_data["nom_specialite"]

		with connection.cursor() as cursor:

			#requéte SQL
			sql = "INSERT INTO core_specialite (nom_specialite)\
					VALUES( %s)"

			#les valeurs de la requéte SQL
			value = (nom_specialite)

			#exécuter le curseur avec la méthode execute() et transmis la requéte SQL
			return cursor.execute(sql, value)
"""


		
