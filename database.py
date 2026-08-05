from sqlalchemy import create_engine , func , or_
from sqlalchemy.orm import sessionmaker
from datetime import date , timedelta , datetime 
from difflib import get_close_matches

from base import Base
from models import EggRecord , MedicineStock, FeedStock , EggPriceSetting , FarmFinancialSetting , FeedPriceSetting , CustomerOrder , Reminder, ReminderRecipient , SavedContact, ReminderReport 


DATABASE_URL = "mysql+pymysql://root:sunfra%40123@localhost:3306/waha_db"
engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine, 
    expire_on_commit=False
)

def create_database():
    Base.metadata.create_all(engine)

def add_production(shed_no, quantity, report_date):

    db = SessionLocal()

    record = (
        db.query(EggRecord)
        .filter(
            EggRecord.shed_no == shed_no,
            EggRecord.date == report_date
        )
        .first()
    )

    if record:
        record.produced = (record.produced or 0) + quantity
    else:
        record = EggRecord(
            date=report_date,
            shed_no=shed_no,
            produced=quantity,
        )
        db.add(record)

    db.commit()
    db.close()

def add_broken(shed_no, quantity, report_date):

    db = SessionLocal()

    record = (
        db.query(EggRecord)
        .filter(
            EggRecord.shed_no == shed_no,
            EggRecord.date == report_date
        )
        .first()
    )

    if record:
        record.broken = (record.broken or 0) + quantity
    else:
        record = EggRecord(
            date=report_date,
            shed_no=shed_no,
            broken=quantity,
        )
        db.add(record)

    db.commit()
    db.close()

def add_sold(shed_no, quantity, report_date):

    db = SessionLocal()

    record = (
        db.query(EggRecord)
        .filter(
            EggRecord.shed_no == shed_no,
            EggRecord.date == report_date
        )
        .first()
    )

    if record:
        record.sold = (record.sold or 0) + quantity
    else:
        record = EggRecord(
            date=report_date,
            shed_no=shed_no,
            sold=quantity,
        )
        db.add(record)

    db.commit()
    db.close()

def get_summary(shed_no, report_date):
    db = SessionLocal()

    # today = str(date.today())

    print("Searching for:")
    print("Shed:", shed_no)
    print("Date:", report_date)

    record = (
        db.query(EggRecord)
        .filter(
            EggRecord.shed_no == shed_no,
            EggRecord.date == report_date
        )
        .first()
    )

    db.close()

    return record

def get_daily_summary(report_date):

    db = SessionLocal()

    records = (
        db.query(EggRecord)
        .filter(EggRecord.date == report_date)
        .order_by(EggRecord.shed_no.asc())
        .all()
    )

    db.close()

    return records

def get_shed_count(report_date):

    db = SessionLocal()

    count = (
        db.query(func.count(func.distinct(EggRecord.shed_no)))
        .filter(EggRecord.date == report_date)
        .scalar()
    )

    db.close()

    return count

def get_farm_stock(report_date):

    db = SessionLocal()

    records = (
        db.query(EggRecord)
        .filter(EggRecord.date == report_date)
        .order_by(EggRecord.shed_no)
        .all()
    )

    db.close()

    return records

def get_records_by_date(report_date):

    db = SessionLocal()

    records = (
        db.query(EggRecord)
        .filter(EggRecord.date == report_date)
        .order_by(EggRecord.shed_no)
        .all()
    )

    db.close()

    return records

def get_weekly_summary(period):

    db = SessionLocal()

    today = date.today()

    if period == "last_week":

        this_week_start = today - timedelta(days=today.weekday())

        start_date = this_week_start - timedelta(days=7)

        end_date = this_week_start - timedelta(days=1)

    else:

        start_date = today - timedelta(days=today.weekday())

        end_date = today

    records = (
        db.query(EggRecord)
        .filter(
            EggRecord.date >= str(start_date),
            EggRecord.date <= str(end_date)
        )
        .order_by(EggRecord.date, EggRecord.shed_no)
        .all()
    )

    db.close()

    return records

def get_monthly_summary(period):

    db = SessionLocal()

    today = date.today()

    if period == "this_month":

        start_date = today.replace(day=1)
        end_date = today

    elif period == "last_month":

        first_day_this_month = today.replace(day=1)

        end_date = first_day_this_month - timedelta(days=1)

        start_date = end_date.replace(day=1)

    else:

        db.close()
        return []

    records = (
        db.query(EggRecord)
        .filter(
            EggRecord.date >= str(start_date),
            EggRecord.date <= str(end_date)
        )
        .order_by(EggRecord.date, EggRecord.shed_no)
        .all()
    )

    db.close()

    return records

def move_record(from_shed, to_shed, field, quantity, report_date):

    db = SessionLocal()

    try:

        source = (
            db.query(EggRecord)
            .filter(
                EggRecord.shed_no == from_shed,
                EggRecord.date == report_date
            )
            .first()
        )

        if source is None:
            db.close()
            return f"No record found for Shed {from_shed} on {report_date}."

        destination = (
            db.query(EggRecord)
            .filter(
                EggRecord.shed_no == to_shed,
                EggRecord.date == report_date
            )
            .first()
        )

        if destination is None:

            destination = EggRecord(
                shed_no=to_shed,
                date=report_date
            )

            db.add(destination)

        available = getattr(source, field) or 0

        if available < quantity:
            db.close()
            return (
                f"Cannot move {quantity} eggs.\n"
                f"Shed {from_shed} has only {available} {field}."
            )

        setattr(source, field, available - quantity)

        current = getattr(destination, field) or 0

        setattr(destination, field, current + quantity)

        db.commit()

        db.close()

        return "SUCCESS"

    except Exception as e:

        db.rollback()
        db.close()

        return str(e)
    
