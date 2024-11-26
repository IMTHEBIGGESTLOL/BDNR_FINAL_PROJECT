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
    if isinstance(objects, list):  # Handle lists of dictionaries
        for obj in objects:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    print(f"{k}: {v}")
                print("=" * 50)
    elif isinstance(objects, dict):  # Handle a single dictionary
        for k, v in objects.items():
            print(f"{k}: {v}")
        print("=" * 50)
    else:
        print("Unsupported object type.")


def get_all_users():
    endpoint = f"{PROJECT_API_URL}/users"
    response = requests.get(endpoint)

    if response.ok:
        users = response.json()
        print("All Users (ID and Name):")
        for user in users:
            print(f"UUID: {user['uuid']}, Username: {user['username']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def get_all_customers():
    endpoint = f"{PROJECT_API_URL}/users/customers"
    response = requests.get(endpoint)

    if response.ok:
        customers = response.json()
        print("All Customers (ID and Name):")
        for customer in customers:
            print(f"UUID: {customer['uuid']}, Username: {customer['username']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")




def get_user():
    get_all_users()
    user_id = input("Enter the User ID to retrieve: ")
    suffix = f"/users/{user_id}"
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)

    if response.ok:
        user = response.json()
        print("User Details:")
        print_object(user)  # Pass the user dictionary directly, not as a list
    else:
        print(f"Error: {response.status_code} - {response.text}")



def get_customer():
    get_all_customers()
    customer_id = input("Enter the Customer ID to retrieve: ")
    suffix = f"/users/customers/{customer_id}"
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)

    if response.ok:
        customer = response.json()
        print("Customer Details:")
        print_object(customer)
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


def update_ticket():
    ticket_id = input("Enter the Ticket ID to update: ")
    update_data = {}

    print("Update Options:")
    print("1. Status")
    print("2. Priority")
    print("3. Both Status and Priority")
    choice = input("Choose what to update (1-3): ")

    if choice == '1' or choice == '3':
        print("Status Options:")
        print("1. Open")
        print("2. Resolved")
        print("3. In Progress")
        status_choice = input("Choose a Status(1-3): ")
        status_map = {'1': 'open', '2': 'resolved', '3': 'in_progress'}
        update_data["status"] = status_map.get(status_choice, None)

    if choice == '2' or choice == '3':
        print("Priority Options:")
        print("1. High")
        print("2. Medium")
        print("3. Low")
        priority_choice = input("Choose a Priority(1-3): ")
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}
        update_data["priority"] = priority_map.get(priority_choice, None)

    if not update_data:  # Ensure at least one field is being updated
        print("No valid updates provided. Exiting.")
        return

    endpoint = f"{PROJECT_API_URL}/tickets/{ticket_id}"
    response = requests.patch(endpoint, json=update_data)
    if response.ok:
        print("Ticket updated successfully:")
        print_object(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")


def main():
    log.info(f"Welcome to books catalog. App requests to: {PROJECT_API_URL}")
    get_customer()
if __name__ == "__main__":
    main()
