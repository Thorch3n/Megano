"""
API представление для аутентификации и работы с профилем пользователя.

Это представление API обрабатывает запросы для аутентификации, создания нового пользователя, получения и обновления профиля пользователя, загрузки и обновления аватара, а также изменения пароля пользователя.

Методы:
    SignInView: Представление для аутентификации пользователя.
    SignUpView: Представление для регистрации нового пользователя.
    ProfileView: Представление для получения и обновления профиля пользователя.
    AvatarUploadView: Представление для загрузки и обновления аватара пользователя.
    ChangeUserPassword: Представление для изменения пароля пользователя.
"""
import json
import os
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile, Avatar


class SignInView(APIView):
    def post(self, request):
        """
            Обработка POST запроса.

            Args:
                request: Запрос HTTP.

            Returns:
                HttpResponse: HTTP ответ с кодом 200 в случае успешной аутентификации и 500 в противном случае.
        """
        data = list(request.POST.keys())[0]
        userdata = json.loads(data)
        username = userdata['username']
        password = userdata['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=200)
        return HttpResponse(status=500)


class SignUpView(APIView):
    def post(self, request):
        """
            Обработка POST запроса для регистрации нового пользователя.

            Args:
                request: Запрос HTTP.

            Returns:
                HttpResponse: HTTP ответ с кодом 200 в случае успешной регистрации и 500 в противном случае.
        """
        data = list(request.POST.keys())[0]
        userdata = json.loads(data)
        name = userdata['name']
        username = userdata['username']
        password = userdata['password']
        if User.objects.filter(username=username).exists():
            return HttpResponse(status=500)
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            avatar = Avatar.objects.create(src=None)
            avatar.save()
            profile = Profile.objects.create(fullName=name, user=user, avatar_id=avatar.id)
            profile.save()
            login(request, user)
            return HttpResponse(status=200)

class ProfileView(APIView):
    def get(self, request):
        """
            Обработка GET запроса для получения профиля пользователя.

            Args:
                request: Запрос HTTP.

            Returns:
                JsonResponse: JSON ответ с данными профиля пользователя.
        """
        user = request.user

        profile = Profile.objects.get(user=user)
        avatar_url = None
        avatar_data = {}  # Инициализация avatar_data до условия
        if profile.avatar:
            try:
                avatar = Avatar.objects.get(id=profile.avatar_id)
            except ValueError:
                # Обработка случая, когда объект Avatar не существует
                avatar = None

            if avatar:
                avatar_data = {
                    'src': avatar.src.url,
                    'alt': avatar.alt,
                }
            else:
                avatar_data = None
        profile_data = {
            'fullName': profile.fullName,
            'email': profile.email,
            'phone': profile.phone,
            'avatar': avatar_data,
        }
        return JsonResponse(profile_data)

    def post(self, request):
        """
            Обработка POST запроса для обновления профиля пользователя.

            Args:
                request: Запрос HTTP.

            Returns:
                Response: HTTP ответ с кодом 200 в случае успешного обновления профиля и 400 в противном случае.
        """
        user = request.user
        fullName = request.data.get('fullName')
        phone = request.data.get('phone')
        email = request.data.get('email')
        profile, created = Profile.objects.get_or_create(user=user)
        profile.fullName = fullName
        profile.phone = phone
        profile.email = email
        profile.save()
        return Response(status=200)


class AvatarUploadView(APIView):
    def post(self, request):
        """
            Обработка POST запроса для загрузки аватара пользователя.

            Args:
                request: Запрос HTTP.

            Returns:
                Response: HTTP ответ с кодом 200 в случае успешной загрузки и 400 в противном случае.
        """
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        try:
            avatar = Avatar.objects.get(id=profile.avatar_id)
        except Avatar.DoesNotExist:
            # Обработка случая, когда объект Avatar не существует
            avatar = None

        if 'avatar' not in request.FILES:
            return Response({'error': 'No avatar file found'}, status=400)

        avatar_file = request.FILES['avatar']
        user_avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars', f'user_{user.id}')
        if not os.path.exists(user_avatar_dir):
            os.makedirs(user_avatar_dir)

        # Удаляем старый аватар, если он существует
        if avatar and avatar.src:
            old_avatar_path = os.path.join(settings.MEDIA_ROOT, avatar.src.name)
            if os.path.exists(old_avatar_path):
                try:
                    os.remove(old_avatar_path)
                    print(f"Old avatar deleted: {old_avatar_path}")
                except Exception as e:
                    print(f"Failed to delete old avatar: {e}")

        # Проверяем тип файла
        if not avatar_file.content_type.startswith('image'):
            return Response({'error': 'Invalid file format. Only image files are allowed.'}, status=400)

        try:
            if avatar is None:
                # Если объект Avatar не существует, создаем новый
                avatar = Avatar.objects.create(src=None)

            # Сохраняем новый аватар
            avatar_path = os.path.join(user_avatar_dir, avatar_file.name)
            with open(avatar_path, 'wb+') as destination:
                for chunk in avatar_file.chunks():
                    destination.write(chunk)

            avatar.src.name = f'avatars/user_{user.id}/{avatar_file.name}'
            avatar.save()

            # Связываем профиль пользователя с обновленным аватаром
            profile.avatar = avatar
            profile.save()

            return Response({'message': 'Avatar uploaded successfully'}, status=200)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            print("Error occurred while saving avatar:", e)  # Выводим отладочную информацию
            return Response({'error': 'An error occurred while saving avatar'}, status=400)


class ChangeUserPassword(APIView):
    def post(self, request):
        """
            Обрабатывает POST запросы, изменяя пароль пользователя.

            Args:
                request: Запрос HTTP.

            Returns:
                Response: HTTP ответ.
        """
        user = request.user
        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')

        print("Current password:", current_password)
        print("New password:", new_password)

        # Проверяем наличие текущего и нового пароля в запросе
        if not current_password or not new_password:
            return Response({'error': 'Current password and new password are required'}, status=500)

        # Проверяем, что текущий пароль верный
        if not user.check_password(current_password):
            return Response({'error': 'Invalid current password'}, status=500)

        # Проверяем, что новый пароль отличается от текущего
        if current_password == new_password:
            return Response({'error': 'New password must be different from the current password'}, status=500)

        # Устанавливаем новый пароль и сохраняем его
        try:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)