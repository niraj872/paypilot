approval_url = next(
    (link["href"] for link in paypal_order.get("links", []) if link.get("rel") == "approve"),
    None,
)