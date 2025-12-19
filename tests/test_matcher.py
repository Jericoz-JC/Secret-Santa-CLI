"""Tests for the matchmaking algorithm."""

import pytest
from uuid import uuid4

from secret_santa.models import Participant, Cluster, SecretSantaData
from secret_santa.matcher import create_assignments, MatcherError, _same_cluster, generate_verification_code


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


class TestSeparateKidsMatching:
    """Tests for kids-only matching feature (when separate_kids=True)."""
    
    def test_kids_match_only_with_kids(self):
        """Kids should only be matched with other kids when separate_kids=True."""
        # 3 kids and 3 adults
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True)
        kid2 = Participant(name="Kid2", email="kid2@test.com", is_kid=True)
        kid3 = Participant(name="Kid3", email="kid3@test.com", is_kid=True)
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False)
        adult2 = Participant(name="Adult2", email="adult2@test.com", is_kid=False)
        adult3 = Participant(name="Adult3", email="adult3@test.com", is_kid=False)
        
        storage = MockStorage([kid1, kid2, kid3, adult1, adult2, adult3])
        
        # Run multiple times since it's random
        for _ in range(50):
            assignments = create_assignments(storage, separate_kids=True)
            
            kid_ids = {kid1.id, kid2.id, kid3.id}
            adult_ids = {adult1.id, adult2.id, adult3.id}
            
            for a in assignments:
                if a.giver_id in kid_ids:
                    # Kid giver should have kid receiver
                    assert a.receiver_id in kid_ids, f"Kid {a.giver_name} matched with adult!"
                else:
                    # Adult giver should have adult receiver
                    assert a.receiver_id in adult_ids, f"Adult {a.giver_name} matched with kid!"
    
    def test_adults_match_only_with_adults(self):
        """Adults should only be matched with other adults when separate_kids=True."""
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True)
        kid2 = Participant(name="Kid2", email="kid2@test.com", is_kid=True)
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False)
        adult2 = Participant(name="Adult2", email="adult2@test.com", is_kid=False)
        
        storage = MockStorage([kid1, kid2, adult1, adult2])
        
        for _ in range(30):
            assignments = create_assignments(storage, separate_kids=True)
            
            for a in assignments:
                giver_is_kid = a.giver_id in {kid1.id, kid2.id}
                receiver_is_kid = a.receiver_id in {kid1.id, kid2.id}
                # They should match: both kids or both adults
                assert giver_is_kid == receiver_is_kid
    
    def test_single_kid_fails_with_separate_kids(self):
        """Only 1 kid should raise an error when separate_kids=True."""
        kid = Participant(name="LonelyKid", email="kid@test.com", is_kid=True)
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False)
        adult2 = Participant(name="Adult2", email="adult2@test.com", is_kid=False)
        
        storage = MockStorage([kid, adult1, adult2])
        
        with pytest.raises(MatcherError, match="Only 1 kid"):
            create_assignments(storage, separate_kids=True)
    
    def test_two_kids_two_adults_separated(self):
        """Minimum viable scenario with both groups separated."""
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True)
        kid2 = Participant(name="Kid2", email="kid2@test.com", is_kid=True)
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False)
        adult2 = Participant(name="Adult2", email="adult2@test.com", is_kid=False)
        
        storage = MockStorage([kid1, kid2, adult1, adult2])
        
        for _ in range(30):
            assignments = create_assignments(storage, separate_kids=True)
            
            # Kids should match: kid1 -> kid2, kid2 -> kid1
            # Adults should match: adult1 -> adult2, adult2 -> adult1
            kid_ids = {kid1.id, kid2.id}
            adult_ids = {adult1.id, adult2.id}
            
            for a in assignments:
                if a.giver_id in kid_ids:
                    assert a.receiver_id in kid_ids
                    assert a.giver_id != a.receiver_id  # Not self
                else:
                    assert a.receiver_id in adult_ids
                    assert a.giver_id != a.receiver_id
    
    def test_kids_with_cluster_exclusion(self):
        """Kids in the same cluster should still not match when separate_kids=True."""
        cluster = Cluster(name="Siblings")
        
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True, cluster_id=cluster.id)
        kid2 = Participant(name="Kid2", email="kid2@test.com", is_kid=True, cluster_id=cluster.id)
        kid3 = Participant(name="Kid3", email="kid3@test.com", is_kid=True)
        kid4 = Participant(name="Kid4", email="kid4@test.com", is_kid=True)
        
        cluster.member_ids = [kid1.id, kid2.id]
        
        storage = MockStorage([kid1, kid2, kid3, kid4], [cluster])
        
        for _ in range(50):
            assignments = create_assignments(storage, separate_kids=True)
            
            for a in assignments:
                # Siblings should never get each other
                if a.giver_id in [kid1.id, kid2.id]:
                    assert a.receiver_id not in [kid1.id, kid2.id]
    
    def test_kids_cluster_too_large_fails(self):
        """If kid cluster has more than half of kids, it should fail when separate_kids=True."""
        cluster = Cluster(name="Big Sibling Group")
        
        # 3 kids in cluster, 4 kids total - impossible
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True, cluster_id=cluster.id)
        kid2 = Participant(name="Kid2", email="kid2@test.com", is_kid=True, cluster_id=cluster.id)
        kid3 = Participant(name="Kid3", email="kid3@test.com", is_kid=True, cluster_id=cluster.id)
        kid4 = Participant(name="Kid4", email="kid4@test.com", is_kid=True)
        
        cluster.member_ids = [kid1.id, kid2.id, kid3.id]
        
        # Add adults so overall there are enough participants
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False)
        adult2 = Participant(name="Adult2", email="adult2@test.com", is_kid=False)
        
        storage = MockStorage([kid1, kid2, kid3, kid4, adult1, adult2], [cluster])
        
        with pytest.raises(MatcherError, match="less than half"):
            create_assignments(storage, separate_kids=True)
    
    def test_kids_with_parent_email(self):
        """Kids with parent email should have it in their assignment."""
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True, parent_email="parent1@test.com")
        kid2 = Participant(name="Kid2", email="kid2@test.com", is_kid=True, parent_email="parent2@test.com")
        
        storage = MockStorage([kid1, kid2])
        
        assignments = create_assignments(storage, separate_kids=True)
        
        for a in assignments:
            # Parent email should be preserved
            if a.giver_id == kid1.id:
                assert a.parent_email == "parent1@test.com"
            elif a.giver_id == kid2.id:
                assert a.parent_email == "parent2@test.com"


