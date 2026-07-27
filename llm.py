import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from the .env file")


client = genai.Client(api_key=api_key)


FRIEND_PROMPT = """
You are chatting with friends in a casual WhatsApp group.

Reply like a normal friend, not like a professional assistant.

Important language rule:
- Detect the language and writing style of the latest message.
- Reply in the same language and the same writing style.
- If the message is in English, reply in English.
- If the message is in Telugu script, reply in Telugu script.
- If the message is Telugu written using English letters, reply in Telugu using English letters.
- If the message mixes English and Telugu words, reply using a similar mix.
- Do not translate the message into another language.
- Match the user's casual tone naturally.

Examples:

Friend: Hi bro, how are you?
Reply: I'm good bro 😄 How are you?

Friend: ela unnav bro?
Reply: bagunna bro 😄 nuvvu ela unnav?

Friend: em chestunnav?
Reply: em ledhu bro, chill avthunna 😄 nuvvu em chestunnav?

Friend: తిన్నావా?
Reply: ఇంకా లేదు 😄 నువ్వు తిన్నావా?

Friend: ekkada unnav?
Reply: ikkade unna bro 😄 nuvvu ekkada unnav?

Friend: office ki vachava bro?
Reply: inka ledhu bro, vastunna 😄

Rules:
- Keep replies short and natural.
- Usually reply in one or two sentences.
- Do not sound formal or professional.
- Do not say "How may I assist you?"
- Do not mention that you are an AI.
- Use simple conversational language.
- Use emojis naturally, but not too many.
- Be friendly and respectful.
- Reply only to the latest message.
"""


def generate_friend_reply(message: str) -> str:

    if not message or not message.strip():
        return "Em message pettaledhu bro 😄"

    try:
        full_prompt = f"""
                {FRIEND_PROMPT}

                Friend's latest message:
                {message}

                Reply:
            """

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=full_prompt
        )

        reply = response.text

        if not reply:
            return "Em cheppalo ardham kavatledhu bro 😄"

        return reply.strip()

    except Exception as error:
        print("LLM error:", error)
        return "Edho problem vachindhi bro 😅"


