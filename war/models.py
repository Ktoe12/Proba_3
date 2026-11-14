from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    # Folosim JSONField pentru a stoca dinamic toate atributele (Health, Type, <key>, etc.)
    raw_data = models.JSONField(default=dict)

    def __str__(self):
        return self.name