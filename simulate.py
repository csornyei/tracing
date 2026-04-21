import asyncio
import json
import random
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000"
USERS_FILE = Path(__file__).parent / "users.json"

TODO_TITLES = [
    "Buy groceries",
    "Read a book",
    "Go for a run",
    "Clean the house",
    "Write some code",
    "Call a friend",
    "Cook dinner",
    "Watch a movie",
    "Take a nap",
    "Learn something new",
    "Fix that bug",
    "Send an email",
    "Pay the bills",
    "Plan the weekend",
    "Do the laundry",
]

USER_NAMES = [
    ("Alice", "alice@example.com"),
    ("Bob", "bob@example.com"),
    ("Carol", "carol@example.com"),
    ("Dave", "dave@example.com"),
    ("Eve", "eve@example.com"),
    ("Frank", "frank@example.com"),
    ("Grace", "grace@example.com"),
    ("Hank", "hank@example.com"),
    ("Ivy", "ivy@example.com"),
    ("Jack", "jack@example.com"),
]


async def load_or_create_users(client: httpx.AsyncClient) -> list[dict]:
    if USERS_FILE.exists():
        users = json.loads(USERS_FILE.read_text())
        print(f"Loaded {len(users)} users from {USERS_FILE}")
        return users

    print("Creating 10 users...")
    users = []
    for name, email in USER_NAMES:
        resp = await client.post("/users/", json={"name": name, "email": email})
        resp.raise_for_status()
        user = resp.json()
        users.append({"id": user["id"], "name": user["name"]})
        print(f"  Created user: {user['name']} (id={user['id']})")

    USERS_FILE.write_text(json.dumps(users, indent=2))
    print(f"Saved users to {USERS_FILE}")
    return users


async def simulate_user(client: httpx.AsyncClient, user: dict):
    user_id = user["id"]
    name = user["name"]

    while True:
        title = random.choice(TODO_TITLES)

        # Create todo
        resp = await client.post("/todos/", json={"title": title, "user_id": user_id})
        resp.raise_for_status()
        todo = resp.json()
        todo_id = todo["id"]
        print(f"[{name}] Created todo #{todo_id}: '{title}'")

        await asyncio.sleep(30)

        # Mark complete
        resp = await client.put(f"/todos/{todo_id}", json={"completed": True})
        if resp.status_code == 404:
            print(f"[{name}] Todo #{todo_id} gone before update, restarting cycle")
            continue
        resp.raise_for_status()
        print(f"[{name}] Completed todo #{todo_id}: '{title}'")

        await asyncio.sleep(30)

        # Delete todo
        resp = await client.delete(f"/todos/{todo_id}")
        if resp.status_code == 404:
            print(f"[{name}] Todo #{todo_id} already deleted, restarting cycle")
            continue
        resp.raise_for_status()
        print(f"[{name}] Deleted todo #{todo_id}: '{title}'")


async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        users = await load_or_create_users(client)
        print(f"\nStarting simulation for {len(users)} users (60s cycle each)...\n")
        await asyncio.gather(*[simulate_user(client, user) for user in users])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