def understand_message(message: str) -> dict:

    prompt = f"""
        You are an egg farm management assistant.

        If the user wants to add production, broken, or sold eggs but does not specify a shed number, return:

        If the user asks "today report" or "today summary", return get_daily_summary.

        If the user asks for a report "in PDF", "as PDF", "pdf report", or "generate pdf", return generate_pdf.

        {{
            "intent":"add_production",
            "shed":null,
            "quantity":10,
            "date":"today", 
            "language":"en", 
            "unit":"egg"
        }}

        Do not guess the shed number.

        Convert the user message into JSON.

        User:
        11-07-2026 summary

        JSON:
        {{
            "intent":"get_daily_summary",
            "shed":null,
            "quantity":null,
            "date":"2026-07-11", 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        11 July 2026 summary

        JSON:
        {{
        "intent":"get_daily_summary",
        "shed":null,
        "quantity":null,
        "date":"2026-07-11", 
        "language":"en" ,
        "unit":"egg"
        }}

        Possible intents:

        - add_production
        - add_broken
        - add_sold
        - get_summary
        - get_production
        - get_broken
        - get_sold
        - get_daily_summary
        - get_remaining
        - get_shed_count
        - get_farm_stock
        - get_total_broken
        - get_total_production
        - get_total_sold
        - get_total_remaining 
        - get_highest_production
        - get_highest_broken
        - get_highest_stock
        - get_highest_sold
        - get_lowest_production
        - get_lowest_broken
        - get_lowest_sold
        - get_lowest_stock
        - get_weekly_summary
        - get_monthly_summary
        - move_record
        - update_record
        - remove_record
        - delete_field
        - delete_record
        - add_birds
        - get_birds
        - get_total_birds
        - add_mortality
        - get_mortality
        - get_total_mortality
        - get_total_live_birds
        - get_missing_sheds
        - get_missing_fields
        - add_feed
        - use_feed
        - get_feed
        - get_feed_remaining
        - get_feed_used
        - get_medicine_summary
        - generate_pdf
        - generate_weekly_pdf

        Return ONLY JSON.

        Required fields:

        intent
        shed
        from_shed
        to_shed
        field
        quantity
        date
        unit
        language

        Output unit:

        - If the user asks in eggs, return:
        "unit":"egg"

        - If the user asks in trays or tray, return:
        "unit":"tray"

        - If the user is adding production, broken or sold,
        always return:
        "unit":"egg"

        Important Rules:

        1. If the user mentions a shed number (e.g., Shed 1, Shed 2, first shed), use the shed-specific intents:
        - get_summary
        - get_production
        - get_broken
        - get_sold

        2. If the user does NOT mention any shed number and asks for today's summary, yesterday's summary, or a daily report, use:
        - get_daily_summary

        - When feed is added to stock, use intent "add_feed".
        - When feed is removed from stock, use intent "remove_feed".
        - Do not use "remove_record" for removing feed stock.
        - Store the feed name in the "feed" field.

        - When medicine is added to stock, use intent "add_medicine".
        - When medicine is removed from stock, use intent "remove_medicine".
        - Do not use "remove_record" for removing medicine stock.
        - Store the medicine name in the "medicine" field.

        - For feed-related messages, unit can be kg or bag.
        - For medicine-related messages, unit can be bottle, packet, tablet, ml, or null.
        - Never set unit to "egg" for medicine or feed queries.

        Examples:

        User:
        "Shed 1 produced 100 eggs"

        Note : 1 tray contains 30 eggs , when the user enters in trays , you need to convert those into eggs . For example , 10 trays = 10 * 30 = 300 days 
        
        
        JSON:
        {{
        "intent":"add_production",
        "shed":1,
        "quantity":100, 
        "language":"en" ,
        "unit":"egg"
        }}

        User:
        "100 eggs are added to first shed"

        JSON:
        {{
        "intent":"add_production",
        "shed":1,
        "quantity":100, 
        "language":"en" ,
        "unit":"egg"
        }}

        User:
        "How many broken eggs in shed 1?"
        JSON:
        {{
            "intent":"get_broken",
            "shed":1,
            "quantity":null,
            "date":null, 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        "How many sold eggs in shed 2?"

        JSON:
        {{
            "intent":"get_sold",
            "shed":2,
            "quantity":null,
            "date":null, 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        "How many eggs were produced in shed 3?"

        JSON:
        {{
            "intent":"get_production",
            "shed":3,
            "quantity":null,
            "date":null, 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        Today's summary

        JSON:
        {{
            "intent":"get_daily_summary",
            "shed":null,
            "quantity":null,
            "date":"today", 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        Yesterday's summary

        JSON:
        {{
            "intent":"get_daily_summary",
            "shed":null,
            "quantity":null,
            "date":"yesterday", 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        Yesterday shed 1 summary

        JSON:
        {{
            "intent":"get_summary",
            "shed":1,
            "quantity":null,
            "date":"yesterday", 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        Today shed 2 summary

        JSON:
        {{
            "intent":"get_summary",
            "shed":2,
            "quantity":null,
            "date":"today", 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        Remaining eggs in shed 1

        JSON:
        {{
            "intent":"get_remaining",
            "shed":1,
            "quantity":null,
            "date":"today", 
            "language":"en", 
            "unit":"egg"
        }}

        User:
        Remaining eggs in shed 1 yesterday

        JSON:
        {{
            "intent":"get_remaining",
            "shed":1,
            "quantity":null,
            "date":"yesterday" ,
            "language":"en", 
            "unit":"egg"
        }}

        User:
        How many trays were produced in shed 2?

        JSON:
        {{
            "intent":"get_production",
            "shed":2,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"tray"
        }}

        User:
        How many eggs were produced in shed 2?

        JSON:
        {{
            "intent":"get_production",
            "shed":2,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Shed 2 produced 289.20 trays

        JSON:
        {{
            "intent":"add_production",
            "shed":2,
            "quantity":8690,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        How many sheds today?

        JSON:
        {{
            "intent":"get_shed_count",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        How many sheds yesterday?

        JSON:
        {{
            "intent":"get_shed_count",
            "shed":null,
            "quantity":null,
            "date":"yesterday",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Farm stock

        JSON:
        {{
            "intent":"get_farm_stock",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        How many eggs are there today?

        JSON:
        {{
            "intent":"get_farm_stock",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Yesterday farm stock

        JSON:
        {{
            "intent":"get_farm_stock",
            "shed":null,
            "quantity":null,
            "date":"yesterday",
            "language":"en",
            "unit":"egg"
        }}

        User:
        How many broken eggs are there today?

        JSON:
        {{
            "intent":"get_total_broken",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Total broken eggs

        JSON:
        {{
            "intent":"get_total_broken",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Yesterday broken eggs

        JSON:
        {{
            "intent":"get_total_broken",
            "shed":null,
            "quantity":null,
            "date":"yesterday",
            "language":"en",
            "unit":"egg"
        }}

        User:
        How many eggs were produced today?

        {{
            "intent":"get_total_production",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        11 July production

        JSON:
        {{
            "intent":"get_total_production",
            "shed":null,
            "quantity":null,
            "date":"2026-07-11",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Production on 11-07-2026

        JSON:
        {{
            "intent":"get_total_production",
            "shed":null,
            "quantity":null,
            "date":"2026-07-11",
            "language":"en",
            "unit":"egg"
        }}

        User:
        How many sold eggs are there today?

        {{
            "intent":"get_total_sold",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        How many remaining eggs are there?

        {{
            "intent":"get_total_remaining",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Which shed produced the most eggs today?

        JSON:
        {{
            "intent":"get_highest_production",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Highest production today

        JSON:
        {{
            "intent":"get_highest_production",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Which shed highest broken eggs today?
        {{
            "intent":"get_highest_broken",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Which shed has highest sold eggs ?
        {{
            "intent":"get_highest_sold",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User: 
        Which shed has highest stock today?
        {{
            "intent":"get_highest_stock",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        which shed has lowest production ?
        {{
            "intent":"get_lowest_production",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        which shed has lowest broken eggs ?
        {{
            "intent":"get_lowest_broken",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        which shed has lowest sold eggs ?

        {{
            "intent":"get_lowest_sold",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        which shed has lowest stock ?

        {{
            "intent":"get_lowest_stock",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Weekly summary / This week report . 

        {{
            "intent":"get_weekly_summary",
            "shed":null,
            "quantity":null,
            "date":"this_week",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Last week report

        JSON:
        {{
            "intent":"get_weekly_summary",
            "shed":null,
            "quantity":null,
            "date":"last_week",
            "language":"en",
            "unit":"egg"
        }}

        User: this week shed 1 data
        Output:
        {{
        "intent":"get_weekly_summary",
        "shed":1,
        "date":"this_week"
        }}

        User: last week shed 2 summary
        Output:
        {{
        "intent":"get_weekly_summary",
        "shed":2,
        "date":"last_week"
        }}

        User:
        Monthly summary / This month report / Last month Summary report . 

        {{
            "intent":"get_monthly_summary",
            "shed":null,
            "quantity":null,
            "date":"this_month",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Move 100 produced eggs from shed 1 to shed 2

        JSON:
        {{
            "intent":"move_record",
            "from_shed":1,
            "to_shed":2,
            "field":"produced",
            "quantity":100,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Move 5 broken eggs from shed 1 to shed 2

        JSON:
        {{
            "intent":"move_record",
            "from_shed":1,
            "to_shed":2,
            "field":"broken",
            "quantity":5,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Move 20 sold eggs from shed 3 to shed 1

        JSON:
        {{
            "intent":"move_record",
            "from_shed":3,
            "to_shed":1,
            "field":"sold",
            "quantity":20,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Change today's production of shed 1 to 500 eggs

        JSON:
        {{
            "intent":"update_record",
            "shed":1,
            "field":"produced",
            "quantity":500,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Update yesterday's broken eggs in shed 2 to 15

        JSON:
        {{
            "intent":"update_record",
            "shed":2,
            "field":"broken",
            "quantity":15,
            "date":"yesterday",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Set sold eggs in shed 3 to 40

        JSON:
        {{
            "intent":"update_record",
            "shed":3,
            "field":"sold",
            "quantity":40,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Remove 20 eggs from today's production of shed 1

        JSON:
        {{
            "intent":"remove_record",
            "shed":1,
            "field":"produced",
            "quantity":20,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Remove 5 broken eggs from shed 2

        JSON:
        {{
            "intent":"remove_record",
            "shed":2,
            "field":"broken",
            "quantity":5,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Remove 10 sold eggs from shed 3 yesterday

        JSON:
        {{
            "intent":"remove_record",
            "shed":3,
            "field":"sold",
            "quantity":10,
            "date":"yesterday",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Delete today's production of shed 1

        JSON:
        {{
            "intent":"delete_field",
            "shed":1,
            "field":"produced",
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Delete broken eggs in shed 2

        JSON:
        {{
            "intent":"delete_field",
            "shed":2,
            "field":"broken",
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Delete sold eggs in shed 3 yesterday

        JSON:
        {{
            "intent":"delete_field",
            "shed":3,
            "field":"sold",
            "quantity":null,
            "date":"yesterday",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Delete today's shed 1 record

        JSON:
        {{
            "intent":"delete_record",
            "shed":1,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"egg"
        }}

        User:
        Shed 1 has 5000 birds

        JSON:
        {{
            "intent":"add_birds",
            "shed":1,
            "quantity":5000,
            "date":"today",
            "language":"en"
        }}
        User:
        Update shed 2 bird count to 4800

        JSON:
        {{
            "intent":"add_birds",
            "shed":2,
            "quantity":4800,
            "date":"today",
            "language":"en"
        }}
        User:
        Bird count in shed 1

        JSON:
        {{
            "intent":"get_birds",
            "shed":1,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}
        User:
        Total birds today

        JSON:
        {{
            "intent":"get_total_birds",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}

        User:
        5 birds died in shed 1

        JSON:
        {{
            "intent":"add_mortality",
            "shed":1,
            "quantity":5,
            "date":"today",
            "language":"en"
        }}

        User:
        Record 3 dead birds in shed 2

        JSON:
        {{
            "intent":"add_mortality",
            "shed":2,
            "quantity":3,
            "date":"today",
            "language":"en"
        }}

        User:
        Mortality in shed 1

        JSON:
        {{
            "intent":"get_mortality",
            "shed":1,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}

        User:
        Today's mortality

        JSON:
        {{
            "intent":"get_total_mortality",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}


        User:
        Today's live birds

        JSON:
        {{
            "intent":"get_total_live_birds",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}

        User:
        Total live birds

        JSON:
        {{
            "intent":"get_total_live_birds",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}

        User:
        How many live birds are there?

        JSON:
        {{
            "intent":"get_total_live_birds",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}

        User:
        Today's missing sheds

        JSON:
        {{
            "intent":"get_missing_sheds",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}
        User:
        Missing sheds

        JSON:
        {{
            "intent":"get_missing_sheds",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}
        User:
        Which sheds have not reported today?

        JSON:
        {{
            "intent":"get_missing_sheds",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}
        User:
        Pending sheds

        JSON:
        {{
            "intent":"get_missing_sheds",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}

        User:
        Today's pending fields

        JSON:
        {{
            "intent":"get_missing_fields",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}
        User:
        Incomplete shed reports

        JSON:
        {{
            "intent":"get_missing_fields",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}
        User:
        Which sheds have incomplete data?

        JSON:
        {{
            "intent":"get_missing_fields",
            "shed":null,
            "quantity":null,
            "date":"today",
            "language":"en"
        }}

        Intent: compare_dates

        Examples:

        User: Compare today and yesterday

        Output:
        {{
            "intent": "compare_dates",
            "date1": "today",
            "date2": "yesterday"
        }}

        User: Compare today and 14th July

        Output:
        {{
            "intent": "compare_dates",
            "date1": "today",
            "date2": "2026-07-14"
        }}

        User: Compare 14-07-2026 and 15-07-2026

        Output:
        {{
            "intent": "compare_dates",
            "date1": "2026-07-14",
            "date2": "2026-07-15"
        }}

        Compare production today and yesterday

        output:
        {{
            "intent":"compare_dates",
            "date1":"today",
            "date2":"yesterday",
            "field":"produced"
        }}

        User:
        Compare this week and last week

        Output:
        {{
            "intent":"compare_weeks",
            "week1":"this_week",
            "week2":"last_week"
        }}

        User:
        Compare last week and this week

        Output:
        {{
            "intent":"compare_weeks",
            "week1":"last_week",
            "week2":"this_week"
        }}

        User:
        Compare this week's production with last week

        Output:
        {{
            "intent":"compare_weeks",
            "week1":"this_week",
            "week2":"last_week",
            "field":"produced"
        }}

        User:
        Compare this month and last month

        Output:
        {{
            "intent":"compare_months",
            "month1":"this_month",
            "month2":"last_month"
        }}

        User : 
        Compare this month's production and last month

        Ouptut:
        {{
            "intent":"compare_months",
            "month1":"this_month",
            "month2":"last_month",
            "field":"produced"
        }}

        User:
        Add 20 bottles Vitamin A in shed 1

        Output:


        {{
            "intent":"add_medicine",
            "shed":1,
            "medicine":"Vitamin A",
            "quantity":20,
            "unit":"bottle"
        }}

        User:
        Add 5 kg Calcium Powder in shed 3

        Output:

        {{
            "intent":"add_medicine",
            "shed":3,
            "medicine":"Calcium Powder",
            "quantity":5,
            "unit":"kg"
        }}


        User:
        Use 5 bottles Vitamin A in shed 1

        Output:

        {{
            "intent":"use_medicine",
            "shed":1,
            "medicine":"Vitamin A",
            "quantity":5
        }}


        User:
        Used 10 ml Antibiotic in shed 4

        Output:

        {{
            "intent":"use_medicine",
            "shed":4,
            "medicine":"Antibiotic",
            "quantity":10
        }}


        User:
        Vitamin A in shed 1

        Output:

        {{
            "intent":"get_medicine",
            "shed":1,
            "medicine":"Vitamin A"
        }}

        User:
        Show Vitamin A in shed 3

        Output:

        {{
            "intent":"get_medicine",
            "shed":3,
            "medicine":"Vitamin A"
        }}

        User:
        How much Vitamin A is remaining in shed 2?

        Output:

        {{
            "intent":"get_medicine_remaining",
            "shed":2,
            "medicine":"Vitamin A"
        }}

        User:
        How much Vitamin A has been used in shed 5?

        Output:

        {{
            "intent":"get_medicine_used",
            "shed":5,
            "medicine":"Vitamin A"
        }}

        User:
        Show medicines in shed 1

        Output:

        {{
            "intent":"get_all_medicines",
            "shed":1
        }}

        User:
        Medicine report for shed 2

        Output:

        {{
            "intent":"get_all_medicines",
            "shed":2
        }}

        User:
        List medicines in shed 4

        Output:


        {{
            "intent":"get_all_medicines",
            "shed":4
        }}

        User:
        5 bottels vitamine A is used in shed 1

        Output:
        {{
            "intent":"use_medicine",
            "shed":1,
            "medicine":"Vitamin A",
            "quantity":5,
            "unit":"bottle"
        }}

        User:
        vitamin a in shed 1

        Output:
        {{
            "intent":"get_medicine",
            "shed":1,
            "medicine":"Vitamin A"
        }}

        User:
        vitamine A stock

        Output:
        {{
            "intent":"get_medicine",
            "shed":1,
            "medicine":"Vitamin A"
        }}


        User:
        Add 1000 kg Layer Feed to shed 1

        JSON:
        {{
            "intent":"add_feed",
            "shed":1,
            "feed":"Layer Feed",
            "quantity":1000,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Add 500 kg Starter Feed to shed 2

        JSON:
        {{
            "intent":"add_feed",
            "shed":2,
            "feed":"Starter Feed",
            "quantity":500,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Use 200 kg Layer Feed in shed 1

        JSON:
        {{
            "intent":"use_feed",
            "shed":1,
            "feed":"Layer Feed",
            "quantity":200,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Use 50 kg Starter Feed in shed 2

        JSON:
        {{
            "intent":"use_feed",
            "shed":2,
            "feed":"Starter Feed",
            "quantity":50,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Layer Feed in shed 1

        JSON:
        {{
            "intent":"get_feed",
            "shed":1,
            "feed":"Layer Feed",
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Starter Feed in shed 2

        JSON:
        {{
            "intent":"get_feed",
            "shed":2,
            "feed":"Starter Feed",
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Remaining feed in shed 1

        JSON:
        {{
            "intent":"get_feed_remaining",
            "shed":1,
            "feed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Remaining Layer Feed in shed 1

        JSON:
        {{
            "intent":"get_feed_remaining",
            "shed":1,
            "feed":"Layer Feed",
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Remaining feed

        JSON:
        {{
            "intent":"get_feed_remaining",
            "shed":null,
            "feed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Used feed in shed 1

        JSON:
        {{
            "intent":"get_feed_used",
            "shed":1,
            "feed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        How much Layer Feed is used in shed 1

        JSON:
        {{
            "intent":"get_feed_used",
            "shed":1,
            "feed":"Layer Feed",
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}

        User:
        Used feed

        JSON:
        {{
            "intent":"get_feed_used",
            "shed":null,
            "feed":null,
            "quantity":null,
            "date":"today",
            "language":"en",
            "unit":"kg"
        }}


        The farm has only 9 sheds numbered 1 to 9.

        If the user mentions any shed outside this range, do NOT generate a normal intent.

        Instead return:

        {{
            "intent":"invalid_shed",
            "shed":10,
            "message":"Invalid shed number"
        }}

        User: today report in pdf

        Output:
        {{
            "intent":"generate_pdf",
            "shed":null,
            "quantity":null,
            "date":"today",
            "feed_name":null,
            "medicine_name":null,
            "language":"en"
        }}

        User: yesterday report pdf

        Output:
        {{
            "intent":"generate_pdf",
            "shed":null,
            "quantity":null,
            "date":"yesterday",
            "feed_name":null,
            "medicine_name":null,
            "language":"en"
        }}

        User: generate today's report as pdf

        Output:
        {{
            "intent":"generate_pdf",
            "shed":null,
            "quantity":null,
            "date":"today",
            "feed_name":null,
            "medicine_name":null,
            "language":"en"
        }}

        User: this week report in pdf

        Output:
        {{
            "intent":"generate_weekly_pdf",
            "shed":null,
            "quantity":null,
            "date":"this_week",
            "feed_name":null,
            "medicine_name":null,
            "language":"en"
        }}

        User: weekly report pdf

        Output:
        {{
            "intent":"generate_weekly_pdf",
            "shed":null,
            "quantity":null,
            "date":"this_week",
            "feed_name":null,
            "medicine_name":null,
            "language":"en"
        }}

        User:
        this month report in pdf

        Output:
        {{
            "intent": "generate_monthly_pdf",
            "date": "this_month"
        }}

        User:
        last month report in pdf

        Output:
        {{
            "intent": "generate_monthly_pdf",
            "date": "last_month"
        }}

        ==========================
        PDF REPORT INTENTS
        ==========================

        1. Farm Daily PDF

        Examples:
        - today's report in pdf
        - yesterday report in pdf
        - 20 july report in pdf

        Output:

        User: today's report in pdf

        {{
            "intent": "generate_pdf",
            "shed": null,
            "quantity": null,
            "date": "today",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: yesterday report in pdf

        {{
            "intent": "generate_pdf",
            "shed": null,
            "quantity": null,
            "date": "yesterday",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        --------------------------------------------------

        2. Farm Weekly PDF

        Examples:
        - this week report in pdf
        - last week report in pdf

        Output:

        User: this week report in pdf

        {{
            "intent": "generate_weekly_pdf",
            "shed": null,
            "quantity": null,
            "date": "this_week",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: last week report in pdf

        {{
            "intent": "generate_weekly_pdf",
            "shed": null,
            "quantity": null,
            "date": "last_week",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        --------------------------------------------------

        3. Farm Monthly PDF

        Examples:
        - this month report in pdf
        - last month report in pdf

        Output:

        User: this month report in pdf

        {{
            "intent": "generate_monthly_pdf",
            "shed": null,
            "quantity": null,
            "date": "this_month",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: last month report in pdf

        {{
            "intent": "generate_monthly_pdf",
            "shed": null,
            "quantity": null,
            "date": "last_month",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}
        --------------------------------------------------

        4. Shed PDF Reports

        Use this intent whenever the user asks for a PDF report of a specific shed.

        Examples:

        - today's shed 1 report in pdf
        - yesterday shed 3 report in pdf
        - shed 2 report in pdf
        - this week shed 4 report in pdf
        - last week shed 6 report in pdf
        - this month shed 5 report in pdf
        - last month shed 7 report in pdf

        Output:

        User: today's shed 1 report in pdf

        {{
            "intent": "generate_shed_pdf",
            "shed": 1,
            "quantity": null,
            "date": "today",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: yesterday shed 3 report in pdf

        {{
            "intent": "generate_shed_pdf",
            "shed": 3,
            "quantity": null,
            "date": "yesterday",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: shed 2 report in pdf

        {{
            "intent": "generate_shed_pdf",
            "shed": 2,
            "quantity": null,
            "date": "today",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: this week shed 4 report in pdf

        {{
            "intent": "generate_shed_pdf",
            "shed": 4,
            "quantity": null,
            "date": "this_week",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: last week shed 6 report in pdf

        {{
            "intent": "generate_shed_pdf",
            "shed": 6,
            "quantity": null,
            "date": "last_week",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: this month shed 5 report in pdf

        {{
            "intent": "generate_shed_pdf",
            "shed": 5,
            "quantity": null,
            "date": "this_month",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}

        User: last month shed 7 report in pdf

        {{
            "intent": "generate_shed_pdf",
            "shed": 7,
            "quantity": null,
            "date": "last_month",
            "feed_name": null,
            "medicine_name": null,
            "language": "en"
        }}
        
        User:
        Compare today and yesterday in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"day",
        "shed":null,
        "quantity":null,
        "date":null,
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        Compare this week and last week in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"week",
        "shed":null,
        "quantity":null,
        "date":null,
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        Compare this month and last month in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"month",
        "shed":null,
        "quantity":null,
        "date":null,
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        Compare Shed 1 today and yesterday in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"day",
        "shed":1,
        "quantity":null,
        "date":null,
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        Compare Shed 1 this week and last week in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"week",
        "shed":1,
        "quantity":null,
        "date":null,
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        Compare Shed 1 this month and last month in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"month",
        "shed":1,
        "quantity":null,
        "date":null,
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        Compare today and 15th July in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"custom_day",
        "shed":null,
        "quantity":null,
        "date1":"today",
        "date2":"2026-07-15",
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        Compare 10th July and 15th July in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"custom_day",
        "shed":null,
        "quantity":null,
        "date1":"2026-07-10",
        "date2":"2026-07-15",
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        Compare Shed 1 today and 15th July in PDF
        Output:
        {{
        "intent":"compare_report_pdf",
        "comparison":"custom_day",
        "shed":1,
        "quantity":null,
        "date1":"today",
        "date2":"2026-07-15",
        "feed_name":null,
        "medicine_name":null,
        "language":"en"
        }}

        User:
        I need 500 eggs

        Output:
        {{
            "intent":"customer_order",
            "quantity":500,
            "language":"en"
        }}

        User:
        I want 1200 eggs

        Output:
        {{
            "intent":"customer_order",
            "quantity":1200,
            "language":"en"
        }}

        User:
        Can I get discount?

        Output:
        {{
            "intent":"customer_discount",
            "discount_percentage": null,
            "language":"en"
        }}


        User:
        Give me 10 percent discount, then I will buy.

        Output:
        {{
            "intent": "customer_discount",
            "discount_percentage": 10,
            "language": "en"
        }}

        User:
        Can you give me 7% discount?

        Output:
        {{
            "intent": "customer_discount",
            "discount_percentage": 7,
            "language": "en"
        }}

        User:
        Confirm

        Output:
        {{
            "intent":"customer_confirm",
            "language":"en"
        }}

        User:
        Cancel order

        Output:
        {{
            "intent":"customer_cancel",
            "language":"en"
        }}

        user : Give 10 percent discount, then I will buy
        output : 
        {{
            "intent" : ""
        }}



        Now convert this:

        {message}
        """


    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        result = response.text

        if not result:
            return {
                "intent": "unknown",
                "shed": None,
                "quantity": None
            }

        result = result.strip()
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

        return json.loads(result)

    except json.JSONDecodeError as error:
        print("Invalid JSON from Gemini:", error)
        print("Gemini response:", result)

        return {
            "intent": "unknown",
            "shed": None,
            "quantity": None
        }

    except Exception as error:
        print("Egg LLM error:", error)

        return {
            "intent": "unknown",
            "shed": None,
            "quantity": None
        }

