from datetime import timedelta

from django.contrib import admin
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import path
from django.utils import timezone


class TransConnectAdminSite(admin.AdminSite):
    # Branding (Admin workshop, block 5)
    site_header = 'TransConnect - Administration'
    site_title = 'TransConnect'
    index_title = 'Pilotage des expéditions, des offres et de la flotte'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'health-check/',
                self.admin_view(self.health_check_view),
                name='health-check',
            ),
        ]
        return custom + urls

    def health_check_view(self, request):
        # Imported here to avoid loading models while the admin site is being set up.
        from EntreprisesApp.models import Entreprise
        from ExpeditionsApp.models import Expedition
        from OffresApp.models import Offre
        from VehiculesApp.models import Vehicule

        maintenant = timezone.now()
        seuil = maintenant - timedelta(days=7)

        def ligne_offre(o):
            return (
                f"Offre #{o.pk} ({o.get_statut_display()}) - {o.transporteur.raison_sociale} "
                f"sur {o.expedition.reference} (expédition : {o.expedition.get_statut_display()})"
            )

        # 1. Orphan offers
        orphelines = (
            Offre.objects.filter(statut_in=['proposee', 'acceptee'])
            .exclude(expedition__statut__in=['publiee', 'attribuee'])
            .select_related('expedition', 'transporteur')
        )

        # 2. Blocked expeditions (published for more than 7 days)
        bloquees = Expedition.objects.filter(
            statut='publiee', created_at__lt=seuil
        ).select_related('entreprise')

        # 3. Carriers without a fleet (annotate/Count, no Python loop)
        sans_flotte = (
            Entreprise.objects.filter(type_entreprise='transporteur')
            .annotate(nb_vehicules=Count('vehicules'))
            .filter(nb_vehicules=0)
        )

        # 4. Availability inconsistency
        incoherents = (
            Vehicule.objects.filter(disponible=True, offres__statut='acceptee')
            .select_related('entreprise')
            .distinct()
        )

        # 5. Duplicate proposals (violation of business rule 4)
        doublons = (
            Offre.objects.filter(statut='proposee')
            .values('expedition__reference', 'transporteur__raison_sociale')
            .annotate(nb=Count('pk'))
            .filter(nb__gt=1)
        )

        # 6. (our own check) Incomplete acceptance cascade (violation of business rule 5)
        cascade_incomplete = (
            Offre.objects.filter(
                Q(statut='acceptee', expedition__statut='publiee')
                | Q(statut='proposee', expedition__offres__statut='acceptee')
            )
            .select_related('expedition', 'transporteur')
            .distinct()
        )

        controles = [
            {
                'numero': 1,
                'titre': 'Offres orphelines',
                'regle': "Offres proposées/acceptées dont l'expédition n'est plus publiée/attribuée.",
                'lignes': [ligne_offre(o) for o in orphelines],
            },
            {
                'numero': 2,
                'titre': 'Expéditions bloquées',
                'regle': "Expéditions publiées depuis plus de 7 jours sans être attribuées.",
                'lignes': [
                    f"{e.reference} - {e.entreprise.raison_sociale} - publiée le "
                    f"{e.created_at:%d/%m/%Y}"
                    for e in bloquees
                ],
            },
            {
                'numero': 3,
                'titre': 'Transporteurs sans flotte',
                'regle': "Entreprises de type transporteur ne possédant aucun véhicule.",
                'lignes': [e.raison_sociale for e in sans_flotte],
            },
            {
                'numero': 4,
                'titre': "Incohérence de disponibilité",
                'regle': "Véhicules disponibles mais assignés à une offre acceptée.",
                'lignes': [f"{v.immatriculation} ({v.entreprise.raison_sociale})" for v in incoherents],
            },
            {
                'numero': 5,
                'titre': 'Doublons de proposition',
                'regle': "Entreprises ayant plus d'une offre proposée sur la même expédition.",
                'lignes': [
                    f"{d['transporteur__raison_sociale']} : {d['nb']} offres proposées "
                    f"sur {d['expedition__reference']}"
                    for d in doublons
                ],
            },
            {
                'numero': 6,
                'titre': "Cascade d'acceptation incomplète",
                'regle': "Offre acceptée alors que l'expédition est encore publiée, ou offre "
                "encore proposée sur une expédition déjà attribuée.",
                'lignes': [ligne_offre(o) for o in cascade_incomplete],
            },
        ]

        context = {
            **self.each_context(request),
            'title': "Contrôle d'intégrité",
            'maintenant': maintenant,
            'controles': controles,
            'nb_anomalies': sum(len(c['lignes']) for c in controles),
        }
        return render(request, 'admin/health_check.html', context)
