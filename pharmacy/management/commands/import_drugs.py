import requests
from django.core.management.base import BaseCommand
from pharmacy.models import Drug
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def summarize_text(text, sentences_count=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return " ".join(str(sentence) for sentence in summary)

POPULAR_DRUGS = [
    "Acetaminophen", "Hydrocodone", "Albuterol", "Alendronate", "Allopurinol", "Alprazolam", "Amoxicillin", "Amoxicillin/Clavulanate", "Amphetamine/Dextroamphetamine", "Amlodipine", "Aripiprazole", "Atenolol", "Atorvastatin", "Azithromycin", "Baclofen", "Benazepril", "Bisoprolol", "Bupropion", "Buspirone", "Butalbital/Acetaminophen/Caffeine", "Buprenorphine/Naloxone", "Captopril", "Carvedilol", "Cefdinir", "Cefuroxime", "Celecoxib", "Cetirizine", "Ciprofloxacin", "Citalopram", "Clindamycin", "Clonazepam", "Clopidogrel", "Cyclobenzaprine", "Dapagliflozin", "Desvenlafaxine", "Diazepam", "Diclofenac", "Dicyclomine", "Digoxin", "Diltiazem", "Diphenhydramine", "Divalproex", "Doxycycline", "Dulaglutide", "Enalapril", "Escitalopram", "Esomeprazole", "Estradiol", "Eszopiclone", "Fentanyl", "Fexofenadine", "Finasteride", "Fluconazole", "Fluoxetine", "Fluticasone", "Fluticasone/Salmeterol", "Gabapentin", "Gemfibrozil", "Glimepiride", "Glipizide", "Hydrochlorothiazide", "Hydrocodone/Acetaminophen", "Hydroxychloroquine", "Ibuprofen", "Insulin Aspart", "Insulin Detemir", "Insulin Glargine", "Insulin Lispro", "Ipratropium/Albuterol", "Isosorbide Mononitrate", "Lamotrigine", "Lansoprazole", "Levetiracetam", "Levothyroxine", "Lisinopril", "Lorazepam", "Losartan", "Lovastatin", "Lurasidone", "Meloxicam", "Memantine", "Metformin", "Methadone", "Methocarbamol", "Methylphenidate", "Metoprolol", "Metronidazole", "Mirtazapine", "Montelukast", "Naproxen", "Nitroglycerin", "Nortriptyline", "Omeprazole", "Ondansetron", "Oxycodone", "Oxycodone/Acetaminophen", "Pantoprazole", "Paroxetine", "Penicillin", "Phenytoin", "Pioglitazone", "Prednisone", "Pregabalin", "Promethazine", "Propranolol", "Quetiapine", "Rabeprazole", "Ranitidine", "Risperidone", "Rosuvastatin", "Sertraline", "Sildenafil", "Simvastatin", "Sitagliptin", "Spironolactone", "Tamsulosin", "Temazepam", "Terazosin", "Tizanidine", "Topiramate", "Tramadol", "Trazodone", "Triamterene/Hydrochlorothiazide", "Valsartan", "Venlafaxine", "Verapamil", "Warfarin", "Zaleplon", "Zolpidem", "Zolmitriptan",
]
class Command(BaseCommand):
    help = 'Import drugs from OpenFDA API'

    def handle(self, *args, **kwargs):
        for drug_name in POPULAR_DRUGS:
            self.stdout.write(f"Processing: {drug_name}")
            try:
                response = requests.get(
                    "https://api.fda.gov/drug/label.json",
                    params={
                        "search": f'openfda.generic_name:"{drug_name}"',
                        "limit": 1
                    },
                    timeout=10
                )
                response.raise_for_status()
                results = response.json().get("results", [])
                if not results:
                    self.stdout.write(f"No data found for {drug_name}")
                    continue
                data = results[0]
                openfda = data.get("openfda", {})
            
                name = openfda.get('generic_name', [None])[0]
                brand = openfda.get('brand_name', [None])[0]
                route = openfda.get('route', [None])[0]
                description = data.get("description", [""])[0]
                dosage = data.get("dosage_and_administration", [""])[0]
                summary_description = summarize_text(description, sentences_count=3)
                summary_dosage = summarize_text(dosage, sentences_count=3)

                Drug.objects.create(
                    name=name,
                    brand=brand,
                    route=route,
                    description=summary_description, 
                    dosage=summary_dosage
                )
                self.stdout.write(self.style.SUCCESS(f"Added drug: {name}"))
            except requests.RequestException as e:
                self.stderr.write(f"Request error for {drug_name}: {e}")
            except Exception as e:
                self.stderr.write(f"Error processing {drug_name}: {e}")