from django.urls import path
from core.views import (
    CourseStudentsView,
    CreateUserView,
    EnrollStudentView,
    UnenrollStudentView, 
    UpdateUserView, 
    SearchUserView, 
    DeleteUserView,
    ListUsersView,
    BatchUploadView,
    UpdateUserRoleView,
    get_user_info,
    CourseCategoryListCreateView,
    CourseCategoryUpdateView,
    CourseCategoryDeleteView,
    CourseCategoryListForInstructorView,
    InstructorCourseCreateView,
    InstructorCourseListView,
    InstructorCourseUpdateView,
    InstructorCourseDeleteView,
    InstructorCoursePublishView,
    InstructorCourseArchiveView,
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
    path("course-categories/", CourseCategoryListCreateView.as_view(), name="create-course-category"),
    path("course-categories/<int:pk>/", CourseCategoryUpdateView.as_view(), name="course-category-update"),
    path("course-categories/<int:pk>/delete/", CourseCategoryDeleteView.as_view(), name="course-category-delete"),
    path("instructor/course-categories/", CourseCategoryListForInstructorView.as_view(), name="instructor-course-categories"),
    path("instructor/create-course/", InstructorCourseCreateView.as_view(), name="instructor-create-course"),
    path("instructor/my-courses/", InstructorCourseListView.as_view(), name="instructor-course-list"),
    path("instructor/update-course/<int:pk>/", InstructorCourseUpdateView.as_view(), name="instructor-update-course"),
    path("instructor/delete-course/<int:pk>/delete/", InstructorCourseDeleteView.as_view(), name="instructor-delete-course"),
    path("instructor/publish-course/<int:pk>/", InstructorCoursePublishView.as_view(), name="publish-course"),
    path("instructor/archive-course/<int:pk>/", InstructorCourseArchiveView.as_view(), name="archive-course"),
    path("instructor/enroll-student/<int:course_id>/", EnrollStudentView.as_view(), name="enroll-student"),
    path("instructor/course-students/<int:course_id>/", CourseStudentsView.as_view(), name="course-students"),
    path("instructor/unenroll-student/<uuid:course_id>/<str:reg_no>/", UnenrollStudentView.as_view(), name="unenroll-student"),


]