# import os
# import json
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()

# genai.configure(
#     api_key=os.getenv("GEMINI_API_KEY")
# )

# model = genai.GenerativeModel(
#     "gemini-3.1-flash-lite"
# )

def translate_response(message, language):

    if language == "en":
        return message

    prompt = f"""
    Translate the following message into the language code '{language}'.

    Rules:
    - Keep all numbers exactly the same.
    - Preserve emojis.
    - Translate words like "Shed", "Produced", "Broken", "Sold", "Stock".
    - Do not change the shed number.
    - Return only the translated text.

    Message:
    {message}
    """

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    # response = model.generate_content(prompt)

    return response.text.strip()

# def understand_message(message):

#     prompt = f"""
#         You are an egg farm management assistant.

#         If the user wants to add production, broken, or sold eggs but does not specify a shed number, return:

#         If the user asks "today report" or "today summary", return get_daily_summary.

#         If the user asks for a report "in PDF", "as PDF", "pdf report", or "generate pdf", return generate_pdf.

#         {{
#             "intent":"add_production",
#             "shed":null,
#             "quantity":10,
#             "date":"today", 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         Do not guess the shed number.

#         Convert the user message into JSON.

#         User:
#         11-07-2026 summary

#         JSON:
#         {{
#             "intent":"get_daily_summary",
#             "shed":null,
#             "quantity":null,
#             "date":"2026-07-11", 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         11 July 2026 summary

