"""Pydantic models for Secret Santa data validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID, uuid4


class Participant(BaseModel):
    """A person participating in the Secret Santa exchange."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr
    parent_email: Optional[EmailStr] = None
    cluster_id: Optional[UUID] = None
    is_kid: bool = False  # Kids are matched only with other kids


class Cluster(BaseModel):
    """A group of participants who should not be matched with each other."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    member_ids: list[UUID] = Field(default_factory=list)


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
    participants: list[Participant] = Field(default_factory=list)
    clusters: list[Cluster] = Field(default_factory=list)
    assignments: list[Assignment] = Field(default_factory=list)
    config: Config = Field(default_factory=Config)
