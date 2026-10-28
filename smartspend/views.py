from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def health(request):
    """Liveness check used by Docker and CI smoke tests."""
    return JsonResponse({"status": "ok", "service": "smartspend", "version": "v1"})
