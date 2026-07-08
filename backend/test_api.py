import requests


BASE_URL = "http://127.0.0.1:8000"


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    print_section("Testing /health")
    health_response = requests.get(f"{BASE_URL}/health", timeout=30)
    print(health_response.status_code)
    print(health_response.json())

    print_section("Testing /ingest")
    ingest_payload = {
        "repo_url": "https://github.com/pallets/click",
        "max_chunks": 120
    }

    ingest_response = requests.post(
        f"{BASE_URL}/ingest",
        json=ingest_payload,
        timeout=300
    )

    print(ingest_response.status_code)
    print(ingest_response.json())

    print_section("Testing /query")
    query_payload = {
        "question": "Where is the command line interface defined?",
        "n_results": 5
    }

    query_response = requests.post(
        f"{BASE_URL}/query",
        json=query_payload,
        timeout=120
    )

    print(query_response.status_code)
    query_json = query_response.json()

    print("Answer preview:")
    print(query_json["answer"][:1200])

    print("\nSources:")
    for source in query_json["sources"]:
        print(f"- {source}")

    print_section("Testing /stats")
    stats_response = requests.get(f"{BASE_URL}/stats", timeout=30)
    print(stats_response.status_code)
    print(stats_response.json())

    print_section("API test completed successfully")


if __name__ == "__main__":
    main()
