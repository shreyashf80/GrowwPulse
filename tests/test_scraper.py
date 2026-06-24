"""Tests for the Play Store scraper module."""

import pytest
from unittest.mock import patch, MagicMock

from mcp_servers.playstore_reviews.scraper import _is_valid_review, fetch_reviews_with_filters, Review

class TestReviewFilters:
    def test_short_reviews_rejected(self):
        """Reviews with < 8 words should be rejected."""
        assert _is_valid_review("This is a short review.") is False
        assert _is_valid_review("One two three four five six seven.") is False
        assert _is_valid_review("One two three four five six seven eight.") is True
        
    def test_emojis_rejected(self):
        """Reviews containing emojis should be rejected."""
        assert _is_valid_review("This is a sufficiently long review but it has emojis 🚀.") is False
        assert _is_valid_review("This app is amazing! I love using it every day 😊.") is False
        assert _is_valid_review("This is a completely normal English review without any emojis.") is True
        
    def test_non_english_rejected(self):
        """Non-English reviews should be rejected."""
        assert _is_valid_review("Esta es una reseña lo suficientemente larga pero en español.") is False
        assert _is_valid_review("C'est une très bonne application que j'utilise tous les jours.") is False
        assert _is_valid_review("This is a completely normal English review without any emojis.") is True

class TestScraper:
    @patch("mcp_servers.playstore_reviews.scraper.fetch_google_reviews")
    def test_fetch_reviews_with_filters_mock(self, mock_fetch):
        """Test fetch logic with mock to verify schema mapping and filtering."""
        # Setup mock to return a mix of valid and invalid reviews
        mock_result = [
            # Valid
            {
                "reviewId": "r1", "userName": "User 1", "score": 5, "content": "This is a great app, I love using it every single day.",
                "at": "2023-01-01T12:00:00", "thumbsUpCount": 10, "reviewCreatedVersion": "1.0.0"
            },
            # Invalid (too short)
            {
                "reviewId": "r2", "userName": "User 2", "score": 4, "content": "Good app.",
                "at": "2023-01-02T12:00:00", "thumbsUpCount": 0, "reviewCreatedVersion": "1.0.0"
            },
            # Invalid (emoji)
            {
                "reviewId": "r3", "userName": "User 3", "score": 3, "content": "This is a great app but it has emojis 🚀 and crashes sometimes.",
                "at": "2023-01-03T12:00:00", "thumbsUpCount": 2, "reviewCreatedVersion": "1.0.0"
            },
            # Valid
            {
                "reviewId": "r4", "userName": "User 4", "score": 2, "content": "I am writing a long enough review to pass the length check.",
                "at": "2023-01-04T12:00:00", "thumbsUpCount": 5, "reviewCreatedVersion": "1.0.1"
            }
        ]
        
        mock_fetch.return_value = (mock_result, None)
        
        reviews = fetch_reviews_with_filters("com.test.app", count=10)
        
        # Only r1 and r4 should survive the filters
        assert len(reviews) == 2
        assert reviews[0].review_id == "r1"
        assert reviews[0].text == "This is a great app, I love using it every single day."
        assert reviews[1].review_id == "r4"
        assert reviews[1].text == "I am writing a long enough review to pass the length check."

    @pytest.mark.integration
    def test_fetch_real_reviews(self):
        """Integration test fetching real reviews to validate the schema mapping."""
        # Using a very small count to just verify schema without taking long
        reviews = fetch_reviews_with_filters("com.nextbillion.groww", count=5)
        
        assert len(reviews) <= 5
        for review in reviews:
            assert isinstance(review, Review)
            assert review.review_id
            assert review.author
            assert review.rating in range(1, 6)
            assert review.text
            assert review.timestamp
            assert isinstance(review.thumbs_up, int)
            # app_version can be None, but if present it's a string
            if review.app_version is not None:
                assert isinstance(review.app_version, str)
            
            # Verify filters applied
            assert len(review.text.split()) >= 8
            # Emojis filter might be hard to strictly assert without the emoji module, but we can trust the scraper logic test above
