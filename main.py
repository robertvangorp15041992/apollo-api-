import requests
import csv
import time
from drive_upload import upload_to_drive

API_KEY = "srUWrqH5wE-RiP_RtNjq-g"
HEADERS = {
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

BASE_URL = "https://api.apollo.io/v1"


def search_people(company_domain, page=1):
    url = f"{BASE_URL}/people/match"
    payload = {
        "q_organization_domains": [company_domain],
        "page": page
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def reveal_email(contact_id):
    url = f"{BASE_URL}/people/{contact_id}/email"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("person", {}).get("email")


def extract_domain(email):
    return email.split("@")[1]


def deduce_pattern(email, first_name, last_name):
    local_part = email.split("@")[0].lower()
    first = first_name.lower()
    last = last_name.lower()

    if local_part == first:
        return "{first}"
    elif local_part == last:
        return "{last}"
    elif local_part == first + last:
        return "{first}{last}"
    elif local_part == first + "." + last:
        return "{first}.{last}"
    elif local_part == first[0] + last:
        return "{f}{last}"
    elif local_part == first[0] + "." + last:
        return "{f}.{last}"
    else:
        return None


def apply_pattern(pattern, first, last):
    f = first[0].lower()
    return pattern.format(first=first.lower(), last=last.lower(), f=f)


def generate_emails(company_domain):
    print(f"🔍 Searching contacts at: {company_domain}")
    data = search_people(company_domain)
    contacts = data.get("people", [])
    if not contacts:
        print("❌ No contacts found.")
        return []

    revealed_email = None
    domain = None
    pattern = None

    for contact in contacts:
        if contact.get("id"):
            try:
                revealed_email = reveal_email(contact["id"])
                print(f"📧 Revealed: {revealed_email}")
                domain = extract_domain(revealed_email)
                pattern = deduce_pattern(revealed_email, contact["first_name"], contact["last_name"])
                if pattern:
                    break
            except Exception as e:
                print(f"⚠️ Failed to reveal email: {e}")

    if not pattern:
        print("❌ Could not deduce pattern.")
        return []

    results = []
    for contact in contacts:
        first = contact["first_name"]
        last = contact["last_name"]
        title = contact.get("title", "")
        email_guess = apply_pattern(pattern, first, last) + "@" + domain

        results.append({
            "First Name": first,
            "Last Name": last,
            "Title": title,
            "Email": email_guess
        })

    return results


def save_to_csv(data, filename):
    keys = ["First Name", "Last Name", "Title", "Email"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    company_domain = "nike.com"
    filename = f"{company_domain.replace('.', '_')}_contacts.csv"

    contacts = generate_emails(company_domain)
    save_to_csv(contacts, filename)
    print(f"✅ Saved {len(contacts)} contacts to CSV")

    try:
        link = upload_to_drive(filename)
        print(f"📁 Uploaded to Drive: {link}")
    except Exception as e:
        print(f"⚠️ Failed to upload to Drive: {e}")


