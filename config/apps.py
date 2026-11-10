from django.contrib.admin.apps import AdminConfig


class TransConnectAdminConfig(AdminConfig):
    """Makes Django use our custom AdminSite (branding + health-check page)."""
    default_site = 'config.admin_site.TransConnectAdminSite'