# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import Counter

from django.core.urlresolvers import reverse
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models import Sum
from django.utils.encoding import smart_str

from core.web.ofm_page_constants import Constants
from users.models import OFMUser

AGE_AT_BIRTH = 17


class Season(models.Model):
    class Meta:
        ordering = ['-number']

    number = models.IntegerField()

    def __str__(self):
        return "%s" % self.number


class Quarter(models.Model):
    QUARTERS = ((0, '1'), (1, '2'), (2, '3'), (3, '4'))

    season = models.ForeignKey(Season)
    quarter = models.IntegerField(choices=QUARTERS)

    def __str__(self):
        return "%s/%s" % (self.season.number, self.quarter)


class Matchday(models.Model):
    class Meta:
        ordering = ['season', '-number']

    season = models.ForeignKey(Season)
    number = models.IntegerField()

    def __str__(self):
        return "%s/%s" % (self.season.number, self.number)

    @staticmethod
    def get_current():
        """ Get the current matchday.

        """
        matchday = Matchday.objects.all()[0]
        finances = Finance.objects.all().order_by('matchday')
        player_statistics = PlayerStatistics.objects.all().order_by('matchday')
        matches = [m for m in Match.objects
                   .filter(matchday__season__number__gte=matchday.season.number)
                   .order_by('matchday')
                   if not m.is_in_future]
        if finances.count() > 0 and finances[0].matchday.number < matchday.number:
            matchday = finances[0].matchday
        if player_statistics.count() > 0 and player_statistics[0].matchday.number > matchday.number:
            matchday = player_statistics[0].matchday
        if matches and matches[0].matchday.number > matchday.number:
            matchday = matches[0].matchday

        return matchday


