"""Matchmaking algorithm for Secret Santa assignments."""

import hashlib
import random
from uuid import UUID

from .models import Participant, Assignment
from .storage import Storage


def generate_verification_code(giver_id: UUID, receiver_id: UUID) -> str:
    """
    Generate a 4-character verification code from giver and receiver IDs.
    
    This code is deterministic and can be used by participants to verify
    their assignment matches what they received in their email.
    """
    combined = f"{giver_id}:{receiver_id}"
    hash_digest = hashlib.sha256(combined.encode()).hexdigest()
    return hash_digest[:4].upper()


class MatcherError(Exception):
    """Raised when matchmaking is impossible."""
    pass


def create_assignments(
    storage: Storage,
    max_attempts: int = 1000,
    separate_kids: bool = False
) -> list[Assignment]:
    """
    Create random Secret Santa assignments respecting cluster rules.
    
    Algorithm:
    1. If separate_kids is True, match kids only with other kids
    2. For each person, find valid receivers (not self, not same cluster)
    3. Use backtracking if we get stuck
    
    Args:
        storage: Storage instance to get participants and clusters
        max_attempts: Maximum shuffle attempts before giving up
        separate_kids: If True, kids only match with kids, adults with adults
    
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
    
    # Build kid map
    kid_map: dict[UUID, bool] = {}
    for p in participants:
        kid_map[p.id] = p.is_kid
    
    # If separating kids, validate kid group sizes
    if separate_kids:
        kids = [p for p in participants if p.is_kid]
        adults = [p for p in participants if not p.is_kid]
        
        # Validate kid group
        if len(kids) == 1:
            raise MatcherError(
                "Only 1 kid found! With --separate-kids, kids can only be matched with other kids. "
                "Add more kids or don't use --separate-kids."
            )
        
        # Check if matchmaking is possible for each group
        _validate_cluster_sizes(kids, cluster_map, "kids")
        _validate_cluster_sizes(adults, cluster_map, "adults")
    else:
        # Without separation, validate all participants together
        _validate_cluster_sizes(participants, cluster_map, "participants")
    
    # Try to find valid assignments
    for attempt in range(max_attempts):
        result = _try_assign(participants, cluster_map, kid_map, separate_kids)
        if result is not None:
            return result
    
    raise MatcherError(
        f"Could not find valid assignments after {max_attempts} attempts. "
        "This may happen with complex cluster configurations."
    )


def _validate_cluster_sizes(
    group: list[Participant],
    cluster_map: dict[UUID, UUID | None],
    group_name: str
) -> None:
    """Validate that no cluster has more than half of the group."""
    if len(group) < 2:
        return  # Skip validation for empty or single-person groups
    
    cluster_counts: dict[UUID | None, int] = {}
    for p in group:
        cid = p.cluster_id
        cluster_counts[cid] = cluster_counts.get(cid, 0) + 1
    
    half = len(group) / 2
    for cid, count in cluster_counts.items():
        if cid is not None and count > half:
            raise MatcherError(
                f"Cluster has {count} members but only {len(group)} {group_name}. "
                f"Each cluster must have less than half of the {group_name} for valid matching."
            )


def _try_assign(
    participants: list[Participant],
    cluster_map: dict[UUID, UUID | None],
    kid_map: dict[UUID, bool],
    separate_kids: bool
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
        giver_is_kid = kid_map.get(giver.id, False)
        
        # Find valid receivers for this giver
        valid_receivers = [
            r for r in receivers
            if r.id not in used_receivers
            and r.id != giver.id  # Can't give to self
            and not _same_cluster(giver.id, r.id, cluster_map)  # Can't give to cluster member
            and (not separate_kids or kid_map.get(r.id, False) == giver_is_kid)  # Kids match kids only if separate_kids
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
            verification_code=generate_verification_code(giver.id, receiver.id),
            is_kid=giver.is_kid,
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


