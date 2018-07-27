import json
from django import forms
from django.utils.translation import gettext as _
from contacts.models import Contact, Company


class ContactForm(forms.ModelForm):
    company = forms.CharField(label='Company', max_length=128, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'company'):
            self.fields['company'].initial = str(self.instance.company)
        self.fields.move_to_end('company', last=False)
        self.fields.move_to_end('name', last=False)

    def save(self, commit=True):
        model = super().save(commit=False)
        company_name = self.cleaned_data['company']

        old_company = None
        if company_name:
            old_company = model.company_id
            model.company = Company.objects.get_or_create(name=company_name)[0]

        if commit:
            model.save()
            if old_company is not None:
                comp = Company.objects.get(id=old_company)
                if comp.contacts.count() == 0:
                    comp.delete()

        return model

    class Meta:
        model = Contact
        exclude = ('company',)


class ImportForm(forms.Form):
    file = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        if file:
            try:
                contacts = json.loads(file.read().decode('utf8'))
            except Exception as e:
                print(e)
                raise forms.ValidationError(_('The file is not correct json'))
            if not isinstance(contacts, list) or any(not isinstance(d, dict) for d in contacts):
                raise forms.ValidationError(_('Wrong file format'))

            cleaned_data['contacts'] = []
            for contact in contacts:
                cform = ContactForm(contact)
                if not cform.is_valid():
                    raise forms.ValidationError(_('Wrong contact data: %(contact)s; %(errors)s'),
                                                params={'contact': contact, 'errors': cform.errors})
                cleaned_data['contacts'].append(cform)
        return cleaned_data

    def save(self, commit=True):
        saved_contacts = []
        for cform in self.cleaned_data['contacts']:
            contact = cform.save(commit)
            saved_contacts.append(contact.id)
        return saved_contacts

    class Meta:
        fields = ('file',)