class Country(models.Model):
    class Meta:
        verbose_name_plural = "Countries"

    COUNTRIES = (
        ('AF', "Afghanistan"),
        ('EG', "Ägypten"),
        ('AL', "Albanien"),
        ('DZ', "Algerien"),
        ('AD', "Andorra"),
        ('AO', "Angola"),
        ('AG', "Antigua und Barbuda"),
        ('GQ', "Äquatorialguinea"),
        ('AR', "Argentinien"),
        ('AM', "Armenien"),
        ('AZ', "Aserbaidschan"),
        ('ET', "Äthiopien"),
        ('AU', "Australien"),
        ('BS', "Bahamas"),
        ('BH', "Bahrain"),
        ('BD', "Bangladesch"),
        ('BB', "Barbados"),
        ('BE', "Belgien"),
        ('BZ', "Belize"),
        ('BJ', "Benin"),
        ('BT', "Bhutan"),
        ('BO', "Bolivien"),
        ('BA', "Bosnien und Herzegowina"),
        ('BW', "Botswana"),
        ('BR', "Brasilien"),
        ('VG', "Britische Jungferninseln"),
        ('BN', "Brunei"),
        ('BG', "Bulgarien"),
        ('BF', "Burkina Faso"),
        ('BI', "Burundi"),
        ('CL', "Chile"),
        ('TW', "Republik China (Taiwan)"),
        ('CN', "Volksrepublik China"),
        ('CR', "Costa Rica"),
        ('DK', "Dänemark"),
        ('DE', "Deutschland"),
        ('DM', "Dominica"),
        ('DO', "Dominikanische Republik"),
        ('DJ', "Dschibuti"),
        ('EC', "Ecuador"),
        ('CI', "Elfenbeinküste"),
        ('SV', "El Salvador"),
        ('ER', "Eritrea"),
        ('EE', "Estland"),
        ('FJ', "Fidschi"),
        ('FI', "Finnland"),
        ('FR', "Frankreich"),
        ('GA', "Gabun"),
        ('GM', "Gambia"),
        ('GE', "Georgien"),
        ('GH', "Ghana"),
        ('GD', "Grenada"),
        ('GR', "Griechenland"),
        ('GT', "Guatemala"),
        ('GN', "Guinea"),
        ('GW', "Guinea-Bissau"),
        ('GY', "Guyana"),
        ('HT', "Haiti"),
        ('HN', "Honduras"),
        ('IN', "Indien"),
        ('ID', "Indonesien"),
        ('IQ', "Irak"),
        ('IR', "Iran"),
        ('IE', "Irland"),
        ('IS', "Island"),
        ('IL', "Israel"),
        ('IT', "Italien"),
        ('JM', "Jamaika"),
        ('JP', "Japan"),
        ('YE', "Jemen"),
        ('JO', "Jordanien"),
        ('YUCS', "Jugoslawien"),
        ('KH', "Kambodscha"),
        ('CM', "Kamerun"),
        ('CA', "Kanada"),
        ('CV', "Kap Verde"),
        ('KZ', "Kasachstan"),
        ('QA', "Katar"),
        ('KE', "Kenia"),
        ('KG', "Kirgisistan"),
        ('KI', "Kiribati"),
        ('CO', "Kolumbien"),
        ('KM', "Komoren"),
        ('CG', "Republik Kongo"),
        ('CD', "Demokr. Republik Kongo"),
        ('KP', "Nordkorea"),
        ('KR', "Südkorea"),
        ('HR', "Kroatien"),
        ('CU', "Kuba"),
        ('KW', "Kuwait"),
        ('LA', "Laos"),
        ('LS', "Lesotho"),
        ('LV', "Lettland"),
        ('LB', "Libanon"),
        ('LR', "Liberia"),
        ('LY', "Libyen"),
        ('LI', "Liechtenstein"),
        ('LT', "Litauen"),
        ('LU', "Luxemburg"),
        ('MG', "Madagaskar"),
        ('MW', "Malawi"),
        ('MY', "Malaysia"),
        ('MV', "Malediven"),
        ('ML', "Mali"),
        ('MT', "Malta"),
        ('MA', "Marokko"),
        ('MH', "Marshallinseln"),
        ('MR', "Mauretanien"),
        ('MU', "Mauritius"),
        ('MK', "Mazedonien"),
        ('MX', "Mexiko"),
        ('FM', "Mikronesien"),
        ('MD', "Moldawien"),
        ('MC', "Monaco"),
        ('MN', "Mongolei"),
        ('ME', "Montenegro"),
        ('MZ', "Mosambik"),
        ('MM', "Myanmar"),
        ('NA', "Namibia"),
        ('NR', "Nauru"),
        ('NP', "Nepal"),
        ('NZ', "Neuseeland"),
        ('NI', "Nicaragua"),
        ('NL', "Niederlande"),
        ('NE', "Niger"),
        ('NG', "Nigeria"),
        ('NO', "Norwegen"),
        ('OM', "Oman"),
        ('AT', "Österreich"),
        ('TL', "Osttimor"),
        ('PK', "Pakistan"),
        ('PW', "Palau"),
        ('PA', "Panama"),
        ('PG', "Papua-Neuguinea"),
        ('PY', "Paraguay"),
        ('PE', "Peru"),
        ('PH', "Philippinen"),
        ('PL', "Polen"),
        ('PT', "Portugal"),
        ('RW', "Ruanda"),
        ('RO', "Rumänien"),
        ('RU', "Russland"),
        ('SB', "Salomonen"),
        ('ZM', "Sambia"),
        ('WS', "Samoa"),
        ('SM', "San Marino"),
        ('ST', "São Tomé und Príncipeão"),
        ('SA', "Saudi-Arabien"),
        ('SE', "Schweden"),
        ('CH', "Schweiz"),
        ('SN', "Senegal"),
        ('RS', "Serbien"),
        ('SC', "Seychellen"),
        ('SL', "Sierra Leone"),
        ('ZW', "Simbabwe"),
        ('SG', "Singapur"),
        ('SK', "Slowakei"),
        ('SI', "Slowenien"),
        ('SO', "Somalia"),
        ('ES', "Spanien"),
        ('LK', "Sri Lanka"),
        ('KN', "St Kitts und Nevis"),
        ('LC', "St Lucia"),
        ('VC', "St Vincent und die Grenadinen"),
        ('ZA', "Südafrika"),
        ('SD', "Sudan"),
        ('SS', "Südsudan"),
        ('SR', "Suriname"),
        ('SZ', "Swasiland"),
        ('SY', "Syrien"),
        ('TJ', "Tadschikistan"),
        ('TZ', "Tansania"),
        ('TH', "Thailand"),
        ('TG', "Togo"),
        ('TO', "Tonga"),
        ('TT', "Trinidad & Tobago"),
        ('TD', "Tschad"),
        ('CZ', "Tschechien"),
        ('TN', "Tunesien"),
        ('TR', "Türkei"),
        ('TM', "Turkmenistan"),
        ('TV', "Tuvalu"),
        ('UG', "Uganda"),
        ('UA', "Ukraine"),
        ('HU', "Ungarn"),
        ('UY', "Uruguay"),
        ('UZ', "Usbekistan"),
        ('VU', "Vanuatu"),
        ('VE', "Venezuela"),
        ('AE', "Vereinigte Arabische Emirate"),
        ('US', "USA"),
        ('GB', "Vereinigtes Königreich"),
        ('VN', "Vietnam"),
        ('BY', "Weißrussland"),
        ('CF', "Zentralafrikanische Republik"),
        ('CY', "Zypern"),
        ('GB-ENG', "England"),
        ('GB-WLS', "Wales"),
        ('GB-SCT', "Schottland"),
        ('GB-NIR', "Nordirland"),
    )

    country = models.CharField(max_length=10, choices=COUNTRIES)

    def __str__(self):
        return smart_str(dict(self.COUNTRIES).get(self.country))

    def get_iso(self):
        return self.country

    @staticmethod
    def get_choices():
        return dict(Country._meta.get_field('country').choices)


