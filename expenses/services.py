"""Expense business rules (SAD 3.1 Expense Service, SRS 6.5 business rules)."""


def category_problem(category, user):
    """Return an error message if this user may not use the category, else None."""
    if not category.is_active:
        return "This category is inactive and cannot be used."
    if category.owner_id is not None and category.owner_id != user.id:
        return "You can only use predefined categories or your own."
    return None