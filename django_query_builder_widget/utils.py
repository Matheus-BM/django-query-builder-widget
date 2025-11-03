from typing import Dict, Any
from decimal import Decimal
from django.db.models import Q, Model, ForeignKey


def get_field_value(object: Model, field: str) -> Any:
    field_obj = object._meta.get_field(field)

    if field_obj.many_to_many:
        return [str(id) for id in getattr(object, field).values_list('id', flat=True)]
    elif field_obj.is_relation and isinstance(field_obj, ForeignKey):
        related_object = getattr(object, field)
        if related_object is None:
            return None
        return str(getattr(related_object, 'id'))

    return getattr(object, field, None)


def compare_values(value: Any, operator: str, rule_value: Any) -> bool:
    if value is None:
        return operator in ['is_null', 'is_empty']

    if isinstance(rule_value, str) and isinstance(value, (int, float, Decimal)):
        rule_value = type(value)(rule_value)
    elif isinstance(value, str) and isinstance(rule_value, (int, float)):
        value = type(rule_value)(value)

    if operator == 'equal':
        if isinstance(value, list):
            return rule_value in value
        return value == rule_value
    elif operator == 'not_equal':
        if isinstance(value, list):
            return rule_value not in value
        return value != rule_value
    elif operator == 'contains':
        return str(rule_value).lower() in str(value).lower()
    elif operator == 'not_contains':
        return str(rule_value).lower() not in str(value).lower()
    elif operator == 'begins_with':
        return str(value).lower().startswith(str(rule_value).lower())
    elif operator == 'ends_with':
        return str(value).lower().endswith(str(rule_value).lower())
    elif operator == 'is_empty':
        return value == '' or value is None or (isinstance(value, list) and len(value) == 0)
    elif operator == 'is_not_empty':
        return value != '' and value is not None and (not isinstance(value, list) or len(value) > 0)
    elif operator == 'is_null':
        return value is None
    elif operator == 'is_not_null':
        return value is not None
    elif operator == 'less':
        return value < rule_value
    elif operator == 'less_or_equal':
        return value <= rule_value
    elif operator == 'greater':
        return value > rule_value
    elif operator == 'greater_or_equal':
        return value >= rule_value
    elif operator == 'between':
        if isinstance(rule_value, list) and len(rule_value) == 2:
            return rule_value[0] <= value <= rule_value[1]
    elif operator == 'not_between':
        if isinstance(rule_value, list) and len(rule_value) == 2:
            return not (rule_value[0] <= value <= rule_value[1])
    elif operator == 'in':
        if isinstance(rule_value, list):
            return value in rule_value
        return value == rule_value
    elif operator == 'not_in':
        if isinstance(rule_value, list):
            return value not in rule_value
        return value != rule_value
    elif operator == 'is_true':
        return bool(value) is True
    elif operator == 'is_false':
        return bool(value) is False

    return False


def evaluate_rule(object: Model, rule: Dict[str, Any]) -> bool:
    if 'condition' in rule:
        condition = rule['condition'].upper()
        rules = rule.get('rules', [])

        if condition == 'AND':
            return all(evaluate_rule(object, r) for r in rules)
        elif condition == 'OR':
            return any(evaluate_rule(object, r) for r in rules)
        else:
            return False

    field = rule.get('field')
    operator = rule.get('operator')
    value = rule.get('value')

    if not field or not operator:
        return False

    field_value = get_field_value(object, field)
    return compare_values(field_value, operator, value)


def build_query_object(rule: Dict[str, Any]) -> Q:
    if 'condition' in rule:
        condition = rule['condition'].upper()
        rules = rule.get('rules', [])

        if not rules:
            return Q()

        query_objects = [build_query_object(r) for r in rules]

        if condition == 'AND':
            result = query_objects[0]
            for q in query_objects[1:]:
                result &= q
            return result
        elif condition == 'OR':
            result = query_objects[0]
            for q in query_objects[1:]:
                result |= q
            return result
        else:
            return Q()

    field = rule.get('field')
    operator = rule.get('operator')
    value = rule.get('value')

    if not field or not operator:
        return Q()

    lookup_map = {
        'equal': f'{field}',
        'not_equal': f'{field}',
        'contains': f'{field}__icontains',
        'not_contains': f'{field}__icontains',
        'begins_with': f'{field}__istartswith',
        'ends_with': f'{field}__iendswith',
        'is_empty': f'{field}',
        'is_not_empty': f'{field}',
        'is_null': f'{field}__isnull',
        'is_not_null': f'{field}__isnull',
        'less': f'{field}__lt',
        'less_or_equal': f'{field}__lte',
        'greater': f'{field}__gt',
        'greater_or_equal': f'{field}__gte',
        'between': f'{field}__range',
        'not_between': f'{field}__range',
        'in': f'{field}__in',
        'not_in': f'{field}__in',
    }

    if operator == 'is_null':
        return Q(**{lookup_map[operator]: True})
    elif operator == 'is_not_null':
        return Q(**{lookup_map[operator]: False})
    elif operator == 'is_empty':
        return Q(**{field: ''}) | Q(**{f'{field}__isnull': True})
    elif operator == 'is_not_empty':
        return ~Q(**{field: ''}) & Q(**{f'{field}__isnull': False})
    elif operator in ['not_equal', 'not_contains', 'not_between', 'not_in']:
        base_operator = operator.replace('not_', '')
        if base_operator in lookup_map:
            return ~Q(**{lookup_map[base_operator]: value})
        return Q()
    elif operator == 'between':
        if isinstance(value, list) and len(value) == 2:
            return Q(**{lookup_map[operator]: value})
        return Q()
    elif operator == 'is_true':
        return Q(**{field: True})
    elif operator == 'is_false':
        return Q(**{field: False})
    elif operator in lookup_map:
        return Q(**{lookup_map[operator]: value})

    return Q()
