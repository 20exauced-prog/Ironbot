from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import License

@login_required
def my_licenses(request):
    licenses = License.objects.filter(user=request.user).order_by("expires_at")
    active_count = sum(1 for license in licenses if license.is_valid)
    expired_count = len(licenses) - active_count
    return render(
        request,
        'licenses/my_licenses.html',
        {
            'licenses': licenses,
            'active_count': active_count,
            'expired_count': expired_count,
        },
    )
