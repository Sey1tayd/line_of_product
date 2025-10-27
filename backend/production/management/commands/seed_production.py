from django.core.management.base import BaseCommand
from production.models import Machine, ToolType


MACHINES_WITH_TOOLS = [
    {
        "name": "Testere",
        "short_name": "Testere",
        "order_in_line": 1,
        "tools": [
            "Testere",
        ],
    },
    {
        "name": "Altıköşe Robot",
        "short_name": "Altıköşe",
        "order_in_line": 2,
        "tools": [
            "Kanal 1 - Takım 1",
            "Kanal 1 - Takım 2",
            "Kanal 2 - Takım 1",
        ],
    },
    {
        "name": "Yargı",
        "short_name": "Yargı",
        "order_in_line": 3,
        "tools": [
            "Kesme Çakısı",
        ],
    },
    {
        "name": "İç Yiv",
        "short_name": "İç Yiv",
        "order_in_line": 4,
        "tools": [
            "Klavuz",
        ],
    },
    {
        "name": "Angelina",
        "short_name": "Angelina",
        "order_in_line": 5,
        "tools": [
            "Yüzey Elması",
            "Dış Elması",
        ],
    },
    {
        "name": "Fanuc",
        "short_name": "Fanuc",
        "order_in_line": 6,
        "tools": [
            "Yüzey Elması",
            "Dış Elması",
        ],
    },
]


class Command(BaseCommand):
    help = "Seeds production machines and related tool types (idempotent)."

    def handle(self, *args, **options):
        created_or_updated = 0
        tooltype_created = 0

        for spec in MACHINES_WITH_TOOLS:
            machine, _ = Machine.objects.update_or_create(
                name=spec["name"],
                defaults={
                    "short_name": spec["short_name"],
                    "order_in_line": spec["order_in_line"],
                    "is_active": True,
                },
            )
            created_or_updated += 1

            existing_names = set(
                ToolType.objects.filter(machine=machine).values_list("name", flat=True)
            )
            for tool_name in spec["tools"]:
                if tool_name not in existing_names:
                    ToolType.objects.create(machine=machine, name=tool_name, is_active=True)
                    tooltype_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completed. Machines upserted: {created_or_updated}, ToolTypes created: {tooltype_created}."
            )
        )


