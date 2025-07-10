"""Test the rally simulation engine functionality."""

import sys
import os
from decimal import Decimal

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bvsim.engine import (
    RallySimulator, RallyState, TeamSide, RallyContext
)
from bvsim.schemas.team_statistics import TeamStatisticsBase


def create_test_team_stats(skill_level: float = 0.7) -> TeamStatisticsBase:
    """Create test team statistics."""
    # Convert skill level to realistic volleyball percentages
    ace_pct = skill_level * 8  # 0-8% ace rate
    serve_error_pct = (1 - skill_level) * 12  # Higher error with poor serve
    
    perfect_pass_pct = skill_level * 35
    good_pass_pct = skill_level * 30 + (1 - skill_level) * 25  
    poor_pass_pct = (1 - skill_level) * 30
    reception_error_pct = (1 - skill_level) * 15
    
    # Normalize reception percentages to sum to 100
    reception_total = perfect_pass_pct + good_pass_pct + poor_pass_pct + reception_error_pct
    if reception_total > 0:
        perfect_pass_pct = perfect_pass_pct / reception_total * 100
        good_pass_pct = good_pass_pct / reception_total * 100
        poor_pass_pct = poor_pass_pct / reception_total * 100
        reception_error_pct = reception_error_pct / reception_total * 100
    
    return TeamStatisticsBase(
        name=f"Team_{skill_level}",
        
        # Serve statistics
        service_ace_percentage=Decimal(str(ace_pct)),
        service_error_percentage=Decimal(str(serve_error_pct)),
        serve_success_rate=Decimal(str(skill_level * 60)),
        
        # Reception statistics
        perfect_pass_percentage=Decimal(str(perfect_pass_pct)),
        good_pass_percentage=Decimal(str(good_pass_pct)),
        poor_pass_percentage=Decimal(str(poor_pass_pct)),
        reception_error_percentage=Decimal(str(reception_error_pct)),
        
        # Setting statistics
        assist_percentage=Decimal(str(skill_level * 45)),
        ball_handling_error_percentage=Decimal(str((1 - skill_level) * 8)),
        
        # Attack statistics
        attack_kill_percentage=Decimal(str(skill_level * 35)),
        attack_error_percentage=Decimal(str((1 - skill_level) * 15)),
        hitting_efficiency=Decimal(str(skill_level * 0.6 - 0.1)),  # -0.1 to 0.5 range
        first_ball_kill_percentage=Decimal(str(skill_level * 25)),
        
        # Defense statistics
        dig_percentage=Decimal(str(skill_level * 70)),
        block_kill_percentage=Decimal(str(skill_level * 12)),
        controlled_block_percentage=Decimal(str(skill_level * 25)),
        blocking_error_percentage=Decimal(str((1 - skill_level) * 8))
    )


def test_single_rally():
    """Test simulating a single rally."""
    print("=== Testing Single Rally Simulation ===")
    
    # Create simulator
    simulator = RallySimulator()
    simulator.set_random_seed(42)  # For reproducible results
    
    # Create test teams
    team_a = create_test_team_stats(0.8)  # Strong team
    team_b = create_test_team_stats(0.6)  # Weaker team
    
    # Simulate rally
    result = simulator.simulate_rally(
        serving_team=TeamSide.TEAM_A,
        team_a_stats=team_a,
        team_b_stats=team_b
    )
    
    print(f"Rally Result:")
    print(f"  Winner: {result.winner}")
    print(f"  Point Outcome: {result.point_outcome}")
    print(f"  Rally Length: {result.rally_length}")
    print(f"  Final State: {result.final_state}")
    print(f"  Total Probability: {result.total_probability}")
    print(f"  Team A Actions: {result.team_a_actions}")
    print(f"  Team B Actions: {result.team_b_actions}")
    
    print(f"\nEvent Summary:")
    event_summary = result.get_event_summary()
    for action, count in event_summary.items():
        print(f"  {action}: {count}")
    
    print(f"\nFirst 5 Events:")
    for i, event in enumerate(result.events[:5]):
        print(f"  {i+1}. {event.performing_team} -> {event.state} (p={event.probability:.3f})")
    
    return result


def test_multiple_rallies():
    """Test simulating multiple rallies."""
    print("\n=== Testing Multiple Rally Simulation ===")
    
    # Create simulator
    simulator = RallySimulator()
    simulator.set_random_seed(42)
    
    # Create test teams
    team_a = create_test_team_stats(0.75)
    team_b = create_test_team_stats(0.65)
    
    # Simulate multiple rallies
    num_rallies = 10
    results = simulator.simulate_multiple_rallies(
        num_rallies=num_rallies,
        serving_team=TeamSide.TEAM_A,
        team_a_stats=team_a,
        team_b_stats=team_b
    )
    
    # Analyze results
    team_a_wins = sum(1 for r in results if r.winner == TeamSide.TEAM_A)
    team_b_wins = sum(1 for r in results if r.winner == TeamSide.TEAM_B)
    avg_rally_length = sum(r.rally_length for r in results) / len(results)
    
    print(f"Results from {num_rallies} rallies:")
    print(f"  Team A wins: {team_a_wins} ({team_a_wins/num_rallies*100:.1f}%)")
    print(f"  Team B wins: {team_b_wins} ({team_b_wins/num_rallies*100:.1f}%)")
    print(f"  Average rally length: {avg_rally_length:.1f}")
    
    # Event type distribution
    all_events = [event for result in results for event in result.events]
    event_types = {}
    for event in all_events:
        action = event.action_type.value
        event_types[action] = event_types.get(action, 0) + 1
    
    print(f"\nEvent type distribution:")
    total_events = len(all_events)
    for action, count in sorted(event_types.items()):
        print(f"  {action}: {count} ({count/total_events*100:.1f}%)")
    
    return results


def test_probability_engine():
    """Test the probability engine directly."""
    print("\n=== Testing Probability Engine ===")
    
    from bvsim.engine.probability_engine import ProbabilityEngine
    
    engine = ProbabilityEngine()
    
    # Create test context
    context = RallyContext(
        current_state=RallyState.SERVE_READY,
        serving_team=TeamSide.TEAM_A,
        rally_length=0,
        team_a_score=0,
        team_b_score=0,
        set_number=1
    )
    
    # Create test teams
    team_a = create_test_team_stats(0.8)
    team_b = create_test_team_stats(0.6)
    
    # Test serve probabilities
    probs = engine.calculate_transition_probabilities(
        RallyState.SERVE_READY, context, team_a, team_b
    )
    
    print(f"Serve probabilities for strong team:")
    for state, prob in probs.transitions.items():
        print(f"  {state}: {prob:.3f}")
    
    # Test with weaker team
    probs_weak = engine.calculate_transition_probabilities(
        RallyState.SERVE_READY, context, team_b, team_a
    )
    
    print(f"\nServe probabilities for weaker team:")
    for state, prob in probs_weak.transitions.items():
        print(f"  {state}: {prob:.3f}")


if __name__ == "__main__":
    try:
        print("Beach Volleyball Rally Simulation Engine Test")
        print("=" * 50)
        
        # Test individual components
        test_probability_engine()
        test_single_rally()
        test_multiple_rallies()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
