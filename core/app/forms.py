from django import forms
from .models import PerfilAluno

class InformacoesAlunoForm(forms.Form):
    nome_completo = forms.CharField(
        label='Nome Completo', 
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    curso = forms.CharField(
        label='Curso', 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class EditarPerfilForm(forms.ModelForm):
    nova_senha = forms.CharField(
        label='Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Deixe em branco para não alterar'}),
    )

    class Meta:
        model = PerfilAluno
        fields = ['nome_completo', 'curso']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
        }
