#import modules to test 
from lmn.models import Venue, Artist, Note, Show
from django.contrib.auth.models import User

import pytest
from django.core.paginator import Paginator as DjangoPaginator
from rest_framework import (
    exceptions, filters, generics, pagination, serializers, status
)
from rest_framework.pagination import PAGE_BREAK, PageLink
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()


class TestPaginationIntegration:
    """
    Integration tests.
    """

    def setup(self):
        class PassThroughSerializer(serializers.BaseSerializer):
            def to_representation(self, item):
                return item

        class EvenItemsOnly(filters.BaseFilterBackend):
            def filter_queryset(self, request, queryset, view):
                return [item for item in queryset if item % 2 == 0]

        class BasicPagination(pagination.PageNumberPagination):
            page_size = 5
            page_size_query_param = 'page_size'
            max_page_size = 10

        self.view = generics.ListAPIView.as_view(
            serializer_class=PassThroughSerializer,
            queryset=range(1, 101),
            filter_backends=[EvenItemsOnly],
            pagination_class=BasicPagination
        )

    def test_filtered_items_are_paginated(self):
        request = factory.get('/', {'page': 2})
        response = self.view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'results': [2, 4, 6, 8],
            'previous': 'http://127.0.0.1:9000/',
            'next': 'http://127.0.0.1:9000/?page=3',
            'count': 10
        }

    def test_setting_page_size(self):
        """
        When 'paginate_by_param' is set, the client may choose a page size.
        """
        request = factory.get('/', {'page_size': 10})
        response = self.view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'results': [2, 4, 6, 8, 10],
            'previous': None,
            'next': 'http://127.0.0.1:9000/?page=2&page_size=10',
            'count': 10
        }

    def test_setting_page_size_over_maximum(self):
        """
        When page_size parameter exceeds maximum allowable,
        then it should be capped to the maximum.
        """
        request = factory.get('/', {'page_size': 100})
        response = self.view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'results': [
                2, 4, 6, 8, 10
            ],
            'previous': None,
            'next': 'http://127.0.0.1:9000/?page=2&page_size=100',
            'count': 10
        }

    def test_setting_page_size_to_zero(self):
        """
        When page_size parameter is invalid it should return to the default.
        """
        request = factory.get('/', {'page_size': 0})
        response = self.view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'results': [2, 4, 6, 8, 10],
            'previous': None,
            'next': 'http://127.0.0.1:9000/?page=2&page_size=0',
            'count': 10
        }

    def test_404_not_found_for_zero_page(self):
        request = factory.get('/', {'page': '0'})
        response = self.view(request)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {
            'detail': 'Invalid page.'
        }

    def test_404_not_found_for_invalid_page(self):
        request = factory.get('/', {'page': 'invalid'})
        response = self.view(request)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {
            'detail': 'Invalid page.'
        }

    
class TestPageNumberPagination:
    """
    Unit tests for `pagination.PageNumberPagination`.
    """

    def setup(self):
        class ExamplePagination(pagination.PageNumberPagination):
            page_size = 10

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_queryset(self.queryset, request))

    def get_paginated_content(self, queryset):
        response = self.pagination.get_paginated_response(queryset)
        return response.data

    def get_html_context(self):
        return self.pagination.get_html_context()

    def test_no_page_number(self):
        request = Request(factory.get('/'))
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        context = self.get_html_context()
        assert queryset == [1, 2, 3, 4, 5]
        assert content == {
            'results': [1, 2, 3, 4, 5],
            'previous': None,
            'next': 'http://127.0.0.1:9000/?page=2',
            'count': 100
        }
        assert context == {
            'previous_url': None,
            'next_url': 'http://127.0.0.1:9000/?page=2',
            'page_links': [
                PageLink('http://127.0.0.1:9000/', 1, True, False),
                PageLink('http://127.0.0.1:9000/?page=2', 2, False, False),
                PageLink('http://127.0.0.1:9000/?page=3', 3, False, False),
                PAGE_BREAK,
                PageLink('http://127.0.0.1:9000/?page=20', 20, False, False),
            ]
        }
        assert self.pagination.display_page_controls
        assert isinstance(self.pagination.to_html(), str)

    def test_second_page(self):
        request = Request(factory.get('/', {'page': 2}))
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        context = self.get_html_context()
        assert queryset == [6, 7, 8, 9, 10]
        assert content == {
            'results': [6, 7, 8, 9, 10],
            'previous': 'http://127.0.0.1:9000/',
            'next': 'http://127.0.0.1:9000/?page=3',
            'count': 10
        }
        assert context == {
            'previous_url': 'http://127.0.0.1:9000/',
            'next_url': 'http://127.0.0.1:9000/?page=3',
            'page_links': [
                PageLink('http://127.0.0.1:9000/', 1, False, False),
                PageLink('http://127.0.0.1:9000/?page=2', 2, True, False),
                PageLink('http://127.0.0.1:9000/?page=3', 3, False, False),
                PAGE_BREAK,
                PageLink('http://127.0.0.1:9000/?page=20', 20, False, False),
            ]
        }

    def test_last_page(self):
        request = Request(factory.get('/', {'page': 'last'}))
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        context = self.get_html_context()
        assert queryset == [96, 97, 98, 99, 100]
        assert content == {
            'results': [96, 97, 98, 99, 100],
            'previous': 'http://127.0.0.1:9000/?page=19',
            'next': None,
            'count': 10
        }
        assert context == {
            'previous_url': 'http://127.0.0.1:9000/?page=19',
            'next_url': None,
            'page_links': [
                PageLink('http://127.0.0.1:9000/', 1, False, False),
                PAGE_BREAK,
                PageLink('http://127.0.0.1:9000/?page=18', 18, False, False),
                PageLink('http://127.0.0.1:9000/?page=19', 19, False, False),
                PageLink('http://127.0.0.1:9000/?page=20', 20, True, False),
            ]
        }
class TestPageNumberPaginationOverride:
    """
    Unit tests for `pagination.PageNumberPagination`.
    the Django Paginator Class is overridden.
    """

    def setup(self):
        class OverriddenDjangoPaginator(DjangoPaginator):
            # override the count in our overridden Django Paginator
            # we will only return one page, with one item
            count = 1

        class ExamplePagination(pagination.PageNumberPagination):
            django_paginator_class = OverriddenDjangoPaginator
            page_size = 10

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_queryset(self.queryset, request))

    def get_paginated_content(self, queryset):
        response = self.pagination.get_paginated_response(queryset)
        return response.data

    def get_html_context(self):
        return self.pagination.get_html_context()

    def test_no_page_number(self):
        request = Request(factory.get('/'))
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        context = self.get_html_context()
        assert queryset == [1]
        assert content == {
            'results': [1, ],
            'previous': None,
            'next': None,
            'count': 1
        }
        assert context == {
            'previous_url': None,
            'next_url': None,
            'page_links': [
                PageLink('http://testserver/', 1, True, False),
            ]
        }
        assert not self.pagination.display_page_controls
        assert isinstance(self.pagination.to_html(), str)

    def test_invalid_page(self):
        request = Request(factory.get('/', {'page': 'invalid'}))
        with pytest.raises(exceptions.NotFound):
            self.paginate_queryset(request)


if __name__ == '__main__':
     unittest.main()