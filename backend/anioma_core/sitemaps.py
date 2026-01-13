from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from apps.stories.models import Story
from backend.apps.blog.models import Blog

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'dashboard:dashboard',
            'ethnographic_survey:submit_survey',
            'diaspora:diaspora_submit',
        ]

    def location(self, item):
        return reverse(item)

class StorySitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Story.objects.filter(published=True)

class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Blog.objects.filter(published=True)

sitemaps = {
    'static': StaticViewSitemap,
    'stories': StorySitemap,
    'blogs': BlogSitemap,
}