def update_record(shed, field, quantity, report_date):

    db = SessionLocal()

    try:

        record = (
            db.query(EggRecord)
            .filter(
                EggRecord.shed_no == shed,
                EggRecord.date == report_date
            )
            .first()
        )

        if record is None:
            db.close()
            return f"No record found for Shed {shed} on {report_date}."

        setattr(record, field, quantity)

        db.commit()

        db.close()

        return "SUCCESS"

    except Exception as e:

        db.rollback()

        db.close()

        return str(e)    
    
def remove_record(shed, field, quantity, report_date):

    db = SessionLocal()

    try:

        record = (
            db.query(EggRecord)
            .filter(
                EggRecord.shed_no == shed,
                EggRecord.date == report_date
            )
            .first()
        )

        if record is None:
            db.close()
            return f"No record found for Shed {shed} on {report_date}."

        current = getattr(record, field) or 0

        if quantity > current:
            db.close()
            return (
                f"❌ Cannot remove {quantity} eggs.\n"
                f"Shed {shed} has only {current} {field} eggs."
            )

        setattr(
            record,
            field,
            current - quantity
        )

        db.commit()

        db.close()

        return "SUCCESS"

    except Exception as e:

        db.rollback()

        db.close()

        return str(e)
    
def delete_field(shed, field, report_date):

    db = SessionLocal()

    try:

        record = (
            db.query(EggRecord)
            .filter(
                EggRecord.shed_no == shed,
                EggRecord.date == report_date
            )
            .first()
        )

        if record is None:
            db.close()
            return f"No record found for Shed {shed} on {report_date}."

        setattr(record, field, None)

        db.commit()

        db.close()

        return "SUCCESS"

    except Exception as e:

        db.rollback()
        db.close()

        return str(e)
    
def delete_record(shed, report_date):

    db = SessionLocal()

    try:

        record = (
            db.query(EggRecord)
            .filter(
                EggRecord.shed_no == shed,
                EggRecord.date == report_date
            )
            .first()
        )

        if record is None:
            db.close()
            return f"No record found for Shed {shed} on {report_date}."

        db.delete(record)

        db.commit()

        db.close()

        return "SUCCESS"

    except Exception as e:

        db.rollback()
        db.close()

        return str(e)

def add_birds(shed_no, birds, report_date):

    db = SessionLocal()

    try:

        record = (
            db.query(EggRecord)
            .filter(
                EggRecord.shed_no == shed_no,
                EggRecord.date == report_date
            )
            .first()
        )

        if record is None:

            record = EggRecord(
                shed_no=shed_no,
                date=report_date,
                birds=birds
            )

            db.add(record)

        else:
            record.birds = birds

        db.commit()

        db.close()

        return f"✅ Bird count updated to {birds} for Shed {shed_no}"

    except Exception as e:

        db.rollback()
        db.close()

        return str(e)
    
def get_birds(shed_no, report_date):

    db = SessionLocal()

    record = (
        db.query(EggRecord)
        .filter(
            EggRecord.shed_no == shed_no,
            EggRecord.date == report_date
        )
        .first()
    )

    db.close()

    if record is None:
        return None

    return record.birds

def get_total_birds(report_date):

    db = SessionLocal()

    total = (
        db.query(func.sum(EggRecord.birds))
        .filter(EggRecord.date == report_date)
        .scalar()
    )

    db.close()

    return total or 0

def get_total_live_birds(report_date):

    total_birds = get_total_birds(report_date)
    total_mortality = get_total_mortality(report_date)

    return total_birds - total_mortality

def add_mortality(shed_no, quantity, report_date):

    db = SessionLocal()

    try:

        record = (
            db.query(EggRecord)
            .filter(
                EggRecord.shed_no == shed_no,
                EggRecord.date == report_date
            )
            .first()
        )

        if record is None:

            record = EggRecord(
                shed_no=shed_no,
                date=report_date,
                mortality=quantity
            )

            db.add(record)

        else:

            birds = record.birds or 0
            if birds is None:
                db.close()
                return (
                    "❌ Please enter the bird count first before recording mortality."
                )
            current_mortality = record.mortality or 0

            if current_mortality + quantity > birds:

                db.close()

                return (
                    f"❌ Cannot record {quantity} mortality.\n"
                    f"Only {birds - current_mortality} live birds remaining in Shed {shed_no}."
                )

            record.mortality = current_mortality + quantity

        db.commit()
        db.close()

        return f"✅ Recorded {quantity} bird deaths in Shed {shed_no}"

    except Exception as e:

        db.rollback()
        db.close()

        return str(e)
    
def get_mortality(shed_no, report_date):

    db = SessionLocal()

    record = (
        db.query(EggRecord)
        .filter(
            EggRecord.shed_no == shed_no,
            EggRecord.date == report_date
        )
        .first()
    )

    db.close()

    if record is None:
        return 0

    return record.mortality or 0

def get_total_mortality(report_date):

    db = SessionLocal()

    total = (
        db.query(func.sum(EggRecord.mortality))
        .filter(EggRecord.date == report_date)
        .scalar()
    )

    db.close()

    return total or 0

def get_missing_sheds(report_date):

    db = SessionLocal()

    all_sheds = set(range(1, 10))   # 1 to 9

    reported_sheds = {
        record.shed_no
        for record in db.query(EggRecord)
        .filter(EggRecord.date == report_date)
        .all()
    }

    db.close()

    missing = sorted(all_sheds - reported_sheds)

    return missing

def get_missing_fields(report_date):

    db = SessionLocal()

    all_sheds = range(1, 10)

    records = (
        db.query(EggRecord)
        .filter(EggRecord.date == report_date)
        .all()
    )

    record_map = {
        record.shed_no: record
        for record in records
    }

    db.close()

    result = {}

    for shed in all_sheds:

        if shed not in record_map:

            result[shed] = ["No report submitted"]
            continue

        record = record_map[shed]

        missing = []

        if record.birds is None:
            missing.append("Bird Count")

        if record.mortality is None:
            missing.append("Mortality")

        if record.produced is None:
            missing.append("Production")

        if record.broken is None:
            missing.append("Broken")

        if record.sold is None:
            missing.append("Sold")

        if missing:
            result[shed] = missing

    return result

