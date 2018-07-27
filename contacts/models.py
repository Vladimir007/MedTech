from django.core.validators import RegexValidator
from django.db import models

WRONG_PHONE = "Phone number must be entered in the format: '+79999999999' or '89999999999'."


class Company(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    address = models.CharField(max_length=1024, default='')

    class Meta:
        db_table = 'company'

    def __str__(self):
        return self.name


class Contact(models.Model):
    phone_regex = RegexValidator(regex=r'^(\+7|8)\d{10}$', message=WRONG_PHONE)

    name = models.CharField(max_length=256)
    company = models.ForeignKey(Company, models.CASCADE, related_name='contacts')
    email = models.EmailField()
    phone = models.CharField(validators=[phone_regex], max_length=12, null=True, blank=True)
    interest = models.CharField(max_length=1024, default='', blank=True)

    class Meta:
        db_table = 'contacts'
