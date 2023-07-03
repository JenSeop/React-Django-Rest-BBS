from django.contrib.auth.models import User # User 모델
from django.contrib.auth.password_validation import validate_password
# Django의 기본 패스워드 검증 도구
from django.contrib.auth import authenticate
# Django의 기본 authenticte 함수, 설정한 DefaultAuthBackend인 TokenAuth 방식 유저 인증

from rest_framework import serializers
from rest_framework.authtoken.models import Token # Token 모델
from rest_framework.validators import UniqueValidator # 이메일 중복 방지 검사 도구

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    # write_only=True 옵션을 통해 클라이언트 => 서버 방향의 역 직렬화는 가능
    # 서버 => 클라이언트 방향의 직렬화는 불가능
    
    def validate(self, data):
        user = authenticate(**data)
        if user:
            token = Token.objects.get(user=user)
            return token
        raise serializers.ValidationError(
            {"error": "Unable to log in with provided credentials."}
        )

class RegisterSerializer(serializers.ModelSerializer): # 회원 가입 시리얼라이저
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())] # 이메일 중복 검증
    )
    password = serializers.CharField(
            write_only=True,
            required=True,
            validators=[validate_password] # 패스워드 검증
        )
    password2 = serializers.CharField( # 비밀번호 확인 필드
            write_only=True,
            required=True
        )
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')
    
    def validate(self, data):
        if data['password']!= data['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didnt match"}
            )    
        return data
    
    def create(self, validated_data):
    # CREATE 요청에 대해 create 메소드 오버라이딩,
    # 유저를 생성, 토큰을 생성
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        
        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return user