def get_comparison_summary(report_date):

    db = SessionLocal()

    records = (
        db.query(EggRecord)
        .filter(EggRecord.date == report_date)
        .all()
    )

    db.close()

    summary = {
        "birds": 0,
        "mortality": 0,
        "feed": 0,
        "produced": 0,
        "broken": 0,
        "sold": 0
    }

    for record in records:

        summary["birds"] += record.birds or 0
        summary["mortality"] += record.mortality or 0
        # summary["feed"] += record.feed or 0

        summary["produced"] += record.produced or 0
        summary["broken"] += record.broken or 0
        summary["sold"] += record.sold or 0

    summary["stock"] = (
        summary["produced"]
        - summary["broken"]
        - summary["sold"]
    )

    summary["live_birds"] = (
        summary["birds"]
        - summary["mortality"]
    )

    return summary

def get_week_comparison_summary(period):

    records = get_weekly_summary(period)

    summary = {
        "birds": 0,
        "live_birds": 0,
        "mortality": 0,
        "feed": 0,
        "produced": 0,
        "broken": 0,
        "sold": 0,
        "stock": 0
    }

    for record in records:

        summary["birds"] += record.birds or 0
        summary["mortality"] += record.mortality or 0
        # summary["feed"] += record.feed or 0

        summary["produced"] += record.produced or 0
        summary["broken"] += record.broken or 0
        summary["sold"] += record.sold or 0

    summary["stock"] = (
        summary["produced"]
        - summary["broken"]
        - summary["sold"]
    )

    summary["live_birds"] = (
        summary["birds"]
        - summary["mortality"]
    )

    return summary

def get_highest(field, report_date):

    db = SessionLocal()

    record = (
        db.query(EggRecord)
        .filter(EggRecord.date == report_date)
        .order_by(getattr(EggRecord, field).desc())
        .first()
    )

    db.close()

    return record

def get_lowest(field, report_date):

    db = SessionLocal()

    record = (
        db.query(EggRecord)
        .filter(EggRecord.date == report_date)
        .order_by(getattr(EggRecord, field).asc())
        .first()
    )

    db.close()

    return record

def get_month_comparison_summary(period):

    records = get_monthly_summary(period)

    summary = {
        "birds": 0,
        "live_birds": 0,
        "mortality": 0,
        "feed": 0,
        "produced": 0,
        "broken": 0,
        "sold": 0,
        "stock": 0
    }

    for record in records:

        summary["birds"] += record.birds or 0
        summary["mortality"] += record.mortality or 0
        # summary["feed"] += record.feed or 0

        summary["produced"] += record.produced or 0
        summary["broken"] += record.broken or 0
        summary["sold"] += record.sold or 0

    summary["stock"] = (
        summary["produced"]
        - summary["broken"]
        - summary["sold"]
    )

    summary["live_birds"] = (
        summary["birds"]
        - summary["mortality"]
    )

    return summary

def find_medicine(db, shed_no, medicine_name):

    medicines = (
        db.query(MedicineStock)
        .filter(
            MedicineStock.shed_no == shed_no
        )
        .all()
    )

    names = [m.medicine_name for m in medicines]

    match = get_close_matches(
        medicine_name,
        names,
        n=1,
        cutoff=0.6
    )

    if not match:
        return None

    return (
        db.query(MedicineStock)
        .filter(
            MedicineStock.shed_no == shed_no,
            MedicineStock.medicine_name == match[0]
        )
        .first()
    )

def add_medicine(shed_no, medicine_name, quantity, unit):

    db = SessionLocal()

    try:

        medicine = (
            db.query(MedicineStock)
            .filter(
                MedicineStock.shed_no == shed_no,
                MedicineStock.medicine_name == medicine_name
            )
            .first()
        )

        if medicine is None:

            medicine = MedicineStock(
                shed_no=shed_no,
                medicine_name=medicine_name,
                available=quantity,
                used=0,
                unit=unit
            )

            db.add(medicine)

        else:

            medicine.available += quantity

        db.commit()

        db.close()

        return (
            f"✅ Added {quantity} {unit} of {medicine_name}\n"
            f"to Shed {shed_no}"
        )

    except Exception as e:

        db.rollback()

        db.close()

        return str(e)

def use_medicine(shed_no, medicine_name, quantity):

    db = SessionLocal()

    try:

        medicine = find_medicine(
            db,
            shed_no,
            medicine_name
        )

        if medicine is None:

            db.close()

            return (
                f"{medicine_name} not found "
                f"in Shed {shed_no}."
            )

        remaining = (
            medicine.available
            - medicine.used
        )

        if quantity > remaining:

            db.close()

            return (
                f"Only {remaining} {medicine.unit} "
                f"remaining."
            )

        medicine.used += quantity

        db.commit()

        db.close()

        return (
            f"✅ Used {quantity} {medicine.unit} "
            f"of {medicine_name}"
        )

    except Exception as e:

        db.rollback()

        db.close()

        return str(e) 

def get_medicine(shed_no, medicine_name):

    db = SessionLocal()

    medicine = find_medicine(
        db,
        shed_no,
        medicine_name
    )

    if medicine is None:
        db.close()
        return None

    result = {
        "medicine_name": medicine.medicine_name,
        "available": medicine.available,
        "used": medicine.used,
        "unit": medicine.unit
    }

    db.close()

    return result

def get_all_medicines(shed_no=None):

    db = SessionLocal()

    query = db.query(MedicineStock)

    if shed_no is not None:
        query = query.filter(
            MedicineStock.shed_no == shed_no
        )

    medicines = query.order_by(
        MedicineStock.shed_no,
        MedicineStock.medicine_name
    ).all()

    db.close()

    return medicines

