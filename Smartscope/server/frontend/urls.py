from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.views.generic import RedirectView


from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='browse/'), name=''),
    path('browse/', views.AutoScreenViewer.as_view(), name='browser'),
    path('browse/filters/', views.navigation_filters, name='navigationFilters'),
    path('browse/getgroups/', views.get_groups, name='getGroups'),
    path('browse/getsessions/', views.get_sessions, name='getSessions'),
    path('browse/getgrids/', views.get_grids, name='getGrids'),
    # path('browse/getreport/', views.get_report, name='getReport'),
    path('evaluatemicrographs/', views.EvaluateMicrographs.as_view(), name='evaluatemicrographs'),
    path('multishot/', views.MultiShotView.as_view(),name='setMultishot'),
    path('multishot/<grid_id>', views.MultiShotView.as_view(),name='setMultishot'),
    path('protocol/<grid_id>',views.ProtocolView.as_view(), name='protocol'),
    path('microscopes/status/', views.MicroscopeStatus.as_view(), name='microscopeStatus'),
    path('preprocessing/',views.PreprocessingPipeline.as_view(),name='preprocessingPipeline'),
    path('preprocessing/getpipeline/',views.PreprocessingPipeline().get_pipeline,name='getPreprocessingPipeline'),
    path('preprocessing/<grid_id>',views.PreprocessingPipeline().get_grid_pipeline,name='getGridPreprocessingPipeline'),
    path('preprocessing/setpipeline/<pipeline>/',views.PreprocessingPipeline().set_pipeline,kwargs={'grid_id': ''},name='setPreprocessingPipeline'),
    path('preprocessing/setpipeline/<pipeline>/<grid_id>',views.PreprocessingPipeline().set_pipeline,name='setPreprocessingPipeline'),
    path('preprocessing/<grid_id>/start',views.PreprocessingPipeline().start,name='startPreprocessingPipeline'),
    path('preprocessing/<grid_id>/stop',views.PreprocessingPipeline().stop,name='stopPreprocessingPipeline'),
    path('collectionstats/<grid_id>/',views.CollectionStatsView.as_view(),name='collectionStats'),
]
if settings.USE_MICROSCOPE:
    urlpatterns += [
        path('run/', RedirectView.as_view(url='setup/'), name='run'),
        path('run/setup/', views.AutoScreenSetup.as_view(), name='setup_autoscreen'),
        path('run/setup/getusers/', views.get_users_in_group, name='getUsersInGroup'),
        path('run/setup/getdetectors/', views.get_microscope_detectors, name='getMicroscopeDetectors'),
        path('run/session/', views.AutoScreenRun.as_view(), name='run_autoscreen'),
        path('run/session/<session_id>/', views.AutoScreenRun.as_view(), name='run_session'),
    ]
