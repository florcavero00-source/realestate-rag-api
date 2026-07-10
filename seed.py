from fastembed import TextEmbedding
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

embedding_model = TextEmbedding()

PROPERTIES = [
    {
        "id": "prop001",
        "name": "Sunset Ridge Apartments",
        "type": "Multi-Family",
        "location": {
            "address": "1234 Sunset Blvd",
            "city": "Austin",
            "state": "TX",
            "zip": "78701"
        },
        "financials": {
            "purchase_price": 2500000,
            "current_value": 3100000,
            "monthly_rent": 18000,
            "annual_noi": 180000,
            "cap_rate": 5.8,
            "cash_on_cash_return": 7.2,
            "roi_5yr": 24.0
        },
        "details": {
            "units": 12,
            "sqft": 9600,
            "year_built": 2005,
            "occupancy_rate": 95
        },
        "risk_rating": "Low",
        "recommendation": "Buy",
        "analyst_notes": "Strong rental demand in Austin tech corridor. Consistent occupancy above 93%. Good long-term appreciation potential."
    },
    {
        "id": "prop002",
        "name": "Downtown Miami Office Tower",
        "type": "Commercial Office",
        "location": {
            "address": "500 Brickell Ave",
            "city": "Miami",
            "state": "FL",
            "zip": "33131"
        },
        "financials": {
            "purchase_price": 8500000,
            "current_value": 9200000,
            "monthly_rent": 65000,
            "annual_noi": 620000,
            "cap_rate": 6.7,
            "cash_on_cash_return": 8.1,
            "roi_5yr": 18.5
        },
        "details": {
            "units": 1,
            "sqft": 42000,
            "year_built": 1998,
            "occupancy_rate": 88
        },
        "risk_rating": "Medium",
        "recommendation": "Hold",
        "analyst_notes": "Prime Brickell location but remote work trends affecting occupancy. Strong tenant base with long-term leases."
    },
    {
        "id": "prop003",
        "name": "Phoenix Industrial Warehouse",
        "type": "Industrial",
        "location": {
            "address": "7890 Commerce Dr",
            "city": "Phoenix",
            "state": "AZ",
            "zip": "85043"
        },
        "financials": {
            "purchase_price": 3200000,
            "current_value": 4100000,
            "monthly_rent": 28000,
            "annual_noi": 295000,
            "cap_rate": 7.2,
            "cash_on_cash_return": 9.4,
            "roi_5yr": 28.1
        },
        "details": {
            "units": 1,
            "sqft": 55000,
            "year_built": 2015,
            "occupancy_rate": 100
        },
        "risk_rating": "Low",
        "recommendation": "Buy",
        "analyst_notes": "E-commerce boom driving industrial demand. Triple net lease with Amazon as tenant. Excellent cash flow."
    },
    {
        "id": "prop004",
        "name": "Nashville Short-Term Rental Portfolio",
        "type": "Short-Term Rental",
        "location": {
            "address": "Various",
            "city": "Nashville",
            "state": "TN",
            "zip": "37201"
        },
        "financials": {
            "purchase_price": 1800000,
            "current_value": 2100000,
            "monthly_rent": 22000,
            "annual_noi": 198000,
            "cap_rate": 9.4,
            "cash_on_cash_return": 11.2,
            "roi_5yr": 35.0
        },
        "details": {
            "units": 6,
            "sqft": 4800,
            "year_built": 2018,
            "occupancy_rate": 82
        },
        "risk_rating": "High",
        "recommendation": "Buy",
        "analyst_notes": "Nashville tourism boom driving strong Airbnb demand. Higher management overhead but exceptional returns. Regulatory risk to monitor."
    },
    {
        "id": "prop005",
        "name": "Denver Retail Strip Mall",
        "type": "Retail",
        "location": {
            "address": "3210 Colorado Blvd",
            "city": "Denver",
            "state": "CO",
            "zip": "80220"
        },
        "financials": {
            "purchase_price": 4500000,
            "current_value": 4200000,
            "monthly_rent": 31000,
            "annual_noi": 290000,
            "cap_rate": 5.2,
            "cash_on_cash_return": 4.8,
            "roi_5yr": 8.2
        },
        "details": {
            "units": 8,
            "sqft": 18000,
            "year_built": 1992,
            "occupancy_rate": 75
        },
        "risk_rating": "High",
        "recommendation": "Sell",
        "analyst_notes": "E-commerce pressure on retail tenants. Two anchor tenants recently vacated. Declining foot traffic in the area."
    },
    {
        "id": "prop006",
        "name": "Seattle Luxury Condos",
        "type": "Residential Condo",
        "location": {
            "address": "900 Pike St",
            "city": "Seattle",
            "state": "WA",
            "zip": "98101"
        },
        "financials": {
            "purchase_price": 5800000,
            "current_value": 7200000,
            "monthly_rent": 42000,
            "annual_noi": 420000,
            "cap_rate": 5.8,
            "cash_on_cash_return": 6.9,
            "roi_5yr": 31.0
        },
        "details": {
            "units": 10,
            "sqft": 12000,
            "year_built": 2019,
            "occupancy_rate": 97
        },
        "risk_rating": "Low-Medium",
        "recommendation": "Buy",
        "analyst_notes": "Tech worker demand keeps luxury rental market strong. Near Amazon HQ. High appreciation in past 5 years."
    },
    {
        "id": "prop007",
        "name": "Chicago Parking Garage",
        "type": "Parking",
        "location": {
            "address": "200 N Michigan Ave",
            "city": "Chicago",
            "state": "IL",
            "zip": "60601"
        },
        "financials": {
            "purchase_price": 6000000,
            "current_value": 5500000,
            "monthly_rent": 38000,
            "annual_noi": 340000,
            "cap_rate": 4.8,
            "cash_on_cash_return": 3.9,
            "roi_5yr": 4.2
        },
        "details": {
            "units": 1,
            "sqft": 80000,
            "year_built": 1985,
            "occupancy_rate": 70
        },
        "risk_rating": "High",
        "recommendation": "Sell",
        "analyst_notes": "Remote work reducing downtown commuters. EV and autonomous vehicle trends threaten long-term demand. Value has declined since purchase."
    },
    {
        "id": "prop008",
        "name": "Raleigh Build-to-Rent Community",
        "type": "Build-to-Rent",
        "location": {
            "address": "4500 Innovation Way",
            "city": "Raleigh",
            "state": "NC",
            "zip": "27601"
        },
        "financials": {
            "purchase_price": 12000000,
            "current_value": 14500000,
            "monthly_rent": 95000,
            "annual_noi": 960000,
            "cap_rate": 6.6,
            "cash_on_cash_return": 8.8,
            "roi_5yr": 29.5
        },
        "details": {
            "units": 48,
            "sqft": 52000,
            "year_built": 2022,
            "occupancy_rate": 96
        },
        "risk_rating": "Low-Medium",
        "recommendation": "Buy",
        "analyst_notes": "Research Triangle population boom. Brand new construction with low maintenance costs. Strong job market driving rental demand."
    }
]


