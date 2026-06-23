import frappe
from frappe.utils import now_datetime


def close_expired_auctions():
    auctions = frappe.get_all(
        "Auction Event",
        filters={"status": "Live"},
        fields=["name", "end_datetime"]
    )

    for auction in auctions:
        if now_datetime() >= auction.end_datetime:
            close_auction_event(auction.name)


def close_auction_event(auction_name):

    auction = frappe.get_doc("Auction Event", auction_name)

    listings = frappe.get_all(
        "Auction Listing",
        filters={"auction_event": auction_name},
        fields=["name", "reserve_price", "current_highest_bid"]
    )

    for listing in listings:

        bid = listing.current_highest_bid or 0

        status = "Sold" if bid >= listing.reserve_price else "Unsold"

        frappe.db.set_value(
            "Auction Listing",
            listing.name,
            "status",
            status
        )

    auction.status = "Closed"
    auction.save()