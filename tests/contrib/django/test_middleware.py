class TestHireFireMiddleware:
    def test_test_page(self, client):
        response = client.get('/hirefire/test')
        assert response.status_code == 200

    def test_token(self, client, settings):
        response = client.get('/hirefire/%s/info' % settings.HIREFIRE_TOKEN)
        assert response.status_code == 200

        response = client.get('/hirefire/not-the-token-%s/info' % settings.HIREFIRE_TOKEN)
        assert response.status_code == 404
