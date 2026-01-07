import django_filters
from .models import Todo,UserProfile


class TodoFilter(django_filters.FilterSet):
    completed = django_filters.BooleanFilter()
    created_after = django_filters.DateFilter(
        field_name='created_at', lookup_expr='gte'
    )
    created_before = django_filters.DateFilter(
        field_name='created_at', lookup_expr='lte'
    )
    class Meta:
        model = Todo
        fields = ['completed']