from django.contrib.auth.forms import UserCreationForm
from .models import Customer


class CustomerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = ("username", "first_name", "last_name", 
                'gender', 'dob', 'mobile_number', 'email')
        fields = ('username','email', 'first_name', 'last_name', 'mobile_number', 'address', 'gender', 'city', 'state')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user