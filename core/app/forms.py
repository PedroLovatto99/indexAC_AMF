from django import forms

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