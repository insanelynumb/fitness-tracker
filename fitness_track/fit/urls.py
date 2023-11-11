from django.urls import path
from fit import views
app_name = 'fit'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('wtlog/', views.logweight, name='wtlog'),
    path('foodrecord/', views.foodrecord, name='foodrecord'),
    path('exercises/', views.exercises, name='exercises'),
    path('exercises/<int:active_exercises>', views.exercises, name='exercises'),
    path('exhome/', views.exhome, name='exlog_home'),
    path('log/<int:pk>/', views.ExlogDetailView.as_view(), name='exlog-detail'),
    path('log/new/', views.ExlogCreateView.as_view(), name='exlog-create'),
    path('log/<int:pk>/update/', views.ExlogUpdateView.as_view(), name='exlog-update'),
    path('log/<int:pk>/delete/', views.ExlogDeleteView.as_view(), name='exlog-delete'),
    path('log/<int:pk>/addexercise/', views.ExerciseCreateView.as_view(), name='exlog-add-exercise'),
    path('log/<int:pk>/updateexercise/', views.ExerciseUpdateView.as_view(), name='exlog-update-exercise'),
    path('log/<int:pk>/deleteexercise/', views.ExerciseDeleteView.as_view(), name='exlog-delete-exercise'),
    path('log/add_ex_to_today_log/<str:exercise_name>/', views.add_from_recommender, name='exlog-add-from-recommender'),
    path('results/', views.results, name='results'),
]