#         JSON:
#         {{
#         "intent":"get_daily_summary",
#         "shed":null,
#         "quantity":null,
#         "date":"2026-07-11", 
#         "language":"en" ,
#         "unit":"egg"
#         }}

#         Possible intents:

#         - add_production
#         - add_broken
#         - add_sold
#         - get_summary
#         - get_production
#         - get_broken
#         - get_sold
#         - get_daily_summary
#         - get_remaining
#         - get_shed_count
#         - get_farm_stock
#         - get_total_broken
#         - get_total_production
#         - get_total_sold
#         - get_total_remaining 
#         - get_highest_production
#         - get_highest_broken
#         - get_highest_stock
#         - get_highest_sold
#         - get_lowest_production
#         - get_lowest_broken
#         - get_lowest_sold
#         - get_lowest_stock
#         - get_weekly_summary
#         - get_monthly_summary
#         - move_record
#         - update_record
#         - remove_record
#         - delete_field
#         - delete_record
#         - add_birds
#         - get_birds
#         - get_total_birds
#         - add_mortality
#         - get_mortality
#         - get_total_mortality
#         - get_total_live_birds
#         - get_missing_sheds
#         - get_missing_fields
#         - add_feed
#         - use_feed
#         - get_feed
#         - get_feed_remaining
#         - get_feed_used
#         - get_medicine_summary
#         - generate_pdf
#         - generate_weekly_pdf

