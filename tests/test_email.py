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


class TestKidParentEmail:
    """Tests for kid assignment emails sent to parents."""
    
    def test_kid_email_mentions_child_name(self):
        """Kid email should mention the child's name."""
        from secret_santa.email import create_kid_email_html
        
        html = create_kid_email_html(
            child_name="Tommy",
            receiver_name="Alice"
        )
        
        assert "Tommy" in html
    
    def test_kid_email_contains_receiver(self):
        """Kid email should contain the receiver's name."""
        from secret_santa.email import create_kid_email_html
        
        html = create_kid_email_html(
            child_name="Tommy",
            receiver_name="Alice"
        )
        
        assert "Alice" in html
    
    def test_kid_email_shows_parent_context(self):
        """Kid email should indicate it's for a parent about their child."""
        from secret_santa.email import create_kid_email_html
        
        html = create_kid_email_html(
            child_name="Tommy",
            receiver_name="Alice"
        )
        
        assert "Your child" in html or "your child" in html.lower()
    
    def test_kid_email_has_child_banner(self):
        """Kid email should have a child banner section."""
        from secret_santa.email import create_kid_email_html
        
        html = create_kid_email_html(
            child_name="Tommy",
            receiver_name="Alice"
        )
        
        assert "child-banner" in html
    
    def test_kid_email_contains_gift_limit(self):
        """Kid email should contain the gift limit."""
        from secret_santa.email import create_kid_email_html
        
        html = create_kid_email_html(
            child_name="Tommy",
            receiver_name="Alice",
            gift_limit=30
        )
        
        assert "$30" in html
    
    def test_kid_email_contains_verification_code(self):
        """Kid email should contain the verification code."""
        from secret_santa.email import create_kid_email_html
        
        html = create_kid_email_html(
            child_name="Tommy",
            receiver_name="Alice",
            verification_code="AB12"
        )
        
        assert "AB12" in html
    
    def test_kid_email_personalized_footer(self):
        """Kid email footer should mention helping the child keep it a secret."""
        from secret_santa.email import create_kid_email_html
        
        html = create_kid_email_html(
            child_name="Tommy",
            receiver_name="Alice"
        )
        
        assert "Help Tommy keep it a secret" in html
    
    def test_kid_email_is_valid_html(self):
        """Kid email should be valid HTML with proper structure."""
        from secret_santa.email import create_kid_email_html
        
        html = create_kid_email_html(
            child_name="Tommy",
            receiver_name="Alice"
        )
        
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "</html>" in html