class TestRandomMatching:
    """Tests for default random matching (separate_kids=False)."""
    
    def test_default_allows_kid_adult_matching(self):
        """By default, kids can be matched with adults."""
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True)
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False)
        
        storage = MockStorage([kid1, adult1])
        
        # Should work fine - kid and adult can match each other
        assignments = create_assignments(storage)  # separate_kids=False by default
        
        assert len(assignments) == 2
        # Verify one gives to other
        givers = {a.giver_id for a in assignments}
        receivers = {a.receiver_id for a in assignments}
        assert givers == {kid1.id, adult1.id}
        assert receivers == {kid1.id, adult1.id}
    
    def test_single_kid_works_in_random_mode(self):
        """Single kid should work fine without separate_kids."""
        kid = Participant(name="Kid1", email="kid@test.com", is_kid=True)
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False)
        adult2 = Participant(name="Adult2", email="adult2@test.com", is_kid=False)
        
        storage = MockStorage([kid, adult1, adult2])
        
        # Should work - no separation enforced
        assignments = create_assignments(storage)  # separate_kids=False by default
        
        assert len(assignments) == 3
    
    def test_mixed_group_can_cross_match(self):
        """Kids and adults can be matched with each other in random mode."""
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True)
        kid2 = Participant(name="Kid2", email="kid2@test.com", is_kid=True)
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False)
        adult2 = Participant(name="Adult2", email="adult2@test.com", is_kid=False)
        
        storage = MockStorage([kid1, kid2, adult1, adult2])
        
        # Run many times and check that cross-matching CAN happen
        cross_match_found = False
        for _ in range(100):
            assignments = create_assignments(storage)  # separate_kids=False by default
            
            for a in assignments:
                giver_is_kid = a.giver_id in {kid1.id, kid2.id}
                receiver_is_kid = a.receiver_id in {kid1.id, kid2.id}
                if giver_is_kid != receiver_is_kid:
                    cross_match_found = True
                    break
            if cross_match_found:
                break
        
        assert cross_match_found, "Cross-matching should be possible in random mode"
    
    def test_all_kids_works_in_random_mode(self):
        """All kids should still work in random mode."""
        kids = [
            Participant(name=f"Kid{i}", email=f"kid{i}@test.com", is_kid=True)
            for i in range(4)
        ]
        
        storage = MockStorage(kids)
        
        assignments = create_assignments(storage)
        assert len(assignments) == 4
    
    def test_all_adults_works_in_random_mode(self):
        """All adults should still work in random mode."""
        adults = [
            Participant(name=f"Adult{i}", email=f"adult{i}@test.com", is_kid=False)
            for i in range(4)
        ]
        
        storage = MockStorage(adults)
        
        assignments = create_assignments(storage)
        assert len(assignments) == 4
    
    def test_cluster_exclusion_still_works_in_random_mode(self):
        """Cluster exclusions should work regardless of separate_kids setting."""
        cluster = Cluster(name="Family")
        
        kid1 = Participant(name="Kid1", email="kid1@test.com", is_kid=True, cluster_id=cluster.id)
        adult1 = Participant(name="Adult1", email="adult1@test.com", is_kid=False, cluster_id=cluster.id)
        kid2 = Participant(name="Kid2", email="kid2@test.com", is_kid=True)
        adult2 = Participant(name="Adult2", email="adult2@test.com", is_kid=False)
        
        cluster.member_ids = [kid1.id, adult1.id]
        
        storage = MockStorage([kid1, adult1, kid2, adult2], [cluster])
        
        for _ in range(50):
            assignments = create_assignments(storage)
            
            for a in assignments:
                # Family members (kid1 and adult1) should not match each other
                if a.giver_id in [kid1.id, adult1.id]:
                    assert a.receiver_id not in [kid1.id, adult1.id]


