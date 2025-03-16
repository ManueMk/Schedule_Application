from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.template.defaultfilters import slugify


def create_slug_salles(nom_salle, type): # new
	slug_chaine = str(type) + "-" + str(nom_salle)
	slug = slugify(slug_chaine)
	qs = Salle.objects.filter(slug=slug)
	exists = qs.exists()
	if exists:
		slug = "%s-%s" %(slug, qs.first().id)
	return slug

def create_slug_classes(filiere, niveau, specialite, groupe): # new
	if specialite == None:
		specialite = ""
	if groupe == None:
		groupe = ""	
	slug_chaine = str(filiere) + "-" + str(niveau) + "-" + str(specialite) + "-" + str(groupe)
	slug = slugify(slug_chaine)
	qs = Classe.objects.filter(slug=slug)
	exists = qs.exists()
	if exists:
		slug = "%s-%s" %(slug, qs.first().id)
	return slug

def create_slug_teachers(full_name,degree): # new
	slug_chaine = str(degree) + "-" + str(full_name)
	slug = slugify(slug_chaine)
	qs = Teacher.objects.filter(slug=slug)
	exists = qs.exists()
	if exists:
		slug = "%s-%s" %(slug, qs.first().id)
	return slug



class Admin(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE)

	class Meta:
		verbose_name_plural = 'Administrators'

	def __str__(self):
		return "admin - " + self.user.username


class Teacher(models.Model):

	PROFFESSOR = "Professor"	
	SENIOR = "Senior lecturer"
	ASSISTANT = "Assistant Lecturer"
	VACCATAIRE = "Vaccataire"
	CONFERENCE = "Conference Lecturer"

	DEGREES = [
        (PROFFESSOR, "Professor"),
        (SENIOR, "Senior lecturer"),
        (ASSISTANT, "Assistant Lecturer"),
        (VACCATAIRE, "Vaccataire"),
        (CONFERENCE, "Conference Lecturer"),
    ]	 

	DEPARTEMENTS = [
		("Biology", "Biology"),
		("Chemistry", "Chemistry"),
		("Informatics", "Informatics"),
		("Mathematics", "Mathematics"),
		("Physics", "Physics"),
		("Geosciences", "Geosciences"),
		("Language", "Language")
    ]

	full_name = models.CharField(max_length=255)
	email = models.EmailField(max_length=255)
	degree = models.CharField(max_length = 100, choices = DEGREES)
	department = models.CharField(max_length = 100, choices = DEPARTEMENTS)
	pp = models.ImageField(upload_to='teachers', blank=True, null = True)
	slug = models.SlugField(null=True, blank=True, unique=True)

	class Meta:
	
		verbose_name_plural = 'Teachers'

	def __str__(self):
		return self.degree + " - " + self.full_name + " - " + self.department

	def save(self, *args, **kwargs):			
		if not self.slug:
			self.slug = create_slug_teachers(self.full_name, self.degree)
		return super().save(*args, **kwargs)


class Specialite(models.Model):

	SPECIALITES = [
		("GENIE LOGICIEL", "GENIE LOGICIEL"),
		("DATASCIENCES", "DATASCIENCES"),
		("SECURITE", "SECURITE"),
		("RESEAUX", "RESEAUX"),
		("PHYSIQUE FONDAMENTALE", "PHYSIQUE FONDAMENTALE"),
		("CHIMIE GENERALE", "CHIMIE GENERALE")
    ]

	nom_specialite = models.CharField(max_length = 100, choices = SPECIALITES)
	
	class Meta:
		verbose_name_plural = 'Specialites'

	def __str__(self):
		return self.nom_specialite


class Salle(models.Model):

	SALLES = [
		("A1001", "A1001"),
		("A1002", "A1002"),
		("A501", "A501"),
		("A502", "A502"),
		("A350", "A350"),
		("A250", "A250"),
		("E300", "E300")
    ]

	TYPES = [
		("Amphi", "Amphi"),
		("Classroom", "Classroom"),
		("Laboratory", "Laboratory"),
	]

	nom_salle = models.CharField(max_length = 100)
	type = models.CharField(max_length = 100, choices=TYPES)
	capacity = models.IntegerField()
	slug = models.SlugField(null=True, blank=True, unique=True)
	

	class Meta:
		verbose_name_plural = 'Salles'

	def __str__(self):
		return self.nom_salle

	def save(self, *args, **kwargs):			
		if not self.slug:
			self.slug = create_slug_salles(self.type, self.nom_salle)
		return super().save(*args, **kwargs)


