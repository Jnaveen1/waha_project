from database import SessionLocal
from models import Message
from llm import generate_friend_reply , understand_message
from waha import (
    get_phone_number_from_lid,
    get_chat_name,
    send_message
)

from datetime import date, timedelta
from tabulate import tabulate 
from report_generator import generate_daily_pdf

from database import (
    add_production,
    add_broken,
    add_sold,
    get_summary,
    get_daily_summary, 
    get_shed_count, 
    get_farm_stock, 
    get_records_by_date, 
    get_weekly_summary, 
    get_monthly_summary , 
    move_record , 
    update_record ,
    remove_record , 
    delete_field,
    delete_record , 
    add_birds,
    get_birds,
    get_total_birds, 
    add_mortality,
    get_mortality,
    get_total_mortality , 
    get_total_live_birds , 
    get_missing_sheds,
    get_missing_fields , 
    get_comparison_summary , 
    get_week_comparison_summary , 
    get_highest, get_lowest , 
    get_month_comparison_summary, 
    add_medicine,
    use_medicine,
    get_medicine,
    get_all_medicines, 
    get_medicine_totals_kg ,
    add_feed_stock,
    use_feed,
    get_feed,
    get_all_feeds,
    get_feed_totals_kg,
    get_day_comparison,
    get_week_comparison,
    get_month_comparison , 
    get_shed_weekly_summary , 
    get_shed_monthly_summary ,
    get_latest_pending_order,
    get_egg_price_setting,
    apply_discount_to_order ,
    create_pending_order , 
    confirm_customer_order ,
    get_daily_financial_report_data
)

ALLOWED_GROUP_ID = "120363423099150354@g.us"
FARM_GROUP_ID = "1234567890"

def save_message(msg):
    db = SessionLocal()

    try:
        message_id = msg.get("id")

        if not message_id:
            print("Message ignored: message ID missing")
            return

        existing = (
            db.query(Message)
            .filter(Message.message_id == message_id)
            .first()
        )

        if existing:
            print("Message already exists")
            return

        message_data = msg.get("_data", {})

        from_id = msg.get("from", "")
        to_id = msg.get("to", "")
        from_me = msg.get("fromMe", False)

        # Find the actual conversation ID
        if from_me:
            chat_id = to_id
        else:
            chat_id = from_id

        # Check whether this conversation is a group
        is_group = chat_id.endswith("@g.us")

        # Get personal contact name or group name
        chat_name = get_chat_name(chat_id)

        # Find the actual sender
        if from_me:
            sender_id = from_id
        else:
            sender_id = msg.get("participant") or from_id

        sender_phone = get_phone_number_from_lid(sender_id)
        sender_name = message_data.get("notifyName")

        new_message = Message(
            message_id=message_id,
            chat_id=chat_id,
            chat_name=chat_name,
            is_group=is_group,
            sender=sender_phone,
            sender_name=sender_name,
            from_me=from_me,
            body=msg.get("body", ""),
            timestamp=msg.get("timestamp"),
            message_type=message_data.get("type", "unknown")
        )

        db.add(new_message)
        db.commit()

        print("Message saved to MySQL")
        print("WhatsApp name:", sender_name)
        print("Chat name:", chat_name)
        print("Is group:", is_group)

        message_body = msg.get("body", "")
        # Reply only to messages sent by another person inside a group
        if (
            is_group
            and not from_me
            and chat_id == ALLOWED_GROUP_ID
        ):

            print("Friends group message:", message_body)

            reply_text = generate_friend_reply(message_body)

            print("LLM Reply:", reply_text)

            send_message(
                chat_id=chat_id,
                text=reply_text
            )
        elif(
            is_group
            and not from_me
            and chat_id == FARM_GROUP_ID
        ):
            print("Farm group message:", message_body)

            parsed_data = understand_message(message_body)

            print("Parsed farm data:", parsed_data)

            result = process_request(parsed_data)

            print("Service result:", result)

            send_message(
                chat_id=chat_id,
                text=str(result)
            )



    except Exception as error:
        db.rollback()
        print("Error saving message:", error)

    finally:
        db.close()

def format_report_table(records):

    lines = []

    lines.append(
        f"{'Shed':<5} {'Birds':>6} {'Eggs':>6} {'Broken':>7} {'Sold':>6} {'Stock':>7}"
    )

    lines.append("-" * 45)

    for record in records:

        shed = record.shed_no or 0

        birds = record.birds or 0
        produced = record.produced or 0
        broken = record.broken or 0
        sold = record.sold or 0

        stock = produced - broken - sold

        lines.append(

            f"{shed:<5}"

            f"{birds:>7}"

            f"{produced:>7}"

            f"{broken:>8}"

            f"{sold:>7}"

            f"{stock:>8}"

        )
    return "```\n" + "\n".join(lines) + "\n```"

def format_summary_comparison_table(summary1, summary2, column1, column2):

    table = [

                [
                    "Birds",
                    summary1["birds"],
                    summary2["birds"],
                    f"{summary1['birds'] - summary2['birds']:+}"
                ],

                [
                    "Live Birds",
                    summary1["live_birds"],
                    summary2["live_birds"],
                    f"{summary1['live_birds'] - summary2['live_birds']:+}"
                ],

                [
                    "Mortality",
                    summary1["mortality"],
                    summary2["mortality"],
                    f"{summary1['mortality'] - summary2['mortality']:+}"
                ],

                [
                    "Produced",
                    summary1["produced"],
                    summary2["produced"],
                    f"{summary1['produced'] - summary2['produced']:+}"
                ],

                [
                    "Broken",
                    summary1["broken"],
                    summary2["broken"],
                    f"{summary1['broken'] - summary2['broken']:+}"
                ],

                [
                    "Sold",
                    summary1["sold"],
                    summary2["sold"],
                    f"{summary1['sold'] - summary2['sold']:+}"
                ],

                [
                    "Stock",
                    summary1["stock"],
                    summary2["stock"],
                    f"{summary1['stock'] - summary2['stock']:+}"
                ],

            ]

    return (
        "```"
        + tabulate(
            table,
            headers=[
                "Metric",
                column1,
                column2 , 
                "Change"
            ],
            tablefmt="github"
        )
        + "```"
    )

def format_comparison_table(summary1, summary2, week1, week2):

    table = [

        ["Birds",
         summary1["birds"],
         summary2["birds"] ,
         f"{summary1['birds'] - summary2['birds']:+}"
         ],

        [
            "Live Birds",
            summary1["live_birds"],
            summary2["live_birds"],
            f"{summary1['live_birds'] - summary2['live_birds']:+}"
        ],

        [
            "Mortality",
            summary1["mortality"],
            summary2["mortality"],
            f"{summary1['mortality'] - summary2['mortality']:+}"
        ],

        # ["Feed (kg)",
        #  summary1["feed"],
        #  summary2["feed"]],

        [
            "Produced",
            summary1["produced"],
            summary2["produced"],
            f"{summary1['produced'] - summary2['produced']:+}"
        ],

        [
            "Broken",
            summary1["broken"],
            summary2["broken"],
            f"{summary1['broken'] - summary2['broken']:+}"
        ],

        [
            "Sold",
            summary1["sold"],
            summary2["sold"],
            f"{summary1['sold'] - summary2['sold']:+}"
        ],

        [
            "Stock",
            summary1["stock"],
            summary2["stock"],
            f"{summary1['stock'] - summary2['stock']:+}"
        ],

    ]

    return (
        "```"
        + tabulate(
            table,
            headers=[
                "Metric",
                week1.replace("_", " ").title(),
                week2.replace("_", " ").title(), 
                "Change"
            ],
            tablefmt="github"
        )
        + "```"
    )

