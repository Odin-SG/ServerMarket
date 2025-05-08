import pytest
import json
from werkzeug.datastructures import MultiDict
from app.admin.forms import ServerForm
from app.models.server import Server


def test_valid_specifications(app):
    with app.test_request_context():
        form = ServerForm(formdata=MultiDict({
            'model_name': 'Mod',
            'slug': 'mod',
            'description': 'descrdescr',
            'price': '1.0',
            'specifications': json.dumps({'a': 1})
        }))
        assert form.validate() is True


def test_invalid_specifications(app):
    with app.test_request_context():
        form = ServerForm(formdata=MultiDict({
            'model_name': 'Mod',
            'slug': 'mod',
            'description': 'descrdescr',
            'price': '1.0',
            'specifications': '{bad json'
        }))
        assert form.validate() is False
        assert 'Неверный JSON' in form.specifications.errors[0]


def test_price_must_be_non_negative(app):
    with app.test_request_context():
        form = ServerForm(formdata=MultiDict({
            'model_name': 'Mod',
            'slug': 'mod2',
            'description': 'descrdescr',
            'price': '-5.00',
            'specifications': ''
        }))
        assert form.validate() is False
        errs = ' '.join(form.price.errors)
        assert 'at least' in errs or 'Number must' in errs


def test_slug_uniqueness_validation(app):
    from app import db
    s = Server(model_name='X', slug='unique-slug', description='descrdescr', price=1, specifications={},
               is_available=True)
    db.session.add(s)
    db.session.commit()
    with app.test_request_context():
        form = ServerForm(formdata=MultiDict({
            'model_name': 'Y',
            'slug': 'unique-slug',
            'description': 'another description',
            'price': '2.00',
            'specifications': ''
        }))
        assert form.validate() is False
        assert 'Slug уже используется' in form.slug.errors


def test_description_length(app):
    with app.test_request_context():
        form = ServerForm(formdata=MultiDict({
            'model_name': 'Mod',
            'slug': 'mod3',
            'description': 'short',
            'price': '1.00',
            'specifications': ''
        }))
        assert form.validate() is False
        assert 'Field must be at least 10 characters long.' in form.description.errors[0]