def property_to_text(prop: dict) -> str:
    """Convert a property document into a text string for embedding."""
    return f"""
Property: {prop['name']} ({prop['id']})
Type: {prop['type']}
Location: {prop['location']['address']}, {prop['location']['city']}, {prop['location']['state']} {prop['location']['zip']}
Risk Rating: {prop['risk_rating']}
Recommendation: {prop['recommendation']}

Financials:
- Purchase Price: ${prop['financials']['purchase_price']:,}
- Current Value: ${prop['financials']['current_value']:,}
- Monthly Rent: ${prop['financials']['monthly_rent']:,}
- Annual NOI: ${prop['financials']['annual_noi']:,}
- Cap Rate: {prop['financials']['cap_rate']}%
- Cash-on-Cash Return: {prop['financials']['cash_on_cash_return']}%
- 5-Year ROI: {prop['financials']['roi_5yr']}%

Property Details:
- Units: {prop['details']['units']}
- Square Footage: {prop['details']['sqft']:,} sqft
- Year Built: {prop['details']['year_built']}
- Occupancy Rate: {prop['details']['occupancy_rate']}%

Analyst Notes: {prop['analyst_notes']}
    """.strip()


def seed_database():
    """Seed the MongoDB properties collection.

    This function clears the existing `properties` collection in MongoDB,
    converts each property into text, computes embeddings for that text,
    augments each property document with the generated text and embedding,
    and inserts the enriched documents into the database.
    """
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["realestate"]
    collection = db["properties"]

    collection.delete_many({})

    texts = [property_to_text(p) for p in PROPERTIES]
    embeddings = list(embedding_model.embed(texts))

    documents = []
    for prop, text, embedding in zip(PROPERTIES, texts, embeddings):
        doc = prop.copy()
        doc["text"] = text
        doc["embedding"] = embedding.tolist()
        documents.append(doc)

    collection.insert_many(documents)
    print(f"Inserted {len(documents)} properties with embeddings into MongoDB")

    client.close()


if __name__ == "__main__":
    seed_database()
