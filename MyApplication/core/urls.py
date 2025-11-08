from django.urls import path
from core.views import (
    CreateUserView, 
    UpdateUserView, 
    SearchUserView, 
    DeleteUserView,
    ListUsersView,
    BatchUploadView,
    UpdateUserRoleView,
    get_user_info,
    CourseCategoryCreateView,
)

urlpatterns = [
    path("create/", CreateUserView.as_view(), name="create-user"),
    path("users/<int:user_id>/", UpdateUserView.as_view(), name="update-user"),
    path("users/delete/<int:user_id>/", DeleteUserView.as_view(), name="delete-user"),
    path("users/search/", SearchUserView.as_view(), name="search-user"),
    path("users/", ListUsersView.as_view(), name="list-users"),
    path("users/batch-upload/", BatchUploadView.as_view(), name="batch-upload"),
    path("users/<int:user_id>/role/", UpdateUserRoleView.as_view(), name="update-user-role"),
    path('user-info/', get_user_info, name='user-info'),
    path("course-categories/", CourseCategoryCreateView.as_view(), name="create-course-category"),
]




