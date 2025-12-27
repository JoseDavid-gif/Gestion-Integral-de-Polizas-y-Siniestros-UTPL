from django import forms
from .models import Poliza

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'usernameInput'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'passwordInput'})
    )

class PolizaForm(forms.ModelForm):
    class Meta:
        model = Poliza
        fields = '__all__'
        exclude = ['fecha_registro', 'usuario_gestor'] # Campos automáticos que no se piden al usuario
        
        widgets = {
            'vigencia_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vigencia_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_emision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'numero_poliza': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_asegurado': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_poliza': forms.TextInput(attrs={'class': 'form-control'}),
            'prima_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prima_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'renovable': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        labels = {
            'estado': '¿Póliza Activa?',
            'renovable': '¿Es Renovable?'
        }

    def clean_estado(self):
        estado_bool = self.cleaned_data.get('estado')
        if estado_bool: # Si es True (marcado)
            return "Activa"
        else: # Si es False (desmarcado)
            # OJO: Si el campo viene vacío del HTML (checkbox sin marcar), Django a veces lo toma como False
            return "Inactiva"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.estado == 'Activa':
            self.initial['estado'] = True
