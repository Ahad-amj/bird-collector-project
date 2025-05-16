from django.test import TestCase

from django.test import TestCase
from django.contrib.auth.models import User
from main_app.models import Bird, Toy, Feeding, Photo
from datetime import date

class ModelsTest(TestCase):
    def setUp(self):
        # user;
        self.user = User.objects.create_user(username='testuser', password='12345')
        # toys;
        self.toy1 = Toy.objects.create(name='Mouse',   color='Gray')
        self.toy2 = Toy.objects.create(name='Ball',    color='Red')
        self.toy3 = Toy.objects.create(name='Feather', color='white')
        # bird; each related to user
        self.bird1 = Bird.objects.create(name='Felix',   breed='Tabby', description='Playful bird',   age=3, user=self.user)
        self.bird2 = Bird.objects.create(name='Whiskers',breed='Tabby', description='A playful bird.',age=5, user=self.user)
        # feeding; two related to bird1
        self.feeding1 = Feeding.objects.create(date=date(2025, 1, 1), meal='B', bird=self.bird1)
        self.feeding2 = Feeding.objects.create(date=date(2024, 1, 1), meal='L', bird=self.bird1)
        self.feeding3 = Feeding.objects.create(date=date(2023, 1, 1), meal='D', bird=self.bird2)
        # photo; each related to one bird
        self.photo1 = Photo.objects.create(bird=self.bird1, url='http://url1.com', title='First')
        self.photo2 = Photo.objects.create(bird=self.bird2, url='http://url2.com', title='First')
        # relate toy1 and toy2 to bird
        self.bird1.toys.set([self.toy1, self.toy2])

    # TESTS
    # tests start with "test_"
    # example

    def test_user_create(self):
        self.assertEqual(str(self.user), 'testuser')
    
    def test_bird_create(self):
        self.assertEqual(str(self.bird1), 'Felix')
        self.assertEqual(str(self.bird2), 'Whiskers')

    def test_toy_create(self):
        self.assertEqual(str(self.toy1), 'Mouse')
        self.assertEqual(str(self.toy2), 'Ball')
        self.assertEqual(str(self.toy3), 'Feather')

    def test_feeding_create(self):
        self.assertEqual(str(self.feeding1), 'B')
        self.assertEqual(str(self.feeding2), 'L')
        self.assertEqual(str(self.feeding3), 'D')

    def test_photo_create(self):
        self.assertEqual(str(self.photo1), 'http://url1.com')
        self.assertEqual(str(self.photo2), 'http://url2.com')

    def test_bird_toys_relationship(self):
        self.assertEqual(self.bird1.toys.count(), 2)
        self.assertIn(self.toy1, self.bird1.toys.all())
        self.assertIn(self.toy2, self.bird1.toys.all())

    def test_bird_user_relationship(self):
        self.assertEqual(self.bird1.user.username, 'testuser')

    def test_bird_feeding_relationship(self):
        self.assertEqual(self.feeding1.bird, self.bird1)
        self.assertEqual(self.feeding1.meal, 'B')
        self.assertEqual(self.feeding2.bird, self.bird1)
        self.assertEqual(self.feeding2.meal, 'L')
        self.assertEqual(self.feeding3.bird, self.bird2)
        self.assertEqual(self.feeding3.meal, 'D')

    def test_bird_photo_relationship(self):
        self.assertEqual(self.photo1.bird, self.bird1)
        self.assertEqual(self.photo2.bird, self.bird2)

    # -------------------
    # Model Methods / Ordering
    # -------------------
    
    def test_feeding_ordering(self):
        # check bird1 feedings in order
        feedings = Feeding.objects.filter(bird=self.bird1.id)
        self.assertEqual(feedings[0].date, date(2025, 1, 1))
        self.assertEqual(feedings[1].date, date(2024, 1, 1))

        # check all feedings
        all_feedings = Feeding.objects.all()
        self.assertEqual(all_feedings[0].date, date(2025, 1, 1))
        self.assertEqual(all_feedings[1].date, date(2024, 1, 1))
        self.assertEqual(all_feedings[2].date, date(2023, 1, 1))

    def test_deleting_user_cascades_to_bird(self):
        self.user.delete()
        self.assertEqual(Bird.objects.count(), 0)

    # bird2 had ONE feeding => should still be two in database related to bird1!
    def test_deleting_bird_cascades_to_feedings(self):
        self.bird2.delete()
        self.assertEqual(Feeding.objects.count(), 2)
        # 2 represent the left feeding for birds which is bird1

    # bird1 had one photo out of two => 1 left over!
    def test_deleting_bird_cascades_to_photo(self):
        self.bird1.delete()
        self.assertEqual(Photo.objects.count(), 1)
