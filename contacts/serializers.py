from rest_framework import serializers

from contacts.models import Contact, Company


class ContactSerializer(serializers.ModelSerializer):
    company = serializers.CharField(min_length=1, max_length=128)

    def create(self, validated_data):
        validated_data['company'] = Company.objects.get_or_create(name=validated_data['company'])[0]
        return Contact.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.interest = validated_data.get('interest', instance.interest)

        old_company_id = instance.company_id
        instance.company = Company.objects.get_or_create(name=validated_data.get('company', instance.interest))[0]
        comp = Company.objects.get(id=old_company_id)
        if comp.contacts.count() == 0:
            comp.delete()
        instance.save()
        return instance

    class Meta:
        model = Contact
        fields = ('id', 'name', 'company', 'phone', 'email', 'interest')


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'address')
