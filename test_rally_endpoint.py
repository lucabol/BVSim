#!/usr/bin/env python3
"""
Simple test script for the Beach Volleyball Simulator Rally endpoint.

This script tests the /rally/simulate endpoint with sample team data.
"""

import requests
import json
from typing import Dict, Any


def create_sample_team_stats(name: str, skill_level: str = "intermediate") -> Dict[str, Any]:
    """
    Create sample team statistics for testing.
    
    Args:
        name: Team name
        skill_level: One of 'beginner', 'intermediate', 'advanced'
    
    Returns:
        Dictionary with team statistics
    """
    
    if skill_level == "beginner":
        return {
            "name": name,
            # Serve stats
            "service_ace_percentage": 5.0,
            "service_error_percentage": 15.0,
            "serve_success_rate": 60.0,
            
            # Reception stats
            "perfect_pass_percentage": 30.0,
            "good_pass_percentage": 40.0,
            "poor_pass_percentage": 20.0,
            "reception_error_percentage": 10.0,
            
            # Setting stats
            "assist_percentage": 45.0,
            "ball_handling_error_percentage": 8.0,
            
            # Attack stats
            "attack_kill_percentage": 35.0,
            "attack_error_percentage": 15.0,
            "hitting_efficiency": 0.20,
            "first_ball_kill_percentage": 25.0,
            
            # Defense stats
            "dig_percentage": 60.0,
            "block_kill_percentage": 8.0,
            "controlled_block_percentage": 25.0,
            "blocking_error_percentage": 10.0
        }
    
    elif skill_level == "advanced":
        return {
            "name": name,
            # Serve stats
            "service_ace_percentage": 12.0,
            "service_error_percentage": 8.0,
            "serve_success_rate": 85.0,
            
            # Reception stats
            "perfect_pass_percentage": 60.0,
            "good_pass_percentage": 30.0,
            "poor_pass_percentage": 8.0,
            "reception_error_percentage": 2.0,
            
            # Setting stats
            "assist_percentage": 65.0,
            "ball_handling_error_percentage": 3.0,
            
            # Attack stats
            "attack_kill_percentage": 55.0,
            "attack_error_percentage": 8.0,
            "hitting_efficiency": 0.47,
            "first_ball_kill_percentage": 45.0,
            
            # Defense stats
            "dig_percentage": 85.0,
            "block_kill_percentage": 15.0,
            "controlled_block_percentage": 40.0,
            "blocking_error_percentage": 5.0
        }
    
    else:  # intermediate
        return {
            "name": name,
            # Serve stats
            "service_ace_percentage": 8.0,
            "service_error_percentage": 12.0,
            "serve_success_rate": 72.0,
            
            # Reception stats
            "perfect_pass_percentage": 45.0,
            "good_pass_percentage": 35.0,
            "poor_pass_percentage": 15.0,
            "reception_error_percentage": 5.0,
            
            # Setting stats
            "assist_percentage": 55.0,
            "ball_handling_error_percentage": 5.0,
            
            # Attack stats
            "attack_kill_percentage": 45.0,
            "attack_error_percentage": 12.0,
            "hitting_efficiency": 0.33,
            "first_ball_kill_percentage": 35.0,
            
            # Defense stats
            "dig_percentage": 72.0,
            "block_kill_percentage": 12.0,
            "controlled_block_percentage": 32.0,
            "blocking_error_percentage": 8.0
        }


