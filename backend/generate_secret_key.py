#!/usr/bin/env python
"""
Django SECRET_KEY Generator

Bu script, Django için güvenli bir SECRET_KEY oluşturur.
Railway deployment için kullanılabilir.

Kullanım:
    python generate_secret_key.py
"""

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("DJANGO SECRET_KEY")
    print("="*70)
    print(f"\n{secret_key}\n")
    print("="*70)
    print("\nBu key'i kopyalayıp Railway environment variables'a ekleyin:")
    print("SECRET_KEY=<yukarıdaki-key>\n")

