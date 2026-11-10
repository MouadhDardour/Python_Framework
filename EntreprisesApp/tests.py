from datetime import date

from django.test import TestCase
from django.urls import reverse

from ExpeditionsApp.models import Expedition
from .models import Entreprise, Utilisateur


class EntrepriseActionsTests(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            username='chargeur',
            email='chargeur@gmail.com',
            password='test-password',
        )
        self.entreprise = Entreprise.objects.create(
            raison_sociale='Entreprise chargeur',
            matricule_fiscal='1234567AAM000',
            type_entreprise='chargeur',
            adresse='Adresse de test suffisamment longue',
            utilisateur=self.utilisateur,
        )

    def test_list_has_add_edit_and_delete_actions(self):
        response = self.client.get(reverse('entreprises:liste'))

        self.assertContains(response, reverse('entreprises:ajouter'))
        self.assertContains(
            response, reverse('entreprises:modifier', args=[self.entreprise.pk])
        )
        self.assertContains(
            response, reverse('entreprises:supprimer', args=[self.entreprise.pk])
        )

    def test_add_uses_an_unlinked_user(self):
        utilisateur = Utilisateur.objects.create_user(
            username='transporteur',
            email='transporteur@gmail.com',
            password='test-password',
        )

        response = self.client.post(
            reverse('entreprises:ajouter'),
            {
                'raison_sociale': 'Nouvelle entreprise',
                'matricule_fiscal': '1234568AAM001',
                'type_entreprise': 'transporteur',
                'adresse': 'Adresse de test suffisamment longue',
                'utilisateur': utilisateur.pk,
            },
        )

        nouvelle = Entreprise.objects.get(raison_sociale='Nouvelle entreprise')
        self.assertRedirects(
            response, reverse('entreprises:detail', args=[nouvelle.pk])
        )

    def test_delete_is_blocked_when_enterprise_has_expeditions(self):
        Expedition.objects.create(
            entreprise=self.entreprise,
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg='100.00',
            date_souhaitee=date(2026, 12, 1),
        )

        response = self.client.post(
            reverse('entreprises:supprimer', args=[self.entreprise.pk])
        )

        self.assertRedirects(
            response, reverse('entreprises:detail', args=[self.entreprise.pk])
        )
        self.assertTrue(Entreprise.objects.filter(pk=self.entreprise.pk).exists())
