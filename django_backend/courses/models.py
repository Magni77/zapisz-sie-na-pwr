from django.db import models

# Create your models here.

class Course(models.Model):
	groupCode = models.CharField(max_length=250)
	courseCode = models.CharField(max_length=250)
	courseName = models.CharField(max_length=250)
	seatsAmount = models.CharField(max_length=50)
	teacher = models.CharField(max_length=500)
	courseType = models.CharField(max_length=250)
	date = models.CharField(max_length=700)
	building = models.CharField(max_length=250)
	room = models.CharField(max_length=250)

	def __repr__(self):
		return '{} - {} - {}'.format(
			self.groupCode,
			self.courseName,
			self.teacher)

	def __str__(self):
		return '{} - {} - {}'.format(
			self.groupCode,
			self.courseName,
			self.teacher)

