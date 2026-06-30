#!/usr/bin/env python3
"""
Flag verification script for CTF challenge
"""

import sys
import requests

FLAG_PARTS = {
    'part1': 'CTF{Sec',
    'part2': 'urity_Br',
    'part3': 'each_20',
    'part4': '24}'
}

CORRECT_FLAG = FLAG_PARTS['part1'] + FLAG_PARTS['part2'] + FLAG_PARTS['part3'] + FLAG_PARTS['part4']

def verify_local(flag):
    """Verify flag locally"""
    if flag == CORRECT_FLAG:
        print("✅ CORRECT! Flag verified successfully!")
        print(f"🎉 Flag: {flag}")
        return True
    else:
        print("❌ INCORRECT flag. Keep trying!")
        return False

def verify_remote(flag, server_url='http://localhost:5000'):
    """Verify flag via remote server"""
    try:
        response = requests.get(f'{server_url}/api/verify', params={'flag': flag})
        data = response.json()
        
        if data.get('status') == 'success':
            print("✅ CORRECT! Flag verified successfully!")
            print(f"🎉 {data.get('message')}")
            return True
        else:
            print("❌ INCORRECT flag. Keep trying!")
            print(f"💡 {data.get('message')}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running. Verifying locally...")
        return verify_local(flag)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python verify_flag.py '<flag>'")
        print(f"Example: python verify_flag.py '{CORRECT_FLAG}'")
        sys.exit(1)
    
    flag = sys.argv[1]
    
    # Try remote verification first
    if not verify_remote(flag):
        sys.exit(1)
