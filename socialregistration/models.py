from django.contrib.sites.models import Site

def get_default_site():
    return Site.objects.get_current()
