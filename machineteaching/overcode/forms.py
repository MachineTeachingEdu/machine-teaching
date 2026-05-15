from django import forms
from questions.models import OnlineClass, Problem

class EscolhaTurmaProblemaForm(forms.Form):

    turma = forms.ModelChoiceField(
        queryset=OnlineClass.objects.none(),  # COMEÇA VAZIO
        label='Turma',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        })
    )

    problema = forms.ModelChoiceField(
        queryset=Problem.objects.none(),
        label='Problema',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # PEGA O USUÁRIO
        super().__init__(*args, **kwargs)

        # FILTRO DE TURMAS PELO PROFESSOR LOGADO
        if user:
            self.fields['turma'].queryset = OnlineClass.objects.filter(
                professor__user=user,
                active=True
            )

        self.fields['problema'].label_from_instance = lambda obj: (
            f"{obj.title} (Dificuldade: {obj.difficulty})"
        )

        turma_id = self.data.get('turma')

        if turma_id:
            try:
                turma_id = int(turma_id)

                self.fields['problema'].queryset = Problem.objects.filter(
                    exerciseset__chapter__deadline__onlineclass__id=turma_id
                ).distinct().order_by('title')

            except (ValueError, TypeError):
                pass
