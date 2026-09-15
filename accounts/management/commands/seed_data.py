from django.core.management.base import BaseCommand
from accounts.models import User
from menu.models import Category, MenuItem, AddOn
from rewards.models import Reward, Nostalgia
from wallet.models import WalletItem


class Command(BaseCommand):
    help = "Seed initial demo data: 1 admin user + sample menu items + sample rewards."

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", email="admin@example.com", password="AdminPass123"
            )
            self.stdout.write(self.style.SUCCESS("Admin user created -> username: admin / password: AdminPass123"))
        else:
            self.stdout.write("Admin user already exists.")

        starters, _ = Category.objects.get_or_create(name="Starters")
        mains, _ = Category.objects.get_or_create(name="Main Course")
        beverages, _ = Category.objects.get_or_create(name="Beverages")

        paneer_tikka, _ = MenuItem.objects.get_or_create(
            name="Paneer Tikka", category=starters, price=180,
            defaults={"description": "Grilled cottage cheese with spices"}
        )
        butter_chicken, _ = MenuItem.objects.get_or_create(
            name="Butter Chicken", category=mains, price=320,
            defaults={"description": "Classic creamy tomato curry"}
        )
        masala_chai, _ = MenuItem.objects.get_or_create(
            name="Masala Chai", category=beverages, price=40,
            defaults={"description": "Hot Indian spiced tea"}
        )

        # Add-ons — like Zomato/Swiggy, customers can add extras to items and the price updates automatically
        extra_cheese, _ = AddOn.objects.get_or_create(name="Extra Cheese", defaults={"price": 30})
        extra_cheese.applicable_items.add(paneer_tikka, butter_chicken)

        extra_gravy, _ = AddOn.objects.get_or_create(name="Extra Gravy", defaults={"price": 40})
        extra_gravy.applicable_items.add(butter_chicken)

        extra_sugar, _ = AddOn.objects.get_or_create(name="Extra Sugar", defaults={"price": 5})
        extra_sugar.applicable_items.add(masala_chai)

        Reward.objects.get_or_create(cards=1, code="R100", reward="₹100 Cashback")
        Reward.objects.get_or_create(cards=2, code="R200", reward="Free Dessert")
        Reward.objects.get_or_create(cards=3, code="R300", reward="20% Off Next Order")

        Nostalgia.objects.get_or_create(
            title="90s Kid", story="Remember waiting all week for your favourite Doordarshan show on Sunday?"
        )
        Nostalgia.objects.get_or_create(
            title="School Canteen Days", story="Ten rupees for a samosa and cutting chai — those were the golden days."
        )

        WalletItem.objects.get_or_create(
            name="Free Chai", points_required=1000,
            defaults={"description": "One free Masala Chai on your next visit"}
        )
        WalletItem.objects.get_or_create(
            name="Free Dessert", points_required=1500,
            defaults={"description": "Any one dessert, free"}
        )
        WalletItem.objects.get_or_create(
            name="₹200 Off Coupon", points_required=2000,
            defaults={"description": "₹200 off on your next order"}
        )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
