import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q
from .models import FighterUnit, Battle, BattleStep
from .forms import FighterUnitForm


# 1. Pagina pentru adăugarea unei unități noi (Ruta: /unit)
def add_unit_view(request):
    if request.method == 'POST':
        form = FighterUnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Unitate adăugată cu succes!")
            return redirect('list_units')
        else:
            messages.error(request, "Există erori în formular.")
    else:
        form = FighterUnitForm()

    return render(request, 'war/add_unit.html', {'form': form})


# 2. Pagina cu toți luptătorii și statisticile (Ruta: /unit/all)
def list_units_view(request):
    units = FighterUnit.objects.all()

    # 4b. Componenta de statistici calculate
    stats = {
        'Blue': get_team_stats('Blue'),
        'Red': get_team_stats('Red')
    }

    return render(request, 'war/list_units.html', {'units': units, 'stats': stats})


def get_team_stats(team_name):
    """Funcție helper pentru a calcula statisticile pe echipă"""
    fights_count = Battle.objects.filter(Q(fighter1__team=team_name) | Q(fighter2__team=team_name)).count()
    damage_caused = BattleStep.objects.filter(attacker__team=team_name).aggregate(total=Sum('damage_dealt'))[
                        'total'] or 0
    damage_taken = BattleStep.objects.filter(defender__team=team_name).aggregate(total=Sum('damage_dealt'))[
                       'total'] or 0
    return {'fights': fights_count, 'dmg_caused': damage_caused, 'dmg_taken': damage_taken}


# Funcție pentru Heal
def heal_unit_view(request, unit_id):
    if request.method == 'POST':
        unit = get_object_or_404(FighterUnit, id=unit_id)
        unit.health = 100
        unit.save()
        messages.success(request, f"{unit.name} a fost vindecat complet!")
    return redirect('list_units')


# 3. Profilul unității și istoricul luptelor (Ruta: /unit/<unit-id>)
def unit_detail_view(request, unit_id):
    unit = get_object_or_404(FighterUnit, id=unit_id)
    # 4a. Aducem toate luptele în care a participat
    battles = Battle.objects.filter(Q(fighter1=unit) | Q(fighter2=unit)).order_by('-created_at')

    return render(request, 'war/unit_detail.html', {'unit': unit, 'battles': battles})


# Funcția centrală care simulează lupta
def simulate_fight_view(request):
    if request.method == 'POST':
        f1_id = request.POST.get('fighter1_id')
        f2_id = request.POST.get('fighter2_id')

        if f1_id == f2_id:
            messages.error(request, "Alegeți doi luptători diferiți!")
            return redirect('list_units')

        f1 = get_object_or_404(FighterUnit, id=f1_id)
        f2 = get_object_or_404(FighterUnit, id=f2_id)

        if f1.team == f2.team:
            messages.error(request, "Luptătorii trebuie să fie din echipe diferite (Red vs Blue)!")
            return redirect('list_units')

        if f1.health <= 0 or f2.health <= 0:
            messages.error(request, "Ambii luptători trebuie să aibă viață pentru a lupta!")
            return redirect('list_units')

        # Inițiem lupta
        battle = Battle.objects.create(fighter1=f1, fighter2=f2)
        step_order = 1

        # Algoritmul de luptă pe rând
        while f1.health > 0 and f2.health > 0:
            # F1 atacă F2
            dmg_f1 = random.randint(0, f1.attack_points)
            f2.health = max(0, f2.health - dmg_f1)
            BattleStep.objects.create(
                battle=battle, step_order=step_order,
                attacker=f1, defender=f2, damage_dealt=dmg_f1,
                attacker_health=f1.health, defender_health=f2.health
            )
            step_order += 1

            if f2.health <= 0:
                break

            # F2 atacă F1
            dmg_f2 = random.randint(0, f2.attack_points)
            f1.health = max(0, f1.health - dmg_f2)
            BattleStep.objects.create(
                battle=battle, step_order=step_order,
                attacker=f2, defender=f1, damage_dealt=dmg_f2,
                attacker_health=f1.health, defender_health=f2.health
            )
            step_order += 1

        # Stabilim câștigătorul și salvăm
        battle.winner = f1 if f1.health > 0 else f2
        battle.save()
        f1.save()
        f2.save()

        messages.success(request, f"Lupta s-a terminat! Câștigător: {battle.winner.name}")

    return redirect('list_units')