#         Return ONLY JSON.

#         Required fields:

#         intent
#         shed
#         from_shed
#         to_shed
#         field
#         quantity
#         date
#         unit
#         language

#         Output unit:

#         - If the user asks in eggs, return:
#         "unit":"egg"

#         - If the user asks in trays or tray, return:
#         "unit":"tray"

#         - If the user is adding production, broken or sold,
#         always return:
#         "unit":"egg"

#         Important Rules:

#         1. If the user mentions a shed number (e.g., Shed 1, Shed 2, first shed), use the shed-specific intents:
#         - get_summary
#         - get_production
#         - get_broken
#         - get_sold

#         2. If the user does NOT mention any shed number and asks for today's summary, yesterday's summary, or a daily report, use:
#         - get_daily_summary

#         Examples:

#         User:
#         "Shed 1 produced 100 eggs"

#         Note : 1 tray contains 30 eggs , when the user enters in trays , you need to convert those into eggs . For example , 10 trays = 10 * 30 = 300 days 
        
        
#         JSON:
#         {{
#         "intent":"add_production",
#         "shed":1,
#         "quantity":100, 
#         "language":"en" ,
#         "unit":"egg"
#         }}

#         User:
#         "100 eggs are added to first shed"

#         JSON:
#         {{
#         "intent":"add_production",
#         "shed":1,
#         "quantity":100, 
#         "language":"en" ,
#         "unit":"egg"
#         }}

#         User:
#         "How many broken eggs in shed 1?"
#         JSON:
#         {{
#             "intent":"get_broken",
#             "shed":1,
#             "quantity":null,
#             "date":null, 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         "How many sold eggs in shed 2?"

#         JSON:
#         {{
#             "intent":"get_sold",
#             "shed":2,
#             "quantity":null,
#             "date":null, 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         "How many eggs were produced in shed 3?"

#         JSON:
#         {{
#             "intent":"get_production",
#             "shed":3,
#             "quantity":null,
#             "date":null, 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         Today's summary

#         JSON:
#         {{
#             "intent":"get_daily_summary",
#             "shed":null,
#             "quantity":null,
#             "date":"today", 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         Yesterday's summary

#         JSON:
#         {{
#             "intent":"get_daily_summary",
#             "shed":null,
#             "quantity":null,
#             "date":"yesterday", 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         Yesterday shed 1 summary

#         JSON:
#         {{
#             "intent":"get_summary",
#             "shed":1,
#             "quantity":null,
#             "date":"yesterday", 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         Today shed 2 summary

#         JSON:
#         {{
#             "intent":"get_summary",
#             "shed":2,
#             "quantity":null,
#             "date":"today", 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         Remaining eggs in shed 1

#         JSON:
#         {{
#             "intent":"get_remaining",
#             "shed":1,
#             "quantity":null,
#             "date":"today", 
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         Remaining eggs in shed 1 yesterday

#         JSON:
#         {{
#             "intent":"get_remaining",
#             "shed":1,
#             "quantity":null,
#             "date":"yesterday" ,
#             "language":"en", 
#             "unit":"egg"
#         }}

#         User:
#         How many trays were produced in shed 2?

#         JSON:
#         {{
#             "intent":"get_production",
#             "shed":2,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"tray"
#         }}

#         User:
#         How many eggs were produced in shed 2?

#         JSON:
#         {{
#             "intent":"get_production",
#             "shed":2,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Shed 2 produced 289.20 trays

#         JSON:
#         {{
#             "intent":"add_production",
#             "shed":2,
#             "quantity":8690,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         How many sheds today?

#         JSON:
#         {{
#             "intent":"get_shed_count",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         How many sheds yesterday?

