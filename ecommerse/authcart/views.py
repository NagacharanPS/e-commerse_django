from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View


# Signup view
def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return render(request, 'authentication/signup.html')

        if User.objects.filter(username=email).exists():
            messages.info(request, "Email already exists")
            return render(request, 'authentication/signup.html')

        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False
        user.save()

        email_subject = "Activate your account"
        message = render_to_string('authentication/activate.html', {
            'user': user,
            'domain': '127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })

        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
        )
        email_message.content_subtype = "html"  # This sets the email to render HTML properly

        email_message.send()

        messages.success(request, "Account created successfully. Check your email for activation link.")
        return redirect('/auth/login')

    return render(request, 'authentication/signup.html')


# Activation view
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully")
            return redirect('/auth/login')

        return render(request, 'authentication/activatefail.html')


# Login view
def handlelogin(request):
    if request.method == "POST":
        username = request.POST['email']
        userpassword = request.POST['pass1']
        myuser = authenticate(username=username, password=userpassword)

        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login Success")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('/auth/login')

    return render(request, 'authentication/login.html')


# Logout view
def handlelogout(request):
    logout(request)
    return redirect('/auth/login')