class League(models.Model):
    LEAGUES = (
        (0, '1. Liga'),
        (1, '2. Liga'),
        (2, 'Regionalliga'),
        (3, 'Oberliga'),
        (4, 'Verbandsliga'),
        (5, 'Landesliga'),
        (6, 'Landesklasse'),
        (7, 'Bezirksliga'),
        (8, 'Bezirksklasse'),
        (9, 'Kreisliga'),
        (10, 'Kreisklasse'),
    )

    league = models.IntegerField(choices=LEAGUES)
    relay = models.CharField(max_length=10)
    country = models.ForeignKey(Country)

    def __str__(self):
        return "%s %s (%s)" % (self.LEAGUES[self.league][1], self.relay, self.country)  # pylint: disable=invalid-sequence-index


class Player(models.Model):
    POSITIONS = (
        ("TW", "Torwart"),
        ("LIB", "Libero"),
        ("LV", "Linker Verteidiger"),
        ("LMD", "Linker Manndecker"),
        ("RMD", "Rechter Manndecker"),
        ("RV", "Rechter Verteidiger"),
        ("VS", "Vorstopper"),
        ("LM", "Linkes Mittelfeld"),
        ("DM", "Defensives Mittelfeld"),
        ("ZM", "Zentrales Mittelfeld"),
        ("RM", "Rechtes Mittelfeld"),
        ("LS", "Linker Stürmer"),
        ("MS", "Mittelstürmer"),
        ("RS", "Rechter Stürmer")
    )

    name = models.CharField(max_length=200)
    position = models.CharField(max_length=3, choices=POSITIONS)
    nationality = models.ForeignKey(Country, blank=True, null=True)
    birth_season = models.ForeignKey(Season)

    def get_position(self):
        return dict(self.POSITIONS).get(self.position)

    def get_absolute_url(self):
        return reverse('core:ofm:player_detail', args=[str(self.id)])

    def __str__(self):
        return self.name


