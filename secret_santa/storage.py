"""JSON file storage for Secret Santa data."""

import json
from pathlib import Path
from typing import Optional
from uuid import UUID

from .models import SecretSantaData, Participant, Cluster, Assignment, Config


class UUIDEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles UUID objects."""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class Storage:
    """Handles persistent storage of Secret Santa data in JSON format."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize storage with optional custom data directory."""
        if data_dir is None:
            self.data_dir = Path.home() / ".secret-santa"
        else:
            self.data_dir = data_dir
        self.data_file = self.data_dir / "data.json"
        self._ensure_data_dir()
        self._data: Optional[SecretSantaData] = None

    def _ensure_data_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> SecretSantaData:
        """Load data from JSON file, creating default if not exists."""
        if self._data is not None:
            return self._data

        if not self.data_file.exists():
            self._data = SecretSantaData()
            self.save()
        else:
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                self._data = SecretSantaData.model_validate(raw_data)
            except (json.JSONDecodeError, Exception):
                # Corrupted file, start fresh
                self._data = SecretSantaData()
                self.save()

        return self._data

    def save(self) -> None:
        """Save current data to JSON file."""
        if self._data is None:
            return

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(
                self._data.model_dump(),
                f,
                indent=2,
                cls=UUIDEncoder
            )

    # Participant operations
    def add_participant(self, participant: Participant) -> Participant:
        """Add a new participant to the store."""
        data = self.load()
        # Check for duplicate email
        for p in data.participants:
            if p.email == participant.email:
                raise ValueError(f"Participant with email {participant.email} already exists")
        data.participants.append(participant)
        self.save()
        return participant

    def get_participant_by_name(self, name: str) -> Optional[Participant]:
        """Find a participant by name (case-insensitive)."""
        data = self.load()
        name_lower = name.lower()
        for p in data.participants:
            if p.name.lower() == name_lower:
                return p
        return None

    def get_participant_by_id(self, id: UUID) -> Optional[Participant]:
        """Find a participant by ID."""
        data = self.load()
        for p in data.participants:
            if p.id == id:
                return p
        return None

    def remove_participant(self, name: str) -> bool:
        """Remove a participant by name. Returns True if found and removed."""
        data = self.load()
        name_lower = name.lower()
        for i, p in enumerate(data.participants):
            if p.name.lower() == name_lower:
                # Also remove from any clusters
                for cluster in data.clusters:
                    if p.id in cluster.member_ids:
                        cluster.member_ids.remove(p.id)
                data.participants.pop(i)
                self.save()
                return True
        return False

    def list_participants(self) -> list[Participant]:
        """Get all participants."""
        return self.load().participants

    # Cluster operations
    def create_cluster(self, cluster: Cluster) -> Cluster:
        """Create a new cluster."""
        data = self.load()
        # Check for duplicate name
        for c in data.clusters:
            if c.name.lower() == cluster.name.lower():
                raise ValueError(f"Cluster '{cluster.name}' already exists")
        data.clusters.append(cluster)
        self.save()
        return cluster

    def get_cluster_by_name(self, name: str) -> Optional[Cluster]:
        """Find a cluster by name (case-insensitive)."""
        data = self.load()
        name_lower = name.lower()
        for c in data.clusters:
            if c.name.lower() == name_lower:
                return c
        return None

    def add_to_cluster(self, cluster_name: str, participant_name: str) -> None:
        """Add a participant to a cluster."""
        data = self.load()
        cluster = self.get_cluster_by_name(cluster_name)
        participant = self.get_participant_by_name(participant_name)

        if cluster is None:
            raise ValueError(f"Cluster '{cluster_name}' not found")
        if participant is None:
            raise ValueError(f"Participant '{participant_name}' not found")

        # Remove from previous cluster if any
        for c in data.clusters:
            if participant.id in c.member_ids:
                c.member_ids.remove(participant.id)

        # Add to new cluster
        cluster.member_ids.append(participant.id)
        participant.cluster_id = cluster.id
        self.save()

    def remove_from_cluster(self, cluster_name: str, participant_name: str) -> None:
        """Remove a participant from a cluster."""
        data = self.load()
        cluster = self.get_cluster_by_name(cluster_name)
        participant = self.get_participant_by_name(participant_name)

        if cluster is None:
            raise ValueError(f"Cluster '{cluster_name}' not found")
        if participant is None:
            raise ValueError(f"Participant '{participant_name}' not found")
        if participant.id not in cluster.member_ids:
            raise ValueError(f"'{participant_name}' is not in cluster '{cluster_name}'")

        cluster.member_ids.remove(participant.id)
        participant.cluster_id = None
        self.save()

    def remove_cluster(self, name: str) -> bool:
        """Remove a cluster by name and clear participant references."""
        data = self.load()
        cluster = self.get_cluster_by_name(name)
        if cluster is None:
            return False
        
        # Clear cluster_id from all members
        for p in data.participants:
            if p.cluster_id == cluster.id:
                p.cluster_id = None
        
        data.clusters = [c for c in data.clusters if c.id != cluster.id]
        self.save()
        return True

    def list_clusters(self) -> list[Cluster]:
        """Get all clusters."""
        return self.load().clusters

    # Assignment operations
    def save_assignments(self, assignments: list[Assignment]) -> None:
        """Save new assignments, replacing any existing ones."""
        data = self.load()
        data.assignments = assignments
        self.save()

    def get_assignments(self) -> list[Assignment]:
        """Get current assignments."""
        return self.load().assignments

    def mark_email_sent(self, giver_id: UUID) -> None:
        """Mark an assignment's email as sent."""
        data = self.load()
        for a in data.assignments:
            if a.giver_id == giver_id:
                a.email_sent = True
                break
        self.save()

    # Config operations
    def get_config(self) -> Config:
        """Get application config."""
        return self.load().config

    def save_config(self, config: Config) -> None:
        """Save application config."""
        data = self.load()
        data.config = config
        self.save()
