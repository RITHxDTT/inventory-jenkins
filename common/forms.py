from django import forms
from django.core.exceptions import ValidationError

def validate_image(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('Images must be no larger than 5 MB.')
    from PIL import Image
    try:
        image = Image.open(value)
        if image.format not in ('JPEG', 'PNG', 'WEBP'):
            raise ValidationError('Upload a JPEG, PNG, or WebP image.')
        if image.width * image.height > 20000000:
            raise ValidationError('Image dimensions are too large.')
        image.verify()
    except ValidationError:
        raise
    except Exception:
        raise ValidationError('Please upload a valid image.')
    finally:
        value.seek(0)

class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-check-input' if isinstance(field.widget, forms.CheckboxInput) else 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3
