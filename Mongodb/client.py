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

def print_user(user):
    for k in user.keys():
        print(f"{k}: {user[k]}")
    print("="*50)


def get_user_by_id(user_id):
    suffix = f"/users/{user_id}"
    endpoint = PROJECT_API_URL + suffix
    response = requests.get(endpoint)
    print("hola justo en el get user")
    if response.ok:
        json_resp = response.json()
        if isinstance(json_resp, list):  # Handle list response
            if json_resp:  # Ensure the list is not empty
                for user in json_resp:
                    print_user(user)
            else:
                print("No user found with the provided ID.")
        else:
            print_user(json_resp)  # If the API unexpectedly returns a single dict
    else:
        print(f"Error: {response.status_code} - {response.text}")



def main():
    log.info(f"Welcome to books catalog. App requests to: {PROJECT_API_URL}")

    parser = argparse.ArgumentParser()

    list_of_actions = ["search", "get", "update", "delete"]
    parser.add_argument("action", choices=list_of_actions, help="Action to be user for the books library")
    parser.add_argument("-i", "--id", help="Provide a book ID which related to the book action", default=None)

    args = parser.parse_args()

    if args.id and not args.action in ["get", "update", "delete"]:
        log.error(f"Can't use arg id with action {args.action}")
        exit(1)

    if args.action == "search":
        print("hola")
        #list_books(args.rating, args.pages, args.ratings_count, args.title, args.limit, args.skip)
    elif args.action == "get" and args.id:
        get_user_by_id(args.id)
    elif args.action == "update" and args.id:
        print("hola")
        #update_book(args.id)
    elif args.action == "delete" and args.id:
        print("hola")
        #delete_book(args.id)

if __name__ == "__main__":
    main()
