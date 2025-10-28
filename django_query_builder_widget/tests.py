from django.test import TestCase

from .widgets import QueryBuilderWidget


class TestQueryBuilderWidget(TestCase):
    def test_media_js(self):
        widget = QueryBuilderWidget()
        html = widget.media.render()
        expected_js = [
            '/static/query-builder-widget/js/lib/jquery-3.6.0.min.js',
            '/static/query-builder-widget/js/lib/query-builder.standalone.min.js',
        ]
        for expected in expected_js:
            self.assertIn(expected, html)

    def test_media_css(self):
        widget = QueryBuilderWidget()
        html = widget.media.render()
        expected_css = [
            '/static/query-builder-widget/css/lib/query-builder.default.min.css',
            '/static/query-builder-widget/css/query-builder-widget.css',
        ]
        for expected in expected_css:
            self.assertIn(expected, html)
