"""TECH-03: base layout, message area and inline error display."""
from django import forms
from django.template.loader import render_to_string


class _DemoForm(forms.Form):
    amount = forms.DecimalField(min_value=0.01)


def test_home_page_has_nav(client):
    html = client.get("/").content.decode()
    assert "<nav>" in html
    assert "SmartSpend" in html


def test_form_errors_partial_shows_field_error():
    form = _DemoForm(data={"amount": "0"})
    assert not form.is_valid()
    html = render_to_string("partials/form_errors.html", {"form": form})
    assert "Amount" in html
    assert 'class="msg error"' in html


def test_form_errors_partial_empty_for_valid_form():
    form = _DemoForm(data={"amount": "5"})
    assert form.is_valid()
    assert "msg error" not in render_to_string("partials/form_errors.html", {"form": form})