def get_medicine_totals_kg():

    db = SessionLocal()

    medicines = db.query(MedicineStock).all()

    db.close()

    total_available = 0
    total_used = 0

    for med in medicines:

        unit = med.unit.lower()

        available = med.available
        used = med.used

        if unit == "kg":
            factor = 1

        elif unit == "ml":
            factor = 0.001

        elif unit == "bottle":
            factor = 2

        else:
            factor = 1

        total_available += available * factor
        total_used += used * factor

    total_remaining = total_available - total_used

    return (
        round(total_available, 2),
        round(total_used, 2),
        round(total_remaining, 2)
    )

def find_feed(db,report_date, shed_no, feed_name):

    feeds = (
        db.query(FeedStock)
        .filter(
            FeedStock.date == report_date,
            FeedStock.shed_no == shed_no
        )
        .all()
    )

    names = [f.feed_name for f in feeds]

    match = get_close_matches(
        feed_name,
        names,
        n=1,
        cutoff=0.6
    )

    if not match:
        return None

    return (
        db.query(FeedStock)
        .filter(
            FeedStock.date == report_date,
            FeedStock.shed_no == shed_no,
            FeedStock.feed_name == match[0]
        )
        .first()
    )

def add_feed_stock(date, shed_no, feed_name, quantity, unit):

    db = SessionLocal()

    try:

        feed = (
            db.query(FeedStock)
            .filter(
                FeedStock.date == date,
                FeedStock.shed_no == shed_no,
                func.lower(FeedStock.feed_name) == feed_name.lower()
            )
            .first()
        )

        if feed:

            feed.available += quantity

        else:

            feed = FeedStock(

                date=date,

                shed_no=shed_no,

                feed_name=feed_name,

                available=quantity,

                used=0,

                unit=unit

            )

            db.add(feed)

        db.commit()

        db.close()

        return (
            f"✅ Added {quantity} {unit} "
            f"of {feed_name} to Shed {shed_no}"
        )

    except Exception as e:

        db.rollback()

        db.close()

        return str(e)
    
def use_feed(report_date, shed_no, feed_name, quantity):

    db = SessionLocal()

    try:

        feed = find_feed(
            db,
            report_date,
            shed_no,
            feed_name
        )

        if feed is None:

            db.close()

            return (
                f"{feed_name} not found "
                f"in Shed {shed_no}."
            )

        remaining = (
            feed.available
            - feed.used
        )

        if quantity > remaining:

            db.close()

            return (
                f"Only {remaining} {feed.unit} "
                f"remaining."
            )

        feed.used += quantity

        db.commit()

        db.close()

        return (
            f"✅ Used {quantity} {feed.unit} "
            f"of {feed.feed_name}"
        )

    except Exception as e:

        db.rollback()

        db.close()

        return str(e)    

def get_feed(report_date, shed_no, feed_name):

    db = SessionLocal()

    feed = find_feed(
        db,
        report_date, 
        shed_no,
        feed_name
    )

    db.close()

    return feed

def get_all_feeds(start_date, end_date=None, shed_no=None):

    db = SessionLocal()

    query = db.query(FeedStock)

    if end_date is None:

        query = query.filter(
            FeedStock.date == start_date
        )

    else:

        query = query.filter(
            FeedStock.date >= str(start_date),
            FeedStock.date <= str(end_date)
        )

    if shed_no is not None:

        query = query.filter(
            FeedStock.shed_no == shed_no
        )

    feeds = query.order_by(
        FeedStock.date,
        FeedStock.shed_no,
        FeedStock.feed_name
    ).all()

    db.close()

    return feeds

def get_feed_totals_kg():

    db = SessionLocal()

    feeds = db.query(FeedStock).all()

    db.close()

    total_available = 0
    total_used = 0

    for feed in feeds:

        total_available += feed.available
        total_used += feed.used

    total_remaining = (
        total_available
        - total_used
    )

    return (
        round(total_available, 2),
        round(total_used, 2),
        round(total_remaining, 2)
    )

def get_monthly_feeds(period):

    db = SessionLocal()

    today = date.today()

    if period == "this_month":

        start_date = today.replace(day=1)
        end_date = today

    elif period == "last_month":

        first_day_this_month = today.replace(day=1)

        end_date = first_day_this_month - timedelta(days=1)

        start_date = end_date.replace(day=1)

    else:

        db.close()
        return []

    feeds = (
        db.query(FeedStock)
        .filter(
            FeedStock.date >= str(start_date),
            FeedStock.date <= str(end_date)
        )
        .order_by(
            FeedStock.date,
            FeedStock.shed_no,
            FeedStock.feed_name
        )
        .all()
    )

    db.close()

    return feeds

def get_shed_daily_summary(report_date, shed_no):

    db = SessionLocal()

    record = (
        db.query(EggRecord)
        .filter(
            EggRecord.date == report_date,
            EggRecord.shed_no == shed_no
        )
        .first()
    )

    db.close()

    return record

def get_shed_weekly_summary(period, shed_no):

    db = SessionLocal()

    today = date.today()

    if period == "last_week":

        this_week_start = today - timedelta(days=today.weekday())

        start_date = this_week_start - timedelta(days=7)

        end_date = this_week_start - timedelta(days=1)

    else:

        start_date = today - timedelta(days=today.weekday())

        end_date = today

    records = (
        db.query(EggRecord)
        .filter(
            EggRecord.date >= str(start_date),
            EggRecord.date <= str(end_date),
            EggRecord.shed_no == shed_no
        )
        .order_by(EggRecord.date)
        .all()
    )

    db.close()

    return records

