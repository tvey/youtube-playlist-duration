import json
import random
import string

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.main import app


@pytest_asyncio.fixture(scope='module')
def client():
    client = TestClient(app)
    yield client


with open('tests/data.json') as f:
    test_data = json.load(f)


@pytest.fixture
def playlist_id_fix():
    valid_ids = test_data['valid_ids']
    return random.choice(valid_ids)


@pytest.fixture
def invalid_playlist_id_fix():
    chars = string.ascii_letters + string.digits + '-_'
    random_chars = ''.join(random.choices(chars, k=random.randint(10, 30)))
    return f'PL{random_chars}'