def _safe_quantity(value):
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def _safe_number(value):
    if value is None:
        return 0

    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

def generate_daily_reminder(report_date):

    missing_sheds = get_missing_sheds(report_date)

    missing_fields = get_missing_fields(report_date)

    reply = f"⏰ Daily Reminder ({report_date})\n\n"

    if missing_sheds:

        reply += "❌ Missing Shed Reports\n"

        for shed in missing_sheds:
            reply += f"• Shed {shed}\n"

        reply += "\n"

    incomplete = False

    for shed, fields in missing_fields.items():

        if fields == ["No report submitted"]:
            continue

        incomplete = True

        reply += (
            f"🐔 Shed {shed}\n"
            f"Missing : {', '.join(fields)}\n\n"
        )

    if not missing_sheds and not incomplete:

        return "✅ All 9 sheds have submitted complete reports."

    return reply

def eggs_to_trays(eggs):
    trays = eggs // 30
    remaining_eggs = eggs % 30
    return f"{trays}.{remaining_eggs:02d}"

def get_report_date(data):

    report_date = data.get("date")

    if report_date is None or report_date == "today":
        return str(date.today())

    elif report_date == "yesterday":
        return str(date.today() - timedelta(days=1))

    return report_date

def format_quantity(eggs, unit):

    if unit == "tray":
        return f"{eggs_to_trays(eggs)} trays"

    return f"{eggs} eggs"

def format_period_table(date, birds, produced, broken, sold, mortality):

    stock = produced - broken - sold

    table = [[
        birds,
        produced,
        broken,
        sold,
        stock,
        mortality
    ]]

    return (
        f"📅 {date}\n\n"
        + "```"
        + tabulate(
            table,
            headers=[
                "Birds",
                "Eggs",
                "Broken",
                "Sold",
                "Stock",
                "Mortality"
            ],
            tablefmt="plain"
        )
        + "```"
    )

def generate_period_summary(records, title):

    if not records:
        return "No records found."

    reply = f"{title}\n\n"

    total_birds = 0
    total_mortality = 0

    total_produced = 0
    total_broken = 0
    total_sold = 0

    current_date = None

    day_birds = 0
    day_mortality = 0

    day_produced = 0
    day_broken = 0
    day_sold = 0

    for record in records:

        if current_date != record.date:

            if current_date is not None:

                reply += format_period_table(

                    current_date,

                    day_birds,

                    day_produced,

                    day_broken,

                    day_sold,

                    day_mortality

                )

                reply += "\n\n"

            current_date = record.date

            day_birds = 0
            day_mortality = 0

            day_produced = 0
            day_broken = 0
            day_sold = 0

        birds = _safe_number(record.birds)
        mortality = _safe_number(record.mortality)

        produced = _safe_number(record.produced)
        broken = _safe_number(record.broken)
        sold = _safe_number(record.sold)

        day_birds += birds
        day_mortality += mortality

        day_produced += produced
        day_broken += broken
        day_sold += sold

        total_birds += birds
        total_mortality += mortality

        total_produced += produced
        total_broken += broken
        total_sold += sold

    # Last day's table
    reply += format_period_table(

        current_date,

        day_birds,

        day_produced,

        day_broken,

        day_sold,

        day_mortality

    )

    reply += "\n\n"

    total_stock = total_produced - total_broken - total_sold

    feed_available, feed_used, feed_remaining = get_feed_totals_kg()

    reply += (
        "--------------------------\n"
        f"Total Birds      : {total_birds}\n"
        f"Total Mortality  : {total_mortality}\n"
        f"Total Feed Used  : {feed_used} kg\n\n"
        f"Total Produced   : {total_produced}\n"
        f"Total Broken     : {total_broken}\n"
        f"Total Sold       : {total_sold}\n"
        f"Current Stock    : {total_stock}"
    )

    med_available, med_used, med_remaining = get_medicine_totals_kg()

    reply += (
        "\n\n💊 Current Medicine Summary\n\n"
        f"Available : {med_available} kg\n"
        f"Used      : {med_used} kg\n"
        f"Remaining : {med_remaining} kg"
    )

    reply += (
        "\n\n🌾 Current Feed Summary\n\n"
        f"Available : {feed_available} kg\n"
        f"Used      : {feed_used} kg\n"
        f"Remaining : {feed_remaining} kg"
    )

    return reply

def get_records_for_period(data):

    period = data["date"]

    if period == "this_week":
        return get_weekly_summary("this_week"), "This Week"

    elif period == "last_week":
        return get_weekly_summary("last_week"), "Last Week"

    elif period == "this_month":
        return get_monthly_summary(), "This Month"

    else:
        report_date = get_report_date(data)
        return get_records_by_date(report_date), report_date

