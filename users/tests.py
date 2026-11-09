from django.test import TestCase
from users.models import TelegramUser


class TelegramUserBalanceTests(TestCase):
    async def test_daily_free_seconds_are_added_only_once_per_day(self):
        user = await TelegramUser.objects.acreate(user_id=101, name="Test")

        self.assertTrue(
            await TelegramUser.check_can_we_add_daily_free_seconds(user.user_id)
        )
        self.assertFalse(
            await TelegramUser.check_can_we_add_daily_free_seconds(user.user_id)
        )

        await user.arefresh_from_db()
        self.assertEqual(user.seconds_balance, 300)

    async def test_balance_equal_to_duration_is_sufficient(self):
        user = await TelegramUser.objects.acreate(
            user_id=102,
            name="Test",
            seconds_balance=60,
        )

        self.assertFalse(await TelegramUser.not_enough_seconds(user.user_id, 60))

    async def test_balance_below_duration_is_insufficient(self):
        user = await TelegramUser.objects.acreate(
            user_id=103,
            name="Test",
            seconds_balance=59,
        )

        self.assertTrue(await TelegramUser.not_enough_seconds(user.user_id, 60))