def test_rally_simulation(base_url: str = "http://localhost:8000") -> None:
    """
    Test the rally simulation endpoint with sample data.
    
    Args:
        base_url: Base URL of the API server
    """
    
    print("🏐 Beach Volleyball Rally Simulation Test")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ API is healthy!")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot connect to API: {e}")
        print("   Make sure the application is running with: .\\dev.bat start")
        return
    
    # Test 2: Single rally simulation
    print("\n2. Testing single rally simulation...")
    
    # Create sample teams
    team_a = create_sample_team_stats("Beach Titans", "advanced")
    team_b = create_sample_team_stats("Sand Warriors", "intermediate")
    
    # Create rally simulation request
    rally_request = {
        "serving_team": "team_a",
        "team_a_stats": team_a,
        "team_b_stats": team_b,
        "team_a_score": 12,
        "team_b_score": 10,
        "set_number": 1,
        "momentum": 0.2,
        "pressure_level": 0.3
    }
    
    try:
        print("   📡 Sending rally simulation request...")
        response = requests.post(
            f"{base_url}/rally/simulate",
            json=rally_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Rally simulation successful!")
            print(f"   🏆 Winner: {result['winner']}")
            print(f"   📊 Rally length: {result['rally_length']} actions")
            print(f"   ⚡ Point outcome: {result['point_outcome']}")
            print(f"   🎯 Final state: {result['final_state']}")
            print(f"   📈 Team A actions: {result['team_a_actions']}")
            print(f"   📈 Team B actions: {result['team_b_actions']}")
            print(f"   🎲 Total probability: {result['total_probability']}")
            
            if result.get('events'):
                print(f"   📝 Events in rally: {len(result['events'])}")
                print("   🔄 Rally progression:")
                for i, event in enumerate(result['events'][:5]):  # Show first 5 events
                    print(f"      {i+1}. {event['action_type']} by {event['performing_team']} (State: {event['state']})")
                if len(result['events']) > 5:
                    print(f"      ... and {len(result['events']) - 5} more events")
            
        else:
            print(f"   ❌ Rally simulation failed: {response.status_code}")
            print(f"   Error details: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Multiple rallies simulation
    print("\n3. Testing multiple rallies simulation...")
    
    multiple_rallies_request = {
        "num_rallies": 5,
        "serving_team": "team_a",
        "team_a_stats": team_a,
        "team_b_stats": team_b,
        "team_a_score": 5,
        "team_b_score": 3,
        "set_number": 1
    }
    
    try:
        print("   📡 Sending multiple rallies request...")
        response = requests.post(
            f"{base_url}/rally/simulate-multiple",
            json=multiple_rallies_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Multiple rallies simulation successful!")
            print(f"   🎯 Rallies simulated: {result['num_rallies']}")
            print(f"   🏆 Team A wins: {result['team_a_wins']} ({result['team_a_win_percentage']:.1f}%)")
            print(f"   🏆 Team B wins: {result['team_b_wins']} ({result['team_b_win_percentage']:.1f}%)")
            print(f"   📊 Average rally length: {result['average_rally_length']:.1f} actions")
            
            if result.get('event_type_distribution'):
                print("   📈 Event distribution:")
                for event_type, count in list(result['event_type_distribution'].items())[:3]:
                    print(f"      {event_type}: {count}")
            
            # Show detailed rally progression for each rally
            if result.get('individual_results'):
                print("   🔄 Individual rally progressions:")
                for rally_idx, rally in enumerate(result['individual_results'], 1):
                    print(f"      Rally {rally_idx}: {rally['winner']} wins ({rally['rally_length']} actions)")
                    if rally.get('events'):
                        for i, event in enumerate(rally['events']):  # Show all events per rally
                            print(f"         {i+1}. {event['action_type']} by {event['performing_team']} → {event['state']}")
                    print()
                    
        else:
            print(f"   ❌ Multiple rallies simulation failed: {response.status_code}")
            print(f"   Error details: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 4: API documentation access
    print("\n4. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("   ✅ API documentation is accessible!")
            print(f"   🌐 Visit: {base_url}/docs")
        else:
            print(f"   ❌ API docs not accessible: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot access API docs: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\n💡 Additional endpoints to explore:")
    print(f"   • API Documentation: {base_url}/docs")
    print(f"   • Health Check: {base_url}/health")
    print(f"   • Test Teams: {base_url}/rally/test-teams")
    print(f"   • Frontend Dashboard: http://localhost:3000")


def main():
    """Main function to run the tests."""
    # You can modify the base URL if your API runs on a different port
    base_url = "http://localhost:8000"
    
    test_rally_simulation(base_url)


if __name__ == "__main__":
    main()