class PlayerStatistics(models.Model):
    class Meta:
        verbose_name_plural = "Player statistics"
        ordering = ['player', '-matchday']

    player = models.ForeignKey(Player, related_name='statistics')
    matchday = models.ForeignKey(Matchday, related_name='player_statistics')

    ep = models.IntegerField(default=0)
    tp = models.IntegerField(default=0)
    awp = models.IntegerField(default=0)
    strength = models.IntegerField(default=1)
    freshness = models.IntegerField(default=0)
    games_in_season = models.IntegerField(default=0)
    goals_in_season = models.IntegerField(default=0)
    won_tacklings_in_season = models.IntegerField(default=0)
    lost_tacklings_in_season = models.IntegerField(default=0)
    won_friendly_tacklings_in_season = models.IntegerField(default=0)
    lost_friendly_tacklings_in_season = models.IntegerField(default=0)
    yellow_cards_in_season = models.IntegerField(default=0)
    red_cards_in_season = models.IntegerField(default=0)
    equity = models.IntegerField(default=0)

    @property
    def age(self):
        return self.matchday.season.number - self.player.birth_season.number

    def __str__(self):
        return "%s/%s: %s" % (self.matchday.season.number, self.matchday.number, self.player.name)


class Contract(models.Model):
    class Meta:
        ordering = ['user', 'player']

    player = models.ForeignKey(Player)
    user = models.ForeignKey(OFMUser)
    bought_on_matchday = models.ForeignKey(Matchday, related_name='bought_players')
    sold_on_matchday = models.ForeignKey(Matchday, blank=True, null=True, related_name='sold_players')

    def __str__(self):
        return "%s: %s" % (self.user.username, self.player.name)


class IterMixin(object):
    def __iter__(self):
        for attr, value in self.__dict__.items():
            if not attr.startswith('_'):
                yield attr, value


class Finance(models.Model, IterMixin):  # pylint: disable=too-many-instance-attributes
    class Meta:
        ordering = ['user', '-matchday']
        unique_together = (('user', 'matchday'),)

    user = models.ForeignKey(OFMUser)
    matchday = models.ForeignKey(Matchday)

    balance = models.IntegerField(default=0)

    income_visitors_league = models.IntegerField(default=0)
    income_sponsoring = models.IntegerField(default=0)
    income_cup = models.IntegerField(default=0)
    income_interests = models.IntegerField(default=0)
    income_loan = models.IntegerField(default=0)
    income_transfer = models.IntegerField(default=0)
    income_visitors_friendlies = models.IntegerField(default=0)
    income_friendlies = models.IntegerField(default=0)
    income_funcup = models.IntegerField(default=0)
    income_betting = models.IntegerField(default=0)

    expenses_player_salaries = models.IntegerField(default=0)
    expenses_stadium = models.IntegerField(default=0)
    expenses_youth = models.IntegerField(default=0)
    expenses_interests = models.IntegerField(default=0)
    expenses_trainings = models.IntegerField(default=0)
    expenses_transfer = models.IntegerField(default=0)
    expenses_compensation = models.IntegerField(default=0)
    expenses_friendlies = models.IntegerField(default=0)
    expenses_funcup = models.IntegerField(default=0)
    expenses_betting = models.IntegerField(default=0)

    def __str__(self):
        return "%s (%s): %s" % (self.user.username, self.matchday, self.balance)

    def diff(self, ot_finance):
        f = Finance()
        f.income_visitors_league = abs(self.income_visitors_league - ot_finance.income_visitors_league)
        f.income_sponsoring = abs(self.income_sponsoring - ot_finance.income_sponsoring)
        f.income_cup = abs(self.income_cup - ot_finance.income_cup)
        f.income_interests = abs(self.income_interests - ot_finance.income_interests)
        f.income_loan = abs(self.income_loan - ot_finance.income_loan)
        f.income_transfer = abs(self.income_transfer - ot_finance.income_transfer)
        f.income_visitors_friendlies = abs(self.income_visitors_friendlies - ot_finance.income_visitors_friendlies)
        f.income_funcup = abs(self.income_funcup - ot_finance.income_funcup)
        f.income_betting = abs(self.income_betting - ot_finance.income_betting)

        f.expenses_player_salaries = -abs(self.expenses_player_salaries - ot_finance.expenses_player_salaries)
        f.expenses_stadium = -abs(self.expenses_stadium - ot_finance.expenses_stadium)
        f.expenses_youth = -abs(self.expenses_youth - ot_finance.expenses_youth)
        f.expenses_interests = -abs(self.expenses_interests - ot_finance.expenses_interests)
        f.expenses_trainings = -abs(self.expenses_trainings - ot_finance.expenses_trainings)
        f.expenses_transfer = -abs(self.expenses_transfer - ot_finance.expenses_transfer)
        f.expenses_compensation = -abs(self.expenses_compensation - ot_finance.expenses_compensation)
        f.expenses_friendlies = -abs(self.expenses_friendlies - ot_finance.expenses_friendlies)
        f.expenses_funcup = -abs(self.expenses_funcup - ot_finance.expenses_funcup)
        f.expenses_betting = -abs(self.expenses_betting - ot_finance.expenses_betting)
        return f

    def income(self):
        my_finances_dict = Counter(dict(self))
        incomes = [value for key, value in my_finances_dict.items() if key.startswith('income')]
        return sum(incomes)

    def expenses(self):
        my_finances_dict = Counter(dict(self))
        incomes = [value for key, value in my_finances_dict.items() if key.startswith('expenses')]
        return sum(incomes)


