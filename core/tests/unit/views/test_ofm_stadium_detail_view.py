from django.test import TestCase

from core.factories.core_factories import MatchdayFactory, MatchFactory, \
    MatchStadiumStatisticsFactory, StadiumStandStatisticsFactory
from users.models import OFMUser


class OFMStadiumDetailsViewTestCase(TestCase):
    def setUp(self):
        MatchdayFactory.create()
        MatchdayFactory.create(number=1)
        user1 = OFMUser.objects.create_user(
            username='alice',
            email='alice@ofmhelper.com',
            password='alice',
            ofm_username='alice',
            ofm_password='alice'
        )
        OFMUser.objects.create_user(
            username='bob',
            email='bob@ofmhelper.com',
            password='bob',
            ofm_username='bob',
            ofm_password='bob'
        )
        match = MatchFactory.create(user=user1)
        self.stadium_stat = MatchStadiumStatisticsFactory.create(match=match)
        StadiumStandStatisticsFactory.create(stadium_statistics=self.stadium_stat, sector='N')
        StadiumStandStatisticsFactory.create(stadium_statistics=self.stadium_stat, sector='S')
        StadiumStandStatisticsFactory.create(stadium_statistics=self.stadium_stat, sector='W')
        StadiumStandStatisticsFactory.create(stadium_statistics=self.stadium_stat, sector='O')
        self.client.login(username='alice', password='alice')

    def test_user_can_see_his_data(self):
        response = self.client.get('/ofm/stadium/' + str(self.stadium_stat.id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('stadium_stat' in response.context_data)
        self.assertTrue('north_stand' in response.context_data)
        self.assertTrue('south_stand' in response.context_data)
        self.assertTrue('west_stand' in response.context_data)
        self.assertTrue('east_stand' in response.context_data)

    def test_user_cannot_see_other_users_data(self):
        self.client.login(username='bob', password='bob')
        response = self.client.get('/ofm/stadium/' + str(self.stadium_stat.id))
        self.assertEqual(response.status_code, 200)
        self.assertFalse('stadium_stat' in response.context_data)
        self.assertFalse('north_stand' in response.context_data)
        self.assertFalse('south_stand' in response.context_data)
        self.assertFalse('west_stand' in response.context_data)
        self.assertFalse('east_stand' in response.context_data)
