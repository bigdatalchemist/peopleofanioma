from django import template

register = template.Library()

@register.filter(name='blog_reaction_count')
def reaction_count(post, reaction_type):
    return post.reactions.filter(type=reaction_type).count()