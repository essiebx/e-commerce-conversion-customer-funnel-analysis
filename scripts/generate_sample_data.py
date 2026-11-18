import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

STAGES = ("landing", "product_view", "cart", "checkout", "purchase")
CAMPAIGNS = ("spring_sale", "new_arrivals", "brand_awareness", "retargeting")
CHANNELS = ("paid_social", "search", "email", "organic")
DEVICES = ("mobile", "desktop", "tablet")


def generate_data(output_path: Path, users: int = 5000, seed: int = 42) -> None:
    random.seed(seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["event_id", "user_id", "session_id", "event_timestamp", "campaign", "channel", "device", "stage", "cart_value", "revenue"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()

        start = datetime(2026, 1, 1, 8, 0)
        event_id = 1

        for index in range(users):
            user_id = f"USR-{index + 1:05d}"
            session_id = f"SES-{index + 1:05d}"
            campaign = random.choices(CAMPAIGNS, weights=(30, 24, 18, 28))[0]
            channel = random.choices(CHANNELS, weights=(32, 38, 12, 18))[0]
            device = random.choices(DEVICES, weights=(58, 38, 4))[0]
            timestamp = start + timedelta(minutes=random.randint(0, 60 * 24 * 30))
            cart_value = 0.0

            progression = {
                "landing": 1.0,
                "product_view": 0.74,
                "cart": 0.48,
                "checkout": 0.34,
                "purchase": 0.27,
            }

            previous_reached = True
            for stage in STAGES:
                if not previous_reached:
                    break

                probability = progression[stage]
                reached = stage == "landing" or random.random() < probability
                if not reached:
                    break

                if stage in ("cart", "checkout", "purchase"):
                    cart_value = round(random.uniform(35, 320), 2)

                revenue = cart_value if stage == "purchase" else 0.0
                writer.writerow({
                    "event_id": f"EVT-{event_id:07d}",
                    "user_id": user_id,
                    "session_id": session_id,
                    "event_timestamp": timestamp.isoformat(),
                    "campaign": campaign,
                    "channel": channel,
                    "device": device,
                    "stage": stage,
                    "cart_value": f"{cart_value:.2f}",
                    "revenue": f"{revenue:.2f}",
                })
                event_id += 1
                timestamp += timedelta(minutes=random.randint(2, 18))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    target = root / "data" / "ecommerce_funnel_events.csv"
    generate_data(target)
    print(f"Generated synthetic funnel data: {target}")
