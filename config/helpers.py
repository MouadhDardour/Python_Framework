from django.utils.html import format_html


def badge(couleur, libelle):
    """Coloured status badge used in the admin list pages."""
    return format_html(
        '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;">{}</span>',
        couleur,
        libelle,
    )
