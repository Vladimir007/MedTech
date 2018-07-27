import json
import mimetypes
from io import BytesIO
from wsgiref.util import FileWrapper

from django.http import StreamingHttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from rest_framework import viewsets

from contacts.models import Contact, Company
from contacts.forms import ContactForm, ImportForm
from contacts.serializers import ContactSerializer, CompanySerializer
from contacts.utils import get_values


class ContactsList(ListView):
    model = Contact
    ordering = 'id'
    paginate_by = 10
    template_name = 'contacts/contacts_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == 'GET' and 'filter-dropdown' in self.request.GET \
                and 'filter-value' in self.request.GET and len(self.request.GET['filter-value'][0]) > 0:

            queryset = queryset.filter(**{
                '{0}__icontains'.format(self.request.GET['filter-dropdown']): self.request.GET['filter-value']
            })
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET' and 'filter-dropdown' in self.request.GET \
                and 'filter-value' in self.request.GET and len(self.request.GET['filter-value'][0]) > 0:
            context['filter_dropdown'] = self.request.GET['filter-dropdown']
            context['filter_value'] = self.request.GET['filter-value']
        return context


class CompaniesList(ListView):
    model = Company
    ordering = 'name'
    template_name = 'contacts/companies.html'


class CreateContactView(CreateView):
    template_name = 'contacts/contact_form.html'
    form_class = ContactForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submit_btn'] = 'Create'
        context['title'] = 'New Contact'
        return context


class EditContactView(UpdateView):
    template_name = 'contacts/contact_form.html'
    form_class = ContactForm
    success_url = reverse_lazy('index')
    model = Contact

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submit_btn'] = 'Save'
        context['title'] = 'Edit Contact'
        return context


class DeleteContactView(DeleteView):
    template_name = 'contacts/contact_delete.html'
    model = Contact
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submit_btn'] = 'Delete'
        context['title'] = 'Contact deletion'
        return context


class InspectContactView(DetailView):
    model = Contact
    template_name = 'contacts/contact_inspect.html'


class InspectCompanyView(DetailView):
    model = Company
    template_name = 'contacts/company.html'


class ImportContactsView(TemplateView):
    template_name = 'contacts/import_contacts.html'

    def post(self, *args, **kwargs):
        form = ImportForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))
        return render(self.request, self.template_name, self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submit_btn'] = 'Import'
        context['title'] = 'Import contacts from json file'
        return context


class ExportContactsView(ListView):
    model = Contact
    ordering = 'id'

    def get(self, *args, **kwargs):
        contacts = list({
            'name': contact.name,
            'company': str(contact.company),
            'email': contact.email,
            'phone': contact.phone,
            'interest': contact.interest
        } for contact in self.get_queryset())

        fp = BytesIO(json.dumps(contacts, sort_keys=True, ensure_ascii=False, indent=2).encode('utf8'))
        file_size = fp.seek(0, 2)
        fp.seek(0)

        filename = 'contacts.json'
        mimetype = mimetypes.guess_type(filename)[0]
        response = StreamingHttpResponse(FileWrapper(fp, 8192), content_type=mimetype)
        response['Content-Length'] = file_size
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response


class ParseWebsite(TemplateView):
    template_name = 'contacts/values.html'

    def get_context_data(self, **kwargs):
        return {'values': get_values()}


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('id')
    serializer_class = ContactSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('name')
    serializer_class = CompanySerializer
