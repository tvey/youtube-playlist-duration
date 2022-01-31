import json


result_url = '/result'


def test_home_view_is_ok(client):
    response = client.get('/')
    assert response.status_code == 200


def test_result_view_get_not_allowed(client):
    response = client.get(result_url)
    assert response.status_code == 405
    assert 'Method Not Allowed' in response.text


def test_result_view(client, playlist_id_fix):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {'playlist': playlist_id_fix}
    response = client.post(result_url, data=json.dumps(data), headers=headers)
    assert response.status_code == 200
