class TestHireFireMiddleware:
    def test_test_page(self, client):
        response = client.get('/hirefire/test')
        assert response.status_code == 200

    def test_token(self, client, settings):
        response = client.get('/hirefire/%s/info' % settings.HIREFIRE_TOKEN)
        assert response.status_code == 200

        response = client.get('/hirefire/not-the-token-%s/info' % settings.HIREFIRE_TOKEN)
        assert response.status_code == 404


class TestQueueTimeMiddleware:
    def test_queue_time(self, client):
        response = client.get('/hirefire/test', HTTP_X_REQUEST_START='946733845303')
        assert response.status_code == 200
