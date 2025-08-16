from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to form fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        
        # Update help texts
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters and cannot be entirely numeric.'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    
    class Meta:
        model = UserProfile
        fields = ['affiliation', 'orcid', 'expertise_areas', 'bio', 'website']
        widgets = {
            'affiliation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your institution or organization'
            }),
            'orcid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0000-0000-0000-0000',
                'pattern': r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]'
            }),
            'expertise_areas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Systematic reviews, Meta-analysis, Clinical trials'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself and your research interests'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-website.com'
            })
        }
        
        help_texts = {
            'orcid': 'Your ORCID identifier (optional) - format: 0000-0000-0000-0000',
            'expertise_areas': 'Describe your research areas and expertise',
            'bio': 'Brief description about yourself (max 500 characters)',
            'website': 'Your personal or professional website (optional)'
        }
    
    def clean_orcid(self):
        """Validate ORCID format"""
        orcid = self.cleaned_data.get('orcid')
        if orcid:
            # Remove any spaces or hyphens and check format
            orcid_clean = orcid.replace('-', '').replace(' ', '')
            if len(orcid_clean) != 16 or not (orcid_clean[:-1].isdigit() and orcid_clean[-1] in '0123456789X'):
                raise forms.ValidationError('ORCID must be in format: 0000-0000-0000-0000')
            # Return formatted ORCID
            return f"{orcid_clean[:4]}-{orcid_clean[4:8]}-{orcid_clean[8:12]}-{orcid_clean[12:16]}"
        return orcid


class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            })
        }
    
    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if another user has this email
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError('A user with this email already exists.')
        return email
