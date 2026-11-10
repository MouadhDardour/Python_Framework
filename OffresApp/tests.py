from datetime import date

from django.test import TestCase
from django.urls import reverse

from EntreprisesApp.models import Entreprise, Utilisateur
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule
from .models import Offre


class OffreActionsTests(TestCase):
    def setUp(self):
        chargeur_user = Utilisateur.objects.create_user(
            username='chargeur',
            email='chargeur@gmail.com',
            password='test-password',
        )
        transporteur_user = Utilisateur.objects.create_user(
            username='transporteur',
            email='transporteur@gmail.com',
            password='test-password',
        )
        self.chargeur = Entreprise.objects.create(
            raison_sociale='Entreprise chargeur',
            matricule_fiscal='1234567AAM000',
            type_entreprise='chargeur',
            adresse='Adresse de test suffisamment longue',
            utilisateur=chargeur_user,
        )
        self.transporteur = Entreprise.objects.create(
            raison_sociale='Entreprise transporteur',
            matricule_fiscal='1234568AAM001',
            type_entreprise='transporteur',
            adresse='Adresse de test suffisamment longue',
            utilisateur=transporteur_user,
        )
        self.expedition = Expedition.objects.create(
            entreprise=self.chargeur,
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg='100.00',
            date_souhaitee=date(2026, 12, 1),
        )
        self.vehicule = Vehicule.objects.create(
            immatriculation='TEST-001',
            type_vehicule='camionnette',
            capacite_kg=1000,
            entreprise=self.transporteur,
        )
        self.offre = Offre.objects.create(
            expedition=self.expedition,
            transporteur=self.transporteur,
            vehicule=self.vehicule,
            prix='50.00',
            delai_jours=3,
        )

    def test_list_has_add_edit_and_delete_actions(self):
        response = self.client.get(reverse('offres:liste'))

        self.assertContains(response, reverse('offres:ajouter'))
        self.assertContains(response, reverse('offres:modifier', args=[self.offre.pk]))
        self.assertContains(response, reverse('offres:supprimer', args=[self.offre.pk]))

    def test_add_and_edit_offre(self):
        autre_expedition = Expedition.objects.create(
            entreprise=self.chargeur,
            ville_depart='Bizerte',
            ville_arrivee='Sfax',
            poids_kg='100.00',
            date_souhaitee=date(2026, 12, 2),
        )
        add_response = self.client.post(
            reverse('offres:ajouter'),
            {
                'expedition': autre_expedition.pk,
                'transporteur': self.transporteur.pk,
                'vehicule': self.vehicule.pk,
                'prix': '60.00',
                'delai_jours': 4,
            },
        )
        nouvelle = Offre.objects.get(prix='60.00')
        self.assertRedirects(add_response, reverse('offres:detail', args=[nouvelle.pk]))

        edit_response = self.client.post(
            reverse('offres:modifier', args=[nouvelle.pk]),
            {
                'expedition': autre_expedition.pk,
                'transporteur': self.transporteur.pk,
                'vehicule': self.vehicule.pk,
                'prix': '70.00',
                'delai_jours': 5,
            },
        )
        self.assertRedirects(edit_response, reverse('offres:detail', args=[nouvelle.pk]))
        nouvelle.refresh_from_db()
        self.assertEqual(str(nouvelle.prix), '70.00')
