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
    Create random Secret Santa assignments respecting cluster and kid rules.
    
    Algorithm:
    1. Separate kids and adults
    2. Match kids only with other kids, adults only with adults
    3. For each group, shuffle and assign respecting cluster rules
    4. Use backtracking if we get stuck
    
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
    
    # Separate kids and adults
    kids = [p for p in participants if p.is_kid]
    adults = [p for p in participants if not p.is_kid]
    
    # Validate kid group
    if len(kids) == 1:
        raise MatcherError(
            "Only 1 kid found! Kids can only be matched with other kids. "
            "Add more kids or remove the --kid flag."
        )
    
    # Build cluster membership map
    cluster_map: dict[UUID, UUID | None] = {}
    for p in participants:
        cluster_map[p.id] = p.cluster_id
    
    # Build kid map
    kid_map: dict[UUID, bool] = {}
    for p in participants:
        kid_map[p.id] = p.is_kid
    
    # Check if matchmaking is possible for each group
    _validate_cluster_sizes(kids, cluster_map, "kids")
    _validate_cluster_sizes(adults, cluster_map, "adults")
    
    # Try to find valid assignments
    for attempt in range(max_attempts):
        result = _try_assign(participants, cluster_map, kid_map)
        if result is not None:
            return result
    
    raise MatcherError(
        f"Could not find valid assignments after {max_attempts} attempts. "
        "This may happen with complex cluster configurations or kid/adult group sizes."
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
    kid_map: dict[UUID, bool]
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
            and kid_map.get(r.id, False) == giver_is_kid  # Kids match kids, adults match adults
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