def get_shed_monthly_summary(period, shed_no):

    db = SessionLocal()

    today = date.today()

    if period == "this_month":

        start_date = today.replace(day=1)

        end_date = today

    elif period == "last_month":

        first_day_this_month = today.replace(day=1)

        end_date = first_day_this_month - timedelta(days=1)

        start_date = end_date.replace(day=1)

    else:

        db.close()

        return []

    records = (
        db.query(EggRecord)
        .filter(
            EggRecord.date >= str(start_date),
            EggRecord.date <= str(end_date),
            EggRecord.shed_no == shed_no
        )
        .order_by(EggRecord.date)
        .all()
    )

    db.close()

    return records

def get_week_comparison(shed_no=None):

    db = SessionLocal()

    today = date.today()

    this_week_start = today - timedelta(days=today.weekday())

    last_week_start = this_week_start - timedelta(days=7)

    last_week_end = this_week_start - timedelta(days=1)

    current_query = db.query(
        func.sum(EggRecord.produced),
        func.sum(EggRecord.broken),
        func.sum(EggRecord.sold),
        func.sum(EggRecord.mortality),
        func.sum(EggRecord.birds)
    ).filter(
        EggRecord.date >= str(this_week_start),
        EggRecord.date <= str(today)
    )

    previous_query = db.query(
        func.sum(EggRecord.produced),
        func.sum(EggRecord.broken),
        func.sum(EggRecord.sold),
        func.sum(EggRecord.mortality),
        func.sum(EggRecord.birds)
    ).filter(
        EggRecord.date >= str(last_week_start),
        EggRecord.date <= str(last_week_end)
    )

    if shed_no is not None:

        current_query = current_query.filter(
            EggRecord.shed_no == shed_no
        )

        previous_query = previous_query.filter(
            EggRecord.shed_no == shed_no
        )

    current = current_query.first()

    previous = previous_query.first()

    db.close()

    return {

        "current":{

            "produced": current[0] or 0,

            "broken": current[1] or 0,

            "sold": current[2] or 0,

            "mortality": current[3] or 0,

            "birds": current[4] or 0

        },

        "previous":{

            "produced": previous[0] or 0,

            "broken": previous[1] or 0,

            "sold": previous[2] or 0,

            "mortality": previous[3] or 0,

            "birds": previous[4] or 0

        }

    }

def get_month_comparison(shed_no=None):

    db = SessionLocal()

    today = date.today()

    this_month_start = today.replace(day=1)

    last_month_end = this_month_start - timedelta(days=1)

    last_month_start = last_month_end.replace(day=1)

    current_query = db.query(
        func.sum(EggRecord.produced),
        func.sum(EggRecord.broken),
        func.sum(EggRecord.sold),
        func.sum(EggRecord.mortality),
        func.sum(EggRecord.birds)
    ).filter(
        EggRecord.date >= str(this_month_start),
        EggRecord.date <= str(today)
    )

    previous_query = db.query(
        func.sum(EggRecord.produced),
        func.sum(EggRecord.broken),
        func.sum(EggRecord.sold),
        func.sum(EggRecord.mortality),
        func.sum(EggRecord.birds)
    ).filter(
        EggRecord.date >= str(last_month_start),
        EggRecord.date <= str(last_month_end)
    )

    if shed_no is not None:

        current_query = current_query.filter(
            EggRecord.shed_no == shed_no
        )

        previous_query = previous_query.filter(
            EggRecord.shed_no == shed_no
        )

    current = current_query.first()

    previous = previous_query.first()

    db.close()

    return {

        "current":{

            "produced": current[0] or 0,

            "broken": current[1] or 0,

            "sold": current[2] or 0,

            "mortality": current[3] or 0,

            "birds": current[4] or 0

        },

        "previous":{

            "produced": previous[0] or 0,

            "broken": previous[1] or 0,

            "sold": previous[2] or 0,

            "mortality": previous[3] or 0,

            "birds": previous[4] or 0

        }

    }

def get_day_comparison(compare_date=None, shed_no=None):
    print("Database compare_date:", compare_date)

    db = SessionLocal()

    if compare_date:

        current_date = datetime.strptime(
            compare_date,
            "%Y-%m-%d"
        ).date()

    else:

        current_date = date.today()

    previous_date = current_date - timedelta(days=1)

    current_query = db.query(
        func.sum(EggRecord.produced),
        func.sum(EggRecord.broken),
        func.sum(EggRecord.sold),
        func.sum(EggRecord.mortality),
        func.sum(EggRecord.birds)
    ).filter(
        EggRecord.date == str(current_date)
    )

    previous_query = db.query(
        func.sum(EggRecord.produced),
        func.sum(EggRecord.broken),
        func.sum(EggRecord.sold),
        func.sum(EggRecord.mortality),
        func.sum(EggRecord.birds)
    ).filter(
        EggRecord.date == str(previous_date)
    )

    if shed_no is not None:

        current_query = current_query.filter(
            EggRecord.shed_no == shed_no
        )

        previous_query = previous_query.filter(
            EggRecord.shed_no == shed_no
        )

    current = current_query.first()

    previous = previous_query.first()

    db.close()

    return {

        "current":{

            "produced": current[0] or 0,

            "broken": current[1] or 0,

            "sold": current[2] or 0,

            "mortality": current[3] or 0,

            "birds": current[4] or 0

        },

        "previous":{

            "produced": previous[0] or 0,

            "broken": previous[1] or 0,

            "sold": previous[2] or 0,

            "mortality": previous[3] or 0,

            "birds": previous[4] or 0

        }

    }