def process_request(data, chat_id=None,customer_whatsapp=None):

    intent = data.get("intent")
    shed = data.get("shed")
    unit = data.get("unit", "egg")

    if intent == "add_production":
        if shed is None and intent not in [
            "get_daily_summary",
            "get_shed_count",
            "get_farm_stock", 
            "get_total_broken", 
            "get_weekly_summary",
            "get_monthly_summary",
        ]:
            return (
                "Please specify the shed number.\n"
                "Example: 'Give summary of shed 1'."
            )

        quantity = _safe_quantity(data.get("quantity"))

        if quantity is None:
            return "Please provide a valid quantity."
        
        quantity = data["quantity"]

        if quantity < 0:
            return (
                "❌ Quantity cannot be negative.\n"
                "Please enter a positive value."
            )

        report_date = data.get("date")

        if report_date is None or report_date == "today":
            report_date = str(date.today())

        elif report_date == "yesterday":
            report_date = str(date.today() - timedelta(days=1))
        add_production(shed, quantity, report_date) 
        return f"✅ Added {quantity} produced eggs to Shed {shed}"

    elif intent == "add_broken":

        quantity = _safe_quantity(data.get("quantity"))

        if quantity is None:
            return "Please provide a valid quantity."
        
        quantity = data["quantity"]

        if quantity < 0:
            return (
                "❌ Quantity cannot be negative.\n"
                "Please enter a positive value."
            )

        report_date = get_report_date(data)

        record = get_summary(shed, report_date)

        if record is None:
            return f"No production record found for Shed {shed} on {report_date}."

        produced = _safe_number(record.produced)
        broken = _safe_number(record.broken)
        sold = _safe_number(record.sold)

        available = produced - broken - sold

        if quantity > available:
            return (
                f"❌ Cannot record {quantity} broken eggs.\n"
                f"Only {available} eggs are available in Shed {shed}."
            )

        add_broken(
            shed,
            quantity,
            report_date
        )

        return f"✅ Recorded {quantity} broken eggs in Shed {shed}"

    elif intent == "add_sold":

        quantity = _safe_quantity(data.get("quantity"))

        if quantity is None:
            return "Please provide a valid quantity."
        
        if quantity < 0:
            return (
                "❌ Quantity cannot be negative.\n"
                "Please enter a positive value."
            )

        report_date = get_report_date(data)

        record = get_summary(shed, report_date)

        if record is None:
            return f"No production record found for Shed {shed} on {report_date}."

        produced = _safe_number(record.produced)
        broken = _safe_number(record.broken)
        sold = _safe_number(record.sold)

        available = produced - broken - sold

        if quantity > available:
            return (
                f"❌ Cannot sell {quantity} eggs.\n"
                f"Only {available} eggs are available in Shed {shed}."
            )

        add_sold(
            shed,
            quantity,
            report_date
        )

        return f"✅ Recorded {quantity} sold eggs from Shed {shed}"    # ---------------- SHED SUMMARY ----------------

    elif intent == "get_summary":

        if shed is None:
            return (
                "Please specify the shed number.\n"
                "Example: 'Give summary of shed 1'."
            )


        period = data.get("date")


        # Weekly handling
        if period in ["this_week", "last_week"]:

            records = get_shed_weekly_summary(
                period,
                shed
            )


            if not records:
                return (
                    f"No data found for Shed {shed} "
                    f"for {period.replace('_',' ')}."
                )


            total_produced = 0
            total_broken = 0
            total_sold = 0
            total_mortality = 0


            for record in records:

                total_produced += _safe_number(record.produced)
                total_broken += _safe_number(record.broken)
                total_sold += _safe_number(record.sold)
                total_mortality += _safe_number(record.mortality)


            stock = (
                total_produced -
                total_broken -
                total_sold
            )


            return (
                f"📊 Shed {shed} "
                f"{period.replace('_',' ').title()} Summary\n\n"

                f"🥚 Produced   : {total_produced}\n"
                f"❌ Broken     : {total_broken}\n"
                f"📦 Sold       : {total_sold}\n"
                f"📦 Stock      : {stock}\n"
                f"💀 Mortality  : {total_mortality}"
            )



        # Daily handling (existing logic)

        report_date = get_report_date(data)


        record = get_summary(
            shed,
            report_date
        )


        if record is None:
            return (
                f"No data found for Shed {shed} "
                f"on {report_date}."
            )


        produced = _safe_number(record.produced)
        broken = _safe_number(record.broken)
        sold = _safe_number(record.sold)


        stock = produced - broken - sold


        return (
            f"📊 Shed {shed} Summary ({report_date})\n\n"
            f"🐔 Birds       : {record.birds}\n"
            f"💀 Mortality  : {record.mortality}\n"
            f"🥚 Produced   : {record.produced}\n"
            f"❌ Broken     : {record.broken}\n"
            f"📦 Sold       : {record.sold}\n"
            f"📦 Stock      : {stock}"
        )

    elif intent == "get_broken":

        if shed is None:
            return "Please specify the shed number."

        report_date = str(date.today())

        record = get_summary(shed, report_date)

        if record is None:
            return f"No data found for Shed {shed} today."

        return f"Shed {shed} has {record.broken} broken eggs today."

    elif intent == "get_sold":

        if shed is None:
            return "Please specify the shed number."

        report_date = str(date.today())

        record = get_summary(shed, report_date)

        if record is None:
            return f"No data found for Shed {shed} today."

        return f"Shed {shed} has {record.sold} sold eggs today."

    elif intent == "get_production":

        if shed is None:
            return "Please specify the shed number."

        report_date = str(date.today())

        record = get_summary(shed, report_date)

        if record is None:
            return f"No data found for Shed {shed} today."

        if unit == "tray":
            trays = eggs_to_trays(record.produced)
            return (
                f"Shed {shed} produced "
                f"{trays} trays."
            )

        return (
            f"Shed {shed} produced "
            f"{format_quantity(record.produced, unit)} today."
        )

    elif intent == "get_daily_summary":

        report_date = get_report_date(data)

        records = get_daily_summary(report_date)

        if not records:
            return f"No data found for {report_date}."

        reply = f"📊 Farm Summary ({report_date})\n\n"

        total_birds = 0
        total_mortality = 0
        # total_feed = 0

        total_produced = 0
        total_broken = 0
        total_sold = 0

        reply += format_report_table(records) + "\n\n"

        for record in records:

            birds = _safe_number(record.birds)
            mortality = _safe_number(record.mortality)
            # feed = _safe_number(record.feed)

            produced = _safe_number(record.produced)
            broken = _safe_number(record.broken)
            sold = _safe_number(record.sold)

            total_birds += birds
            total_mortality += mortality
            # total_feed += feed

            total_produced += produced
            total_broken += broken
            total_sold += sold
        total_stock = total_produced - total_broken - total_sold

        reply += (
            "--------------------------\n"
            f"Total Birds      : {total_birds}\n"
            f"Total Mortality  : {total_mortality}\n"
            # f"Total Feed       : {total_feed} kg\n\n"
            f"Total Produced   : {total_produced}\n"
            f"Total Broken     : {total_broken}\n"
            f"Total Sold       : {total_sold}\n"
            f"Current Stock    : {total_stock}"
        )

        available, used, remaining = get_medicine_totals_kg()

        reply += (

            "\n\n💊Current Medicine Summary\n\n"

            f"Available : {available} kg\n"

            f"Used      : {used} kg\n"

            f"Remaining : {remaining} kg"

        )

        available, used, remaining = get_feed_totals_kg()

        reply += (

            "\n\n🌾Current Feed Summary\n\n"

            f"Available : {available} kg\n"

            f"Used      : {used} kg\n"

            f"Remaining : {remaining} kg"

        )

        return reply 
    
    elif intent == "get_remaining":

        if shed is None:
            return "Please specify the shed number."

        report_date = get_report_date(data)

        record = get_summary(shed, report_date)

        if record is None:
            return f"No data found for Shed {shed} on {report_date}."
        
        produced = _safe_number(record.produced)
        broken = _safe_number(record.broken)
        sold = _safe_number(record.sold)

        remaining = produced - broken - sold

        if unit == "tray":
            trays = eggs_to_trays(remaining)
            return (
                f"Shed {shed} has "
                f"{trays} trays remaining."
            )

        return (
            f"Shed {shed} has "
            f"{remaining} eggs remaining."
        )

    elif intent == "get_shed_count":

        report_date = get_report_date(data)

        count = get_shed_count(report_date)

        return f"There are {count} sheds on {report_date}."
    
    elif intent == "get_farm_stock":

        report_date = get_report_date(data)

        records = get_farm_stock(report_date)

        if not records:
            return f"No data found for {report_date}."

        reply = f"📦 Farm Stock ({report_date})\n\n"

        total_stock = 0

        for record in records:

            produced = _safe_number(record.produced)
            broken = _safe_number(record.broken)
            sold = _safe_number(record.sold)

            stock = produced - broken - sold

            if unit == "tray":
                stock_display = f"{eggs_to_trays(stock)} trays"
            else:
                stock_display = f"{stock} eggs"

            reply += (
                f"🐔 Shed {record.shed_no} : {stock_display}\n"
            )

            total_stock += stock

        if unit == "tray":
            total_display = f"{eggs_to_trays(total_stock)} trays"
        else:
            total_display = f"{total_stock} eggs"

        reply += (
            "\n--------------------------\n"
            f"Total Stock : {total_display}"
        )

        return reply

    elif intent == "get_total_broken":

        records, title = get_records_for_period(data)

        total = sum(
            _safe_number(record.broken)
            for record in records
        )

        return (
            f"❌ Total Broken ({title})\n\n"
            f"{format_quantity(total, unit)}"
        )
    
    elif intent == "get_total_production":

        records, title = get_records_for_period(data)

        total = sum(
            _safe_number(record.produced)
            for record in records
        )

        return (
            f"🥚 Total Production ({title})\n\n"
            f"{format_quantity(total, unit)}"
        )

    elif intent == "get_total_sold":

        records, title = get_records_for_period(data)

        total = sum(
            _safe_number(record.sold)
            for record in records
        )

        return (
            f"📦 Total Sold ({title})\n\n"
            f"{format_quantity(total, unit)}"
        )
    
    elif intent == "get_total_remaining":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        total = sum(
            (_safe_number(record.produced))
            - (_safe_number(record.broken))
            - (_safe_number(record.sold))
            for record in records
        )

        return (
            f"🥚 Total Remaining ({report_date})\n\n"
            f"{format_quantity(total, unit)}"
        )    

    elif intent == "get_highest_production":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        if not records:
            return f"No data found for {report_date}."

        highest = max(records, key=lambda r: _safe_number(r.produced))

        return (
            f"🏆 Highest Production ({report_date})\n\n"
            f"🐔 Shed {highest.shed_no}\n"
            f"Produced : {format_quantity(_safe_number(highest.produced), unit)}"
        )
    
    elif intent == "get_highest_broken":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        if not records:
            return f"No data found for {report_date}."

        highest = max(records, key=lambda r: _safe_number(r.broken))

        return (
            f"🥚 Highest Broken Eggs ({report_date})\n\n"
            f"🐔 Shed {highest.shed_no}\n"
            f"Broken : {format_quantity(_safe_number(highest.broken), unit)}"
        )

    elif intent == "get_highest_sold":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        if not records:
            return f"No data found for {report_date}."

        highest = max(records, key=lambda r: _safe_number(r.sold))

        return (
            f"🥚 Highest Sold Eggs ({report_date})\n\n"
            f"🐔 Shed {highest.shed_no}\n"
            f"Sold : {format_quantity(_safe_number(highest.sold), unit)}"
        )

    elif intent == "get_highest_stock":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        if not records:
            return f"No data found for {report_date}."

        highest = max(
            records,
            key=lambda r: _safe_number(r.produced) - _safe_number(r.broken) - _safe_number(r.sold)
        )

        stock = _safe_number(highest.produced) - _safe_number(highest.broken) - _safe_number(highest.sold)

        return (
            f"📦 Highest Stock ({report_date})\n\n"
            f"🐔 Shed {highest.shed_no}\n"
            f"Stock : {format_quantity(stock, unit)}"
        )
    
    elif intent == "get_highest_mortality":

        report_date = get_report_date(data)

        record = get_highest("mortality", report_date)

        if record is None:
            return f"No data found for {report_date}."

        return (
            f"🏆 Highest Mortality ({report_date})\n\n"
            f"🐔 Shed {record.shed_no}\n"
            f"💀 Mortality : {record.mortality}"
        )

    elif intent == "get_highest_birds":

        report_date = get_report_date(data)

        record = get_highest("birds", report_date)

        if record is None:
            return f"No data found for {report_date}."

        return (
            f"🏆 Highest Bird Count ({report_date})\n\n"
            f"🐔 Shed {record.shed_no}\n"
            f"Birds : {record.birds}"
        )

    elif intent == "get_lowest_production":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        if not records:
            return f"No data found for {report_date}."

        lowest = min(records, key=lambda r: _safe_number(r.produced))

        return (
            f"📉 Lowest Production ({report_date})\n\n"
            f"🐔 Shed {lowest.shed_no}\n"
            f"Produced : {format_quantity(_safe_number(lowest.produced), unit)}"
        )

    elif intent == "get_lowest_broken":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        if not records:
            return f"No data found for {report_date}."

        lowest = min(records, key=lambda r: _safe_number(r.broken))

        return (
            f"📉 Lowest Broken Eggs ({report_date})\n\n"
            f"🐔 Shed {lowest.shed_no}\n"
            f"Broken : {format_quantity(_safe_number(lowest.broken), unit)}"
        )

    elif intent == "get_lowest_sold":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        if not records:
            return f"No data found for {report_date}."

        lowest = min(records, key=lambda r: _safe_number(r.sold))

        return (
            f"📉 Lowest Sold Eggs ({report_date})\n\n"
            f"🐔 Shed {lowest.shed_no}\n"
            f"Sold : {format_quantity(_safe_number(lowest.sold), unit)}"
        )

    elif intent == "get_lowest_stock":

        report_date = get_report_date(data)

        records = get_records_by_date(report_date)

        if not records:
            return f"No data found for {report_date}."

        lowest = min(
            records,
            key=lambda r: _safe_number(r.produced) - _safe_number(r.broken) - _safe_number(r.sold)
        )

        stock = _safe_number(lowest.produced) - _safe_number(lowest.broken) - _safe_number(lowest.sold)

        return (
            f"📉 Lowest Stock ({report_date})\n\n"
            f"🐔 Shed {lowest.shed_no}\n"
            f"Stock : {format_quantity(stock, unit)}"
        )

    elif intent == "get_lowest_mortality":

        report_date = get_report_date(data)

        record = get_lowest("mortality", report_date)

        if record is None:
            return f"No data found for {report_date}."

        return (
            f"📉 Lowest Mortality ({report_date})\n\n"
            f"🐔 Shed {record.shed_no}\n"
            f"💀 Mortality : {_safe_number(record.mortality)} birds"
        )

    elif intent == "get_lowest_birds":

        report_date = get_report_date(data)

        record = get_lowest("birds", report_date)

        if record is None:
            return f"No data found for {report_date}."

        return (
            f"📉 Lowest Bird Count ({report_date})\n\n"
            f"🐔 Shed {record.shed_no}\n"
            f"🐔 Birds : {_safe_number(record.birds)}"
        )

    elif intent == "get_weekly_summary":

        period = data.get("date", "this_week")

        shed_no = data.get("shed")


        if shed_no:

            records = get_shed_weekly_summary(
                period,
                shed_no
            )

            title = (
                f"📅 Shed {shed_no} "
                f"{period.replace('_',' ').title()} Report"
            )


        else:

            records = get_weekly_summary(
                period
            )

            if period == "last_week":
                title = "📅 Last Week Report"
            else:
                title = "📅 This Week Report"


        return generate_period_summary(
            records,
            title
        )

    elif intent == "get_monthly_summary":

        period = data.get("date", "this_month")

        shed_no = data.get("shed")

        if shed_no:

            records = get_shed_monthly_summary(
                period,
                shed_no
            )

            title = (
                f"📊 Shed {shed_no} "
                f"{period.replace('_',' ').title()} Summary"
            )


        else:

            records = get_monthly_summary(
                period
            )


            if period == "last_month":
                title = "📊 Last Month Summary"
            else:
                title = "📊 This Month Summary"


        return generate_period_summary(
            records,
            title
        )

    elif intent == "move_record":

        from_shed = data["from_shed"]
        to_shed = data["to_shed"]
        field = data["field"]
        quantity = data["quantity"]

        report_date = get_report_date(data)

        result = move_record(
            from_shed,
            to_shed,
            field,
            quantity,
            report_date
        )

        if result == "SUCCESS":

            return (
                f"✅ Successfully moved {quantity} {field} eggs\n\n"
                f"From Shed {from_shed}\n"
                f"To Shed {to_shed}"
            )

        return result
    
    elif intent == "update_record":

        shed = data["shed"]
        field = data["field"]
        quantity = data["quantity"]

        report_date = get_report_date(data)

        result = update_record(
            shed,
            field,
            quantity,
            report_date
        )

        if result == "SUCCESS":

            return (
                f"✅ Updated {field} of Shed {shed} "
                f"to {quantity} eggs."
            )

        return result
    
    elif intent == "remove_record":

        shed = data["shed"]
        field = data["field"]
        quantity = data["quantity"]

        report_date = get_report_date(data)

        result = remove_record(
            shed,
            field,
            quantity,
            report_date
        )

        if result == "SUCCESS":

            return (
                f"✅ Removed {quantity} {field} eggs "
                f"from Shed {shed}"
            )

        return result

    elif intent == "delete_field":

        shed = data["shed"]
        field = data["field"]

        report_date = get_report_date(data)

        result = delete_field(
            shed,
            field,
            report_date
        )

        if result == "SUCCESS":

            return (
                f"✅ Deleted {field} data "
                f"from Shed {shed}"
            )

        return result

    elif intent == "delete_record":

        shed = data["shed"]

        report_date = get_report_date(data)

        result = delete_record(
            shed,
            report_date
        )

        if result == "SUCCESS":

            return (
                f"✅ Deleted all records "
                f"of Shed {shed} "
                f"for {report_date}"
            )

        return result

    elif intent == "add_birds":

        shed = data["shed"]
        quantity = data["quantity"]
        if quantity < 0:
            return (
                "❌ Quantity cannot be negative.\n"
                "Please enter a positive value."
            )

        report_date = get_report_date(data)

        result = add_birds(
            shed,
            quantity,
            report_date
        )

        return result

    elif intent == "get_birds":

        shed = data["shed"]
        
        report_date = get_report_date(data)

        # <-- This part must be OUTSIDE the if/elif

        birds = get_birds(
            shed,
            report_date
        )

        if birds is None:
            return f"No bird count found for Shed {shed} on {report_date}."

        return (
            f"🐔 Bird Count ({report_date})\n\n"
            f"Shed {shed} : {birds} birds"
        )

    elif intent == "get_total_birds":

        records, title = get_records_for_period(data)

        total = sum(
            _safe_number(record.birds)
            for record in records
        )

        return (
            f"🐔 Total Birds ({title})\n\n"
            f"{total}"
        )

    elif intent == "add_mortality":

        shed = data["shed"]
        report_date = get_report_date(data)
        quantity = data["quantity"]

        if quantity < 0:
            return (
                "❌ Quantity cannot be negative.\n"
                "Please enter a positive value."
            )

        result = add_mortality(
            shed,
            quantity,
            report_date
        )

        return result
    
    elif intent == "get_mortality":

        shed = data["shed"]
        report_date = get_report_date(data)
        mortality = get_mortality(
            shed,
            report_date
        )

        return (
            f"🐔 Shed {shed}\n\n"
            f"Mortality : {mortality} birds"
        )
    
    elif intent == "get_total_mortality":

        records, title = get_records_for_period(data)

        total = sum(
            _safe_number(record.mortality)
            for record in records
        )

        return (
            f"💀 Total Mortality ({title})\n\n"
            f"{total}"
        )
    
    elif intent == "add_feed":

        shed = data["shed"]

        feed = data["feed"]

        quantity = data["quantity"]

        unit = data.get("unit", "kg")

        report_date = get_report_date(data)

        return add_feed_stock(

            report_date,

            shed,

            feed,

            quantity,

            unit

    )
  
    elif intent == "use_feed":

        shed = data["shed"]

        feed = data["feed"]

        quantity = data["quantity"]

        report_date = get_report_date(data)

        return use_feed(

            report_date , 

            shed,

            feed,

            quantity

        )

    elif intent == "get_feed":

        shed = data.get("shed")

        feed = data.get("feed")

        report_date = get_report_date(data)
        print("data", report_date)
        # No feed specified → show all feeds
        if feed is None:

            feeds = get_all_feeds(report_date, shed)

            if not feeds:

                if shed is None:
                    return "No feed found."

                return f"No feed found in Shed {shed}."

            title = (
                f"🌾 Feed Summary - Shed {shed}"
                if shed is not None
                else "🌾 Feed Summary - All Sheds"
            )

            reply = title + "\n\n"

            current_shed = None

            for item in feeds:

                if shed is None and current_shed != item.shed_no:

                    current_shed = item.shed_no

                    reply += f"🐔 Shed {current_shed}\n"

                remaining = item.available - item.used

                reply += (
                    f"{item.feed_name}\n"
                    f"Available : {item.available} {item.unit}\n"
                    f"Used      : {item.used} {item.unit}\n"
                    f"Remaining : {remaining} {item.unit}\n\n"
                )

            return reply

        # Single feed
        record = get_feed(report_date ,shed, feed)

        if record is None:

            return f"{feed} not found in Shed {shed}."

        remaining = record.available - record.used

        return (
            f"🌾 {record.feed_name}\n\n"
            f"🐔 Shed : {shed}\n"
            f"Available : {record.available} {record.unit}\n"
            f"Used : {record.used} {record.unit}\n"
            f"Remaining : {remaining} {record.unit}"
        )

    elif intent == "get_feed_remaining":

        shed = data.get("shed")

        feed = data.get("feed")

        # Show all feeds
        if feed is None:

            feeds = get_all_feeds(shed)

            if not feeds:

                if shed is None:
                    return "No feed found."

                return f"No feed found in Shed {shed}."

            title = (
                f"🌾 Remaining Feed - Shed {shed}"
                if shed is not None
                else "🌾 Remaining Feed - All Sheds"
            )

            reply = title + "\n\n"

            current_shed = None

            for item in feeds:

                if shed is None and current_shed != item.shed_no:

                    current_shed = item.shed_no

                    reply += f"🐔 Shed {current_shed}\n"

                remaining = item.available - item.used

                reply += (
                    f"{item.feed_name}\n"
                    f"Remaining : {remaining} {item.unit}\n\n"
                )

            return reply

        # Single feed
        record = get_feed(shed, feed)

        if record is None:

            return f"{feed} not found in Shed {shed}."

        remaining = record.available - record.used

        return (
            f"🌾 {record.feed_name}\n\n"
            f"Remaining : {remaining} {record.unit}"
        )

    elif intent == "get_feed_used":

        shed = data.get("shed")

        feed = data.get("feed")

        if feed is None:

            feeds = get_all_feeds(shed)

            if not feeds:

                if shed is None:
                    return "No feed found."

                return f"No feed found in Shed {shed}."

            title = (
                f"🌾 Feed Usage - Shed {shed}"
                if shed is not None
                else "🌾 Feed Usage - All Sheds"
            )

            reply = title + "\n\n"

            current_shed = None

            for item in feeds:

                if shed is None and current_shed != item.shed_no:

                    current_shed = item.shed_no

                    reply += f"🐔 Shed {current_shed}\n"

                reply += (
                    f"{item.feed_name}\n"
                    f"Used : {item.used} {item.unit}\n\n"
                )

            return reply

        record = get_feed(shed, feed)

        if record is None:

            return f"{feed} not found in Shed {shed}."

        return (
            f"🌾 {record.feed_name}\n\n"
            f"Used : {record.used} {record.unit}"
        )

    elif intent == "get_total_live_birds":

        report_date = get_report_date(data)

        live_birds = get_total_live_birds(report_date)

        return (
            f"🐓 Total Live Birds ({report_date})\n\n"
            f"{live_birds} birds"
        )
    
    elif intent == "get_missing_sheds":

        report_date = get_report_date(data)

        missing = get_missing_sheds(report_date)

        if not missing:
            return (
                f"✅ All 9 sheds have submitted today's report."
            )

        reply = f"⚠️ Missing Shed Reports ({report_date})\n\n"

        for shed in missing:
            reply += f"• Shed {shed}\n"

        reply += f"\nTotal Missing : {len(missing)}"

        return reply
    
    elif intent == "get_missing_fields":

        report_date = get_report_date(data)

        result = get_missing_fields(report_date)

        if not result:
            return (
                f"✅ All 9 sheds have completed today's report."
            )

        reply = f"⚠️ Pending Report Fields ({report_date})\n\n"

        for shed in sorted(result.keys()):

            reply += f"🐔 Shed {shed}\n"

            for field in result[shed]:
                reply += f"• {field}\n"

            reply += "\n"

        return reply
    
    elif intent == "compare_dates":

        date1 = data["date1"]
        date2 = data["date2"]

        # Convert relative dates
        if date1 == "today":
            date1 = str(date.today())
        elif date1 == "yesterday":
            date1 = str(date.today() - timedelta(days=1))

        if date2 == "today":
            date2 = str(date.today())
        elif date2 == "yesterday":
            date2 = str(date.today() - timedelta(days=1))

        summary1 = get_comparison_summary(date1)
        summary2 = get_comparison_summary(date2)
        field = data.get("field")
        if field:

            value1 = summary1[field]
            value2 = summary2[field]

            difference = value1 - value2

            return (
                f"{field.title()} Comparison\n\n"
                f"{date1}: {value1}\n"
                f"{date2}: {value2}\n\n"
                f"Difference: {difference:+}"
            )

        # reply = (
        #     f"📊 Date Comparison\n\n"
        #     f"{date1}  ↔  {date2}\n\n"

        #     f"🐔 Birds\n"
        #     f"{summary1['birds']} → {summary2['birds']}\n\n"

        #     f"🐥 Live Birds\n"
        #     f"{summary1['live_birds']} → {summary2['live_birds']}\n\n"

        #     f"💀 Mortality\n"
        #     f"{summary1['mortality']} → {summary2['mortality']}\n\n"

        #     f"🌾 Feed\n"
        #     f"{summary1['feed']} kg → {summary2['feed']} kg\n\n"

        #     f"🥚 Produced\n"
        #     f"{summary1['produced']} → {summary2['produced']}\n\n"

        #     f"❌ Broken\n"
        #     f"{summary1['broken']} → {summary2['broken']}\n\n"

        #     f"📦 Sold\n"
        #     f"{summary1['sold']} → {summary2['sold']}\n\n"

        #     f"📦 Stock\n"
        #     f"{summary1['stock']} → {summary2['stock']}"
        # )

        reply = (
            "📊 Date Comparison\n\n"
            f"{date1} ↔ {date2}\n\n"
        )

        reply += format_summary_comparison_table(

            summary1,

            summary2,

            date1,

            date2

        )

        return reply
    
    elif intent == "compare_weeks":

        week1 = data["week1"]
        week2 = data["week2"]

        summary1 = get_week_comparison_summary(week1)
        summary2 = get_week_comparison_summary(week2)

        field = data.get("field")

        if field:

            value1 = summary1[field]
            value2 = summary2[field]

            difference = value1 - value2

            if difference > 0:
                status = f"📈 Increased by {difference}"
            elif difference < 0:
                status = f"📉 Decreased by {abs(difference)}"
            else:
                status = "➖ No Change"

            unit = ""

            if field == "feed":
                unit = " kg"

            elif field in ["produced", "broken", "sold", "stock"]:
                unit = " eggs"

            elif field in ["birds", "live_birds", "mortality"]:
                unit = " birds"

            return (
                f"📊 {field.replace('_',' ').title()} Weekly Comparison\n\n"
                f"{week1} : {value1}{unit}\n"
                f"{week2} : {value2}{unit}\n\n"
                f"{status}"
            )
        
        reply = (
                "📊 Weekly Comparison\n\n"
                f"{week1.replace('_',' ').title()} ↔ "
                f"{week2.replace('_',' ').title()}\n\n"
            )

        reply += format_comparison_table(
            summary1,
            summary2,
            week1,
            week2
            )

        return reply
   
    elif intent == "compare_months":

        month1 = data["month1"]
        month2 = data["month2"]

        summary1 = get_month_comparison_summary(month1)
        summary2 = get_month_comparison_summary(month2)

        field = data.get("field")

        if field:

            value1 = summary1[field]
            value2 = summary2[field]

            difference = value1 - value2

            if difference > 0:
                status = f"📈 Increased by {difference}"
            elif difference < 0:
                status = f"📉 Decreased by {abs(difference)}"
            else:
                status = "➖ No Change"

            unit = ""

            if field == "feed":
                unit = " kg"

            elif field in ["produced", "broken", "sold", "stock"]:
                unit = " eggs"

            elif field in ["birds", "live_birds", "mortality"]:
                unit = " birds"

            return (
                f"📊 {field.replace('_',' ').title()} Monthly Comparison\n\n"
                f"{month1} : {value1}{unit}\n"
                f"{month2} : {value2}{unit}\n\n"
                f"{status}"
            )
        
        reply = (
            "📊 Monthly Comparison\n\n"
            f"{month1.replace('_', ' ').title()} ↔ "
            f"{month2.replace('_', ' ').title()}\n\n"
        )
        
        reply += format_summary_comparison_table(
            summary1,
            summary2,
            month1,
            month2
        )

        return reply 
    
    elif intent == "add_medicine":

        shed = data["shed"]

        medicine = data["medicine"]

        quantity = data["quantity"]

        unit = data["unit"]

        return add_medicine(
            shed,
            medicine,
            quantity,
            unit
        )

    elif intent == "use_medicine":

        shed = data["shed"]

        medicine = data["medicine"]

        quantity = data["quantity"]

        return use_medicine(
            shed,
            medicine,
            quantity
        )

    elif intent == "get_medicine":

        shed = data["shed"]

        medicine = data["medicine"]

        record = get_medicine(
            shed,
            medicine
        )

        if record is None:

            return (
                f"{medicine} not found "
                f"in Shed {shed}."
            )

        remaining = (
            record["available"]
            - record["used"]
        )

        return (
            f"💊 {record["medicine_name"]}\n\n"

            f"🐔 Shed : {shed}\n"

            f"Available : {record["available"]} {record["unit"]}\n"

            f"Used : {record["used"]} {record["unit"]}\n"

            f"Remaining : {remaining} {record["unit"]}"
    )

    elif intent == "get_all_medicines":

        shed = data["shed"]

        medicines = get_all_medicines(shed)

        if not medicines:

            return (
                f"No medicines found "
                f"in Shed {shed}."
            )

        reply = (
            f"💊 Medicines in Shed {shed}\n\n"
        )

        for medicine in medicines:

            remaining = (
                medicine.available
                - medicine.used
            )

            reply += (
                f"{medicine.medicine_name}\n"

                f"Available : {medicine.available} {medicine.unit}\n"

                f"Used : {medicine.used} {medicine.unit}\n"

                f"Remaining : {remaining} {medicine.unit}\n\n"
            )

        return reply

    elif intent == "get_medicine_remaining":

        shed = data["shed"]
        medicine = data.get("medicine")

        if medicine is None:

            medicines = get_all_medicines(shed)

            if not medicines:
                return f"No medicines found in Shed {shed}."

            message = f"💊 Remaining Medicines - Shed {shed}\n\n"

            for med in medicines:

                remaining = med.available - med.used

                message += (
                    f"{med.medicine_name}\n"
                    f"Remaining : {remaining} {med.unit}\n\n"
                )

            return message

        record = get_medicine(shed, medicine)


        record = get_medicine(
            shed,
            medicine
        )

        if record is None:

            return (
                f"{medicine} not found in Shed {shed}."
            )

        remaining = (
            record.available
            - record.used
        )

        return (
            f"💊 {medicine}\n\n"
            f"Remaining : {remaining} {record.unit}"
        )

    elif intent == "get_medicine_used":

        shed = data.get("shed")
        medicine = data.get("medicine")

        # CASE 1: No medicine mentioned → show all medicines
        if medicine is None:

            medicines = get_all_medicines(shed)

            if not medicines:

                if shed is None:
                    return "No medicines found."

                return f"No medicines found in Shed {shed}."

            title = (
                f"💊 Medicine Usage - Shed {shed}"
                if shed is not None
                else "💊 Medicine Usage - All Sheds"
            )

            message = f"{title}\n\n"

            current_shed = None

            for med in medicines:

                if shed is None:

                    if current_shed != med.shed_no:

                        current_shed = med.shed_no

                        message += f"🐔 Shed {current_shed}\n"

                message += (
                    f"{med.medicine_name} : "
                    f"{med.used} {med.unit}\n"
                )

            return message

        # CASE 2: Particular medicine
        record = get_medicine(
            shed,
            medicine
        )

        if record is None:

            return (
                f"{medicine} not found "
                f"in Shed {shed}."
            )

        return (
            f"💊 {record['medicine_name']}\n\n"
            f"🐔 Shed : {shed}\n"
            f"Used : {record['used']} {record['unit']}"
        )
    
    elif intent == "generate_pdf":

        from report_generator import generate_daily_pdf_report

        report_date = get_report_date(data)

        pdf_path = generate_daily_pdf_report(report_date)

        return {
            "type": "pdf",
            "file": pdf_path
        }

    elif intent == "generate_weekly_pdf":

        from report_generator import generate_weekly_pdf_report

        period = data.get("date")

        if period == "last_week":
            pdf_path = generate_weekly_pdf_report("last_week")
        else:
            pdf_path = generate_weekly_pdf_report("this_week")

        return {
            "type": "pdf",
            "file": pdf_path
        }

    elif intent == "generate_monthly_pdf":

        from report_generator import generate_monthly_pdf_report

        report_period = data.get("date")

        if report_period == "last_month":

            pdf_path = generate_monthly_pdf_report("last_month")

        else:

            pdf_path = generate_monthly_pdf_report("this_month")

        return {
            "type": "pdf",
            "file": pdf_path
        }

    elif intent == "invalid_shed":
        return (
            f"❌ Shed {data['shed']} does not exist.\n"
            "Valid sheds are 1 to 9."
        )

    elif intent == "generate_shed_pdf":

        from report_generator import generate_shed_pdf_report

        shed_no = data.get("shed")

        period = data.get("date", "today")

        pdf_path = generate_shed_pdf_report(
            shed_no,
            period
        )

        return {
            "type": "pdf",
            "file": pdf_path
        }

    elif intent == "compare_report":

        comparison = data.get("comparison")
        shed_no = data.get("shed")

        if comparison == "day":
            result = get_day_comparison(shed_no)

        elif comparison == "week":
            result = get_week_comparison(shed_no)

        elif comparison == "month":
            result = get_month_comparison(shed_no)

        else:
            return "Invalid comparison period."

        current = result["current"]
        previous = result["previous"]

        title = "📊 Comparison Report"

        if shed_no:
            title += f" (Shed {shed_no})"

        message = (
            f"{title}\n\n"

            f"🥚 Produced\n"
            f"Current : {current['produced']}\n"
            f"Previous: {previous['produced']}\n\n"

            f"💥 Broken\n"
            f"Current : {current['broken']}\n"
            f"Previous: {previous['broken']}\n\n"

            f"🛒 Sold\n"
            f"Current : {current['sold']}\n"
            f"Previous: {previous['sold']}\n\n"

            f"🐔 Mortality\n"
            f"Current : {current['mortality']}\n"
            f"Previous: {previous['mortality']}\n\n"

            f"🐥 Birds\n"
            f"Current : {current['birds']}\n"
            f"Previous: {previous['birds']}"
        )

        return message

    elif intent == "compare_report_pdf":

        from report_generator import generate_comparison_pdf_report

        comparison = data.get("comparison")

        date1 = data.get("date1")

        date2 = data.get("date2")

        shed_no = data.get("shed")

        print("Comparison :", comparison)
        print("Date1 :", date1)
        print("Date2 :", date2)

        pdf_path = generate_comparison_pdf_report(
            comparison=comparison,
            date1=date1,
            date2=date2,
            shed_no=shed_no
        )

        return {

            "type": "pdf",

            "file": pdf_path

        }

    elif intent == "customer_order":

        quantity = data.get("quantity")

        return create_customer_quotation(
            chat_id=chat_id,
            customer_whatsapp=customer_whatsapp,
            quantity_eggs=quantity
        )

    elif intent == "customer_discount":

        requested_discount = data.get("discount_percentage")

        return process_customer_discount(
            chat_id=chat_id,
            requested_discount=requested_discount
        )

    elif intent == "customer_confirm":

        return process_order_confirmation(chat_id)

    elif intent == "get_financial_report":

        report_date = get_report_date(data)

        report = get_daily_financial_report_data(report_date)

        report_format = data.get("format", "message")

        if report_format == "message":

            return format_daily_financial_report(report)

        elif report_format == "pdf":

            from report_generator import generate_financial_report_pdf

            pdf_path = generate_financial_report_pdf(report)

            return {
                "type": "pdf",
                "file": pdf_path
            }



