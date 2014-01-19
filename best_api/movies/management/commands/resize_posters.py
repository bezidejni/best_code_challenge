from django.core.management.base import NoArgsCommand
from PIL import Image
from movies.models import Movie


class Command(NoArgsCommand):
    args = ''
    help = 'Resizes movie posters to fixed dimension 200x283px'

    def handle_noargs(self, **options):
        for m in Movie.objects.exclude(poster=""):
            img = Image.open(m.poster)
            if img.size != (200, 283):
                resized_img = img.resize((200, 283), Image.ANTIALIAS)
                resized_img.save(m.poster.path)
            m.poster.file.close()

