import os
import random
import sys
from datetime import date, timedelta

import pandas as pd
from faker import Faker
from loguru import logger

# --- INITIAL CONFIGURATION ---

# Configure Loguru for clear and informative output
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Initialize Faker for US English data
fake = Faker()

# Define the amount of data to be generated
NUM_CUSTOMERS = 5000
NUM_MOVEMENTS = 20000
NUM_CAMPAIGN_DISPATCHES = 30000
NUM_USAGE_RECORDS = 40000
NUM_INVOICES = 50000
NUM_SUPPORT_TICKETS = 7500

# --- GENERATION FUNCTIONS ---


def generate_dim_product():
    """Generates the product catalog."""
    products = [
        (101, "Prepaid Mobile", "Mobile", 20.00),
        (102, "Control Mobile", "Mobile", 50.00),
        (103, "Postpaid Mobile", "Mobile", 100.00),
        (201, "Broadband 300 MB", "Broadband", 99.90),
        (202, "Broadband 500 MB", "Broadband", 119.90),
        (203, "Broadband 1 GB", "Broadband", 199.90),
        (301, "Essential TV", "TV", 79.90),
        (302, "TV+Streaming", "TV", 129.90),
        (303, "TV+Streaming+Music", "TV", 159.90),
    ]
    return pd.DataFrame(
        products, columns=["product_id", "product_name", "category", "monthly_fee"]
    )


def generate_dim_campaign():
    """Generates the marketing campaign catalog."""
    campaigns, campaign_names = [], [
        "Postpaid Discount",
        "Broadband Upgrade",
        "Mother's Day Offer",
        "Mobile Black Friday",
        "Christmas More Gigs",
        "Family Combo",
        "Refer & Earn",
    ]
    channels = ["SMS", "Email", "Push App", "Whatsapp"]
    for i, name_base in enumerate(campaign_names):
        start_date = fake.date_between(start_date="-3y", end_date="today")
        campaigns.append(
            (
                50 + i,
                f"{name_base} {random.choice([2023, 2024, 2025])}",
                random.choice(channels),
                start_date,
                start_date + timedelta(days=random.randint(15, 60)),
            )
        )
    return pd.DataFrame(
        campaigns,
        columns=[
            "campaign_id",
            "campaign_name",
            "dispatch_channel",
            "start_date",
            "end_date",
        ],
    )


def generate_dim_customer(num_customers):
    """Generates the customer dimension table with enriched fields."""
    customers = []
    payment_methods = ["Direct Debit", "Credit Card", "Bank Slip"]
    acquisition_channels = ["Physical Store", "Online", "Telesales", "Partner"]
    for i in range(num_customers):
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
        min_signup_date = birth_date + timedelta(days=18 * 365)
        if min_signup_date > date.today():
            min_signup_date = date.today()
        signup_date = fake.date_between(start_date=min_signup_date, end_date="today")

        # Simulate churn (15% of customers have churned)
        cancellation_date = None
        if random.random() < 0.15:
            cancellation_date = fake.date_between(
                start_date=signup_date, end_date=date.today()
            )

        customers.append(
            (
                i + 1,
                fake.ssn(),
                fake.name(),
                birth_date,
                random.choice(["Single", "Married", "Divorced", "Widowed"]),
                random.choice(["A", "B", "C", "D"]),
                signup_date,
                fake.city(),
                fake.state_abbr(),
                random.choice(payment_methods),
                random.choice(acquisition_channels),
                random.randint(300, 850),
                cancellation_date,
            )
        )
    return pd.DataFrame(
        customers,
        columns=[
            "customer_id",
            "ssn",
            "name",
            "birth_date",
            "marital_status",
            "income_bracket",
            "signup_date",
            "city",
            "state",
            "payment_method",
            "acquisition_channel",
            "credit_score",
            "cancellation_date",
        ],
    ).where(pd.notnull, None)


