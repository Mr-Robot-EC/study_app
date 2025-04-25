import uuid
from unittest.mock import patch, MagicMock
import pytest


class TestTokenHandling:
    def test_refresh_token(self, auth_client, valid_access_token, mock_env_vars):
        # Mocked token verification
        with patch('backend.services.auth_service.src.api.tokens.get_user') as mock_get_user:
            mock_user = MagicMock()
            mock_user.id = uuid.UUID(TEST_USER_ID)
            mock_user.email = TEST_EMAIL

            mock_get_user.return_value = mock_user

            # Mocked refresh token in DB
            with patch('backend.services.auth_service.src.db.models.token.RefreshToken') as mock_refresh_model:
                # Mock the database query
                with patch('backend.services.auth_service.src.db.session.SessionLocal') as mock_session:
                    mock_db = MagicMock()
                    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
                    mock_session.return_value = mock_db

                    response = auth_client.post(
                        "/token/refresh",
                        json={"refresh_token": valid_access_token}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "access_token" in data
                    assert "refresh_token" in data