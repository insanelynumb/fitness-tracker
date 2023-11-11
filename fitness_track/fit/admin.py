from django.contrib import admin
from fit.models import weight_log, Food, ExerciseLog, Exercise
# Register your models here.
admin.site.register(weight_log)
admin.site.register(Food)
admin.site.register(ExerciseLog)
admin.site.register(Exercise)
