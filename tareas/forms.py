from django import forms

from tareas.models import Tarea


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ["titulo", "prioridad", "fecha_limite"]
        widgets = {
            "titulo": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Qué hay que hacer",
                    "autocomplete": "off",
                    "maxlength": 200,
                }
            ),
            "prioridad": forms.Select(attrs={"class": "select"}),
            "fecha_limite": forms.DateInput(
                attrs={"class": "input", "type": "date"},
                format="%Y-%m-%d",
            ),
        }
        labels = {
            "titulo": "Título",
            "prioridad": "Prioridad",
            "fecha_limite": "Fecha límite",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["titulo"].error_messages["required"] = "Escribí qué hay que hacer."
        if not self.is_bound:
            return
        for nombre, campo in self.fields.items():
            if self.errors.get(nombre):
                campo.widget.attrs["aria-invalid"] = "true"
                campo.widget.attrs["aria-describedby"] = f"error-{nombre}"

    def clean_titulo(self) -> str:
        titulo = self.cleaned_data["titulo"].strip()
        if not titulo:
            raise forms.ValidationError("Escribí qué hay que hacer.")
        return titulo