def generate_daily_pdf_report(report_date):

    production_records = get_daily_summary(report_date)

    feed_records = get_all_feeds(report_date)

    medicine_records = get_all_medicines()

    feed_totals = get_feed_totals_kg()

    medicine_totals = get_medicine_totals_kg()

    pending_reports = []

    missing_sheds = get_missing_sheds(report_date)

    for shed in missing_sheds:

        pending_reports.append({

            "shed": shed,

            "missing": ["Report Not Submitted"]

        })

    missing_fields = get_missing_fields(report_date)

    for shed, fields in missing_fields.items():

        if shed in missing_sheds:
            continue

        pending_reports.append({

            "shed": shed,

            "missing": fields

        })

    report_data = {

        "report_date": report_date,

        "production_records": production_records,

        "feed_records": feed_records,

        "medicine_records": medicine_records,

        "production_totals": {},

        "feed_totals": feed_totals,

        "medicine_totals": medicine_totals,

        "pending_reports": pending_reports,

    }

    pdf_path = generate_daily_pdf(report_data)

    return pdf_path

def create_customer_quotation(
    chat_id,
    customer_whatsapp,
    quantity_eggs
):
    if not quantity_eggs or quantity_eggs <= 0:
        return {
            "success": False,
            "message": "Please provide a valid egg quantity."
        }

    setting = get_egg_price_setting()

    if not setting:
        return {
            "success": False,
            "message": "Egg price settings are not available."
        }

    if quantity_eggs > setting.available_eggs:
        return {
            "success": False,
            "message": (
                f"Sorry, only {setting.available_eggs} eggs "
                f"are currently available."
            )
        }

    subtotal = quantity_eggs * setting.price_per_egg

    order = create_pending_order(
        chat_id=chat_id,
        customer_whatsapp=customer_whatsapp,
        quantity_eggs=quantity_eggs,
        subtotal=subtotal
    )

    if not order:
        return {
            "success": False,
            "message": "Unable to create the quotation."
        }

    trays = quantity_eggs / setting.eggs_per_tray

    message = (
        f"🥚 Egg Price Details\n\n"
        f"Quantity       : {quantity_eggs} eggs\n"
        f"Equivalent trays: {trays:.2f}\n"
        f"Price per egg  : ₹{setting.price_per_egg:.2f}\n"
        f"Price per tray : ₹{setting.price_per_tray:.2f}\n"
        f"Total amount   : ₹{subtotal:.2f}\n\n"
        f"Your quotation is pending."
    )

    return {
        "success": True,
        "message": message,
        "order_id": order.id
    }

