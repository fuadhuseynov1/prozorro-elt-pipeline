import requests
import json
import csv

BASE_URL = "https://public-api.prozorro.gov.ua/api/2.5"

def fetch_tenders(limit=1): #fetch initial tender id's

    response = requests.get(f"{BASE_URL}/tenders", params={"limit": limit})
    if response.status_code != 200:
        raise Exception(f"API call failed: {response.status_code}")
    return response.json()



def fetch_tender_detail(tender_id): #further fetch data for each tender id, that we previously got

    response = requests.get(f'{BASE_URL}/tenders/{tender_id}')
    if response.status_code != 200:
        raise Exception(f"Failed to fetch tender {tender_id}: {response.status_code}")
    return response.json()["data"] #return the body of json



# takes one tender detail and returns exactly one dict — one tender, one row.
def parse_tender(detail):
    # The hight level
    tender_period = detail.get('tenderPeriod', {})
    minimal_step = detail.get('minimalStep', {})
    value = detail.get('value', {})
    procuring_entity = detail.get('procuringEntity', {})
    contact_point = procuring_entity.get('contactPoint', {})
    identifier = procuring_entity.get('identifier', {})
    address = procuring_entity.get('address', {})

    # Inner level
    return {
        "tender_id": detail.get('tenderID'),
        "internal_id": detail.get('id'),
        "tender_start_dt": tender_period.get('startDate'),
        "tender_end_dt": tender_period.get('endDate'),
        "description": detail.get('description'),
        "title": detail.get('title'),
        "procurement_method": detail.get('procurementMethod'),
        "procurement_method_type": detail.get('procurementMethodType'),
        "award_criteria": detail.get('awardCriteria'),
        "submission_method": detail.get('submissionMethod'),
        "minimal_step_amount": minimal_step.get('amount'),
        "minimal_step_currency": minimal_step.get('currency'),
        "value_amount": value.get('amount'),
        "value_currency": value.get('currency'),
        "value_added_tax_included": value.get('valueAddedTaxIncluded'),
        "buyer_name": contact_point.get('name'),
        "buyer_email": contact_point.get('email'),
        "buyer_id": identifier.get('id'),
        "buyer_legal_name": identifier.get('legalName'),
        "buyer_postal_code": address.get('postalCode'),
        "buyer_country_name": address.get('countryName'),
        "buyer_street_address": address.get('streetAddress'),
        "buyer_region": address.get('region'),
        "buyer_city": address.get('locality'),
        "status": detail.get('status'),
        "date_created": detail.get('dateCreated'),
        "date_modified": detail.get('dateModified'),
        "owner": detail.get('owner'),
    }



# Takes one tender detail, but that one tender can contain multiple items, and each item can have multiple 
# additionalClassifications. So a single call to parse_items might need to produce zero, one, or many 
# rows — hence it needs its own internal list (rows = [], rows.append(...), return rows) to collect 
# however many rows come out of that one tender.
def parse_items(detail):
    tender_id = detail.get('tenderID')
    rows = []
    for item in detail.get('items', []):
        classification = item.get('classification', {})
        unit = item.get('unit', {})
        for extra in item.get('additionalClassifications', [{}]):
            rows.append({
                "tender_id": tender_id,
                "item_description": item.get('description'),
                "item_quantity": item.get('quantity'),
                "item_unit_name": unit.get('name'),
                "classification_scheme": classification.get('scheme'),
                "classification_description": classification.get('description'),
                "additional_classification_description": extra.get('description'),
            })
    return rows


def write_csv(rows, path):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    feed = fetch_tenders(limit=5)
    tender_rows = []
    item_rows = []

    for entry in feed["data"]:
        detail = fetch_tender_detail(entry["id"])
        tender_rows.append(parse_tender(detail))
        item_rows.extend(parse_items(detail))

    write_csv(tender_rows, "data/tenders.csv")
    write_csv(item_rows, "data/tender_items.csv")

    # data = resp.json()
    # data_json_formatted = json.dumps(data, indent=4)
    # print(data_json_formatted)


# tenderID
# id
# tenderPeriod --> startDate, endDate
# description
# title
# procurementMethod
# procurementMethodType
# awardCriteria
# submissionMethod
# minimalStep --> amount, currency
# items --> additionalClassifications --> description
# items --> description
# items --> unit --> name
# items --> classification --> scheme, description
# items --> quantity
# value --> currency, amount, valueAddedTaxIncluded
# procuringEntity --> contactPoint --> name, email
# procuringEntity --> identifier --> id, legalName
# procuringEntity --> address --> postalCode, countryName, streetAddress, region, locality

# status
# dateCreated
# dateModified
# owner