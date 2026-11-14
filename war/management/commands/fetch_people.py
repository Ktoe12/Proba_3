import asyncio
import aiohttp
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from war.models import Person

BASE_URL = "https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net"


# Funcție asincronă pentru a salva în baza de date Django
@sync_to_async
def save_person_to_db(person_dict):
    # Presupunem că numele vine sub cheia 'name' sau 'Name'
    name = person_dict.get('name', person_dict.get('Name', 'Unknown'))
    person, created = Person.objects.update_or_create(
        name=name,
        defaults={'raw_data': person_dict}
    )
    return person


class Command(BaseCommand):
    help = "Extrage datele asincron de la API și îl caută pe Hellstorm Fireburn"

    def handle(self, *args, **options):
        self.stdout.write("Începem procesul de drafting asincron...")
        asyncio.run(self.process_api())

    async def fetch_person_details(self, session, url, semaphore):
        # Folosim un semafor pentru a nu supraîncărca serverul dintr-o dată (ex: max 50 requesturi simultane)
        async with semaphore:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.stderr.write(f"Eroare {response.status} la {url}")
                    return None

    async def process_api(self):
        async with aiohttp.ClientSession() as session:
            self.stdout.write(f"Interogăm endpoint-ul principal: {BASE_URL}/people")
            async with session.get(f"{BASE_URL}/people") as response:
                if response.status != 200:
                    self.stderr.write(f"Nu am putut accesa /people. Status: {response.status}")
                    return

                data = await response.json()

            # --- DEBUG ȘI EXTRAGERE ---
            self.stdout.write(f"Tipul datelor primite: {type(data)}")

            if isinstance(data, dict):
                self.stdout.write(f"Am primit un dicționar cu cheile: {list(data.keys())}")
                # Extragem automat prima listă găsită în dicționar
                for key in data.keys():
                    if isinstance(data[key], list):
                        data = data[key]
                        self.stdout.write(f"Am extras lista din cheia '{key}'")
                        break

            self.stdout.write(f"Exemplu date extrase: {str(data)[:150]}...")
            # --------------------------

            people_data = []

            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                self.stdout.write("Am primit obiectele direct. Le procesăm...")
                people_data = data

            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
                self.stdout.write(f"Am primit o listă de {len(data)} referințe. Începem interogarea paralelă...")
                semaphore = asyncio.Semaphore(100)

                tasks = []
                for item in data:
                    url = f"{BASE_URL}{item}" if item.startswith('/') else f"{BASE_URL}/people/{item}"
                    tasks.append(self.fetch_person_details(session, url, semaphore))

                results = await asyncio.gather(*tasks)
                people_data = [res for res in results if res is not None]
            else:
                self.stdout.write(
                    self.style.ERROR("Eroare: Formatul datelor tot nu a putut fi procesat. Vezi exemplul de mai sus."))

            # Salvăm în baza de date și îl căutăm pe Hellstorm
            self.stdout.write("Salvăm datele în baza de date...")
            hellstorm_found = False

            for p_data in people_data:
                await save_person_to_db(p_data)
                name = p_data.get('name', p_data.get('Name', ''))

                if "Hellstorm" in name or "Fireburn" in name:
                    self.stdout.write(self.style.SUCCESS(f"\n[!!!] L-AM GĂSIT PE HELLSTORM FIREBURN!"))
                    self.stdout.write(str(p_data))

                    # Extragem cheia (orice cheie care nu e 'name' sau atribute standard)
                    for key, value in p_data.items():
                        if key.lower() not in ['name', 'type', 'health', 'attackpoints', 'profileimagelink']:
                            self.stdout.write(self.style.SUCCESS(f"Cheia secretă găsită pare a fi: {key} -> {value}"))
                            self.stdout.write(
                                self.style.WARNING(f"Instrucțiuni ascunse cel mai probabil la: {BASE_URL}/{value}"))
                    hellstorm_found = True

            if not hellstorm_found:
                self.stdout.write(self.style.ERROR("\nNu l-am găsit pe Hellstorm. Verifică output-ul de debug."))
            else:
                self.stdout.write("\nProcesare finalizată cu succes.")