def process_customer_discount(chat_id, requested_discount=None):

    order = get_latest_pending_order(chat_id)

    if not order:
        return {
            "success": False,
            "message": "No pending order was found."
        }

    setting = get_egg_price_setting()

    if not setting:
        return {
            "success": False,
            "message": "Egg price settings were not found."
        }

    maximum_discount = setting.discount_percentage

    if requested_discount is None:
        approved_discount = maximum_discount

    else:
        requested_discount = float(requested_discount)

        if requested_discount > maximum_discount:
            return {
                "success": False,
                "message": (
                    f"Sorry, the maximum available discount is "
                    f"{maximum_discount:.2f}%."
                ),
                "order_id": order.id
            }

        approved_discount = requested_discount

    discount_amount = (
        order.subtotal * approved_discount / 100
    )

    final_amount = (
        order.subtotal - discount_amount
    )

    updated_order = apply_discount_to_order(
        order_id=order.id,
        discount_percentage=approved_discount,
        final_amount=final_amount
    )

    discount_amount = (
        updated_order.subtotal *
        updated_order.discount_percentage / 100
    )

    return {
        "success": True,
        "message": (
            f"✅ Discount Details\n\n"
            f"Quantity        : {updated_order.quantity_eggs} eggs\n"
            f"Original amount : ₹{updated_order.subtotal:.2f}\n"
            f"Discount        : {updated_order.discount_percentage:.2f}%\n"
            f"Discount amount : ₹{discount_amount:.2f}\n"
            f"Final amount    : ₹{updated_order.final_amount:.2f}\n\n"
            f'Reply "Confirm" to place the order.'
        ),
        "order_id": updated_order.id
    }