class MatchTeamStatistics(models.Model):
    class Meta:
        verbose_name_plural = "MatchTeamStatistics"

    team_name = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    strength = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    ball_possession = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    chances = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)


class Match(models.Model):
    class Meta:
        ordering = ['user', '-matchday']
        verbose_name_plural = "Matches"

    MATCHTYPE = (
        ("L", "Liga"),
        ("F", "Friendly"),
        ("P", "Pokal"),
        ("F", "Fun-Cup"),
    )

    user = models.ForeignKey(OFMUser)
    matchday = models.ForeignKey(Matchday, related_name='matches')
    match_type = models.CharField(max_length=1, choices=MATCHTYPE, default='L')
    is_home_match = models.BooleanField()
    venue = models.CharField(max_length=200)  # should this be in MatchStadiumStatistics?
    home_team_statistics = models.ForeignKey(MatchTeamStatistics, related_name='matches_as_home_team')
    guest_team_statistics = models.ForeignKey(MatchTeamStatistics, related_name='matches_as_guest_team')

    @property
    def is_won(self):
        if self.is_home_match:
            return self.home_team_statistics.score > self.guest_team_statistics.score
        else:
            return self.home_team_statistics.score < self.guest_team_statistics.score

    @property
    def is_draw(self):
        return self.home_team_statistics.score == self.guest_team_statistics.score and not self.is_in_future

    @property
    def is_lost(self):
        if self.is_home_match:
            return self.home_team_statistics.score < self.guest_team_statistics.score
        else:
            return self.home_team_statistics.score > self.guest_team_statistics.score

    @property
    def is_in_future(self):
        return self.home_team_statistics.score == 0 and self.guest_team_statistics.score == 0 and not self.venue

    @property
    def harmonic_strength(self):
        return 2 * self.home_team_statistics.strength * self.guest_team_statistics.strength / \
               (self.home_team_statistics.strength + self.guest_team_statistics.strength)

    def __str__(self):
        return "(%s) %s:%s - %s:%s" % (self.matchday,
                                       self.home_team_statistics.team_name, self.guest_team_statistics.team_name,
                                       self.home_team_statistics.score, self.guest_team_statistics.score
                                       )


