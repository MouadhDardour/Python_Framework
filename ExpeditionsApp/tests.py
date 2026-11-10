from datetime import date

from django.test import TestCase
from django.urls import reverse

from EntreprisesApp.models import Entreprise, Utilisateur
from .models import Expedition


class ExpeditionActionsTests(TestCase):
    def setUp(self):
        utilisateur = Utilisateur.objects.create_user(
            username='chargeur',
            email='chargeur@gmail.com',
            password='test-password',
        )
        self.entreprise = Entreprise.objects.create(
            raison_sociale='Entreprise chargeur',
            matricule_fiscal='1234567AAM000',
            type_entreprise='chargeur',
            adresse='Adresse de test suffisamment longue',
            utilisateur=utilisateur,
        )
        self.expedition = Expedition.objects.create(
            entreprise=self.entreprise,
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg='100.00',
            date_souhaitee=date(2026, 12, 1),
        )

    def test_list_has_add_edit_and_delete_actions(self):
        response = self.client.get(reverse('expeditions:liste'))

        self.assertContains(response, reverse('expeditions:ajouter'))
        self.assertContains(
            response, reverse('expeditions:modifier', args=[self.expedition.reference])
        )
        self.assertContains(
            response, reverse('expeditions:supprimer', args=[self.expedition.reference])
        )

    def test_add_and_edit_expedition(self):
        add_response = self.client.post(
            reverse('expeditions:ajouter'),
            {
                'entreprise': self.entreprise.pk,
                'ville_depart': 'Bizerte',
                'ville_arrivee': 'Sfax',
                'poids_kg': '125.00',
                'date_souhaitee': '2026-12-10',
                'description': 'Nouvelle expédition',
                'statut': 'publiee',
            },
        )
        nouvelle = Expedition.objects.get(ville_depart='Bizerte')
        self.assertRedirects(
            add_response,
            reverse('expeditions:detail', args=[nouvelle.reference]),
        )

        edit_response = self.client.post(
            reverse('expeditions:modifier', args=[nouvelle.reference]),
            {
                'entreprise': self.entreprise.pk,
                'ville_depart': 'Gabès',
                'ville_arrivee': 'Sfax',
                'poids_kg': '125.00',
                'date_souhaitee': '2026-12-10',
                'description': 'Expédition modifiée',
                'statut': 'publiee',
            },
        )
        self.assertRedirects(
            edit_response,
            reverse('expeditions:detail', args=[nouvelle.reference]),
        )
        nouvelle.refresh_from_db()
        self.assertEqual(nouvelle.ville_depart, 'Gabès')

    def test_delete_requires_post(self):
        url = reverse('expeditions:supprimer', args=[self.expedition.reference])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Expedition.objects.filter(pk=self.expedition.pk).exists())
