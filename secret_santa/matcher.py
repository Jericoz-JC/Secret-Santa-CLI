"""Matchmaking algorithm for Secret Santa assignments."""

import random
from uuid import UUID

from .models import Participant, Assignment
from .storage import Storage


class MatcherError(Exception):
    """Raised when matchmaking is impossible."""
    pass


def create_assignments(storage: Storage, max_attempts: int = 1000) -> list[Assignment]:
    """
    Create random Secret Santa assignments respecting cluster rules.
    
    Algorithm:
    1. Shuffle all participants
    2. For each person, find valid receivers (not self, not same cluster)
    3. Use backtracking if we get stuck
    
    Args:
        storage: Storage instance to get participants and clusters
        max_attempts: Maximum shuffle attempts before giving up
    
    Returns:
        List of Assignment objects
    
    Raises:
        MatcherError: If valid assignments are impossible
    """
    participants = storage.list_participants()
    
    if len(participants) < 2:
        raise MatcherError("Need at least 2 participants for Secret Santa!")
    
    # Build cluster membership map
    cluster_map: dict[UUID, UUID | None] = {}
    for p in participants:
        cluster_map[p.id] = p.cluster_id
    
    # Check if matchmaking is possible
    # Count participants per cluster
    cluster_counts: dict[UUID | None, int] = {}
    for p in participants:
        cid = p.cluster_id
        cluster_counts[cid] = cluster_counts.get(cid, 0) + 1
    
    # If any cluster has more than half the participants, it's impossible
    half = len(participants) / 2
    for cid, count in cluster_counts.items():
        if cid is not None and count > half:
            raise MatcherError(
                f"Cluster has {count} members but only {len(participants)} total participants. "
                f"Each cluster must have less than half of all participants for valid matching."
            )
    
    # Try to find valid assignments
    for attempt in range(max_attempts):
        result = _try_assign(participants, cluster_map)
        if result is not None:
            return result
    
    raise MatcherError(
        f"Could not find valid assignments after {max_attempts} attempts. "
        "This may happen with complex cluster configurations."
    )


def _try_assign(
    participants: list[Participant],
    cluster_map: dict[UUID, UUID | None]
) -> list[Assignment] | None:
    """
    Attempt to create valid assignments using randomized approach.
    
    Returns None if this attempt failed.
    """
    givers = participants.copy()
    receivers = participants.copy()
    random.shuffle(givers)
    random.shuffle(receivers)
    
    assignments: list[Assignment] = []
    used_receivers: set[UUID] = set()
    
    for giver in givers:
        # Find valid receivers for this giver
        valid_receivers = [
            r for r in receivers
            if r.id not in used_receivers
            and r.id != giver.id  # Can't give to self
            and not _same_cluster(giver.id, r.id, cluster_map)  # Can't give to cluster member
        ]
        
        if not valid_receivers:
            # This attempt failed
            return None
        
        # Pick a random valid receiver
        receiver = random.choice(valid_receivers)
        used_receivers.add(receiver.id)
        
        assignments.append(Assignment(
            giver_id=giver.id,
            receiver_id=receiver.id,
            giver_name=giver.name,
            receiver_name=receiver.name,
            giver_email=giver.email,
            receiver_email=receiver.email,
            parent_email=giver.parent_email,
        ))
    
    return assignments


def _same_cluster(id1: UUID, id2: UUID, cluster_map: dict[UUID, UUID | None]) -> bool:
    """Check if two participants are in the same cluster."""
    c1 = cluster_map.get(id1)
    c2 = cluster_map.get(id2)
    
    # If either has no cluster, they're not in the same cluster
    if c1 is None or c2 is None:
        return False
    
    return c1 == c2