def get_day_comparison_between_dates(date1, date2, shed_no=None):

    db = SessionLocal()

    # Convert "today" to actual date
    if date1 == "today":
        current_date = date.today()
    else:
        current_date = datetime.strptime(
            date1,
            "%Y-%m-%d"
        ).date()

    if date2 == "today":
        previous_date = date.today()
    else:
        previous_date = datetime.strptime(
            date2,
            "%Y-%m-%d"
        ).date()

    current_query = db.query(
        func.sum(EggRecord.produced),
        func.sum(EggRecord.broken),
        func.sum(EggRecord.sold),
        func.sum(EggRecord.mortality),
        func.sum(EggRecord.birds)
    ).filter(
        EggRecord.date == str(current_date)
    )

    previous_query = db.query(
        func.sum(EggRecord.produced),
        func.sum(EggRecord.broken),
        func.sum(EggRecord.sold),
        func.sum(EggRecord.mortality),
        func.sum(EggRecord.birds)
    ).filter(
        EggRecord.date == str(previous_date)
    )

    if shed_no is not None:

        current_query = current_query.filter(
            EggRecord.shed_no == shed_no
        )

        previous_query = previous_query.filter(
            EggRecord.shed_no == shed_no
        )

    current = current_query.first()

    previous = previous_query.first()

    db.close()

    return {

        "current": {

            "produced": current[0] or 0,
            "broken": current[1] or 0,
            "sold": current[2] or 0,
            "mortality": current[3] or 0,
            "birds": current[4] or 0

        },

        "previous": {

            "produced": previous[0] or 0,
            "broken": previous[1] or 0,
            "sold": previous[2] or 0,
            "mortality": previous[3] or 0,
            "birds": previous[4] or 0

        }

    }

def add_egg_price_setting(
    price_per_egg,
    eggs_per_tray,
    price_per_tray,
    discount_threshold,
    discount_percentage,
    available_eggs
):
    db = SessionLocal()

    setting = EggPriceSetting(
        price_per_egg=price_per_egg,
        eggs_per_tray=eggs_per_tray,
        price_per_tray=price_per_tray,
        discount_threshold=discount_threshold,
        discount_percentage=discount_percentage,
        available_eggs=available_eggs
    )

    db.add(setting)
    db.commit()
    db.close()

def get_egg_price_setting():
    db = SessionLocal()

    try:
        setting = (
            db.query(EggPriceSetting)
            .order_by(EggPriceSetting.id.desc())
            .first()
        )

        return setting

    finally:
        db.close()