class StadiumLevelItem(models.Model):
    class Meta:
        ordering = ['-current_level', '-value', '-daily_costs']

    current_level = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    daily_costs = models.IntegerField(default=0)

    def __str__(self):
        return "%s - %s - %s" % (self.current_level, self.value, self.daily_costs)


class StadiumLevel(models.Model):
    light = models.ForeignKey(StadiumLevelItem, related_name="stadium_levels_light")
    screen = models.ForeignKey(StadiumLevelItem, related_name="stadium_levels_screen")
    security = models.ForeignKey(StadiumLevelItem, related_name="stadium_levels_security")
    parking = models.ForeignKey(StadiumLevelItem, related_name="stadium_levels_parking")

    def __str__(self):
        return "light: %s / screen: %s / security: %s / parking: %s" % (
            self.light, self.screen, self.security, self.parking)


# will only be created, if home match
class MatchStadiumStatistics(models.Model):
    class Meta:
        ordering = ['match']
        verbose_name_plural = "Match stadium statistics"

    match = models.OneToOneField(Match, related_name='stadium_statistics')
    level = models.ForeignKey(StadiumLevel, related_name="stadium_statistics")

    def get_absolute_url(self):
        return reverse('core:ofm:stadium_detail', args=[str(self.id)])

    def get_configuration(self):
        config = {'light': self.level.light.current_level, 'screen': self.level.screen.current_level,
                  'security': self.level.security.current_level, 'parking': self.level.parking.current_level}

        north_stand = StadiumStandStatistics.objects.filter(stadium_statistics=self, sector='N')
        south_stand = StadiumStandStatistics.objects.filter(stadium_statistics=self, sector='S')
        west_stand = StadiumStandStatistics.objects.filter(stadium_statistics=self, sector='W')
        east_stand = StadiumStandStatistics.objects.filter(stadium_statistics=self, sector='O')
        config['north_capacity'] = north_stand[0].level.capacity if north_stand.count() > 0 else 0
        config['south_capacity'] = south_stand[0].level.capacity if south_stand.count() > 0 else 0
        config['west_capacity'] = west_stand[0].level.capacity if west_stand.count() > 0 else 0
        config['east_capacity'] = east_stand[0].level.capacity if east_stand.count() > 0 else 0
        config['north_has_seats'] = north_stand[0].level.has_seats if north_stand.count() > 0 else 0
        config['south_has_seats'] = south_stand[0].level.has_seats if south_stand.count() > 0 else 0
        config['west_has_seats'] = west_stand[0].level.has_seats if west_stand.count() > 0 else 0
        config['east_has_seats'] = east_stand[0].level.has_seats if east_stand.count() > 0 else 0
        config['north_has_roof'] = north_stand[0].level.has_roof if north_stand.count() > 0 else 0
        config['south_has_roof'] = south_stand[0].level.has_roof if south_stand.count() > 0 else 0
        config['west_has_roof'] = west_stand[0].level.has_roof if west_stand.count() > 0 else 0
        config['east_has_roof'] = east_stand[0].level.has_roof if east_stand.count() > 0 else 0

        return config

    @property
    def visitors(self):
        return StadiumStandStatistics.objects.filter(stadium_statistics=self).aggregate(Sum('visitors'))[
            'visitors__sum']

    @property
    def capacity(self):
        return StadiumStandStatistics.objects.filter(stadium_statistics=self).aggregate(Sum('level__capacity'))[
            'level__capacity__sum']

    @property
    def earnings(self):
        result = 0
        for stand in StadiumStandStatistics.objects.filter(stadium_statistics=self):
            result += stand.earnings
        return result

    @property
    def daily_costs(self):
        return self.level.light.daily_costs + self.level.screen.daily_costs + \
               self.level.security.daily_costs + self.level.parking.daily_costs

    def __str__(self):
        return "%s (%s)" % (self.match.venue, self.match.matchday)


class StandLevel(models.Model):
    capacity = models.IntegerField(default=0)
    has_roof = models.BooleanField(default=False)
    has_seats = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s - %s" % (self.capacity, self.has_roof, self.has_seats)


