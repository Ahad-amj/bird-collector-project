from django.contrib import admin
# Add Feeding to the import
from .models import Bird, Feeding, Toy, Photo

admin.site.register(Bird)
admin.site.register(Feeding)
admin.site.register(Toy)
# Register the new Photo model
admin.site.register(Photo)