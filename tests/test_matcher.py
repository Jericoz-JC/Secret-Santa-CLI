"""Tests for the matchmaking algorithm."""

import pytest
from uuid import uuid4

from secret_santa.models import Participant, Cluster, SecretSantaData
from secret_santa.matcher import create_assignments, MatcherError, _same_cluster


class MockStorage:
    """Mock storage for testing."""
    
    def __init__(self, participants: list[Participant] = None, clusters: list[Cluster] = None):
        self.participants = participants or []
        self.clusters = clusters or []
    
    def list_participants(self):
        return self.participants
    
    def list_clusters(self):
        return self.clusters


class TestSameCluster:
    """Tests for the _same_cluster helper function."""
    
    def test_both_no_cluster(self):
        """Two participants without clusters are not in the same cluster."""
        id1, id2 = uuid4(), uuid4()
        cluster_map = {id1: None, id2: None}
        assert _same_cluster(id1, id2, cluster_map) is False
    
    def test_one_no_cluster(self):
        """One participant without cluster is not in same cluster as one with cluster."""
        id1, id2 = uuid4(), uuid4()
        cluster_id = uuid4()
        cluster_map = {id1: None, id2: cluster_id}
        assert _same_cluster(id1, id2, cluster_map) is False
    
    def test_same_cluster(self):
        """Two participants in the same cluster are detected."""
        id1, id2 = uuid4(), uuid4()
        cluster_id = uuid4()
        cluster_map = {id1: cluster_id, id2: cluster_id}
        assert _same_cluster(id1, id2, cluster_map) is True
    
    def test_different_clusters(self):
        """Two participants in different clusters are not in same cluster."""
        id1, id2 = uuid4(), uuid4()
        cluster_id1, cluster_id2 = uuid4(), uuid4()
        cluster_map = {id1: cluster_id1, id2: cluster_id2}
        assert _same_cluster(id1, id2, cluster_map) is False


class TestCreateAssignments:
    """Tests for the main assignment algorithm."""
    
    def test_minimum_participants(self):
        """Need at least 2 participants."""
        storage = MockStorage([
            Participant(name="Alice", email="alice@test.com")
        ])
        with pytest.raises(MatcherError, match="at least 2 participants"):
            create_assignments(storage)
    
    def test_no_self_assignment(self):
        """No one should get themselves."""
        participants = [
            Participant(name=f"Person{i}", email=f"p{i}@test.com")
            for i in range(10)
        ]
        storage = MockStorage(participants)
        
        # Run multiple times since it's random
        for _ in range(50):
            assignments = create_assignments(storage)
            for a in assignments:
                assert a.giver_id != a.receiver_id
    
    def test_everyone_gives_and_receives(self):
        """Everyone should give exactly once and receive exactly once."""
        participants = [
            Participant(name=f"Person{i}", email=f"p{i}@test.com")
            for i in range(10)
        ]
        storage = MockStorage(participants)
        
        assignments = create_assignments(storage)
        
        givers = {a.giver_id for a in assignments}
        receivers = {a.receiver_id for a in assignments}
        participant_ids = {p.id for p in participants}
        
        assert givers == participant_ids
        assert receivers == participant_ids
    
    def test_cluster_exclusion(self):
        """Participants in the same cluster should never match."""
        cluster = Cluster(name="Family")
        
        alice = Participant(name="Alice", email="alice@test.com", cluster_id=cluster.id)
        bob = Participant(name="Bob", email="bob@test.com", cluster_id=cluster.id)
        charlie = Participant(name="Charlie", email="charlie@test.com")
        diana = Participant(name="Diana", email="diana@test.com")
        
        cluster.member_ids = [alice.id, bob.id]
        
        storage = MockStorage(
            participants=[alice, bob, charlie, diana],
            clusters=[cluster]
        )
        
        # Run multiple times
        for _ in range(50):
            assignments = create_assignments(storage)
            for a in assignments:
                # If giver is Alice or Bob, receiver shouldn't be Bob or Alice
                giver_in_cluster = a.giver_id in [alice.id, bob.id]
                receiver_in_cluster = a.receiver_id in [alice.id, bob.id]
                if giver_in_cluster:
                    assert not receiver_in_cluster
    
    def test_impossible_cluster_fails(self):
        """If a cluster has more than half of participants, it's impossible."""
        cluster = Cluster(name="Big Family")
        
        # 3 people in cluster, 4 total - impossible
        participants = [
            Participant(name=f"Person{i}", email=f"p{i}@test.com", cluster_id=cluster.id if i < 3 else None)
            for i in range(4)
        ]
        cluster.member_ids = [p.id for p in participants[:3]]
        
        storage = MockStorage(participants, [cluster])
        
        with pytest.raises(MatcherError, match="less than half"):
            create_assignments(storage)
    
    def test_multiple_clusters(self):
        """Multiple clusters should all be respected."""
        cluster1 = Cluster(name="Family1")
        cluster2 = Cluster(name="Family2")
        
        # 2 families of 2, plus 2 unclustered
        p1 = Participant(name="P1", email="p1@test.com", cluster_id=cluster1.id)
        p2 = Participant(name="P2", email="p2@test.com", cluster_id=cluster1.id)
        p3 = Participant(name="P3", email="p3@test.com", cluster_id=cluster2.id)
        p4 = Participant(name="P4", email="p4@test.com", cluster_id=cluster2.id)
        p5 = Participant(name="P5", email="p5@test.com")
        p6 = Participant(name="P6", email="p6@test.com")
        
        cluster1.member_ids = [p1.id, p2.id]
        cluster2.member_ids = [p3.id, p4.id]
        
        storage = MockStorage(
            participants=[p1, p2, p3, p4, p5, p6],
            clusters=[cluster1, cluster2]
        )
        
        # Run multiple times
        for _ in range(50):
            assignments = create_assignments(storage)
            
            for a in assignments:
                # Check cluster1
                if a.giver_id in [p1.id, p2.id]:
                    assert a.receiver_id not in [p1.id, p2.id]
                # Check cluster2
                if a.giver_id in [p3.id, p4.id]:
                    assert a.receiver_id not in [p3.id, p4.id]


class TestAssignmentData:
    """Tests for assignment data integrity."""
    
    def test_assignment_has_names_and_emails(self):
        """Assignments should include names and emails for convenience."""
        alice = Participant(name="Alice", email="alice@test.com", parent_email="parent@test.com")
        bob = Participant(name="Bob", email="bob@test.com")
        
        storage = MockStorage([alice, bob])
        assignments = create_assignments(storage)
        
        for a in assignments:
            assert a.giver_name in ["Alice", "Bob"]
            assert a.receiver_name in ["Alice", "Bob"]
            assert "@test.com" in a.giver_email
            assert "@test.com" in a.receiver_email