def generate_fact_usage(dim_customer, dim_product, num_records):
    """Generates the service usage fact table."""
    usage_data = []
    for i in range(num_records):
        customer = dim_customer.sample(1).iloc[0]
        end_date = (
            customer["cancellation_date"]
            if pd.notna(customer["cancellation_date"])
            else date.today()
        )
        if customer["signup_date"] >= end_date:
            continue

        ref_date = fake.date_between_dates(
            date_start=customer["signup_date"], date_end=end_date
        )
        ref_date = ref_date.replace(day=1)  # Aggregate by month

        product = dim_product.sample(1).iloc[0]
        data_gb, voice_minutes, sms_count = 0.0, 0, 0
        if product["category"] == "Mobile":
            data_gb, voice_minutes, sms_count = (
                round(random.uniform(1, 50), 2),
                random.randint(0, 1000),
                random.randint(0, 300),
            )
        elif product["category"] == "Broadband":
            data_gb = round(random.uniform(50, 1000), 2)

        usage_data.append(
            (
                i + 1,
                int(ref_date.strftime("%Y%m%d")),
                customer["customer_id"],
                product["product_id"],
                data_gb,
                voice_minutes,
                sms_count,
            )
        )
    return pd.DataFrame(
        usage_data,
        columns=[
            "usage_id",
            "date_ref_id",
            "customer_id",
            "product_id",
            "data_usage_gb",
            "voice_minutes",
            "sms_count",
        ],
    )


def generate_fact_billing(dim_customer, num_invoices):
    """Generates the billing and payments fact table."""
    invoices = []
    for i in range(num_invoices):
        customer = dim_customer.sample(1).iloc[0]
        end_date = (
            customer["cancellation_date"]
            if pd.notna(customer["cancellation_date"])
            else date.today()
        )
        if customer["signup_date"] >= end_date:
            continue

        due_date = fake.date_between_dates(
            date_start=customer["signup_date"], date_end=end_date
        )
        total_amount = round(random.uniform(30.0, 450.0), 2)

        status, paid_amount, payment_date = None, 0.0, None
        if random.random() < 0.90:  # 90% are paid
            status = "Paid"
            paid_amount = total_amount
            payment_date = due_date - timedelta(days=random.randint(0, 5))
        else:  # 10% are open or overdue
            status = "Overdue" if due_date < date.today() else "Open"

        invoices.append(
            (
                i + 1,
                customer["customer_id"],
                int(due_date.strftime("%Y%m%d")),
                int(payment_date.strftime("%Y%m%d")) if payment_date else None,
                total_amount,
                paid_amount,
                status,
            )
        )
    return pd.DataFrame(
        invoices,
        columns=[
            "invoice_id",
            "customer_id",
            "due_date_id",
            "payment_date_id",
            "total_amount",
            "paid_amount",
            "invoice_status",
        ],
    ).where(pd.notnull, None)


def generate_fact_support_tickets(dim_customer, num_tickets):
    """Generates the support tickets fact table."""
    tickets = []
    channels = ["App", "Phone", "Website", "Store", "Social Media"]
    reasons = [
        "Invoice question",
        "Technical issue",
        "Plan change",
        "Cancellation request",
        "Information",
        "Complaint",
    ]
    for i in range(num_tickets):
        customer = dim_customer.sample(1).iloc[0]
        end_date = (
            customer["cancellation_date"]
            if pd.notna(customer["cancellation_date"])
            else date.today()
        )
        if customer["signup_date"] >= end_date:
            continue

        open_date = fake.date_between_dates(
            date_start=customer["signup_date"], date_end=end_date
        )
        tickets.append(
            (
                i + 1,
                customer["customer_id"],
                int(open_date.strftime("%Y%m%d")),
                random.choice(channels),
                random.choice(reasons),
                random.choice(["Resolved", "In Progress", "Pending"]),
            )
        )
    return pd.DataFrame(
        tickets,
        columns=[
            "ticket_id",
            "customer_id",
            "open_date_id",
            "support_channel",
            "contact_reason",
            "ticket_status",
        ],
    )


def generate_fact_campaign_dispatch(dim_customer, dim_campaign, num_dispatches):
    """Generates the campaign dispatch fact table."""
    dispatches = []
    for i in range(num_dispatches):
        customer, campaign = (
            dim_customer.sample(1).iloc[0],
            dim_campaign.sample(1).iloc[0],
        )
        if campaign["start_date"] <= campaign["end_date"]:
            dispatch_date = fake.date_between_dates(
                date_start=campaign["start_date"], date_end=campaign["end_date"]
            )
            dispatches.append(
                (
                    1001 + i,
                    int(dispatch_date.strftime("%Y%m%d")),
                    campaign["campaign_id"],
                    customer["customer_id"],
                    random.choice([True, False]),
                )
            )
    return pd.DataFrame(
        dispatches,
        columns=[
            "dispatch_id",
            "date_id",
            "campaign_id",
            "customer_id",
            "clicked_link",
        ],
    )


