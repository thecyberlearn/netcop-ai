#!/usr/bin/env python
"""
Simple script to manage test users for development
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcop_ai_agent.settings.development')
django.setup()

from users.models import User

def list_users():
    print("Current users:")
    for user in User.objects.all():
        print(f"- {user.email} (Balance: ${user.wallet_balance}, Created: {user.created_at.strftime('%Y-%m-%d')})")

def delete_user(email):
    try:
        user = User.objects.get(email=email)
        user.delete()
        print(f"Deleted user: {email}")
    except User.DoesNotExist:
        print(f"User not found: {email}")

def add_balance(email, amount):
    try:
        user = User.objects.get(email=email)
        user.add_balance(amount)
        print(f"Added ${amount} to {email}. New balance: ${user.wallet_balance}")
    except User.DoesNotExist:
        print(f"User not found: {email}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        list_users()
    elif sys.argv[1] == 'delete' and len(sys.argv) == 3:
        delete_user(sys.argv[2])
    elif sys.argv[1] == 'balance' and len(sys.argv) == 4:
        add_balance(sys.argv[2], float(sys.argv[3]))
    else:
        print("Usage:")
        print("  python manage_users.py                    # List all users")
        print("  python manage_users.py delete <email>     # Delete user")
        print("  python manage_users.py balance <email> <amount>  # Add balance")