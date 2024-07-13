from django.db import models
from django.db.models.signals import post_save, pre_delete
from slugify import slugify
from django.dispatch import receiver
import os, threading

def tailwind_build():
    os.system('npx tailwindcss build -i ./src/input.css -o ./core/static/css/pages.css --content "./templates/trash/**/*.{html,js}"')

class Page(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Page, self).save(*args, **kwargs)


class Component(models.Model):
    label = models.CharField(max_length=255)
    html_id = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    category = models.CharField(max_length=255, blank=True, null=True)
    attributes = models.JSONField(blank=True, null=True)

class Scripts(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    config = models.JSONField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

@receiver(post_save, sender=Component)
def component_post_save(sender, instance, *args, **kwargs):
    with open(f'templates/trash/components_cache/{instance.html_id}.html', 'w') as f:
        f.write(instance.content)
        
    threading.Thread(target=tailwind_build).start()


post_save.connect(component_post_save, sender=Component)


@receiver(pre_delete, sender=Component)
def component_pre_delete(sender, instance, *args, **kwargs):
    os.remove(f'templates/trash/components_cache/{instance.html_id}.html')


pre_delete.connect(component_pre_delete, sender=Component)


@receiver(post_save, sender=Page)
def page_post_save(sender, instance, *args, **kwargs):
    with open(f'templates/trash/pages_cache/{instance.slug}.html', 'w') as f:
        f.write(instance.content)

    threading.Thread(target=tailwind_build).start()

post_save.connect(page_post_save, sender=Page)


@receiver(pre_delete, sender=Page)
def page_pre_delete(sender, instance, *args, **kwargs):
    os.remove(f'templates/trash/pages_cache/{instance.slug}.html')


pre_delete.connect(page_pre_delete, sender=Page)