#         JSON:
#         {{
#             "intent":"get_shed_count",
#             "shed":null,
#             "quantity":null,
#             "date":"yesterday",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Farm stock

#         JSON:
#         {{
#             "intent":"get_farm_stock",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         How many eggs are there today?

#         JSON:
#         {{
#             "intent":"get_farm_stock",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Yesterday farm stock

#         JSON:
#         {{
#             "intent":"get_farm_stock",
#             "shed":null,
#             "quantity":null,
#             "date":"yesterday",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         How many broken eggs are there today?

#         JSON:
#         {{
#             "intent":"get_total_broken",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Total broken eggs

#         JSON:
#         {{
#             "intent":"get_total_broken",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Yesterday broken eggs

#         JSON:
#         {{
#             "intent":"get_total_broken",
#             "shed":null,
#             "quantity":null,
#             "date":"yesterday",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         How many eggs were produced today?

#         {{
#             "intent":"get_total_production",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         11 July production

#         JSON:
#         {{
#             "intent":"get_total_production",
#             "shed":null,
#             "quantity":null,
#             "date":"2026-07-11",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Production on 11-07-2026

#         JSON:
#         {{
#             "intent":"get_total_production",
#             "shed":null,
#             "quantity":null,
#             "date":"2026-07-11",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         How many sold eggs are there today?

#         {{
#             "intent":"get_total_sold",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         How many remaining eggs are there?

#         {{
#             "intent":"get_total_remaining",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Which shed produced the most eggs today?

#         JSON:
#         {{
#             "intent":"get_highest_production",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Highest production today

#         JSON:
#         {{
#             "intent":"get_highest_production",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Which shed highest broken eggs today?
#         {{
#             "intent":"get_highest_broken",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Which shed has highest sold eggs ?
#         {{
#             "intent":"get_highest_sold",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User: 
#         Which shed has highest stock today?
#         {{
#             "intent":"get_highest_stock",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         which shed has lowest production ?
#         {{
#             "intent":"get_lowest_production",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         which shed has lowest broken eggs ?
#         {{
#             "intent":"get_lowest_broken",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         which shed has lowest sold eggs ?

#         {{
#             "intent":"get_lowest_sold",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         which shed has lowest stock ?

#         {{
#             "intent":"get_lowest_stock",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Weekly summary / This week report . 

#         {{
#             "intent":"get_weekly_summary",
#             "shed":null,
#             "quantity":null,
#             "date":"this_week",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Last week report

#         JSON:
#         {{
#             "intent":"get_weekly_summary",
#             "shed":null,
#             "quantity":null,
#             "date":"last_week",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User: this week shed 1 data
#         Output:
#         {{
#         "intent":"get_weekly_summary",
#         "shed":1,
#         "date":"this_week"
#         }}

#         User: last week shed 2 summary
#         Output:
#         {{
#         "intent":"get_weekly_summary",
#         "shed":2,
#         "date":"last_week"
#         }}

#         User:
#         Monthly summary / This month report / Last month Summary report . 

#         {{
#             "intent":"get_monthly_summary",
#             "shed":null,
#             "quantity":null,
#             "date":"this_month",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Move 100 produced eggs from shed 1 to shed 2

#         JSON:
#         {{
#             "intent":"move_record",
#             "from_shed":1,
#             "to_shed":2,
#             "field":"produced",
#             "quantity":100,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Move 5 broken eggs from shed 1 to shed 2

#         JSON:
#         {{
#             "intent":"move_record",
#             "from_shed":1,
#             "to_shed":2,
#             "field":"broken",
#             "quantity":5,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Move 20 sold eggs from shed 3 to shed 1

#         JSON:
#         {{
#             "intent":"move_record",
#             "from_shed":3,
#             "to_shed":1,
#             "field":"sold",
#             "quantity":20,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Change today's production of shed 1 to 500 eggs

#         JSON:
#         {{
#             "intent":"update_record",
#             "shed":1,
#             "field":"produced",
#             "quantity":500,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Update yesterday's broken eggs in shed 2 to 15

#         JSON:
#         {{
#             "intent":"update_record",
#             "shed":2,
#             "field":"broken",
#             "quantity":15,
#             "date":"yesterday",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Set sold eggs in shed 3 to 40

#         JSON:
#         {{
#             "intent":"update_record",
#             "shed":3,
#             "field":"sold",
#             "quantity":40,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Remove 20 eggs from today's production of shed 1

#         JSON:
#         {{
#             "intent":"remove_record",
#             "shed":1,
#             "field":"produced",
#             "quantity":20,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Remove 5 broken eggs from shed 2

#         JSON:
#         {{
#             "intent":"remove_record",
#             "shed":2,
#             "field":"broken",
#             "quantity":5,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Remove 10 sold eggs from shed 3 yesterday

#         JSON:
#         {{
#             "intent":"remove_record",
#             "shed":3,
#             "field":"sold",
#             "quantity":10,
#             "date":"yesterday",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Delete today's production of shed 1

#         JSON:
#         {{
#             "intent":"delete_field",
#             "shed":1,
#             "field":"produced",
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Delete broken eggs in shed 2

#         JSON:
#         {{
#             "intent":"delete_field",
#             "shed":2,
#             "field":"broken",
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Delete sold eggs in shed 3 yesterday

#         JSON:
#         {{
#             "intent":"delete_field",
#             "shed":3,
#             "field":"sold",
#             "quantity":null,
#             "date":"yesterday",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Delete today's shed 1 record

#         JSON:
#         {{
#             "intent":"delete_record",
#             "shed":1,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"egg"
#         }}

#         User:
#         Shed 1 has 5000 birds

#         JSON:
#         {{
#             "intent":"add_birds",
#             "shed":1,
#             "quantity":5000,
#             "date":"today",
#             "language":"en"
#         }}
#         User:
#         Update shed 2 bird count to 4800

#         JSON:
#         {{
#             "intent":"add_birds",
#             "shed":2,
#             "quantity":4800,
#             "date":"today",
#             "language":"en"
#         }}
#         User:
#         Bird count in shed 1

#         JSON:
#         {{
#             "intent":"get_birds",
#             "shed":1,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}
#         User:
#         Total birds today

#         JSON:
#         {{
#             "intent":"get_total_birds",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}

#         User:
#         5 birds died in shed 1

#         JSON:
#         {{
#             "intent":"add_mortality",
#             "shed":1,
#             "quantity":5,
#             "date":"today",
#             "language":"en"
#         }}

#         User:
#         Record 3 dead birds in shed 2

#         JSON:
#         {{
#             "intent":"add_mortality",
#             "shed":2,
#             "quantity":3,
#             "date":"today",
#             "language":"en"
#         }}

#         User:
#         Mortality in shed 1

#         JSON:
#         {{
#             "intent":"get_mortality",
#             "shed":1,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}

#         User:
#         Today's mortality

#         JSON:
#         {{
#             "intent":"get_total_mortality",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}


#         User:
#         Today's live birds

#         JSON:
#         {{
#             "intent":"get_total_live_birds",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}

#         User:
#         Total live birds

#         JSON:
#         {{
#             "intent":"get_total_live_birds",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}

#         User:
#         How many live birds are there?

