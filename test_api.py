#!/usr/bin/env python3
"""
Test script for Voice Agent FastAPI server
"""

import asyncio
import aiohttp
import json
import base64
import os

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

async def test_health_endpoints():
    """Test health check endpoints"""
    print("🔍 Testing health endpoints...")
    
    async with aiohttp.ClientSession() as session:
        # Test root endpoint
        async with session.get(f"{BASE_URL}/") as response:
            data = await response.json()
            print(f"✅ Root endpoint: {data}")
        
        # Test health endpoint
        async with session.get(f"{BASE_URL}/health") as response:
            data = await response.json()
            print(f"✅ Health endpoint: {data}")

async def test_chat_endpoint():
    """Test chat endpoint"""
    print("\n🤖 Testing chat endpoint...")
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, this is a test message."
            }
        ],
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Chat endpoint: Response received")
                print(f"   Message: {data['message']['content'][:100]}...")
            else:
                error_text = await response.text()
                print(f"❌ Chat endpoint failed: {response.status} - {error_text}")

async def test_text_to_speech_endpoint():
    """Test text-to-speech endpoint"""
    print("\n🔊 Testing text-to-speech endpoint...")
    
    payload = {
        "text": "Hello, this is a test message for text to speech conversion.",
        "voice_name": "Bill",
        "model_id": "eleven_multilingual_v2"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/text-to-speech",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                audio_data = await response.read()
                print(f"✅ Text-to-speech endpoint: Audio generated ({len(audio_data)} bytes)")
            else:
                error_text = await response.text()
                print(f"❌ Text-to-speech endpoint failed: {response.status} - {error_text}")

async def test_speech_to_text_endpoint():
    """Test speech-to-text endpoint with base64 data"""
    print("\n🎤 Testing speech-to-text endpoint...")
    
    # Create a dummy base64 audio (this won't actually work, but tests the endpoint structure)
    dummy_audio = base64.b64encode(b"dummy audio data").decode('utf-8')
    
    payload = {
        "audio": dummy_audio,
        "format": "webm",
        "model_id": "whisper-large-v3"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/speech-to-text",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 400:
                # Expected to fail with dummy data
                print("✅ Speech-to-text endpoint: Correctly rejected invalid audio data")
            else:
                print(f"⚠️  Speech-to-speech endpoint: Unexpected response {response.status}")

async def main():
    """Run all tests"""
    print("🚀 Starting Voice Agent API tests...\n")
    
    try:
        await test_health_endpoints()
        await test_chat_endpoint()
        await test_text_to_speech_endpoint()
        await test_speech_to_text_endpoint()
        
        print("\n🎉 All tests completed!")
        print(f"📖 API Documentation available at: {BASE_URL}/docs")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 