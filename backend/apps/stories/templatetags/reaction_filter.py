from django import template

register = template.Library()

@register.filter
def story_reaction_count(story, reaction_type):
    return story.reactions.filter(type=reaction_type).count()