"""
Shared pagination class. `page_size_query_param` lets any list endpoint's
caller ask for more than the default 25/page (capped at `max_page_size`) —
added when the invoice creation UX's client picker needed to see all of a
company's clients, not just the first page, but this benefits every list
endpoint, not just that one.
"""

from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100
