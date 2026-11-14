from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Person(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    # Folosim JSONField pentru a stoca dinamic toate atributele (Health, Type, <key>, etc.)
    raw_data = models.JSONField(default=dict)
    rank = models.CharField(max_length=100, null=True, blank=True) # <-- CÂMPUL NOU

    def __str__(self):
        return f"{self.name} - {self.rank}"

class FighterUnit(models.Model):
    TYPE_CHOICES = [
        ('Infantry', 'Infantry'),
        ('Cannon', 'Cannon'),
        ('Cavalry', 'Cavalry'),
        ('Knight', 'Knight'),
    ]
    TEAM_CHOICES = [
        ('Blue', 'Blue'),
        ('Red', 'Red'),
    ]

    name = models.CharField(max_length=255)
    unit_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    team = models.CharField(max_length=10, choices=TEAM_CHOICES)

    # Validatoare stricte conform cerinței (Health între 0 și 100, Attack între 0 și 50)
    health = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    attack_points = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    profile_image_link = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.name} - {self.team} {self.unit_type}"


class Battle(models.Model):
    """Model pentru a stoca rezultatul global al unei lupte între 2 unități"""
    fighter1 = models.ForeignKey(FighterUnit, on_delete=models.CASCADE, related_name='battles_as_f1')
    fighter2 = models.ForeignKey(FighterUnit, on_delete=models.CASCADE, related_name='battles_as_f2')
    winner = models.ForeignKey(FighterUnit, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='battles_won')
    created_at = models.DateTimeField(auto_now_add=True)


class BattleStep(models.Model):
    """Model pentru a stoca istoricul pas cu pas, exact cum cere documentul"""
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='steps')
    step_order = models.IntegerField()  # Pentru a ști ordinea atacurilor
    attacker = models.ForeignKey(FighterUnit, on_delete=models.CASCADE, related_name='attacks_made')
    defender = models.ForeignKey(FighterUnit, on_delete=models.CASCADE, related_name='defenses_made')
    damage_dealt = models.IntegerField()
    attacker_health = models.IntegerField()
    defender_health = models.IntegerField()