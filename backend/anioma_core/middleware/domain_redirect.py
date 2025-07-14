from django.http import HttpResponsePermanentRedirect

class ForceCanonicalDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.canonical_domain = 'peopleofanioma.com'

    def __call__(self, request):
        host = request.get_host().lower()
        if host.endswith('.onrender.com') or host.startswith('www.peopleofanioma.com'):
            new_url = request.build_absolute_uri().replace(host, self.canonical_domain)
            return HttpResponsePermanentRedirect(new_url)
        return self.get_response(request)
