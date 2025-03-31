from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.program_list_view, name='program_list'),
    path('program/<str:program_id>/', views.program_view, name='program'),
    path('concert/<path:concert_id>/', views.concert_view, name='concert'),
    path('sparql/', views.sparql_query_view, name='sparql_query'),
    re_path(r'^composer/(?P<composer_uri>.+)/$',
            views.composer_view, name='composer'),
    re_path(r'^conductor/(?P<conductor_uri>.+)/$',
            views.conductor_view, name='conductor'),
    path('soloist/<str:soloist_name>/', views.soloist_view, name='soloist'),
    re_path(r'^movement/(?P<movement_uri>.+)/$',  # Changed from path to re_path
            views.movement_view, name='movement'),
]
