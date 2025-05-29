from django import template
register = template.Library()

@register.filter
def med_icon(route):
    return {
        "ORAL": "fa-capsules",
        "RESPIRATORY (INHALATION)": "fa-lungs",
        "INTRATHECAL": "fa-syringe",
        "OPHTHALMIC": "fa-eye",
        "TOPICAL": "fa-pump-soap",
        "SUBCUTANEOUS": "fa-syringe",
        "INTRAMUSCULAR": "fa-syringe",
        "INTRAVENOUS": "fa-droplet",
        "SUBLINGUAL": "fa-mouth",
        "NASAL": "fa-head-side-cough",
    }.get(route, "fa-question")