def create_pending_order(
    chat_id,
    customer_whatsapp,
    quantity_eggs,
    subtotal
):
    db = SessionLocal()

    try:
        order = CustomerOrder(
            chat_id=chat_id,
            customer_whatsapp=customer_whatsapp,
            quantity_eggs=quantity_eggs,
            subtotal=subtotal,
            discount_percentage=0,
            final_amount=subtotal,
            status="pending"
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    except Exception as error:
        db.rollback()
        print("Error creating pending order:", error)
        return None

    finally:
        db.close()

def get_latest_pending_order(chat_id):
    db = SessionLocal()

    try:
        order = (
            db.query(CustomerOrder)
            .filter(
                CustomerOrder.chat_id == chat_id,
                CustomerOrder.status == "pending"
            )
            .order_by(CustomerOrder.id.desc())
            .first()
        )

        return order

    finally:
        db.close()

def apply_discount_to_order(
    order_id,
    discount_percentage,
    final_amount
):
    db = SessionLocal()

    try:
        order = (
            db.query(CustomerOrder)
            .filter(CustomerOrder.id == order_id)
            .first()
        )

        if not order:
            return None

        order.discount_percentage = discount_percentage
        order.final_amount = final_amount

        db.commit()
        db.refresh(order)

        return order

    except Exception as error:
        db.rollback()
        print("Error applying discount:", error)
        return None

    finally:
        db.close()

def confirm_customer_order(chat_id):
    db = SessionLocal()

    try:
        order = (
            db.query(CustomerOrder)
            .filter(
                CustomerOrder.chat_id == chat_id,
                CustomerOrder.status == "pending"
            )
            .order_by(CustomerOrder.id.desc())
            .first()
        )

        if not order:
            return {
                "success": False,
                "message": "No pending order was found."
            }

        setting = (
            db.query(EggPriceSetting)
            .order_by(EggPriceSetting.id.desc())
            .first()
        )

        if not setting:
            return {
                "success": False,
                "message": "Egg price settings are not available."
            }

        if order.quantity_eggs > setting.available_eggs:
            return {
                "success": False,
                "message": (
                    f"Only {setting.available_eggs} eggs are currently available."
                )
            }

        order.status = "confirmed"
        order.confirmed_at = datetime.now()

        setting.available_eggs -= order.quantity_eggs

        db.commit()
        db.refresh(order)

        return {
            "success": True,
            "order_id": order.id,
            "quantity_eggs": order.quantity_eggs,
            "subtotal": order.subtotal,
            "discount_percentage": order.discount_percentage,
            "final_amount": order.final_amount,
            "remaining_eggs": setting.available_eggs
        }

    except Exception as error:
        db.rollback()
        print("Error confirming customer order:", error)

        return {
            "success": False,
            "message": "Unable to confirm the order."
        }

    finally:
        db.close()        

def confirm_customer_order(chat_id):
    db = SessionLocal()

    try:
        order = (
            db.query(CustomerOrder)
            .filter(
                CustomerOrder.chat_id == chat_id,
                CustomerOrder.status == "pending"
            )
            .order_by(CustomerOrder.id.desc())
            .first()
        )

        if not order:
            return {
                "success": False,
                "message": "No pending order was found."
            }

        setting = (
            db.query(EggPriceSetting)
            .order_by(EggPriceSetting.id.desc())
            .first()
        )

        if not setting:
            return {
                "success": False,
                "message": "Egg price settings were not found."
            }

        if order.quantity_eggs > setting.available_eggs:
            return {
                "success": False,
                "message": (
                    f"Not enough eggs are available.\n"
                    f"Requested: {order.quantity_eggs}\n"
                    f"Available: {setting.available_eggs}"
                )
            }

        # Reduce available stock
        setting.available_eggs -= order.quantity_eggs

        # Confirm the order
        order.status = "confirmed"
        order.confirmed_at = datetime.now()

        db.commit()
        db.refresh(order)

        # Store normal values before closing the database session
        result = {
            "success": True,
            "message": "Order confirmed successfully.",
            "order_id": order.id,
            "quantity_eggs": order.quantity_eggs,
            "subtotal": order.subtotal,
            "discount_percentage": order.discount_percentage or 0,
            "final_amount": order.final_amount,
            "remaining_eggs": setting.available_eggs
        }

        return result

    except Exception as error:
        db.rollback()

        print("Error confirming customer order:", error)

        return {
            "success": False,
            "message": "An error occurred while confirming the order."
        }

    finally:
        db.close()

def get_farm_financial_setting(report_date=None):

    db = SessionLocal()

    try:

        if report_date is None:
            report_date = date.today()

        if isinstance(report_date, str):
            report_date = date.fromisoformat(report_date)

        setting = (
            db.query(FarmFinancialSetting)
            .filter(
                FarmFinancialSetting.effective_date <= report_date
            )
            .order_by(
                FarmFinancialSetting.effective_date.desc()
            )
            .first()
        )

        if not setting:
            return None

        return {
            "egg_price": float(setting.egg_price),
            "expected_percentage": float(
                setting.expected_percentage
            ),
            "effective_date": str(setting.effective_date)
        }

    finally:
        db.close()

def get_feed_price_setting(feed_name, report_date=None):

    db = SessionLocal()

    try:

        if report_date is None:
            report_date = date.today()

        if isinstance(report_date, str):
            report_date = date.fromisoformat(report_date)

        setting = (
            db.query(FeedPriceSetting)
            .filter(
                FeedPriceSetting.feed_name == feed_name,
                FeedPriceSetting.effective_date <= report_date
            )
            .order_by(
                FeedPriceSetting.effective_date.desc()
            )
            .first()
        )

        if not setting:
            return None

        return {
            "feed_name": setting.feed_name,
            "cost_per_ton": float(setting.cost_per_ton),
            "effective_date": str(setting.effective_date)
        }

    finally:
        db.close()

def get_daily_financial_report_data(report_date=None):

    db = SessionLocal()

    try:

        if report_date is None:
            report_date = date.today()

        if isinstance(report_date, date):
            report_date_str = report_date.isoformat()
        else:
            report_date_str = report_date

        farm_setting = get_farm_financial_setting(report_date_str)

        if not farm_setting:
            return {
                "error": "Farm financial settings not found"
            }

        egg_records = (
            db.query(EggRecord)
            .filter(EggRecord.date == report_date_str)
            .order_by(EggRecord.shed_no)
            .all()
        )

        if not egg_records:
            return {
                "error": f"No production data found for {report_date_str}"
            }

        production_rows = []

        birds_by_shed = {}

        total_production_value = 0

        production_rows = []

        total_production_value = 0

        for record in egg_records:

            birds = record.birds or 0
            birds_by_shed[record.shed_no] = birds
            mortality = record.mortality or 0

            first_collection = record.first_collection or 0
            second_collection = record.second_collection or 0

            total_eggs = record.produced or 0

            egg_price = farm_setting["egg_price"]

            expected_percentage = farm_setting[
                "expected_percentage"
            ]

            actual_percentage = 0

            if birds > 0:
                actual_percentage = (
                    total_eggs / birds
                ) * 100

            production_value = total_eggs * egg_price

            total_production_value += production_value

            production_rows.append({
                "shed_no": record.shed_no,
                "birds": birds,
                "first_collection": first_collection,
                "second_collection": second_collection,
                "total_eggs": total_eggs,
                "mortality": mortality,
                "expected_percentage": expected_percentage,
                "actual_percentage": round(
                    actual_percentage,
                    2
                ),
                "egg_price": egg_price,
                "production_value": round(
                    production_value,
                    2
                )
            })

        feed_records = (
            db.query(FeedStock)
            .filter(FeedStock.date == report_date_str)
            .all()
        )

        feed_rows = []

        feed_by_shed = {}

        total_feed_cost = 0

        for feed in feed_records:

            feed_used_kg = float(feed.used or 0)

            price_setting = get_feed_price_setting(
                feed.feed_name,
                report_date_str
            )

            cost_per_ton = 0

            if price_setting:
                cost_per_ton = float(
                    price_setting["cost_per_ton"]
                )

            feed_cost = (
                feed_used_kg / 1000
            ) * cost_per_ton

            total_feed_cost += feed_cost

            shed = feed.shed_no

            if shed not in feed_by_shed:

                feed_by_shed[shed] = {
                    "feed_used_kg": 0,
                    "total_feed_cost": 0
                }

            feed_by_shed[shed]["feed_used_kg"] += feed_used_kg
            feed_by_shed[shed]["total_feed_cost"] += feed_cost

        for shed_no, values in feed_by_shed.items():

            birds = birds_by_shed.get(shed_no, 0)

            feed_used_kg = values["feed_used_kg"]

            feed_consumed_mt = feed_used_kg / 1000

            feed_cost_per_ton = 0

            if feed_consumed_mt > 0:
                feed_cost_per_ton = (
                    values["total_feed_cost"]
                    / feed_consumed_mt
                )

            feed_rows.append({
                "shed_no": shed_no,

                "feed_consumed_mt": round(
                    feed_consumed_mt,
                    3
                ),

                "feed_per_bird_g": round(
                    (feed_used_kg * 1000) / birds,
                    2
                ) if birds else 0,

                "feed_cost_per_ton": round(
                    feed_cost_per_ton,
                    2
                ),

                "total_feed_cost": round(
                    values["total_feed_cost"],
                    2
                )
            })
        total_expenses = total_feed_cost

        net_profit_or_loss = (
            total_production_value - total_expenses
        )

        return {
            "date": report_date_str,
            "production_overview": production_rows,
            "feed_consumption": feed_rows,
            "pnl_summary": {
                "total_production_value": round(
                    total_production_value,
                    2
                ),
                "total_feed_cost": round(
                    total_feed_cost,
                    2
                ),
                "total_expenses": round(
                    total_expenses,
                    2
                ),
                "net_profit_or_loss": round(
                    net_profit_or_loss,
                    2
                )
            }
        }

    finally:
        db.close()

def save_reminder(request):

    db = SessionLocal()

    try:
        schedule_date = None

        if request.schedule_date:
            schedule_date = datetime.strptime(
                request.schedule_date,
                "%Y-%m-%d"
            ).date()

        schedule_time = datetime.strptime(
            request.schedule_time,
            "%H:%M"
        ).time()

        reminder = Reminder(
            message=request.message.strip(),
            repeat_type=request.repeat_type,
            schedule_date=schedule_date,
            schedule_time=schedule_time,
            week_day=request.week_day,
            is_active=True
        )

        db.add(reminder)

        # Generate reminder.id before commit
        db.flush()

        for recipient in request.recipients:

            reminder_recipient = ReminderRecipient(
                reminder_id=reminder.id,
                recipient_name=recipient.recipient_name,
                chat_id=recipient.chat_id,
                recipient_type=recipient.recipient_type
            )

            db.add(reminder_recipient)

        reminder.job_id = f"reminder_{reminder.id}"

        db.commit()
        db.refresh(reminder)

        # Return the required values before closing the session
        return {
            "id": reminder.id,
            "message": reminder.message,
            "repeat_type": reminder.repeat_type,
            "schedule_date": reminder.schedule_date,
            "schedule_time": reminder.schedule_time,
            "week_day": reminder.week_day,
            "is_active": reminder.is_active,
            "job_id": reminder.job_id
        }

    except Exception as error:
        db.rollback()

        print("Save reminder error:", error)

        raise

    finally:
        db.close()

def get_all_reminders():

    db = SessionLocal()

    try:
        reminders = (
            db.query(Reminder)
            .order_by(Reminder.id.desc())
            .all()
        )

        result = []

        for reminder in reminders:

            recipients = []

            for recipient in reminder.recipients:

                recipients.append({
                    "id": recipient.id,
                    "recipient_name": recipient.recipient_name,
                    "chat_id": recipient.chat_id,
                    "recipient_type": recipient.recipient_type
                })

            result.append({
                "id": reminder.id,
                "message": reminder.message,
                "repeat_type": reminder.repeat_type,
                "schedule_date": (
                    reminder.schedule_date.isoformat()
                    if reminder.schedule_date
                    else None
                ),
                "schedule_time": (
                    reminder.schedule_time.strftime("%H:%M")
                    if reminder.schedule_time
                    else None
                ),
                "week_day": reminder.week_day,
                "is_active": reminder.is_active,
                "job_id": reminder.job_id,
                "created_at": (
                    reminder.created_at.isoformat()
                    if reminder.created_at
                    else None
                ),
                "recipients": recipients
            })

        return result

    finally:
        db.close()
        
def delete_reminder(reminder_id):

    db = SessionLocal()

    try:

        reminder = (
            db.query(Reminder)
            .filter(Reminder.id == reminder_id)
            .first()
        )

        if not reminder:
            return False

        db.delete(reminder)

        db.commit()

        return True

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()

def update_reminder_status(reminder_id, is_active):

    db = SessionLocal()

    try:
        reminder = (
            db.query(Reminder)
            .filter(Reminder.id == reminder_id)
            .first()
        )

        if not reminder:
            return None

        reminder.is_active = is_active

        db.commit()

        db.refresh(reminder)

        return reminder.is_active

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def get_reminder_by_id(reminder_id):

    db = SessionLocal()

    try:
        reminder = (
            db.query(Reminder)
            .filter(Reminder.id == reminder_id)
            .first()
        )

        if not reminder:
            return None

        recipients = (
            db.query(ReminderRecipient)
            .filter(
                ReminderRecipient.reminder_id == reminder_id
            )
            .all()
        )

        return {
            "id": reminder.id,
            "message": reminder.message,
            "is_active": reminder.is_active,
            "recipients": [
                {
                    "recipient_name": recipient.recipient_name,
                    "chat_id": recipient.chat_id,
                    "recipient_type": recipient.recipient_type
                }
                for recipient in recipients
            ]
        }

    finally:
        db.close()

def save_contact(request):

    db = SessionLocal()

    try:
        name = request.name.strip()
        number = request.whatsapp_number.strip()

        if not name:
            raise ValueError("Contact name is required")

        if not number:
            raise ValueError("WhatsApp number is required")

        number = number.replace(" ", "").replace("+", "")

        existing_contact = (
            db.query(SavedContact)
            .filter(
                SavedContact.whatsapp_number == number
            )
            .first()
        )

        if existing_contact:
            raise ValueError(
                "This WhatsApp number is already saved"
            )

        chat_id = f"{number}@c.us"

        contact = SavedContact(
            name=name,
            whatsapp_number=number,
            chat_id=chat_id
        )

        db.add(contact)
        db.commit()
        db.refresh(contact)

        return {
            "id": contact.id,
            "name": contact.name,
            "whatsapp_number": contact.whatsapp_number,
            "chat_id": contact.chat_id
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def get_saved_contacts():

    db = SessionLocal()

    try:
        contacts = (
            db.query(SavedContact)
            .order_by(SavedContact.name)
            .all()
        )

        return [
            {
                "id": contact.id,
                "name": contact.name,
                "whatsapp_number": contact.whatsapp_number,
                "chat_id": contact.chat_id,
                "recipient_type": "contact"
            }
            for contact in contacts
        ]

    finally:
        db.close()

def delete_saved_contact(contact_id):

    db = SessionLocal()

    try:
        contact = (
            db.query(SavedContact)
            .filter(SavedContact.id == contact_id)
            .first()
        )

        if not contact:
            return False

        db.delete(contact)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


