import frappe

def get_context(context):

    # =========================
    # CONSIGNED ITEMS (INVENTORY)
    # =========================
    context.items = frappe.get_all(
        "Consigned Items",   # VERIFY this name in DocType list
        filters={
            "status": ["in", ["Approved", "Listed"]]
        },
        fields=[
            "name",
            "item_name",
            "item_image",
            "condition",
            "category"
        ],
        limit=5
    )

    # =========================
    # LIVE AUCTION LISTING
    # =========================
    live_listing = frappe.get_all(
        "Auction Listing",
        filters={
            "status": "Live"
        },
        fields=[
            "name",
            "reserve_price",
            "starting_bid",
            "current_highest_bid",
            "auction_event"   # important for linking
        ],
        limit=1
    )

    context.live_listing = live_listing[0] if live_listing else None

    # Total value of all live auction listings
    volume = frappe.db.sql("""
        SELECT SUM(current_highest_bid)
        FROM `tabAuction Listing`
        WHERE status='Live'
    """)[0][0] or 0

    context.current_volume = volume

    # Total bidders
    participants = frappe.db.sql("""
    SELECT COUNT(DISTINCT bidder)
    FROM `tabBid`
    """)[0][0] or 0

    context.participants = participants
    

    # Successful auctions
    total_auctions = frappe.db.count("Auction Result")

    successful_auctions = frappe.db.count(
        "Auction Result",
        {"status": "Sold"}
    )

    if total_auctions > 0:
        context.success_rate = round(
            (successful_auctions / total_auctions) * 100
        )
    else:
        context.success_rate = 0

    return context