def process_order_confirmation(chat_id):
    result = confirm_customer_order(chat_id)

    if not result["success"]:
        return result

    message = (
        f"✅ Order Confirmed\n\n"
        f"Order ID        : {result['order_id']}\n"
        f"Quantity        : {result['quantity_eggs']} eggs\n"
        f"Original amount : ₹{result['subtotal']:.2f}\n"
        f"Discount        : {result['discount_percentage']:.2f}%\n"
        f"Final amount    : ₹{result['final_amount']:.2f}\n\n"
        f"Thank you for your order."
    )

    return {
        "success": True,
        "message": message,
        "order_id": result["order_id"]
    }

def format_daily_financial_report(report_data):

    if not report_data:
        return "No financial report data found."

    if "error" in report_data:
        return report_data["error"]

    report_date = report_data["date"]

    production_rows = report_data["production_overview"]
    feed_rows = report_data["feed_consumption"]
    pnl = report_data["pnl_summary"]

    message = (
        f"📊 DAILY FARM FINANCIAL REPORT\n"
        f"📅 Date: {report_date}\n\n"
    )

    message += "1️⃣ PRODUCTION & FINANCIAL OVERVIEW\n"

    for row in production_rows:

        message += (
            f"\n🏠 Shed {row['shed_no']}\n"
            f"Birds: {row['birds']}\n"
            f"1st Collection: {row['first_collection']}\n"
            f"2nd Collection: {row['second_collection']}\n"
            f"Total Eggs: {row['total_eggs']}\n"
            f"Mortality: {row['mortality']}\n"
            f"Expected: {row['expected_percentage']:.2f}%\n"
            f"Actual: {row['actual_percentage']:.2f}%\n"
            f"Egg Price: ₹{row['egg_price']:.2f}\n"
            f"Production Value: ₹{row['production_value']:,.2f}\n"
        )

    message += "\n2️⃣ FEED CONSUMPTION\n"

    if not feed_rows:
        message += "\nNo feed consumption data found.\n"

    for row in feed_rows:

        message += (
            f"\n🏠 Shed {row['shed_no']}\n"
            f"Feed: {row['feed_name']}\n"
            f"Feed Consumed: {row['feed_consumed_mt']:.3f} MT\n"
            f"Feed/Bird: {row['feed_per_bird_g']:.2f} g/day\n"
            f"Feed Cost/Ton: ₹{row['feed_cost_per_ton']:,.2f}\n"
            f"Total Feed Cost: ₹{row['total_feed_cost']:,.2f}\n"
        )

    profit_or_loss = pnl["net_profit_or_loss"]

    result_label = (
        "Net Profit"
        if profit_or_loss >= 0
        else "Net Loss"
    )

    message += (
        "\n3️⃣ DAILY P&L SUMMARY\n\n"
        f"Total Production Value: "
        f"₹{pnl['total_production_value']:,.2f}\n"
        f"Total Feed Cost: "
        f"₹{pnl['total_feed_cost']:,.2f}\n"
        f"Total Expenses: "
        f"₹{pnl['total_expenses']:,.2f}\n"
        f"{result_label}: "
        f"₹{abs(profit_or_loss):,.2f}"
    )

    return message