#!/usr/bin/env python3
"""
Sixth stage test runner

Run all tests in the sixth stage, including:
1. API gateway and CLI interface tests
2. End-to-end integration tests
3. Error handling and exception tests
4. Performance and scalability tests
"""

import sys
import os
from pathlib import Path

# Add project root directory to system path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Import test modules
from tests.stage_6.test_api_gateway_cli import run_tests as run_api_cli_tests
from tests.stage_6.test_end_to_end_integration import run_tests as run_integration_tests


def main():
    """Run all tests in the sixth stage"""
    print("🚀 Starting sixth stage test: Integration and Unified Call Interface")
    print("=" * 100)
    
    all_success = True
    
    # Run API gateway and CLI interface tests
    print("\n📋 1. API gateway and CLI interface tests")
    print("-" * 50)
    try:
        success1 = run_api_cli_tests()
        if not success1:
            all_success = False
            print("❌ API gateway and CLI interface tests failed")
        else:
            print("✅ API gateway and CLI interface tests passed")
    except Exception as e:
        print(f"❌ API gateway and CLI interface test execution exception: {e}")
        all_success = False
    
    # Run end-to-end integration tests
    print("\n🔗 2. End-to-end integration tests")
    print("-" * 50)
    try:
        success2 = run_integration_tests()
        if not success2:
            all_success = False
            print("❌ End-to-end integration tests failed")
        else:
            print("✅ End-to-end integration tests passed")
    except Exception as e:
        print(f"❌ End-to-end integration test execution exception: {e}")
        all_success = False
    
    # Output final result
    print("\n" + "=" * 100)
    print("Sixth stage test final result")
    print("=" * 100)
    
    if all_success:
        print("🎉 All sixth stage tests passed!")
        print("\n✅ Passed test modules:")
        print("   • API gateway unified entry function")
        print("   • CLI command line interface")
        print("   • End-to-end process integration")
        print("   • Environment setup and check")
        print("   • Error handling mechanism")
        print("   • Performance and scalability")
        
        print("\n🎯 Sixth stage verification completed:")
        print("   • Unified call interface works normally")
        print("   • CLI parameter parsing is correct")
        print("   • Complete process can run end-to-end")
        print("   • System具备生产就绪能力")
        
    else:
        print("❌ Some sixth stage tests failed")
        print("Please check the above test output and fix related issues before running tests again")
    
    return all_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