class TestVerificationCode:
    """Tests for verification code generation."""
    
    def test_verification_code_is_deterministic(self):
        """Same giver/receiver pair should always produce the same code."""
        giver_id = uuid4()
        receiver_id = uuid4()
        
        code1 = generate_verification_code(giver_id, receiver_id)
        code2 = generate_verification_code(giver_id, receiver_id)
        
        assert code1 == code2
    
    def test_verification_code_is_4_characters(self):
        """Verification codes should be exactly 4 characters."""
        giver_id = uuid4()
        receiver_id = uuid4()
        
        code = generate_verification_code(giver_id, receiver_id)
        
        assert len(code) == 4
    
    def test_verification_code_is_uppercase(self):
        """Verification codes should be uppercase."""
        giver_id = uuid4()
        receiver_id = uuid4()
        
        code = generate_verification_code(giver_id, receiver_id)
        
        assert code == code.upper()
    
    def test_different_pairs_different_codes(self):
        """Different giver/receiver pairs should have different codes."""
        id1, id2, id3 = uuid4(), uuid4(), uuid4()
        
        code1 = generate_verification_code(id1, id2)
        code2 = generate_verification_code(id1, id3)
        code3 = generate_verification_code(id2, id1)
        
        # All should be different
        assert code1 != code2
        assert code1 != code3
        assert code2 != code3
    
    def test_order_matters(self):
        """Swapping giver and receiver should produce different codes."""
        id1, id2 = uuid4(), uuid4()
        
        code1 = generate_verification_code(id1, id2)
        code2 = generate_verification_code(id2, id1)
        
        assert code1 != code2


class TestAssignmentHasVerificationCode:
    """Tests for verification codes in assignments."""
    
    def test_all_assignments_have_verification_codes(self):
        """Every assignment should have a non-empty verification code."""
        participants = [
            Participant(name=f"Person{i}", email=f"p{i}@test.com")
            for i in range(5)
        ]
        storage = MockStorage(participants)
        
        assignments = create_assignments(storage)
        
        for a in assignments:
            assert a.verification_code, f"Assignment for {a.giver_name} missing verification code"
            assert len(a.verification_code) == 4
    
    def test_verification_codes_are_unique_per_assignment(self):
        """Each assignment should have a unique verification code."""
        participants = [
            Participant(name=f"Person{i}", email=f"p{i}@test.com")
            for i in range(10)
        ]
        storage = MockStorage(participants)
        
        assignments = create_assignments(storage)
        codes = [a.verification_code for a in assignments]
        
        # All codes should be unique
        assert len(codes) == len(set(codes)), "Some verification codes are duplicated"
    
    def test_verification_code_matches_expected(self):
        """Verification code should match what generate_verification_code produces."""
        alice = Participant(name="Alice", email="alice@test.com")
        bob = Participant(name="Bob", email="bob@test.com")
        
        storage = MockStorage([alice, bob])
        
        assignments = create_assignments(storage)
        
        for a in assignments:
            expected = generate_verification_code(a.giver_id, a.receiver_id)
            assert a.verification_code == expected
