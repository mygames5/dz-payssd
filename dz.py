# models.py and management command

from django.db import models
from django.utils.text import slugify
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404
from django.urls import path

# Model definition
class Phone(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(max_length=500)
    release_date = models.DateField()
    lte_exists = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Management command for importing phones from CSV
class Command(BaseCommand):
    help = 'Import phones from a CSV file'

    def handle(self, *args, **options):
        with open('phones.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                phone, created = Phone.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'price': float(row['price']),
                        'image': row['image'],
                        'release_date': datetime.strptime(row['release_date'], '%Y-%m-%d').date(),
                        'lte_exists': row['lte_exists'].lower() == 'true',
                        'slug': slugify(row['name']),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Phone {phone.name} imported'))

# Views for displaying catalog and phone detail
from django.http import HttpRequest, HttpResponse

def catalog(request):
    sort = request.GET.get('sort')
    if sort == 'name':
        phones = Phone.objects.all().order_by('name')
    elif sort == 'min_price':
        phones = Phone.objects.all().order_by('price')
    elif sort == 'max_price':
        phones = Phone.objects.all().order_by('-price')
    else:
        phones = Phone.objects.all()
    return render(request, 'catalog.html', {'phones': phones})

def phone_detail(request, slug):
    phone = get_object_or_404(Phone, slug=slug)
    return render(request, 'phone_detail.html', {'phone': phone})

# URL configuration
urlpatterns = [
    path('catalog/', catalog, name='catalog'),
    path('catalog/<slug:slug>/', phone_detail, name='phone_detail'),
]
