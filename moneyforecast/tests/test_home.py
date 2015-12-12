def test_home_with_admin(admin_client):
    response = admin_client.get('/')
    assert response.status_code == 200
