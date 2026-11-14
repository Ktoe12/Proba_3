from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Când cineva intră pe '/', îl trimitem la '/unit/all/'
    path('', RedirectView.as_view(url='/unit/all/', permanent=False), name='home'),

    # Am adăugat '/' la finalul fiecărei rute
    path('unit/add/', views.add_unit_view, name='add_unit'),
    path('unit/all/', views.list_units_view, name='list_units'),
    path('unit/<int:unit_id>/', views.unit_detail_view, name='unit_detail'),

    # Rute de acțiune
    path('unit/<int:unit_id>/heal/', views.heal_unit_view, name='heal_unit'),
    path('unit/simulate/', views.simulate_fight_view, name='simulate_fight'),
]