from app.rules import RISKY_KEYWORDS, COLUMN_ALIASES
import pandas as pd

def format_issue(issue_text, scan_type):
    if scan_type == "amazon":
        return f"Amazon policy risk: {issue_text}"
    elif scan_type == "walmart":
        return f"Walmart listing risk: {issue_text}"
    else:
        return f"Generic catalog risk: {issue_text}"

def map_columns(df):
    normalized_columns = {str(col).strip().lower(): col for col in df.columns}
    column_mapping = {}

    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized_columns:
                column_mapping[normalized_columns[alias]] = standard_name
                break

    return df.rename(columns=column_mapping)

def clean_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def scan_catalog(df, scan_type="generic"):
    results = []

    df = map_columns(df)
    df.columns = [str(col).strip().lower() for col in df.columns]

    required_columns = ["sku", "title", "description", "price"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df["sku"] = df["sku"].apply(clean_value)
    df["title"] = df["title"].apply(clean_value)
    df["description"] = df["description"].apply(clean_value)
    df["price"] = df["price"].apply(clean_value)

    duplicate_skus = df[df["sku"].duplicated(keep=False)]["sku"].tolist()

    for _, row in df.iterrows():
        sku = row["sku"] or "No SKU"
        title = row["title"]
        description = row["description"]
        price = row["price"]

        title_lower = title.lower()

        for keyword in RISKY_KEYWORDS:
            if keyword in title_lower:
                results.append({
                    "sku": sku,
                    "title": title,
                    "issue": format_issue(f'Risky keyword found: "{keyword}"', scan_type),
                    "severity": "BLOCKER"
                })

        if sku and sku in duplicate_skus:
            results.append({
                "sku": sku,
                "title": title,
                "issue": format_issue("Duplicate SKU found", scan_type),
                "severity": "WARNING"
            })

        if not title:
            results.append({
                "sku": sku,
                "title": title,
                "issue": format_issue("Missing title", scan_type),
                "severity": "WARNING"
            })

        if not description:
            results.append({
                "sku": sku,
                "title": title,
                "issue": format_issue("Missing description", scan_type),
                "severity": "WARNING"
            })

        if not price:
            results.append({
                "sku": sku,
                "title": title,
                "issue": format_issue("Missing price", scan_type),
                "severity": "WARNING"
            })

    return results