# always avoid alliterations.
class StadiumStandStatistics(models.Model):
    class Meta:
        verbose_name_plural = "Stadium stand statistics"

    SECTOR = (
        ("N", "Nord"),
        ("S", "Süd"),
        ("W", "West"),
        ("O", "Ost"),
    )

    def get_sector(self):
        return dict(self.SECTOR).get(self.sector)

    @property
    def earnings(self):
        return self.visitors * self.ticket_price

    stadium_statistics = models.ForeignKey(MatchStadiumStatistics, related_name="stand_statistics")
    sector = models.CharField(max_length=1, choices=SECTOR)
    visitors = models.IntegerField(default=0)
    ticket_price = models.IntegerField(default=0)
    condition = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    level = models.ForeignKey(StandLevel, related_name="stand_statistics")

    def __str__(self):
        return "%s - %s - %s" % (self.visitors, self.ticket_price, self.condition)


class Dictionary(models.Model):
    """A model that represents a dictionary. This model implements most of the dictionary interface,
    allowing it to be used like a python dictionary.

    """
    name = models.CharField(max_length=255)

    @staticmethod
    def get_dict(name):
        """Get the Dictionary of the given name.

        """
        df = Dictionary.objects.select_related().get(name=name)

        return df

    def __getitem__(self, key):
        """Returns the value of the selected key.

        """
        return self.keyvaluepair_set.get(key=key).value

    def __setitem__(self, key, value):
        """Sets the value of the given key in the Dictionary.

        """
        try:
            kvp = self.keyvaluepair_set.get(key=key)

        except KeyValuePair.DoesNotExist:
            KeyValuePair.objects.create(container=self, key=key, value=value)

        else:
            kvp.value = value
            kvp.save()

    def __delitem__(self, key):
        """Removed the given key from the Dictionary.

        """
        try:
            kvp = self.keyvaluepair_set.get(key=key)

        except KeyValuePair.DoesNotExist:
            raise KeyError

        else:
            kvp.delete()

    def __len__(self):
        """Returns the length of this Dictionary.

        """
        return self.keyvaluepair_set.count()

    def iterkeys(self):
        """Returns an iterator for the keys of this Dictionary.

        """
        return iter(kvp.key for kvp in self.keyvaluepair_set.all())

    def itervalues(self):
        """Returns an iterator for the keys of this Dictionary.

        """
        return iter(kvp.value for kvp in self.keyvaluepair_set.all())

    __iter__ = iterkeys

    def iteritems(self):
        """Returns an iterator over the tuples of this Dictionary.

        """
        return iter((kvp.key, kvp.value) for kvp in self.keyvaluepair_set.all())

    def keys(self):
        """Returns all keys in this Dictionary as a list.

        """
        return [kvp.key for kvp in self.keyvaluepair_set.all()]

    def values(self):
        """Returns all values in this Dictionary as a list.

        """
        return [kvp.value for kvp in self.keyvaluepair_set.all()]

    def items(self):
        """Get a list of tuples of key, value for the items in this Dictionary.
        This is modeled after dict.items().

        """
        return [(kvp.key, kvp.value) for kvp in self.keyvaluepair_set.all()]

    def get(self, key, default=None):
        """Gets the given key from the Dictionary. If the key does not exist, it
        returns default.

        """
        try:
            return self[key]

        except KeyError:
            return default

    def has_key(self, key):
        """Returns true if the Dictionary has the given key, false if not.

        """
        return self.contains(key)

    def contains(self, key):
        """Returns true if the Dictionary has the given key, false if not.

        """
        try:
            self.keyvaluepair_set.get(key=key)
            return True

        except KeyValuePair.DoesNotExist:
            return False

    def clear(self):
        """Deletes all keys in the Dictionary.

        """
        self.keyvaluepair_set.all().delete()

    def as_py_dict(self):
        """Get a python dictionary that represents this Dictionary object.
        This object is read-only.

        """
        field_dict = dict()

        for kvp in self.keyvaluepair_set.all():
            field_dict[kvp.key] = kvp.value

        return field_dict


