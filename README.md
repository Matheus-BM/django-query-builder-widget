# Django Query Builder Widget

A Django admin widget that integrates jQuery QueryBuilder for building complex database queries through an intuitive visual interface.

## Preview
<img width="1224" height="542" alt="image" src="https://github.com/user-attachments/assets/e14befe9-fd88-4a05-a0ea-a440c3c72469" />

## Features

- Visual query building interface in Django admin
- Automatic field detection from Django models
- Support for all major Django field types
- Customizable operators per field type
- Support for custom fields and operators
- JSON-based query storage
- Works seamlessly with Django admin

## Installation

Install via pip:

```bash
pip install django-query-builder-widget
```

## Quick Start

### 1. Add to your Django project

Add the app to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_query_builder_widget',
    # ...
]
```

### 2. Collect static files

```bash
python manage.py collectstatic
```

### 3. Use in your admin

```python
from django.contrib import admin
from django_query_builder_widget import QueryBuilderWidget
from .models import YourModel

class YourModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': QueryBuilderWidget(model=YourModel)},
    }

admin.site.register(YourModel, YourModelAdmin)
```

## Usage Examples

### Basic Usage with Model

```python
from django_query_builder_widget import QueryBuilderWidget

# Auto-generate filters from model fields
widget = QueryBuilderWidget(model=MyModel)
```

### Specify Specific Fields

```python
# Only include specific fields
widget = QueryBuilderWidget(
    model=MyModel,
    fields=['name', 'email', 'age', 'created_at']
)
```

### Custom Field Configuration

```python
widget = QueryBuilderWidget(
    model=MyModel,
    field_config={
        'status': {
            'widget': 'select',
            'choices': [
                ('active', 'Active'),
                ('inactive', 'Inactive'),
                ('pending', 'Pending')
            ]
        },
        'priority': {
            'operators': ['equal', 'not_equal', 'greater', 'less']
        }
    }
)
```

### Add Custom Filters

```python
widget = QueryBuilderWidget(
    model=MyModel,
    extra_filters=[
        {
            'id': 'custom_field',
            'label': 'Custom Field',
            'type': 'string',
            'operators': ['equal', 'contains'],
            'input': 'text'
        }
    ]
)
```

## Field Type Mapping

The widget automatically maps Django field types to QueryBuilder types:

| Django Field | QueryBuilder Type | Default Operators |
|--------------|-------------------|-------------------|
| CharField, TextField, EmailField, URLField | string | equal, not_equal, contains, not_contains, begins_with, ends_with, is_null, is_not_null |
| IntegerField, BigIntegerField, PositiveIntegerField | integer | equal, not_equal, less, less_or_equal, greater, greater_or_equal, between, is_null, is_not_null |
| FloatField, DecimalField | double | equal, not_equal, less, less_or_equal, greater, greater_or_equal, between, is_null, is_not_null |
| BooleanField | boolean | equal |
| DateField | date | equal, not_equal, less, less_or_equal, greater, greater_or_equal, between, is_null, is_not_null |
| DateTimeField | datetime | equal, not_equal, less, less_or_equal, greater, greater_or_equal, between, is_null, is_not_null |
| TimeField | time | equal, not_equal, less, less_or_equal, greater, greater_or_equal, between |
| ForeignKey, OneToOneField | integer | equal, not_equal, less, less_or_equal, greater, greater_or_equal, between, is_null, is_not_null |

## Configuration Options

### Widget Parameters

- `model`: Django model class to generate filters from
- `fields`: List of field names to include (default: all fields)
- `field_config`: Dictionary of custom configurations per field
- `extra_filters`: List of additional custom filters
- `attrs`: Standard Django widget attributes

### Field Configuration Options

Each field can be customized with:

- `widget`: Input type ('text', 'textarea', 'select', 'radio', 'checkbox', 'number')
- `choices` or `values`: List of tuples or dictionary for select options
- `operators`: List of allowed operators for the field

## Output Format

The widget stores queries as JSON in the following format:

```json
{
  "condition": "AND",
  "rules": [
    {
      "id": "name",
      "field": "name",
      "type": "string",
      "input": "text",
      "operator": "contains",
      "value": "John"
    },
    {
      "condition": "OR",
      "rules": [
        {
          "id": "age",
          "field": "age",
          "type": "integer",
          "input": "number",
          "operator": "greater",
          "value": 25
        }
      ]
    }
  ]
}
```

## Requirements

- Python >= 3.8
- Django >= 3.2

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

This widget integrates [jQuery QueryBuilder](https://querybuilder.js.org/) by Damien Sorel.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.
