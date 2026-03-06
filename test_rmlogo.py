#!/usr/bin/env python3
"""
test_rmlogo.py — Quick test script for rmlogo package

Run this after installation to verify everything works:
    python test_rmlogo.py
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all modules can be imported."""
    print("=" * 70)
    print("TEST 1: Import rmlogo modules")
    print("=" * 70)

    try:
        from rmlogo import __version__

        print(f"[PASS] rmlogo version: {__version__}")
    except ImportError as e:
        print(f"[FAIL] Failed to import rmlogo: {e}")
        return False

    try:
        from rmlogo.cli import main, parse_gemini_hint

        print("[PASS] rmlogo.cli imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import rmlogo.cli: {e}")
        return False

    try:
        from rmlogo.auto_mask import generate_mask

        print("[PASS] rmlogo.auto_mask imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import rmlogo.auto_mask: {e}")
        return False

    try:
        from rmlogo.inference import remove_logo

        print("[PASS] rmlogo.inference imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import rmlogo.inference: {e}")
        return False

    return True


def test_gemini_parser():
    """Test the Gemini hint parser."""
    print("\n" + "=" * 70)
    print("TEST 2: Gemini hint parser (parse_gemini_hint)")
    print("=" * 70)

    from rmlogo.cli import parse_gemini_hint

    test_cases = [
        ("watermark in bottom right corner", "bottom-right"),
        ("logo is in top left", "top-left"),
        ("centered watermark", "center"),
        ("entire image watermark", "full"),
        ("I don't know where it is", "auto"),
    ]

    all_passed = True
    for text, expected in test_cases:
        result = parse_gemini_hint(text)
        if result == expected:
            print(f"[PASS] '{text}' -> {result}")
        else:
            print(f"[FAIL] '{text}' -> got {result}, expected {expected}")
            all_passed = False

    return all_passed


def test_cli_help():
    """Test that CLI help works."""
    print("\n" + "=" * 70)
    print("TEST 3: CLI help command")
    print("=" * 70)

    from rmlogo.cli import main
    import io
    from contextlib import redirect_stdout, redirect_stderr

    try:
        # Capture help output
        f = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(f), redirect_stderr(err):
            try:
                main(["--help"])
            except SystemExit:
                pass  # --help causes sys.exit(0)

        help_output = f.getvalue() + err.getvalue()
        if "rmlogo" in help_output and "--bgrm" in help_output:
            print("[PASS] CLI help contains expected content")
            print(f"  - Found 'rmlogo' in help")
            print(f"  - Found '--bgrm' flag")
            return True
        else:
            print("[FAIL] CLI help missing expected content")
            return False
    except Exception as e:
        print(f"[FAIL] Error testing CLI help: {e}")
        return False


def test_version():
    """Test version command."""
    print("\n" + "=" * 70)
    print("TEST 4: Version check")
    print("=" * 70)

    from rmlogo import __version__

    if __version__ == "2.1.0":
        print(f"[PASS] Version is correct: {__version__}")
        return True
    else:
        print(f"[FAIL] Version mismatch: got {__version__}, expected 2.1.0")
        return False


def test_dependencies():
    """Test that all dependencies are available."""
    print("\n" + "=" * 70)
    print("TEST 5: Check dependencies")
    print("=" * 70)

    dependencies = {
        "cv2": "opencv-python",
        "numpy": "numpy",
        "PIL": "pillow",
        "tqdm": "tqdm",
    }

    all_present = True
    for module_name, package_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"[PASS] {package_name} is installed")
        except ImportError:
            print(f"[FAIL] {package_name} is NOT installed")
            all_present = False

    return all_present


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("rmlogo Test Suite")
    print("=" * 70)
    print()

    results = {
        "Imports": test_imports(),
        "Gemini Parser": test_gemini_parser(),
        "CLI Help": test_cli_help(),
        "Version": test_version(),
        "Dependencies": test_dependencies(),
    }

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("=" * 70)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - rmlogo is ready to use!")
        print("=" * 70)
        return 0
    else:
        print("[ERROR] SOME TESTS FAILED - please check the output above")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