class KeyValuePair(models.Model):
    """A Key-Value pair with a pointer to the Dictionary that owns it.

    """
    container = models.ForeignKey(Dictionary, db_index=True)
    key = models.IntegerField(db_index=True)
    value = models.IntegerField()


class AwpBoundaries(Dictionary):
    class Meta:
        verbose_name_plural = "AWP Boundaries"
        ordering = ['-name']

    @staticmethod
    def get_or_create_from_matchday(matchday):
        """Get the Dictionary of the given matchday.

        """
        awp_boundary, _ = AwpBoundaries.objects.get_or_create(name=AwpBoundaries._name_from_matchday(matchday))
        return awp_boundary

    @staticmethod
    def get_from_matchday(matchday):
        """Get the AWP Boundaries of the given matchday.

        """
        try:
            awp_boundaries = Dictionary.objects.select_related().get(name=AwpBoundaries._name_from_matchday(matchday))
        except Dictionary.DoesNotExist:
            awp_boundaries = AwpBoundaries.get_or_create_from_matchday(matchday)
            for i in range(26):
                awp_boundaries[i + 1] = 0
        return awp_boundaries

    @staticmethod
    def _name_from_matchday(matchday):
        if Constants.Quarters.FOURTH_QUARTER_LEVEL_UP_DAY <= matchday.number < Constants.Quarters.FIRST_QUARTER_LEVEL_UP_DAY:  # pylint: disable=line-too-long
            return 'awp_boundaries_' + str(matchday.season.number) + '_0'
        elif Constants.Quarters.FIRST_QUARTER_LEVEL_UP_DAY <= matchday.number < Constants.Quarters.SECOND_QUARTER_LEVEL_UP_DAY:  # pylint: disable=line-too-long
            return 'awp_boundaries_' + str(matchday.season.number) + '_1'
        elif Constants.Quarters.SECOND_QUARTER_LEVEL_UP_DAY <= matchday.number < Constants.Quarters.THIRD_QUARTER_LEVEL_UP_DAY:  # pylint: disable=line-too-long
            return 'awp_boundaries_' + str(matchday.season.number) + '_2'
        else:
            return 'awp_boundaries_' + str(matchday.season.number) + '_3'


class Checklist(models.Model):
    user = models.OneToOneField(OFMUser)


class ChecklistItem(models.Model):
    class Meta:
        ordering = ['priority']

    checklist = models.ForeignKey(Checklist)
    name = models.CharField(max_length=255)
    priority = models.IntegerField(default=0)
    last_checked_on_matchday = models.ForeignKey(Matchday, default=None, blank=True, null=True)
    to_be_checked_on_matchdays = models.CharField(blank=True, null=True, max_length=255,
                                                  validators=[validate_comma_separated_integer_list])
    to_be_checked_on_matchday_pattern = models.IntegerField(blank=True, null=True)
    to_be_checked_if_home_match_tomorrow = models.BooleanField(default=False)
    is_inversed = models.BooleanField(default=False)


class ParsingSetting(models.Model):  # refactor to a dictionary?
    user = models.OneToOneField(OFMUser)
    parsing_chain_includes_player_statistics = models.BooleanField(default=True)
    parsing_chain_includes_awp_boundaries = models.BooleanField(default=True)
    parsing_chain_includes_finances = models.BooleanField(default=True)
    parsing_chain_includes_matches = models.BooleanField(default=True)
    parsing_chain_includes_match_details = models.BooleanField(default=False)
    parsing_chain_includes_match_details_only_for_current_matchday = models.BooleanField(default=False)
    parsing_chain_includes_stadium_details = models.BooleanField(default=False)
    parsing_chain_includes_transfers = models.BooleanField(default=True)
