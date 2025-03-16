from django.contrib import admin

# Register your models here.

from .models import (Admin, Classe, Courses, Plages, Salle, Schedulers, Specialite, Teacher)


admin.site.register(Teacher)
admin.site.register(Plages)
admin.site.register(Classe)
admin.site.register(Specialite)
admin.site.register(Courses)
admin.site.register(Salle)
admin.site.register(Schedulers)
admin.site.register(Admin)


