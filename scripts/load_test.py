"""Locust load test for INCEPT API.

Usage:
    locust -f scripts/load_test.py --headless -u 5 -r 1 -t 60s
    locust -f scripts/load_test.py --headless -u 50 -r 5 -t 300s
"""

from __future__ import annotations

from locust import HttpUser, between, task


class InceptUser(HttpUser):
    """Simulated user for INCEPT API load testing."""

    wait_time = between(0.5, 2.0)
    host = "http://localhost:8080"

    @task(5)
    def post_command(self) -> None:
        """Submit a natural language command request."""
        queries = [
            "find all log files larger than 100MB",
            "list running processes",
            "show disk usage",
            "install nginx",
            "check if port 80 is open",
            "create a directory called backup",
            "search for errors in syslog",
            "compress the /var/log directory",
            "view the last 50 lines of /var/log/syslog",
            "check the status of the ssh service",
        ]
        import random

        query = random.choice(queries)
        self.client.post(
            "/v1/command",
            json={"nl": query},
            headers={"Content-Type": "application/json"},
        )

    @task(2)
    def get_health(self) -> None:
        """Check health endpoint."""
        self.client.get("/v1/health")

    @task(1)
    def get_intents(self) -> None:
        """Fetch supported intents."""
        self.client.get("/v1/intents")
