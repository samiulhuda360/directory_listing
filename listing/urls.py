from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('unique-domain/', views.unique_consecutive_domain, name='unique_consecutive_domain'),
    path('site-data/', views.site_data, name='site_data'),
    path('rest-api-test/', views.rest_api_test, name='rest_api_test'),
    path('geo-net/', views.content_gen_view, name='content_gen'),
    path('api/content-gen-status/<str:task_id>/', views.content_gen_status_view, name='content_gen_status'),
    path('list-files-geo/', views.list_files_geo, name='list_files_geo'),
    path('download-file-geo/<str:file_name>/', views.download_file_geo, name='download_file_geo'),
    path('delete-all-files/', views.delete_all_files_geo, name='delete_all_files_geo'), 
    path('delete-links/', views.delete_posts, name='delete_posts'),
    path('check_delete_status/', views.check_delete_task_status, name='check_delete_status'),
    path('test-status-update/', views.test_status_update, name='test_status_update'),  # URL pattern for AJAX request
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('get-task-result/<str:task_id>/', views.get_task_result, name='get_task_result'),
    path('get-task-result-unique/<str:task_id>/', views.get_task_result_unique, name='get_task_result_unique'),
    path('api-config-data/', views.get_api_config_data, name='api_config_data'),
    path('get-generated-links-json/', views.get_generated_links_json, name='get-generated-links-json'),
    path('download-failed-tests/', views.download_failed_list, name='download_failed_tests'),
    path('download-excel/', views.download_excel_latest, name='download_excel'),
    path('list-files/', views.list_files, name='list_files'),
    path('download-file/', views.download_file, name='download_file'),
    path('post-update/', views.post_update_view, name='post_update'),
    path('delete-all-files/', views.delete_all_files, name='delete_all_files'),
    path('flash-posted-website/', views.flash_posted_website, name='flash_posted_website'),

    
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
