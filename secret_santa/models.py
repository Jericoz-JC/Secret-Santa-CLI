"""Pydantic models for Secret Santa data validation."""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID, uuid4


class Participant(BaseModel):
    """A person participating in the Secret Santa exchange."""
    id: UUID = None
    name: str
    email: EmailStr
    parent_email: Optional[EmailStr] = None
    cluster_id: Optional[UUID] = None

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid4()
        super().__init__(**data)


class Cluster(BaseModel):
    """A group of participants who should not be matched with each other."""
    id: UUID = None
    name: str
    member_ids: list[UUID] = []

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid4()
        super().__init__(**data)


class Assignment(BaseModel):
    """A Secret Santa assignment: giver buys a gift for receiver."""
    giver_id: UUID
    receiver_id: UUID
    giver_name: str
    receiver_name: str
    giver_email: EmailStr
    receiver_email: EmailStr
    parent_email: Optional[EmailStr] = None
    email_sent: bool = False


class Config(BaseModel):
    """Application configuration for email sending."""
    brevo_api_key: Optional[str] = None
    sender_email: Optional[EmailStr] = None
    sender_name: str = "Secret Santa"


class SecretSantaData(BaseModel):
    """Complete data store for the application."""
    participants: list[Participant] = []
    clusters: list[Cluster] = []
    assignments: list[Assignment] = []
    config: Config = Config()