class Classe(models.Model):

	GROUPES = [
		("A", "A"),
		("B", "B"),
		("C", "C"),
		("D", "D"),
		("E", "E"),
    ]	 
		
	FILIERES = [
		("Bios", "Bios"),
		("Chm", "Chm"),
		("Infos", "Infos"),
		("Maths", "Maths"),
		("phy", "phy"),
		("STU", "STU"),
		("Geos", "Geos")
    ]

	NIVEAUX = [
		("L1", "L1"),
		("L2", "L2"),
		("L3", "L3"),
		("M1", "M1"),
	]

	#dictionnaire pour avoir le nom complet d'une filiere
	NAME_FILIERES = {"Bios":"Biosciences", "Chm":"Chemistry", "Infos":"Informatics",
				"Maths":"Mathematics", "phy":"Physics", "STU":"STU"}

	filiere = models.CharField(max_length = 100, choices = FILIERES)
	complete_name_filiere = models.CharField(max_length = 100, default = "", null=True, blank=True)
	niveau = models.CharField(max_length = 100, choices = NIVEAUX)
	groupe = models.CharField(max_length = 100, choices = GROUPES, null=True, blank=True)
	effectif = models.IntegerField()
	specialite = models.ForeignKey(Specialite, on_delete=models.CASCADE, null=True, blank=True)
	slug = models.SlugField(null=True, blank=True, unique=True)

	class Meta:
		verbose_name_plural = 'Classes'

	def __str__(self):
		if (self.specialite == None or self.specialite == "") and (self.groupe == None or self.groupe == ""):
			return self.filiere + " - " + self.niveau 
		elif self.specialite != None:
			if (self.groupe == None or self.groupe == ""):
				return self.filiere + " - " + self.niveau + " - " + str(self.specialite)
			else:
				return self.filiere + " - " + self.niveau + " - " + str(self.specialite) + " - " + self.groupe
		elif self.groupe != None:
			if (self.specialite == None or self.specialite == ""):
				return self.filiere + " - " + self.niveau + " - " + self.groupe
			else:
				return self.filiere + " - " + self.niveau + " - " + str(self.specialite) + " - " + self.groupe

	def save(self, *args, **kwargs):
		self.complete_name_filiere = self.NAME_FILIERES[self.filiere]		
		if not self.slug:
			self.slug = create_slug_classes(self.filiere, self.niveau, self.specialite, self.groupe)
		return super().save(*args, **kwargs)



class Courses(models.Model):

	code_ue = models.CharField(max_length = 10)
	libele = models.CharField(max_length = 100)
	classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
	

	class Meta:
		verbose_name_plural = 'Courses'

	def __str__(self):
		return self.code_ue + ' (' + str(self.classe) + ')'


class Plages(models.Model):

	HF = [
		("10h05", "10h05"),
		("13h05", "13h05"),
		("16h05", "16h05"),
		("19h05", "19h05"),
		("21h55", "21h55") ]

	HD = [
		("07h00", "07h00"),
		("10h05", "10h05"),
		("13h05", "13h05"),
		("16h05", "16h05"),
		("19h05", "19h05") ]	 

	DAYS = [
		("Monday", "Monday"),
		("Tuesday", "Tuesday"),
		("Wednesday", "Wednesday"),
		("Thursday", "Thursday"),
		("Friday", "Friday"),
		("Saturday", "Saturday"),
		("Sunday", "Sunday") ]	 

	start_hour = models.CharField(max_length = 100, choices = HD)
	end_hour = models.CharField(max_length = 100, choices = HF)
	day = models.CharField(max_length = 100, choices = DAYS)

	class Meta:
		verbose_name_plural = 'Plages horaires'

	def __str__(self):
		return self.day + " : " + self.start_hour + " - " + self.end_hour 


class Schedulers(models.Model):

	course = models.ForeignKey(Courses, on_delete = models.CASCADE)
	salle = models.ForeignKey(Salle, on_delete = models.CASCADE)
	teacher1 = models.ForeignKey(Teacher, on_delete = models.CASCADE, related_name='teacher1')
	teacher2 = models.ForeignKey(Teacher, on_delete = models.CASCADE, null=True, blank=True, related_name='teacher2')
	plage = models.ForeignKey(Plages, on_delete = models.CASCADE)
	is_td = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = 'Schedulers'


	def __str__(self):
		return str(self.course) + " - " + str(self.salle) + " - " + str(self.plage)
		
