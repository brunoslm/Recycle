from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Obra, Acordo, Avaliacao

class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = ['descricao', 'tipo_residuo','imagem', 'endereco', 'bairro', 'cidade', 'estado', 'latitude', 'longitude']
        widgets = {
            'descricao': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition',
                'rows': 3,
                'placeholder': 'Ex: 10 caçambas de entulho misto (tijolo, cimento)'
            }),
            'tipo_residuo': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition',
                'placeholder': 'Ex: Alvenaria, Madeira, Metal'
            }),
            'imagem': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none transition file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100'}),
            'endereco': forms.TextInput(attrs={'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition', 'placeholder': 'Rua e Número'}),
            'bairro': forms.TextInput(attrs={'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition', 'placeholder': 'Cidade'}),
            'estado': forms.TextInput(attrs={'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition', 'placeholder': 'Ex: PE'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class CadastroForm(UserCreationForm):
    tipo_usuario = forms.ChoiceField(
        choices=[('GERADOR', 'Sou um Pequeno Gerador (Tenho entulho)'), 
                 ('CENTRO', 'Sou um Centro de Reciclagem (Busco entulho)')],
        label='Qual o seu perfil?',
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition mt-1 bg-white'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nome de Usuário', 
            'email': 'Endereço de E-mail',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'tipo_usuario':
                field.widget.attrs['class'] = 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition mt-1'

class FormaPagamentoForm(forms.ModelForm):
    class Meta:
        model = Acordo
        fields = ['forma_pagamento']
        widgets = {
            'forma_pagamento': forms.Select(attrs={'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition bg-white'})
        }

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'titulo', 'comentario']
        widgets = {
            'nota': forms.Select(attrs={'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 bg-white font-semibold text-slate-700'}),
            'titulo': forms.TextInput(attrs={'class': 'w-full p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-base transition-all text-slate-800', 'placeholder': 'O que é mais importante saber?'}),
            'comentario': forms.Textarea(attrs={'class': 'w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none', 'rows': 3, 'placeholder': 'Como foi negociar com este usuário?'}),
        }
