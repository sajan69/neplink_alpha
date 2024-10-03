#bascially i am storing all types of files,audio,video,images in the same folder chat_files,so i want to create a tag  that will help me use  sepearte it directly in the tenplate by checkingthe format like.png,.mp3,.mp4 etc
#
from django import template
register = template.Library()

@register.filter
def file_seperator(value):
    if value.endswith('.png') or value.endswith('.jpg') or value.endswith('.jpeg'):
        return 'image'
    if value.endswith('.mp3') or value.endswith('.wav') or value.endswith('.ogg'):
        return 'audio'
    if value.endswith('.mp4') or value.endswith('.avi') or value.endswith('.mkv'):
        return 'video'
    return 'file'

#how to use it in the template
# {% load file_seperator %}
#
# <img src="{{ message.file.url }}" alt="File" class="img-fluid" style="max-width: 100%;" {% if message.file.url|file_seperator == 'image' %} {% endif %}>
# <audio controls {% if message.file.url|file_seperator == 'audio' %} {% endif %}>
#     <source src="{{ message.file.url }}" type="audio/mpeg">