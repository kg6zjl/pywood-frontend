#!/usr/bin/env python3
"""
Test script to verify multi-client WebSocket broadcasting and state synchronization.
Run this while the Flask server is running to test:
1. Multiple concurrent client connections
2. Live result broadcasting to all clients
3. New client state synchronization
4. Reset signal propagation
"""

import socketio
import time
import sys
from threading import Thread
import requests
import json

class TestClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.sio = socketio.Client()
        self.events = {
            'connected': False,
            'results': [],
            'resets': 0
        }
        
        # Register event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('new_results', self.on_new_results)
        self.sio.on('reset_results', self.on_reset_results)
    
    def on_connect(self):
        self.events['connected'] = True
        print(f"  ✓ Client {self.client_id}: Connected")
    
    def on_disconnect(self):
        self.events['connected'] = False
        print(f"  ✗ Client {self.client_id}: Disconnected")
    
    def on_new_results(self, data):
        self.events['results'].append(data)
        print(f"  📊 Client {self.client_id}: Received {data}")
    
    def on_reset_results(self):
        self.events['resets'] += 1
        print(f"  🔄 Client {self.client_id}: Reset signal received")
    
    def connect(self, url):
        try:
            self.sio.connect(url)
            return True
        except Exception as e:
            print(f"  ❌ Client {self.client_id}: Connection error - {e}")
            return False
    
    def disconnect(self):
        try:
            self.sio.disconnect()
        except:
            pass
    
    def wait(self, seconds):
        time.sleep(seconds)

def test_broadcast():
    """Test broadcasting results to multiple clients"""
    print("\n🔵 Test 1: Broadcasting results to 3 simultaneous clients")
    print("=" * 70)
    
    # Create 3 clients
    clients = []
    for i in range(3):
        client = TestClient(i + 1)
        clients.append(client)
    
    # Connect all clients
    print("\n📡 Connecting 3 clients...")
    for client in clients:
        if not client.connect('http://localhost:5000'):
            print("❌ Failed to connect client")
            return 1
        time.sleep(0.3)
    
    # Wait for connections to settle
    time.sleep(1)
    
    # Send test results
    print("\n📤 Posting test results...")
    test_results = {
        "first": 1,
        "second": 3,
        "third": 4,
        "fourth": 2
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/v1/results',
            json=test_results,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"  Response status: {response.status_code}")
        if response.status_code != 201:
            print(f"  ❌ Unexpected status: {response.text}")
    except Exception as e:
        print(f"  ❌ Error posting results: {e}")
        return 1
    
    # Wait for results to propagate
    time.sleep(2)
    
    # Send reset signal
    print("\n🔄 Sending reset signal...")
    try:
        response = requests.post('http://localhost:5000/api/v1/reset', timeout=5)
        print(f"  Reset status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error posting reset: {e}")
    
    # Wait for reset to propagate
    time.sleep(1)
    
    # Disconnect all clients
    print("\n🔌 Disconnecting clients...")
    for client in clients:
        client.disconnect()
    
    time.sleep(1)
    
    # Print results
    print("\n" + "=" * 70)
    print("📈 Test Results:")
    for client in clients:
        print(f"\n  Client {client.client_id}:")
        print(f"    Connected: {client.events['connected']}")
        print(f"    Results received: {len(client.events['results'])}")
        if client.events['results']:
            print(f"    Result data: {client.events['results'][0]}")
        print(f"    Reset signals: {client.events['resets']}")
    
    # Validate - each client should have received results and reset
    success = all(
        len(client.events['results']) > 0 and 
        client.events['resets'] > 0 
        for client in clients
    )
    
    if success:
        print("\n✅ PASS: Multi-client broadcasting works correctly!")
        return 0
    else:
        print("\n❌ FAIL: Not all clients received results/resets")
        return 1

def test_state_sync():
    """Test that new clients receive current race state on connect"""
    print("\n🔵 Test 2: New client state synchronization")
    print("=" * 70)
    
    # Clear any previous results
    try:
        requests.post('http://localhost:5000/api/v1/reset', timeout=5)
        time.sleep(1)
    except:
        pass
    
    # Post initial results
    print("\n📤 Posting initial results...")
    test_results = {
        "first": 2,
        "second": 1
    }
    
    try:
        requests.post(
            'http://localhost:5000/api/v1/results',
            json=test_results,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print("  Results posted successfully")
    except Exception as e:
        print(f"  ❌ Error posting results: {e}")
        return 1
    
    time.sleep(1)
    
    # Connect a new client - should immediately receive state
    print("\n🔌 Connecting new client (should receive current state)...")
    new_client = TestClient(99)
    if not new_client.connect('http://localhost:5000'):
        print("  ❌ Failed to connect")
        return 1
    
    # Wait for state to be received
    time.sleep(2)
    
    new_client.disconnect()
    
    if new_client.events['results']:
        print(f"✅ PASS: New client received state on connect: {new_client.events['results'][0]}")
        return 0
    else:
        print("❌ FAIL: New client did not receive state on connect")
        return 1

if __name__ == '__main__':
    print("\n🚀 PyWood Endgate Multi-Client Test Suite")
    print("=" * 70)
    print("Make sure the Flask server is running: python main.py\n")
    
    try:
        # Test connectivity
        try:
            response = requests.get('http://localhost:5000/results', timeout=2)
            print("✅ Server is accessible\n")
        except Exception as e:
            print(f"❌ Cannot reach server at http://localhost:5000")
            print(f"   Error: {e}")
            print(f"   Make sure to run: python main.py\n")
            sys.exit(1)
        
        # Run tests
        result1 = test_broadcast()
        time.sleep(2)
        
        result2 = test_state_sync()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 Test Summary")
        print("=" * 70)
        if result1 == 0 and result2 == 0:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Some tests failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
