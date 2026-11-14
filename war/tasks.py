import requests
from celery import shared_task
from .models import Person

BASE_URL = "https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net"


# Setăm politica de Retry pentru orice eroare (ex: timeout),
# reîncercând de max 5 ori, crescând timpul între încercări (backoff)
@shared_task(bind=True, max_retries=5, autoretry_for=(Exception,), retry_backoff=True)
def process_draft_batch(self, batch_path):
    url = f"{BASE_URL}{batch_path}"
    print(f"[TASK START] Fetching batch from: {url}")

    # 1. Extragem datele cu timeout de 10 secunde
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Aruncă excepție (prinsă de Celery retry) dacă statusul nu e 200

    data = response.json()
    people_list = []
    next_batch_val = None

    # 2. Extragem robust datele
    if isinstance(data, dict):
        # API-ul pune probabil oamenii într-o cheie ('data', 'results' etc)
        for key, value in data.items():
            if isinstance(value, list):
                people_list = value

        # Conform instrucțiunilor: "the next attribute x as /draft/x"
        next_batch_val = data.get('x') or data.get('next')
    elif isinstance(data, list):
        people_list = data

    # 3. Procesăm draft-ul (adăugăm rank)
    for p_data in people_list:
        name = p_data.get('name', p_data.get('Name', ''))
        rank = p_data.get('rank', p_data.get('Rank', 'Private'))

        person = Person.objects.filter(name=name).first()
        if person:
            person.rank = rank

            # Verificăm din nou surpriza ascunsă de la Hellstorm
            if "Hellstorm" in name or "Fireburn" in name:
                print("\n=================================================")
                print(f"[!!!] HELLSTORM DRAFTED! Date noi:")
                print(p_data)
                for k, v in p_data.items():
                    if k.lower() not in ['name', 'id', 'age', 'rank']:
                        print(f"-> CHEIA NOUĂ PARE SĂ FIE: {k} = {v}")
                print("=================================================\n")

            person.save()

    print(f"[TASK DONE] Procesat {len(people_list)} persoane.")

    # 4. Declanșăm următorul batch asincron
    if next_batch_val is not None:
        next_path = f"/draft/{next_batch_val}"
        print(f"Lansăm background task pentru următorul batch: {next_path}")
        process_draft_batch.delay(next_path)
    else:
        print("[FINAL] Nu mai există alte batch-uri. Draft-ul s-a încheiat!")