from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from .models import Bird, Feeding, Toy, Photo
from .serializers import BirdSerializer, FeedingSerializer, ToySerializer, PhotoSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# Define the home view
class Home(APIView):
  def get(self, request):
    content = {'message': 'Welcome to the bird-collector api home route!'}
    return Response(content)


# User Registration
class CreateUserView(generics.CreateAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer

  def create(self, request, *args, **kwargs):
    try:
      response = super().create(request, *args, **kwargs)
      user = User.objects.get(username=response.data['username'])
      refresh = RefreshToken.for_user(user)
      content = {'refresh': str(refresh), 'access': str(refresh.access_token), 'user': response.data }
      return Response(content, status=status.HTTP_201_CREATED)
    except Exception as err:
      return Response({ 'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):

  def post(self, request):
    try:
      username = request.data.get('username')
      password = request.data.get('password')
      user = authenticate(username=username, password=password)
      if user:
        refresh = RefreshToken.for_user(user)
        content = {'refresh': str(refresh), 'access': str(refresh.access_token),'user': UserSerializer(user).data}
        return Response(content, status=status.HTTP_200_OK)
      return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as err:
      return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyUserView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    try:
      user = User.objects.get(username=request.user.username)
      try:
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh),'access': str(refresh.access_token),'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
      except Exception as token_error:
        return Response({"detail": "Failed to generate token.", "error": str(token_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as err:
      return Response({"detail": "Unexpected error occurred.", "error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BirdsIndex(APIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = BirdSerializer

  def get(self, request):
    try:
      queryset = Bird.objects.filter(user_id=request.user.id)
      serializer = self.serializer_class(queryset, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as err:
      return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def post(self, request, *args, **kwargs):
    try:
      serializer = self.serializer_class(data=request.data)
      if serializer.is_valid():
        serializer.save(user_id=request.user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
      return Response({"error": str(err)})



class BirdDetail(APIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = BirdSerializer
  lookup_field = 'id'

  def get(self, request, bird_id):
    try:
      bird = get_object_or_404(Bird, id=bird_id)
      feedings = Feeding.objects.filter(bird=bird_id)
      toysBirdHas = Toy.objects.filter(bird=bird_id)
      toysBirdDoesntHave = Toy.objects.exclude(id__in=bird.toys.all().values_list('id'))
      return Response({
          "bird": BirdSerializer(bird).data,
          "feedings": FeedingSerializer(feedings, many=True).data,
          "toysBirdHas": ToySerializer(toysBirdHas, many=True).data,
          "toysBirdDoesntHave": ToySerializer(toysBirdDoesntHave, many=True).data
      }, status=status.HTTP_200_OK)
    except Exception as err:
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def put(self, request, bird_id):
    try:
        bird = get_object_or_404(Bird, id=bird_id)
        serializer = self.serializer_class(bird, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def delete(self, request, bird_id):
    try:
        bird = get_object_or_404(Bird, id=bird_id)
        bird.delete()
        return Response({'success': True}, status=status.HTTP_200_OK)
    except Exception as err:
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class FeedingsIndex(APIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = FeedingSerializer

  def get(self, request, bird_id):
    try:
      queryset = Feeding.objects.filter(bird=bird_id)
      return Response(self.serializer_class(queryset, many=True).data, status=status.HTTP_200_OK)
    except Exception as err:
      return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
  def post(self, request, bird_id):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      serializer.save()
      queryset = Feeding.objects.filter(bird=bird_id)
      feedings = FeedingSerializer(queryset, many=True)
      return Response(feedings.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ToyIndex(generics.ListCreateAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = ToySerializer
  queryset = Toy.objects.all()

class ToyDetail(APIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = ToySerializer
  lookup_field = 'id'
  
  def get(self, request, toy_id):
    try:
      toy = get_object_or_404(Toy, id=toy_id)
      return Response(self.serializer_class(toy).data, status=status.HTTP_200_OK)
    except Exception as err:
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def put(self, request, toy_id):
    try:
      toy = get_object_or_404(Toy, id=toy_id)
      serializer = self.serializer_class(toy, data=request.data)
      if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def delete(self, request, toy_id):
    try:
      toy = Toy.objects.get(id=toy_id)
      toy.delete()
      return Response({'success': True}, status=status.HTTP_200_OK)
    except Exception as err:
      return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddToyToBird(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, bird_id, toy_id):
    try:
      bird = get_object_or_404(Bird, id=bird_id)
      toy = get_object_or_404(Toy, id=toy_id)
      bird.toys.add(toy)
      toys_bird_does_have = Toy.objects.filter(bird=bird_id)
      toys_bird_doesnt_have = Toy.objects.exclude(id__in = bird.toys.all().values_list('id'))
      return Response({
        "toysBirdHas": ToySerializer(toys_bird_does_have, many=True).data,
        "toysBirdDoesntHave": ToySerializer(toys_bird_doesnt_have, many=True).data
        }, status=status.HTTP_200_OK)
    except Exception as err:
      return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RemoveToyFromBird(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, bird_id, toy_id):
    try:
      bird = get_object_or_404(Bird, id=bird_id)
      toy = get_object_or_404(Toy, id=toy_id)
      bird.toys.remove(toy)
      toys_bird_does_have = Toy.objects.filter(bird=bird_id)
      toys_bird_doesnt_have = Toy.objects.exclude(id__in = bird.toys.all().values_list('id'))
      return Response({
        "toysBirdHas": ToySerializer(toys_bird_does_have, many=True).data,
        "toysBirdDoesntHave": ToySerializer(toys_bird_doesnt_have, many=True).data
        }, status=status.HTTP_200_OK)
    except Exception as err:
      return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PhotoDetail(APIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = PhotoSerializer

  def post(self, request, bird_id):
    try:
      serializer = self.serializer_class(data=request.data)
      if serializer.is_valid():
        existing_photo = Photo.objects.filter(bird=bird_id).first()
        if existing_photo:
          existing_photo.delete()
        bird = get_object_or_404(Bird, id=bird_id)
        serializer.save(bird=bird)
        return Response(BirdSerializer(bird).data, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)