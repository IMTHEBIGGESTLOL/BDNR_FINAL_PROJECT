#!/usr/bin/env python3
import argparse
import logging
import os
import requests

# Set logger
log = logging.getLogger()
log.setLevel('INFO')
handler = logging.FileHandler('project.log')
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

# Read env vars related to API connection
PROJECT_API_URL = os.getenv("PROJECT_API_URL", "http://localhost:8003")

def print_object(objects):
    for k in objects.keys():
        print(f"{k}: {objects[k]}")
    print("="*50)

def get_user_by_id(user_id):
    suffix = f"/users/{user_id}"
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)
    if response.ok:
        json_resp = response.json()
        if isinstance(json_resp, list):  # Handle list response
            if json_resp:  # Ensure the list is not empty
                for user in json_resp:
                    print_object(user)
            else:
                print("No user found with the provided ID.")
        else:
            print_object(json_resp)  # If the API unexpectedly returns a single dict
    else:
        print(f"Error: {response.status_code} - {response.text}")


def search_ticket_by():
    suffix = '/nothing'
    print("Filter Options:")
    print("1. Customer ID")
    print("2. Status")
    print("3. Priority")
    filter_choice = input("Choose a filter Option (1-3): ")

    if filter_choice == '1':  # Ensure that the input is a string, as input() returns a string
        customer_id = input("Insert CustomerId: ")
        suffix = f"/tickets/customerID/{customer_id}"

    elif filter_choice == '2':  # Use elif to avoid checking the other conditions
        print("Status Options:")
        print("1. Open")
        print("2. Resolved")
        print("3. In Progress")
        status_choice = input("Choose a Status(1-3): ")
        status_map = {'1': 'open', '2': 'resolved', '3': 'in_progress'}
        status = status_map.get(status_choice, None)
        suffix = f"/tickets/status/{status}"

    elif filter_choice == '3':  # Use elif for the last option
        print("Priority Options:")
        print("1. High")
        print("2. Medium")
        print("3. Low")
        priority_choice = input("Choose a Priority(1-3): ")
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}
        priority = priority_map.get(priority_choice, None)
        suffix = f"/tickets/priority/{priority}"

    # Send request based on the selected filter
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)
    print("\nTickets:\n")
    if response.ok:
        json_resp = response.json()
        if isinstance(json_resp, list):  # Handle list response
            if json_resp:  # Ensure the list is not empty
                for ticket in json_resp:
                    print_object(ticket)
            else:
                print("No ticket found with the provided filter.")
        else:
            print_object(json_resp)  # If the API unexpectedly returns a single dict
    else:
        print(f"Error: {response.status_code} - {response.text}")



def main():
    log.info(f"Welcome to books catalog. App requests to: {PROJECT_API_URL}")
    search_ticket_by()

if __name__ == "__main__":
    main()
