"""Tests for CLI commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from secret_santa.cli import cli
from secret_santa.storage import Storage


@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage for testing."""
    return Storage(data_dir=tmp_path / ".secret-santa")


@pytest.fixture
def cli_runner(temp_storage, monkeypatch):
    """Create a CLI runner with temporary storage."""
    # Monkeypatch the global storage in cli module
    import secret_santa.cli as cli_module
    monkeypatch.setattr(cli_module, 'storage', temp_storage)
    return CliRunner()


class TestQuickClustersCommand:
    """Tests for the 'santa clusters' shortcut command."""
    
    def test_clusters_shortcut_shows_no_clusters(self, cli_runner):
        """santa clusters should show no clusters message when empty."""
        result = cli_runner.invoke(cli, ['clusters'])
        
        assert result.exit_code == 0
        assert "No clusters" in result.output or "no clusters" in result.output.lower()
    
    def test_clusters_shortcut_works(self, cli_runner):
        """santa clusters should list created clusters."""
        # Create a cluster via the regular command
        cli_runner.invoke(cli, ['cluster', 'create', 'Test Family'], input='y\n')
        
        # Use the shortcut
        result = cli_runner.invoke(cli, ['clusters'])
        
        assert result.exit_code == 0
        assert "Test Family" in result.output


class TestAddWithClusterFlag:
    """Tests for the --cluster flag on 'santa add'."""
    
    def test_add_with_existing_cluster(self, cli_runner):
        """Adding with --cluster to existing cluster should work."""
        # Create a cluster first
        cli_runner.invoke(cli, ['cluster', 'create', 'Smith Family'], input='y\n')
        
        # Add a person to that cluster
        result = cli_runner.invoke(cli, [
            'add', 'John', 'john@test.com', '--cluster', 'Smith Family'
        ])
        
        assert result.exit_code == 0
        assert "Added" in result.output
        assert "cluster" in result.output.lower()
    
    def test_add_creates_new_cluster(self, cli_runner):
        """Adding with --cluster should auto-create cluster if needed."""
        result = cli_runner.invoke(cli, [
            'add', 'Alice', 'alice@test.com', '--cluster', 'New Family'
        ])
        
        assert result.exit_code == 0
        assert "Created new cluster" in result.output or "New Family" in result.output
        assert "Added" in result.output
    
    def test_add_short_flag_c(self, cli_runner):
        """The -c short flag should work for --cluster."""
        result = cli_runner.invoke(cli, [
            'add', 'Bob', 'bob@test.com', '-c', 'Another Family'
        ])
        
        assert result.exit_code == 0
        assert "Added" in result.output


class TestAddKidOption:
    """Tests for the --kid option."""
    
    def test_add_kid_shows_kid_label(self, cli_runner):
        """Adding a kid should show the KID label."""
        result = cli_runner.invoke(cli, [
            'add', 'Tommy', 'parent@test.com', '--kid'
        ])
        
        assert result.exit_code == 0
        assert "KID" in result.output
    
    def test_add_kid_short_flag(self, cli_runner):
        """The -k short flag should work for --kid."""
        result = cli_runner.invoke(cli, [
            'add', 'Sara', 'parent@test.com', '-k'
        ])
        
        assert result.exit_code == 0
        assert "KID" in result.output


class TestCombinedFlags:
    """Tests for combining multiple flags."""
    
    def test_add_kid_with_cluster(self, cli_runner):
        """Should be able to add a kid directly to a cluster."""
        result = cli_runner.invoke(cli, [
            'add', 'Tommy', 'parent@test.com', '--kid', '--cluster', 'Johnson Family'
        ])
        
        assert result.exit_code == 0
        assert "KID" in result.output
        assert "cluster" in result.output.lower() or "Johnson Family" in result.output
