# Run this file with:
# python manage.py shell < jsonToDatabase.py

# Add Exercises from json file to database
import os
import django
from django.conf import settings

from fitness_track.fitness_track.fitness_track.settings import BASE_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fitness_track.settings")

# Configure Django settings
settings.configure(
    DEBUG=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    },
    # Other settings...
)


django.setup()


import json
from fit.models import Exercise
with open('Exercises.json') as f:
    exer_json = json.load(f)

for exe in exer_json:
    exercise = Exercise(name=exe['name'], group=exe['group'], group_code=exe['group_code'], description=exe['description'], image_link=exe['image_link'], ex_id=exe['ex_id'])
    exercise.save()
