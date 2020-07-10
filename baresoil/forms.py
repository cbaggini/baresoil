from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


MY_MONTH_CHOICES = [('',''),('01','January'), ('02',"February"), ('03','March'), ('04','April'), ('05','May'), 
    ('06','June'), ('07','July'), ('08','August'), ('09','September'), ('10', 'October'), ('11','November'), 
    ('12','December')]
MY_YEAR_CHOICES = [('',''),('2018','2018'), ('2019','2019'), ('2020','2020')]

class DateForm(forms.Form):
    mnth = forms.ChoiceField(choices=MY_MONTH_CHOICES)
    yr = forms.ChoiceField(choices=MY_YEAR_CHOICES)
    nelat = forms.FloatField(widget=forms.HiddenInput())
    nelng = forms.FloatField(widget=forms.HiddenInput())
    swlat = forms.FloatField(widget=forms.HiddenInput())
    swlng = forms.FloatField(widget=forms.HiddenInput())

class NDVIForm(forms.Form):
    ndvi = forms.DecimalField(max_digits=4, decimal_places=3, 
        validators=[MinValueValidator(0), MaxValueValidator(2.5)], initial = 0.241, 
        label = "Upper NDVI value")
    ndvi_low = forms.DecimalField(max_digits=4, decimal_places=3, 
        validators=[MinValueValidator(0), MaxValueValidator(2.5)], initial = 0, 
        label = "Lower NDVI value")
    mnth = forms.CharField(widget=forms.HiddenInput())
    yr = forms.CharField(widget=forms.HiddenInput())
    nelat = forms.FloatField(widget=forms.HiddenInput())
    nelng = forms.FloatField(widget=forms.HiddenInput())
    swlat = forms.FloatField(widget=forms.HiddenInput())
    swlng = forms.FloatField(widget=forms.HiddenInput())
    calculated = forms.CharField(widget=forms.HiddenInput(), initial = 'No')
