"""
Test script for Phase 3 match simulation features.
Tests the new match-level simulation API endpoints.
"""

import asyncio
import json
import time
import httpx
from decimal import Decimal

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_DATA_FILE = "test_match_request.json"


async def test_match_simulation():
    """Test the complete match simulation functionality."""
    print("🏐 Testing Phase 3: Match Simulation Features")
    print("=" * 60)
    
    # Load test data
    with open(TEST_DATA_FILE, 'r') as f:
        test_request = json.load(f)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test 1: Health check
        print("\n1. Health Check")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ API is healthy")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test 2: Single match simulation
        print("\n2. Single Match Simulation")
        try:
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/match/single-match",
                json=test_request
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Single match completed in {duration:.2f}s")
                print(f"   Winner: Team {result['winner']}")
                print(f"   Sets: {len(result['sets'])}")
                print(f"   Format: {result['match_format']}")
                
                # Show set details
                for i, set_result in enumerate(result['sets'], 1):
                    print(f"   Set {i}: {set_result['team_a_score']}-{set_result['team_b_score']} (Winner: Team {set_result['winner']})")
            else:
                print(f"❌ Single match failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Single match error: {e}")
        
        # Test 3: Quick match comparison
        print("\n3. Quick Match Comparison")
        try:
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/match/quick-comparison",
                json=test_request
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Quick comparison completed in {duration:.2f}s")
                print(f"   Team A win rate: {result['team_a']['win_probability']:.3f}")
                print(f"   Team B win rate: {result['team_b']['win_probability']:.3f}")
                print(f"   Favorite: {result['competitiveness']['favorite']}")
                print(f"   Close matchup: {result['competitiveness']['is_close_matchup']}")
                print(f"   Margin of error: {result['competitiveness']['margin_of_error']:.3f}")
            else:
                print(f"❌ Quick comparison failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Quick comparison error: {e}")
        
        # Test 4: Full match simulation (1000 matches)
        print("\n4. Full Match Simulation (1000 matches)")
        try:
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/match/simulate",
                json=test_request
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                stats = result['statistics']
                
                print(f"✅ Match simulation completed in {duration:.2f}s")
                print(f"   Total matches: {stats['total_matches']}")
                print(f"   Team A wins: {stats['team_a_wins']} ({float(stats['team_a_win_probability']):.3f})")
                print(f"   Team B wins: {stats['team_b_wins']} ({float(stats['team_b_win_probability']):.3f})")
                print(f"   Confidence interval: [{float(stats['confidence_interval_lower']):.3f}, {float(stats['confidence_interval_upper']):.3f}]")
                print(f"   Margin of error: ±{float(stats['margin_of_error']):.3f}")
                print(f"   Statistically significant: {stats['is_statistically_significant']}")
                
                # Match details
                print(f"   Average sets per match: {float(stats['avg_sets_per_match']):.2f}")
                print(f"   Straight set wins (A): {stats['straight_set_wins_a']}")
                print(f"   Straight set wins (B): {stats['straight_set_wins_b']}")
                print(f"   Three-set matches: {stats['three_set_matches']}")
                
                # Rally analytics
                print(f"   Average rallies per set: {float(stats['avg_rallies_per_set']):.1f}")
                print(f"   Average rally length: {float(stats['avg_rally_length']):.1f} contacts")
                print(f"   Longest rally: {stats['longest_rally_contacts']} contacts")
                
                # Performance metrics
                matches_per_second = stats['total_matches'] / duration
                print(f"   Performance: {matches_per_second:.1f} matches/second")
                
            else:
                print(f"❌ Match simulation failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Match simulation error: {e}")
        
        # Test 5: Best-of-1 format
        print("\n5. Best-of-1 Match Format")
        try:
            bo1_request = test_request.copy()
            bo1_request['match_format'] = 'best_of_1'
            bo1_request['num_simulations'] = 500
            
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/match/simulate",
                json=bo1_request
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                stats = result['statistics']
                
                print(f"✅ Best-of-1 simulation completed in {duration:.2f}s")
                print(f"   Team A win rate: {float(stats['team_a_win_probability']):.3f}")
                print(f"   Average sets per match: {float(stats['avg_sets_per_match']):.2f} (should be 1.0)")
                print(f"   Three-set matches: {stats['three_set_matches']} (should be 0)")
                
            else:
                print(f"❌ Best-of-1 simulation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Best-of-1 simulation error: {e}")
        
        # Test 6: Momentum and pressure effects
        print("\n6. Momentum and Pressure Effects")
        try:
            # Test with effects disabled
            no_effects_request = test_request.copy()
            no_effects_request['momentum_effects'] = False
            no_effects_request['pressure_effects'] = False
            no_effects_request['num_simulations'] = 500
            
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/match/simulate",
                json=no_effects_request
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result_no_effects = response.json()
                
                # Test with effects enabled
                effects_request = test_request.copy()
                effects_request['momentum_effects'] = True
                effects_request['pressure_effects'] = True
                effects_request['num_simulations'] = 500
                
                response = await client.post(
                    f"{BASE_URL}/match/simulate",
                    json=effects_request
                )
                
                if response.status_code == 200:
                    result_with_effects = response.json()
                    
                    print(f"✅ Effects comparison completed")
                    print(f"   Without effects - Team A: {float(result_no_effects['statistics']['team_a_win_probability']):.3f}")
                    print(f"   With effects - Team A: {float(result_with_effects['statistics']['team_a_win_probability']):.3f}")
                    
                    # Calculate difference
                    diff = abs(float(result_with_effects['statistics']['team_a_win_probability']) - 
                             float(result_no_effects['statistics']['team_a_win_probability']))
                    print(f"   Difference: {diff:.3f}")
                    
            else:
                print(f"❌ Effects comparison failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Effects comparison error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Phase 3 Testing Complete!")


