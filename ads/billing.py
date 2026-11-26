from decimal import Decimal

from rest_framework.exceptions import APIException

from .models import Campaign


class CampaignBudgetExhausted(APIException):
    status_code = 409
    default_detail = "The campaign has insufficient remaining budget."
    default_code = "campaign_budget_exhausted"


def bill_event(ad, event, *, valid_view=False):
    if event == "impression" and ad.pricing_model == "CPM":
        amount = ad.price / Decimal("1000")
    elif (event == "click" and ad.pricing_model == "CPC") or (
        event == "view" and ad.pricing_model == "CPV" and valid_view
    ):
        amount = ad.price
    else:
        return Decimal("0")

    if amount <= 0:
        return Decimal("0")

    campaign = Campaign.objects.select_for_update().get(pk=ad.campaign_id)
    if campaign.spent + amount > campaign.budget:
        raise CampaignBudgetExhausted()

    campaign.spent += amount
    campaign.save(update_fields=["spent", "updated_at"])
    return amount