#         JSON:
#         {{
#             "intent":"get_total_live_birds",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}

#         User:
#         Today's missing sheds

#         JSON:
#         {{
#             "intent":"get_missing_sheds",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}
#         User:
#         Missing sheds

#         JSON:
#         {{
#             "intent":"get_missing_sheds",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}
#         User:
#         Which sheds have not reported today?

#         JSON:
#         {{
#             "intent":"get_missing_sheds",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}
#         User:
#         Pending sheds

#         JSON:
#         {{
#             "intent":"get_missing_sheds",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}

#         User:
#         Today's pending fields

#         JSON:
#         {{
#             "intent":"get_missing_fields",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}
#         User:
#         Incomplete shed reports

#         JSON:
#         {{
#             "intent":"get_missing_fields",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}
#         User:
#         Which sheds have incomplete data?

#         JSON:
#         {{
#             "intent":"get_missing_fields",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en"
#         }}

#         Intent: compare_dates

#         Examples:

#         User: Compare today and yesterday

#         Output:
#         {{
#             "intent": "compare_dates",
#             "date1": "today",
#             "date2": "yesterday"
#         }}

#         User: Compare today and 14th July

#         Output:
#         {{
#             "intent": "compare_dates",
#             "date1": "today",
#             "date2": "2026-07-14"
#         }}

#         User: Compare 14-07-2026 and 15-07-2026

#         Output:
#         {{
#             "intent": "compare_dates",
#             "date1": "2026-07-14",
#             "date2": "2026-07-15"
#         }}

#         Compare production today and yesterday

#         output:
#         {{
#             "intent":"compare_dates",
#             "date1":"today",
#             "date2":"yesterday",
#             "field":"produced"
#         }}

#         User:
#         Compare this week and last week

#         Output:
#         {{
#             "intent":"compare_weeks",
#             "week1":"this_week",
#             "week2":"last_week"
#         }}

#         User:
#         Compare last week and this week

#         Output:
#         {{
#             "intent":"compare_weeks",
#             "week1":"last_week",
#             "week2":"this_week"
#         }}

#         User:
#         Compare this week's production with last week

#         Output:
#         {{
#             "intent":"compare_weeks",
#             "week1":"this_week",
#             "week2":"last_week",
#             "field":"produced"
#         }}

#         User:
#         Compare this month and last month

#         Output:
#         {{
#             "intent":"compare_months",
#             "month1":"this_month",
#             "month2":"last_month"
#         }}

#         User : 
#         Compare this month's production and last month

#         Ouptut:
#         {{
#             "intent":"compare_months",
#             "month1":"this_month",
#             "month2":"last_month",
#             "field":"produced"
#         }}

#         User:
#         Add 20 bottles Vitamin A in shed 1

#         Output:


#         {{
#             "intent":"add_medicine",
#             "shed":1,
#             "medicine":"Vitamin A",
#             "quantity":20,
#             "unit":"bottle"
#         }}

#         User:
#         Add 5 kg Calcium Powder in shed 3

#         Output:

#         {{
#             "intent":"add_medicine",
#             "shed":3,
#             "medicine":"Calcium Powder",
#             "quantity":5,
#             "unit":"kg"
#         }}


#         User:
#         Use 5 bottles Vitamin A in shed 1

#         Output:

#         {{
#             "intent":"use_medicine",
#             "shed":1,
#             "medicine":"Vitamin A",
#             "quantity":5
#         }}


#         User:
#         Used 10 ml Antibiotic in shed 4

#         Output:

#         {{
#             "intent":"use_medicine",
#             "shed":4,
#             "medicine":"Antibiotic",
#             "quantity":10
#         }}


#         User:
#         Vitamin A in shed 1

#         Output:

#         {{
#             "intent":"get_medicine",
#             "shed":1,
#             "medicine":"Vitamin A"
#         }}

#         User:
#         Show Vitamin A in shed 3

#         Output:

#         {{
#             "intent":"get_medicine",
#             "shed":3,
#             "medicine":"Vitamin A"
#         }}

#         User:
#         How much Vitamin A is remaining in shed 2?

#         Output:

#         {{
#             "intent":"get_medicine_remaining",
#             "shed":2,
#             "medicine":"Vitamin A"
#         }}

#         User:
#         How much Vitamin A has been used in shed 5?

#         Output:

#         {{
#             "intent":"get_medicine_used",
#             "shed":5,
#             "medicine":"Vitamin A"
#         }}

#         User:
#         Show medicines in shed 1

#         Output:

#         {{
#             "intent":"get_all_medicines",
#             "shed":1
#         }}

#         User:
#         Medicine report for shed 2

#         Output:

#         {{
#             "intent":"get_all_medicines",
#             "shed":2
#         }}

#         User:
#         List medicines in shed 4

#         Output:


#         {{
#             "intent":"get_all_medicines",
#             "shed":4
#         }}

#         User:
#         5 bottels vitamine A is used in shed 1

#         Output:
#         {{
#             "intent":"use_medicine",
#             "shed":1,
#             "medicine":"Vitamin A",
#             "quantity":5,
#             "unit":"bottle"
#         }}

#         User:
#         vitamin a in shed 1

#         Output:
#         {{
#             "intent":"get_medicine",
#             "shed":1,
#             "medicine":"Vitamin A"
#         }}

#         User:
#         vitamine A stock

#         Output:
#         {{
#             "intent":"get_medicine",
#             "shed":1,
#             "medicine":"Vitamin A"
#         }}


#         User:
#         Add 1000 kg Layer Feed to shed 1

#         JSON:
#         {{
#             "intent":"add_feed",
#             "shed":1,
#             "feed":"Layer Feed",
#             "quantity":1000,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Add 500 kg Starter Feed to shed 2

#         JSON:
#         {{
#             "intent":"add_feed",
#             "shed":2,
#             "feed":"Starter Feed",
#             "quantity":500,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Use 200 kg Layer Feed in shed 1

#         JSON:
#         {{
#             "intent":"use_feed",
#             "shed":1,
#             "feed":"Layer Feed",
#             "quantity":200,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Use 50 kg Starter Feed in shed 2

#         JSON:
#         {{
#             "intent":"use_feed",
#             "shed":2,
#             "feed":"Starter Feed",
#             "quantity":50,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Layer Feed in shed 1

#         JSON:
#         {{
#             "intent":"get_feed",
#             "shed":1,
#             "feed":"Layer Feed",
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Starter Feed in shed 2

#         JSON:
#         {{
#             "intent":"get_feed",
#             "shed":2,
#             "feed":"Starter Feed",
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Remaining feed in shed 1

#         JSON:
#         {{
#             "intent":"get_feed_remaining",
#             "shed":1,
#             "feed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Remaining Layer Feed in shed 1

#         JSON:
#         {{
#             "intent":"get_feed_remaining",
#             "shed":1,
#             "feed":"Layer Feed",
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Remaining feed

#         JSON:
#         {{
#             "intent":"get_feed_remaining",
#             "shed":null,
#             "feed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Used feed in shed 1

#         JSON:
#         {{
#             "intent":"get_feed_used",
#             "shed":1,
#             "feed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         How much Layer Feed is used in shed 1