async def test_async_simulation():
    """Test asynchronous simulation for large datasets."""
    print("\n7. Asynchronous Simulation (Large Dataset)")
    
    # Load test data and increase simulation count
    with open(TEST_DATA_FILE, 'r') as f:
        test_request = json.load(f)
    
    test_request['num_simulations'] = 5000  # Trigger async mode
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # Start async simulation
            response = await client.post(
                f"{BASE_URL}/match/simulate-async",
                json=test_request
            )
            
            if response.status_code == 200:
                result = response.json()
                simulation_id = result['simulation_id']
                print(f"✅ Async simulation started: {simulation_id}")
                print(f"   Estimated time: {result['estimated_time_minutes']:.1f} minutes")
                
                # Poll for completion
                max_polls = 60  # Maximum polls (5 minutes at 5-second intervals)
                poll_count = 0
                
                while poll_count < max_polls:
                    await asyncio.sleep(5)  # Wait 5 seconds
                    
                    status_response = await client.get(f"{BASE_URL}/match/status/{simulation_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data['status']
                        
                        print(f"   Status check {poll_count + 1}: {status}")
                        
                        if status == 'completed':
                            result_data = status_data['result']
                            stats = result_data['statistics']
                            print(f"✅ Async simulation completed!")
                            print(f"   Total matches: {stats['total_matches']}")
                            print(f"   Team A win rate: {stats['team_a_win_probability']:.3f}")
                            print(f"   Simulation time: {result_data['simulation_time_seconds']:.1f}s")
                            break
                        elif status == 'failed':
                            print(f"❌ Async simulation failed: {status_data.get('error', 'Unknown error')}")
                            break
                    
                    poll_count += 1
                
                if poll_count >= max_polls:
                    print("❌ Async simulation timed out")
            
            else:
                print(f"❌ Async simulation start failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Async simulation error: {e}")


if __name__ == "__main__":
    print("Starting Phase 3 Match Simulation Tests...")
    asyncio.run(test_match_simulation())
    # Uncomment to test async simulation
    # asyncio.run(test_async_simulation())
