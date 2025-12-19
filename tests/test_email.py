"""Tests for email functionality."""

import pytest

from secret_santa.email import create_email_html


class TestEmailContent:
    """Tests for email HTML content."""
    
    def test_email_contains_receiver_name(self):
        """Email should contain the receiver's name."""
        html = create_email_html("John Doe")
        
        assert "John Doe" in html
    
    def test_email_contains_gift_limit(self):
        """Email should contain the gift limit."""
        html = create_email_html("Jane", gift_limit=25)
        
        assert "$25" in html
    
    def test_email_contains_custom_gift_limit(self):
        """Email should respect custom gift limit."""
        html = create_email_html("Jane", gift_limit=50)
        
        assert "$50" in html
    
    def test_email_contains_verification_code(self):
        """Email should contain the verification code."""
        html = create_email_html("Jane", verification_code="A1B2")
        
        assert "A1B2" in html
    
    def test_email_has_verification_section(self):
        """Email should have verification code section."""
        html = create_email_html("Jane", verification_code="XY12")
        
        assert "Verification Code" in html
        assert "XY12" in html
    
    def test_email_has_gift_limit_section(self):
        """Email should have gift limit section."""
        html = create_email_html("Jane", gift_limit=25)
        
        assert "Gift Limit" in html
    
    def test_email_is_valid_html(self):
        """Email should be valid HTML with proper structure."""
        html = create_email_html("Test", gift_limit=25, verification_code="TEST")
        
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "</html>" in html
        assert "<body>" in html
        assert "</body>" in html
    
    def test_email_contains_secret_reminder(self):
        """Email should remind to keep it a secret."""
        html = create_email_html("Test")
        
        assert "secret" in html.lower()
    
    def test_default_gift_limit_is_25(self):
        """Default gift limit should be $25."""
        html = create_email_html("Test")
        
        assert "$25" in html