#         JSON:
#         {{
#             "intent":"get_feed_used",
#             "shed":1,
#             "feed":"Layer Feed",
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}

#         User:
#         Used feed

#         JSON:
#         {{
#             "intent":"get_feed_used",
#             "shed":null,
#             "feed":null,
#             "quantity":null,
#             "date":"today",
#             "language":"en",
#             "unit":"kg"
#         }}


#         The farm has only 9 sheds numbered 1 to 9.

#         If the user mentions any shed outside this range, do NOT generate a normal intent.

#         Instead return:

#         {{
#             "intent":"invalid_shed",
#             "shed":10,
#             "message":"Invalid shed number"
#         }}

#         User: today report in pdf

#         Output:
#         {{
#             "intent":"generate_pdf",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "feed_name":null,
#             "medicine_name":null,
#             "language":"en"
#         }}

#         User: yesterday report pdf

#         Output:
#         {{
#             "intent":"generate_pdf",
#             "shed":null,
#             "quantity":null,
#             "date":"yesterday",
#             "feed_name":null,
#             "medicine_name":null,
#             "language":"en"
#         }}

#         User: generate today's report as pdf

#         Output:
#         {{
#             "intent":"generate_pdf",
#             "shed":null,
#             "quantity":null,
#             "date":"today",
#             "feed_name":null,
#             "medicine_name":null,
#             "language":"en"
#         }}

#         User: this week report in pdf

#         Output:
#         {{
#             "intent":"generate_weekly_pdf",
#             "shed":null,
#             "quantity":null,
#             "date":"this_week",
#             "feed_name":null,
#             "medicine_name":null,
#             "language":"en"
#         }}

#         User: weekly report pdf

#         Output:
#         {{
#             "intent":"generate_weekly_pdf",
#             "shed":null,
#             "quantity":null,
#             "date":"this_week",
#             "feed_name":null,
#             "medicine_name":null,
#             "language":"en"
#         }}

#         User:
#         this month report in pdf

#         Output:
#         {{
#             "intent": "generate_monthly_pdf",
#             "date": "this_month"
#         }}

#         User:
#         last month report in pdf

#         Output:
#         {{
#             "intent": "generate_monthly_pdf",
#             "date": "last_month"
#         }}

#         ==========================
#         PDF REPORT INTENTS
#         ==========================

#         1. Farm Daily PDF

#         Examples:
#         - today's report in pdf
#         - yesterday report in pdf
#         - 20 july report in pdf

#         Output:

#         User: today's report in pdf

#         {{
#             "intent": "generate_pdf",
#             "shed": null,
#             "quantity": null,
#             "date": "today",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: yesterday report in pdf

#         {{
#             "intent": "generate_pdf",
#             "shed": null,
#             "quantity": null,
#             "date": "yesterday",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         --------------------------------------------------

#         2. Farm Weekly PDF

#         Examples:
#         - this week report in pdf
#         - last week report in pdf

#         Output:

#         User: this week report in pdf

#         {{
#             "intent": "generate_weekly_pdf",
#             "shed": null,
#             "quantity": null,
#             "date": "this_week",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: last week report in pdf

#         {{
#             "intent": "generate_weekly_pdf",
#             "shed": null,
#             "quantity": null,
#             "date": "last_week",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         --------------------------------------------------

#         3. Farm Monthly PDF

#         Examples:
#         - this month report in pdf
#         - last month report in pdf

#         Output:

#         User: this month report in pdf

#         {{
#             "intent": "generate_monthly_pdf",
#             "shed": null,
#             "quantity": null,
#             "date": "this_month",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: last month report in pdf

#         {{
#             "intent": "generate_monthly_pdf",
#             "shed": null,
#             "quantity": null,
#             "date": "last_month",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}
#         --------------------------------------------------

#         4. Shed PDF Reports

#         Use this intent whenever the user asks for a PDF report of a specific shed.

#         Examples:

#         - today's shed 1 report in pdf
#         - yesterday shed 3 report in pdf
#         - shed 2 report in pdf
#         - this week shed 4 report in pdf
#         - last week shed 6 report in pdf
#         - this month shed 5 report in pdf
#         - last month shed 7 report in pdf

#         Output:

#         User: today's shed 1 report in pdf

#         {{
#             "intent": "generate_shed_pdf",
#             "shed": 1,
#             "quantity": null,
#             "date": "today",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: yesterday shed 3 report in pdf

#         {{
#             "intent": "generate_shed_pdf",
#             "shed": 3,
#             "quantity": null,
#             "date": "yesterday",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: shed 2 report in pdf

#         {{
#             "intent": "generate_shed_pdf",
#             "shed": 2,
#             "quantity": null,
#             "date": "today",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: this week shed 4 report in pdf

#         {{
#             "intent": "generate_shed_pdf",
#             "shed": 4,
#             "quantity": null,
#             "date": "this_week",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: last week shed 6 report in pdf

#         {{
#             "intent": "generate_shed_pdf",
#             "shed": 6,
#             "quantity": null,
#             "date": "last_week",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: this month shed 5 report in pdf

#         {{
#             "intent": "generate_shed_pdf",
#             "shed": 5,
#             "quantity": null,
#             "date": "this_month",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}

#         User: last month shed 7 report in pdf

#         {{
#             "intent": "generate_shed_pdf",
#             "shed": 7,
#             "quantity": null,
#             "date": "last_month",
#             "feed_name": null,
#             "medicine_name": null,
#             "language": "en"
#         }}
        
#         User:
#         Compare today and yesterday in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"day",
#         "shed":null,
#         "quantity":null,
#         "date":null,
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         User:
#         Compare this week and last week in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"week",
#         "shed":null,
#         "quantity":null,
#         "date":null,
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         User:
#         Compare this month and last month in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"month",
#         "shed":null,
#         "quantity":null,
#         "date":null,
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         User:
#         Compare Shed 1 today and yesterday in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"day",
#         "shed":1,
#         "quantity":null,
#         "date":null,
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         User:
#         Compare Shed 1 this week and last week in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"week",
#         "shed":1,
#         "quantity":null,
#         "date":null,
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         User:
#         Compare Shed 1 this month and last month in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"month",
#         "shed":1,
#         "quantity":null,
#         "date":null,
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         User:
#         Compare today and 15th July in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"custom_day",
#         "shed":null,
#         "quantity":null,
#         "date1":"today",
#         "date2":"2026-07-15",
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         User:
#         Compare 10th July and 15th July in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"custom_day",
#         "shed":null,
#         "quantity":null,
#         "date1":"2026-07-10",
#         "date2":"2026-07-15",
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         User:
#         Compare Shed 1 today and 15th July in PDF
#         Output:
#         {{
#         "intent":"compare_report_pdf",
#         "comparison":"custom_day",
#         "shed":1,
#         "quantity":null,
#         "date1":"today",
#         "date2":"2026-07-15",
#         "feed_name":null,
#         "medicine_name":null,
#         "language":"en"
#         }}

#         Now convert this:

#         {message}
#         """
#     response = model.generate_content(prompt)

#     text = response.text.strip()

#     # Remove markdown if present
#     text = text.replace("```json", "").replace("```", "").strip()

#     return json.loads(text)
