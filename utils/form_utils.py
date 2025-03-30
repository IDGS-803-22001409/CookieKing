class FormField:
    """Base class for form fields"""
    
    def __init__(self, id, name, label, value="", required=False, **kwargs):
        self.id = id
        self.name = name
        self.label = label
        self.value = value
        self.required = required
        self.attrs = kwargs
        self.template = "components/forms/input_text.html"
    
    def get_dict(self):
        """Return a dictionary representation of this field"""
        return {
            'id': self.id,
            'name': self.name,
            'label': self.label,
            'value': self.value,
            'required': self.required,
            'template': self.template,
            'attrs': self.attrs
        }

class TextField(FormField):
    """Text input field"""
    
    def __init__(self, id, name, label, value="", required=False, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.template = "components/forms/input_text.html"

class DateField(FormField):
    """Date input field"""
    
    def __init__(self, id, name, label, value="", required=False, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.template = "components/forms/input_date.html"

class TextAreaField(FormField):
    """Textarea input field"""
    
    def __init__(self, id, name, label, value="", required=False, rows=4, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.rows = rows
        self.template = "components/forms/input_textarea.html"
    
    def get_dict(self):
        """Return a dictionary representation of this field"""
        dict_data = super().get_dict()
        dict_data['rows'] = self.rows
        return dict_data

class NumberField(FormField):
    """Number input field"""
    
    def __init__(self, id, name, label, value="", min=None, max=None, required=False, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.min = min
        self.max = max
        self.template = "components/forms/input_number.html"
    
    def get_dict(self):
        """Return a dictionary representation of this field"""
        dict_data = super().get_dict()
        dict_data['min'] = self.min
        dict_data['max'] = self.max
        return dict_data

class SelectField(FormField):
    """Select dropdown field"""
    
    def __init__(self, id, name, label, options=None, value="", required=False, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.options = options or []
        self.template = "components/forms/input_select.html"
    
    def get_dict(self):
        """Return a dictionary representation of this field"""
        dict_data = super().get_dict()
        dict_data['options'] = self.options
        return dict_data

class HiddenField(FormField):
    """Hidden input field"""
    
    def __init__(self, id, name, value="", **kwargs):
        super().__init__(id, name, "", value, False, **kwargs)
        self.template = "components/forms/input_hidden.html"