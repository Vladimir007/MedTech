import re
import requests

from html.parser import HTMLParser

from django.db.models import Q

from contacts.models import Contact, Company


class ImportContactsFromURL:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()

    def import_contacts(self):
        data = self.__get_data()
        if not isinstance(data, list):
            raise ValueError('Wrong json format')

        created_companies = {}

        new_contacts = []
        for d in data:
            if 'name' not in d or not isinstance(d['name'], str) or len(d['name']) == 0:
                continue
            if 'email' not in d or not isinstance(d['email'], str) or len(d['email']) == 0:
                continue
            if 'company' not in d or not isinstance(d['company'], dict) or 'name' not in d['company'] \
                    or not isinstance(d['company']['name'], str) or len(d['company']['name']) == 0:
                continue
            if d['company']['name'] in created_companies:
                company = created_companies[d['company']['name']]
            else:
                company = Company.objects.get_or_create(name=d['company']['name'])[0]
                created_companies[d['company']['name']] = company

            new_contacts.append(Contact(
                name=d['name'], email=d['email'], company=company, phone=self.__parse_phone(d.get('phone'))
            ))
        Contact.objects.bulk_create(new_contacts)
        print('{0} contacts are created'.format(len(new_contacts)))

    def __get_data(self):
        resp = self.session.get(self.url)

        if resp.status_code != 200:
            status_code = resp.status_code
            resp.close()
            raise ValueError('Got unexpected status code "{0}"'.format(status_code))
        if resp.headers['content-type'] != 'application/json' and 'error' in resp.json():
            raise ValueError('Wrong response content type: {0}'.format(resp.headers['content-type']))
        return resp.json()

    def __parse_phone(self, source):
        if source is None or not isinstance(source, str) or len(source) > 10:
            return None
        phone = ''
        i = 0
        if source[0] == '+':
            phone += '+'
            i = 1
        for j in range(i, len(source)):
            if source[j].isdigit():
                phone += phone[j]
        if re.match(r'^(\+7|8)\d{10}$', phone):
            return phone
        return None


def import_contacts():
    ImportContactsFromURL('https://jsonplaceholder.typicode.com/users').import_contacts()


class MyHTMLParser(HTMLParser):
    title = '5 базовых ценностей BREFFI'

    def __init__(self):
        super().__init__()

        self.reset()
        self.entered = False
        self.inside_div = False
        self.values = []
        self.current_value = None

    def has_class(self, avalue, attrs):
        for name, value in attrs:
            if name == 'class' and value == avalue:
                return True
        else:
            return False

    def handle_starttag(self, tag, attrs):
        if tag != 'div':
            return
        self.inside_div = True

        if self.entered and self.has_class('content-section__itemtitle', attrs):
            self.current_value = ''
        elif self.has_class('content-section__title', attrs):
            self.entered = True
        elif self.entered and self.has_class('content-section facts', attrs):
            self.entered = False

    def handle_data(self, data):
        if self.current_value is not None:
            self.current_value += data

    def handle_endtag(self, tag):
        if tag == 'div' and self.inside_div:
            self.inside_div = False
            if self.current_value is not None:
                if self.current_value not in self.values:
                    self.values.append(self.current_value)
                self.current_value = None


def get_values():
    session = requests.Session()
    resp = session.get('http://breffi.ru/ru/about')
    parser = MyHTMLParser()
    parser.feed(resp.content.decode('utf8'))
    return parser.values


class TestAPI:
    def __init__(self):
        self.session = requests.Session()

    def create_contact(self, **kwargs):
        resp = self.session.post('http://127.0.0.1:8000/rest/contacts/', data=kwargs)
        print(resp.status_code)
        return resp

    def update_contact(self, c_id, **kwargs):
        resp = self.session.patch('http://127.0.0.1:8000/rest/contacts/{0}/'.format(c_id), data=kwargs)
        print(resp.status_code)
        return resp

    def contact_details(self, c_id):
        resp = self.session.get('http://127.0.0.1:8000/rest/contacts/{0}/'.format(c_id))
        print(resp.status_code)
        return resp

    def create_company(self, **kwargs):
        resp = self.session.post('http://127.0.0.1:8000/rest/companies/', data=kwargs)
        print(resp.status_code)
        return resp

    def update_company(self, c_id, **kwargs):
        resp = self.session.patch('http://127.0.0.1:8000/rest/companies/{0}/'.format(c_id), data=kwargs)
        print(resp.status_code)
        return resp


def test_api():
    api = TestAPI()
    res = api.create_contact(name='Oleg', company='Auto', email='vovangrat@bk.ru', phone='89637397333', interest='Cars')
    print(res.json())
    api.update_contact(24, name='Oleg')
    print(api.contact_details(24).json())


def filter_by_word(word):
    return Company.objects.filter(address__contains=word)


# Available kwargs: country, region, city, street, building, office (and only one is allowed)
def filter_can_have_word(**kwargs):
    keywords = ['country', 'region', 'city', 'street', 'building', 'office']
    if len(kwargs) != 1:
        raise ValueError('Only one argument is supported')

    key = next(kwargs.__iter__())

    for i in range(len(keywords)):
        if keywords[i] == key:
            index = i
            break
    else:
        raise ValueError('Unsupported kwarg: %s' % key)

    patterns = ['[\w|\.|\s|\d]+'] * index
    patterns.append(kwargs[key])
    strict_pattern = '^%s.*$' % '\s*,\s*'.join(patterns)
    light_pattern = '^%s$' % '(\s*,\s*)?'.join(list('(%s)?' % p for p in patterns))

    return Company.objects.filter(Q(address__regex=strict_pattern) | Q(address__regex=light_pattern))
