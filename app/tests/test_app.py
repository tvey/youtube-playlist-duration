import json

result_url = '/result'


def test_home_view_is_ok(client):
    response = client.get('/')
    print(dir(response))
    assert response.status_code == 200


def test_result_view_not_allows_get(client):
    response = client.get(result_url)
    assert response.status_code == 405
    assert 'Method Not Allowed' in str(response.data)


def test_result_view(client, playlist_id_fix):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {'playlist': playlist_id_fix}  # !! FAILS CUZ IT'S EMPTY
    response = client.post(result_url, data=json.dumps(data), headers=headers)
    print(response.data)
    assert response.is_json
    assert response.status_code == 200