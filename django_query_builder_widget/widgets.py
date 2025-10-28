import json
from django import forms
from django.db import models
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.safestring import mark_safe


class QueryBuilderWidget(AdminTextareaWidget):
    WIDGET_MAP = {
        forms.TextInput: 'text', forms.Textarea: 'textarea', forms.EmailInput: 'text',
        forms.URLInput: 'text', forms.NumberInput: 'number', forms.Select: 'select',
        forms.RadioSelect: 'radio', forms.CheckboxInput: 'checkbox',
        forms.DateInput: 'text', forms.DateTimeInput: 'text', forms.TimeInput: 'text',
        forms.SelectMultiple: 'select',
    }

    FIELD_TYPE_MAP = {
        models.CharField: 'string', models.TextField: 'string',
        models.EmailField: 'string', models.URLField: 'string', models.SlugField: 'string',
        models.IntegerField: 'integer', models.BigIntegerField: 'integer',
        models.SmallIntegerField: 'integer', models.PositiveIntegerField: 'integer',
        models.FloatField: 'double', models.DecimalField: 'double',
        models.BooleanField: 'boolean', models.DateField: 'date',
        models.DateTimeField: 'datetime', models.TimeField: 'time',
        models.ForeignKey: 'integer', models.OneToOneField: 'integer',
    }

    OPERATORS_MAP = {
        'string': ['equal', 'not_equal', 'contains', 'not_contains', 'begins_with', 'ends_with', 'is_null', 'is_not_null'],
        'integer': ['equal', 'not_equal', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'is_null', 'is_not_null'],
        'double': ['equal', 'not_equal', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'is_null', 'is_not_null'],
        'boolean': ['equal'],
        'date': ['equal', 'not_equal', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'is_null', 'is_not_null'],
        'datetime': ['equal', 'not_equal', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'is_null', 'is_not_null'],
        'time': ['equal', 'not_equal', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between'],
    }

    @property
    def media(self):
        return forms.Media(
            js=(
                'query-builder-widget/js/lib/jquery-3.6.0.min.js',
                'query-builder-widget/js/lib/query-builder.standalone.min.js',
            ),
            css={'all': (
                'query-builder-widget/css/lib/query-builder.default.min.css',
                'query-builder-widget/css/query-builder-widget.css',
            )}
        )

    def __init__(self, model=None, attrs=None, fields=None, field_config=None, extra_filters=None):
        super().__init__(attrs)
        self.model = model
        self.fields = fields
        self.field_config = field_config or {}
        self.extra_filters = extra_filters or []

    def _get_widget_type(self, widget):
        if isinstance(widget, str):
            return widget

        widget_class = widget if isinstance(widget, type) else widget.__class__

        for widget_class_option, field_type in self.WIDGET_MAP.items():
            if issubclass(widget_class, widget_class_option):
                return field_type
        return 'text'

    def _get_field_type(self, field):
        for field_class, qb_type in self.FIELD_TYPE_MAP.items():
            if isinstance(field, field_class):
                return qb_type
        return 'string'

    def _get_field_input(self, field):
        if isinstance(field, models.BooleanField):
            return 'radio'
        if isinstance(field, models.TextField):
            return 'textarea'
        return 'text'

    def _get_field_label(self, field):

        if hasattr(field, 'verbose_name'):
            return field.verbose_name.title()

        return field.name.replace('_', ' ').title()

    def _get_field_values(self, field):
        if hasattr(field, 'choices') and field.choices:
            return {str(k): str(v) for k, v in field.choices}
        if isinstance(field, models.BooleanField):
            return {'1': 'Yes', '0': 'No'}
        return None

    def _normalize_choices(self, choices):
        if isinstance(choices, list):
            return {str(k): str(v) for k, v in choices}
        return choices

    def _apply_custom_config(self, filter_config, custom_config):
        if 'widget' in custom_config:
            filter_config['input'] = self._get_widget_type(custom_config['widget'])

        for key in ('choices', 'values'):
            if key in custom_config:
                filter_config['values'] = self._normalize_choices(custom_config[key])
                if 'widget' not in custom_config:
                    filter_config['input'] = 'select'
                break

        if 'operators' in custom_config:
            filter_config['operators'] = custom_config['operators']

        return filter_config

    def _build_filter_config(self, field):
        field_type = self._get_field_type(field)
        config = {
            'id': field.name,
            'label': self._get_field_label(field),
            'type': field_type,
            'operators': self.OPERATORS_MAP.get(field_type, ['equal', 'not_equal']),
            'input': self._get_field_input(field),
        }

        values = self._get_field_values(field)
        if values:
            config['values'] = values
            config['input'] = 'select'

        if field.name in self.field_config:
            config = self._apply_custom_config(config, self.field_config[field.name])

        return config

    def generate_filters(self):
        if not self.model:
            return self.extra_filters

        filters = [
            self._build_filter_config(field)
            for field in self.model._meta.get_fields()
            if (self.fields is None or field.name in self.fields)
        ]

        return filters + self.extra_filters

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['style'] = 'display: none;'

        widget_id = attrs.get('id', f'id_{name}')
        builder_id = f'{widget_id}_builder'
        filters_json = json.dumps(self.generate_filters())

        initial_rules = 'null'
        parsed = json.loads(value)
        if parsed and isinstance(parsed, dict) and 'condition' in parsed:
            initial_rules = value

        textarea_html = super().render(name, value, attrs, renderer)

        return mark_safe(f"""
            {textarea_html}
            <div id="{builder_id}" class="query-builder-container"></div>
            <script>
            (function() {{
                var filters = {filters_json};
                var initialRules = {initial_rules};

                function initQueryBuilder($) {{
                    $('#{builder_id}').queryBuilder({{
                        allow_empty: true,
                        display_errors: true,
                        filters: filters,
                        rules: initialRules !== null ? initialRules : undefined,
                    }});

                    $('#{builder_id}').on('afterAddGroup.queryBuilder afterAddRule.queryBuilder afterDeleteGroup.queryBuilder afterDeleteRule.queryBuilder afterUpdateRuleValue.queryBuilder afterUpdateGroupCondition.queryBuilder', function() {{
                        var rules = $('#{builder_id}').queryBuilder('getRules');
                        if (rules) $('#{widget_id}').val(JSON.stringify(rules, null, 2));
                    }});

                    $('form').on('submit', function() {{
                        var rules = $('#{builder_id}').queryBuilder('getRules');
                        if (rules) $('#{widget_id}').val(JSON.stringify(rules, null, 2));
                    }});
                }}

                initQueryBuilder(window.jQuery)
            }})();
            </script>
        """)
