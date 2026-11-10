from django.test import TestCase
from django.urls import reverse

from EntreprisesApp.models import Entreprise, Utilisateur
from .models import Vehicule


class VehiculeActionsTests(TestCase):
    def setUp(self):
        utilisateur = Utilisateur.objects.create_user(
            username='transporteur',
            email='transporteur@gmail.com',
            password='test-password',
        )
        self.entreprise = Entreprise.objects.create(
            raison_sociale='Entreprise transporteur',
            matricule_fiscal='1234567AAM000',
            type_entreprise='transporteur',
            adresse='Adresse de test suffisamment longue',
            utilisateur=utilisateur,
        )
        self.vehicule = Vehicule.objects.create(
            immatriculation='TEST-001',
            type_vehicule='camionnette',
            capacite_kg=1000,
            entreprise=self.entreprise,
        )

    def test_list_has_add_edit_and_delete_actions(self):
        response = self.client.get(reverse('vehicules:liste'))

        self.assertContains(response, reverse('vehicules:ajouter'))
        self.assertContains(
            response, reverse('vehicules:modifier', args=[self.vehicule.pk])
        )
        self.assertContains(
            response, reverse('vehicules:supprimer', args=[self.vehicule.pk])
        )

    def test_add_and_edit_vehicule(self):
        add_response = self.client.post(
            reverse('vehicules:ajouter'),
            {
                'immatriculation': 'TEST-002',
                'type_vehicule': 'camionnette',
                'capacite_kg': 1200,
                'disponible': 'on',
                'entreprise': self.entreprise.pk,
            },
        )
        nouvelle = Vehicule.objects.get(immatriculation='TEST-002')
        self.assertRedirects(
            add_response, reverse('vehicules:detail', args=[nouvelle.pk])
        )

        edit_response = self.client.post(
            reverse('vehicules:modifier', args=[nouvelle.pk]),
            {
                'immatriculation': 'TEST-002',
                'type_vehicule': 'camionnette',
                'capacite_kg': 1400,
                'disponible': 'on',
                'entreprise': self.entreprise.pk,
            },
        )
        self.assertRedirects(
            edit_response, reverse('vehicules:detail', args=[nouvelle.pk])
        )
        nouvelle.refresh_from_db()
        self.assertEqual(nouvelle.capacite_kg, 1400)
