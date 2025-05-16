from django.urls import path
from .views import Home, BirdDetail, BirdsIndex, FeedingsIndex, ToyIndex, ToyDetail, AddToyToBird, RemoveToyFromBird, PhotoDetail, CreateUserView, LoginView, VerifyUserView


urlpatterns = [
  path('', Home.as_view(), name='home'),
  path('birds/', BirdsIndex.as_view(), name='bird-index'),
  path('birds/<int:bird_id>/', BirdDetail.as_view(), name='bird-detail'),
  path('birds/<int:bird_id>/feedings/', FeedingsIndex.as_view(), name='feeding-create'),
  path('toys/', ToyIndex.as_view(), name='toy-index'),
  path('toys/<int:toy_id>/', ToyDetail.as_view(), name='toy-detail'),
  path('birds/<int:bird_id>/associate-toy/<int:toy_id>/', AddToyToBird.as_view(), name='associate-toy'),
  path('birds/<int:bird_id>/remove-toy/<int:toy_id>/', RemoveToyFromBird.as_view(), name='remove-toy'),
  path('birds/<int:bird_id>/add-photo/', PhotoDetail.as_view(), name='add-photo'),
  path('users/signup/', CreateUserView.as_view(), name='signup'),
  path('users/login/', LoginView.as_view(), name='login'),
  path('users/token/refresh/', VerifyUserView.as_view(), name='token_refresh'),
]
