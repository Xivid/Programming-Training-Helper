from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class problem(models.Model):
	creator = models.ForeignKey(User)
	editor = models.TextField()
	name = models.CharField(max_length = 10)
	description = models.TextField()
	hint = models.TextField()
	inputformat = models.TextField()
	outputformat = models.TextField()
	inputsample = models.TextField()
	outputsample = models.TextField()
	solution = models.TextField()
	code = models.TextField()
	mycode = models.TextField()
	viewcount = models.IntegerField()
	def __unicode__(self):
		return self.name

class realauth(models.Model):
	user = models.ForeignKey(User)
	identity = models.CharField(max_length = 10)
	name = models.CharField(max_length = 15)
	card = models.ImageField(upload_to='images',max_length=255)
	is_active = models.BooleanField()
	def __unicode__(self):
		return self.name

class problemAdmin(admin.ModelAdmin):
	list_display = ('name','creator')
	search_fields = ('name',)
		
admin.site.register(problem,problemAdmin)
admin.site.register(realauth)