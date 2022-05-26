import jwt
from rest_framework.authentication import BaseAuthentication
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from django.contrib.auth import get_user_model

public_key = open("/home/piyush/Desktop/Keys/jwt-key.pub").read()
User = get_user_model()


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        return reason


class SafeJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return None
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(access_token, bytes(public_key, 'utf-8'), algorithms=['RS256'])

        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            raise exceptions.AuthenticationFailed('access token expired')
        except jwt.InvalidAlgorithmError:
            raise exceptions.AuthenticationFailed('invalid access token')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')
        except:
            raise exceptions.ParseError("please provide a token")

        user = User.objects.filter(email=payload['user_email']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        # self.enforce_csrf(request)
        return user, None

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for session based authentication.
        """

        def dummy_get_response(request):  # pragma: no cover
            return None

        check = CSRFCheck(dummy_get_response)
        # populates request.META['CSRF_COOKIE'], which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