def generate_fact_movement(dim_customer, dim_product, dim_campaign, num_movements):
    """Generates the customer movement fact table (signups, upgrades, etc.)."""
    movements = []
    types = ["New Customer", "Upgrade", "Downgrade", "Plan Migration", "Cancellation"]
    for i in range(num_movements):
        customer = dim_customer.sample(1).iloc[0]
        end_date = (
            customer["cancellation_date"]
            if pd.notna(customer["cancellation_date"])
            else date.today()
        )
        if customer["signup_date"] >= end_date:
            continue
        mov_date = fake.date_between_dates(
            date_start=customer["signup_date"], date_end=end_date
        )
        prev_prod_id, new_prod_id, prev_val, new_val, conv_camp_id = (
            None,
            None,
            0.0,
            0.0,
            None,
        )
        mov_type = random.choice(types)

        if mov_type == "New Customer":
            new_prod_id = dim_product.sample(1).iloc[0]["product_id"]
        elif mov_type == "Cancellation":
            prev_prod_id = dim_product.sample(1).iloc[0]["product_id"]
        else:
            p1, p2 = dim_product.sample(2).iterrows()
            prev_prod_id, new_prod_id = p1[1]["product_id"], p2[1]["product_id"]

        if prev_prod_id:
            prev_val = dim_product.loc[
                dim_product["product_id"] == prev_prod_id, "monthly_fee"
            ].iloc[0]
        if new_prod_id:
            new_val = dim_product.loc[
                dim_product["product_id"] == new_prod_id, "monthly_fee"
            ].iloc[0]

        discount = (
            round(random.uniform(0.05, 0.2) * new_val, 2)
            if random.random() < 0.25 and new_val > 0
            else 0.0
        )

        movements.append(
            (
                i + 1,
                int(mov_date.strftime("%Y%m%d")),
                customer["customer_id"],
                mov_type,
                prev_prod_id,
                new_prod_id,
                conv_camp_id,
                prev_val,
                new_val,
                discount,
            )
        )
    return pd.DataFrame(
        movements,
        columns=[
            "movement_id",
            "date_id",
            "customer_id",
            "movement_type",
            "previous_product_id",
            "new_product_id",
            "conversion_campaign_id",
            "previous_value",
            "new_value",
            "applied_discount",
        ],
    ).where(pd.notnull, None)


# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    logger.info("Starting data generation process... This may take a moment. ⏳")

    # 1. Generate Dimensions
    logger.info("[STEP 1/3] Generating dimension tables...")
    dim_product = generate_dim_product()
    dim_campaign = generate_dim_campaign()
    dim_customer = generate_dim_customer(NUM_CUSTOMERS)
    logger.success(
        f"Dimensions generated: {len(dim_customer)} customers, {len(dim_product)} products, {len(dim_campaign)} campaigns."
    )

    # 2. Generate Facts
    logger.info("[STEP 2/3] Generating fact tables...")
    fact_movement = generate_fact_movement(
        dim_customer, dim_product, dim_campaign, NUM_MOVEMENTS
    )
    fact_campaign_dispatch = generate_fact_campaign_dispatch(
        dim_customer, dim_campaign, NUM_CAMPAIGN_DISPATCHES
    )
    fact_usage = generate_fact_usage(dim_customer, dim_product, NUM_USAGE_RECORDS)
    fact_billing = generate_fact_billing(dim_customer, NUM_INVOICES)
    fact_support_tickets = generate_fact_support_tickets(
        dim_customer, NUM_SUPPORT_TICKETS
    )
    logger.success(
        f"Facts generated: {len(fact_movement)} movements, {len(fact_campaign_dispatch)} dispatches, {len(fact_usage)} usage records, {len(fact_billing)} invoices, {len(fact_support_tickets)} tickets."
    )

    # 3. Save to CSV files
    tables = {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_campaign": dim_campaign,
        "fact_movement": fact_movement,
        "fact_campaign_dispatch": fact_campaign_dispatch,
        "fact_usage": fact_usage,
        "fact_billing": fact_billing,
        "fact_support_tickets": fact_support_tickets,
    }
    logger.info("[STEP 3/3] Saving tables to CSV files... 💾")
    for filename, dataframe in tables.items():
        if not os.path.exists("telco_project/seeds"):
            os.makedirs("telco_project/seeds")
        dataframe.to_csv(f"telco_project/seeds/{filename}.csv", index=False)
        logger.debug(f"File '{filename}.csv' saved successfully.")

    logger.success("Data generation process completed successfully! 🎉")
