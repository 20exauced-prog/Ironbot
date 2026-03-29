from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import SignUpForm
from .models import LoginAttempt


def _client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


class IronbotLoginView(LoginView):
    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST' and self._is_locked(request):
            raise PermissionDenied("Trop de tentatives de connexion. Reessaie plus tard.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        LoginAttempt.objects.filter(ip_address=_client_ip(self.request)).delete()
        return super().form_valid(form)

    def form_invalid(self, form):
        self._record_failure(self.request)
        messages.error(self.request, "Connexion refusee. Verifie tes identifiants.")
        return super().form_invalid(form)

    def _is_locked(self, request):
        window_start = timezone.now() - timezone.timedelta(seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS)
        attempt = LoginAttempt.objects.filter(ip_address=_client_ip(request)).first()
        if not attempt:
            return False
        if attempt.last_attempt_at < window_start:
            attempt.delete()
            return False
        return attempt.failures >= settings.LOGIN_RATE_LIMIT_ATTEMPTS

    def _record_failure(self, request):
        ip_address = _client_ip(request)
        username = request.POST.get('username', '')[:150]
        now = timezone.now()
        window_start = now - timezone.timedelta(seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS)
        attempt, created = LoginAttempt.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'last_username': username,
                'failures': 1,
                'first_attempt_at': now,
                'last_attempt_at': now,
            },
        )
        if created:
            return

        if attempt.last_attempt_at < window_start:
            attempt.failures = 1
            attempt.first_attempt_at = now
        else:
            attempt.failures += 1

        attempt.last_username = username
        attempt.last_attempt_at = now
        attempt.save(update_fields=['last_username', 'failures', 'first_attempt_at', 'last_attempt_at'])


def signup(request):
    if request.user.is_authenticated:
        return redirect('my_licenses')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Ton compte a ete cree avec succes.")
            return redirect('my_licenses')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})
