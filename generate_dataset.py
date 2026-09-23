import csv
import random

# ─────────────────────────────────────────────────────────────────
# WORDLISTS
# ─────────────────────────────────────────────────────────────────

names_male   = ["Ramu", "Srinu", "Babai", "Chitti", "Venky", "Bunny", "Gopi",
                "Suresh", "Naidu", "Ravi", "Kiran", "Arjun", "Sekhar", "Prasad",
                "Mahesh", "Naveen", "Rajesh", "Sai", "Teja", "Vikram", "Yadav",
                "Bhaskar", "Nani", "Lucky", "Surya"]
names_female = ["Lakshmi", "Suma", "Priya", "Divya", "Sravani", "Mounika",
                "Kavya", "Swathi", "Anu", "Bhavana", "Deepika", "Haritha",
                "Indu", "Jyothi", "Keerthi"]
places       = ["Hyderabad", "Vijayawada", "Guntur", "Vizag", "Tirupati",
                "Warangal", "Nellore", "Karimnagar", "Kurnool", "Rajahmundry"]
colleges     = ["college", "university", "hostel", "mess", "canteen",
                "library", "exam hall", "lab", "seminar hall", "placement cell"]
subjects     = ["maths", "physics", "DBMS", "OS", "DSA", "networks",
                "chemistry", "English", "ML", "algorithms", "CN", "TOC"]
foods        = ["idli", "dosa", "biryani", "pulihora", "pesarattu", "upma",
                "vada", "sambar", "pongal", "gongura rice", "chicken curry",
                "egg rice", "roti", "chapati"]
vehicles     = ["bike", "bus", "auto", "RTC bus", "share auto", "cycle",
                "Activa", "Splendor"]
tollywood    = ["Pawan Kalyan", "Mahesh Babu", "Allu Arjun", "NTR", 
                "Chiranjeevi", "Balayya", "Prabhas", "Vijay Deverakonda"]
apps         = ["Swiggy", "Zomato", "PhonePe", "GPay", "Instagram",
                "YouTube", "WhatsApp", "Hotstar"]
emotions     = ["happy", "sad", "shocked", "confused", "tensed", "nervous",
                "proud", "embarrassed"]
jobs         = ["software engineer", "doctor", "IAS officer", "teacher",
                "data scientist", "CA", "pilot", "engineer"]

# ─────────────────────────────────────────────────────────────────
# SPELLING VARIANTS  (the key to authentic Tenglish feel)
# ─────────────────────────────────────────────────────────────────

variants = {
    "nuvvu"    : ["nuvvu","nuvu","nuwu","nuvvuu"],
    "cheppadu" : ["cheppadu","chepadu","cheppdu","chepdu","cheppadu"],
    "ekkada"   : ["ekkada","ekkado","ekada","ekado","ekkadaa"],
    "ledu"     : ["ledu","edu","ledhu","laedu","leduu"],
    "undi"     : ["undi","undie","undhi","undy","undii"],
    "bro"      : ["bro","broo","brow","broh","brooo"],
    "ayya"     : ["ayya","aya","ayyaa","ayaa"],
    "chala"    : ["chala","challa","chaala","chaalaa","challaa"],
    "anukunta" : ["anukunta","anukuntaa","anukunde","anukuntunna"],
    "avunu"    : ["avunu","avnu","avvunu","avunuu","avunuu"],
    "kaadu"    : ["kaadu","kadu","kaadhu","kaaduu"],
    "yemaina"  : ["yemaina","emaina","yemina","emina","yemaindi"],
    "okka"     : ["okka","oka","okkka","okaa"],
    "meeru"    : ["meeru","miru","meeru","meru"],
    "ra"       : ["ra","raa","raa","da","daa"],
    "adi"      : ["adi","adii","adhi","adi"],
    "ante"     : ["ante","antee","anti","antey"],
    "cheyyadam": ["cheyyadam","cheyyatam","cheyyadham","cheyydam"],
    "telugu"   : ["telugu","Telugu","telgu","teluguu"],
    "amma"     : ["amma","ammaa","amma","ammaaa"],
    "nanna"    : ["nanna","nannaa","nanna","nanaa"],
    "vasindi"  : ["vasindi","vasindhi","vasindy","vasindii"],
    "chusaka"  : ["chusaka","chusaaka","chusaka","chooska"],
    "poindi"   : ["poindi","poindhi","poindy","poindii"],
    "chesadu"  : ["chesadu","chesadhu","chesdu","chesaadu"],
}

laughs   = ["lol", "lmao", "haha", "😂", "🤣", "💀", "😭😭", "gg", "bruh"]
cries    = ["😭", "😭😭", "rip", "F", "💔", "gone case", "finished"]
shocks   = ["wait what", "bro what", "excuse me", "seriously??", "no way"]
neutral_emojis = ["👍", "🙏", "🙂", "ok", "🤔", "cool", "hmm", "right", "sure", "👍👍", "🙌"]

def v(w):   return random.choice(variants.get(w, [w]))
def p(lst): return random.choice(lst)
def laugh(prob=0.6): return p(laughs) if random.random() < prob else ""
def cry(prob=0.5):   return p(cries)  if random.random() < prob else ""
def neut(prob=0.5):  return p(neutral_emojis) if random.random() < prob else ""
def maybe(w, prob=0.4): return w if random.random() < prob else ""

# ─────────────────────────────────────────────────────────────────
# HUMOROUS GENERATORS  (6 distinct categories × ~12 templates each)
# ─────────────────────────────────────────────────────────────────

def joke_college():
    name = p(names_male); sub = p(subjects); col = p(colleges)
    bank = [
        f"{name} {v('bro')} exam ki prepare {v('ledu')}, result vasthe 'paper tough {v('undi')}' ani blame chesadu {laugh()}",
        f"naa {sub} paper lo {v('okka')} question {v('kaadu')} telivindi, kani confident ga {v('avunu')} rasa — confidence bro not knowledge {laugh()}",
        f"{name} {col} lo attendance {v('ledu')} {v('bro')}, but {v('amma')} tho 'daily velthunna' antadu — technically {v('ledu')} {laugh()}",
        f"professor 'open book exam' {v('ante')} {name} library motham bag lo pettukochadu {laugh(0.8)}",
        f"naa {sub} marks chusaka {v('okka')} nimisham silent ga {v('undi')}, grief {v('kaadu')} {v('bro')} — pure shock",
        f"{name} assignment last minute chesadu, font 16, margins wide, 3 pages done — engineering genius {laugh()}",
        f"exam lo {name} pray chesadu 'God MCQ lo A avvani {v('cheyyadam')}' — specific prayer works {laugh(0.7)}",
        f"naa {sub} professor {v('chala')} fast {v('bro')}, notes {v('ledu')}, brain {v('ledu')}, hope {v('ledu')}, future {v('ledu')} {cry()}",
        f"{name} back bench lo {v('undi')} kani first bencher kanna better marks — back lo wifi strong {v('undi')} {laugh()}",
        f"internals lo {name} ki 9/30 vasthe 'grace marks' antadu, grace means 9 ye {v('bro')} {laugh(0.8)}",
        f"placement cell lo HR adugadu 'where do you see yourself in 5 years', {name} 'sleeping' annadu — honest answer {laugh()}",
        f"college {col} lo {sub} class {v('ledu')} today {v('ante')} {name} {v('amma')} ki call chesadu 'holiday' ani — smart move {laugh()}",
    ]
    return p(bank)

def joke_family():
    name = p(names_male); food = p(foods); place = p(places)
    bank = [
        f"{v('amma')} cheppindi 'doctor avutav' ani, naa {p(subjects)} marks chusaka 'compounder avvachu' ani update chesindi {laugh()}",
        f"{v('nanna')} smartphone istE WhatsApp lo naa result forward chesadu relatives ki — thanks {v('nanna')} {cry()}",
        f"{v('amma')}: {v('nuvvu')} {v('ekkada')} unnav? nenu: library lo. {v('amma')}: mee college lo library {v('ekkada')} {v('undi')} ra? caught {laugh()}",
        f"{v('nanna')} 'maa time lo {v('chala')} {v('cheyyadam')} kashtapaddamu' {v('ante')}, aatime lo {p(subjects)} {v('ledu')} {v('bro')} — different struggle",
        f"{v('amma')} {food} chesindi, nenu '{v('chala')} {v('undi')}' annanu — {v('ledu')}, pure diplomacy {v('bro')} {laugh(0.5)}",
        f"{v('nanna')} bike ki petrol {v('ledu')}, naaku pocket money {v('ledu')}, iddaru same team {cry()}",
        f"{v('amma')} WhatsApp status 'my son is my pride' pettindi, naa result {v('vasindi')} — delete {v('chesadu')} {laugh()}",
        f"babai cheppadu '{name} ni chuso {v('chala')} {v('undi')}' — {name} fail {v('avunu')} {v('bro')}, different level inspiration {laugh(0.6)}",
        f"relatives adugutunnaru 'what are your plans' ani, nenu {p(subjects)} pass avvadam plan {v('bro')} — small goals {laugh()}",
        f"{v('amma')} 'oka {p(jobs)} ni chadi, set avutav' {v('ante')}, nenu still {p(subjects)} clear cheyyalekapotunna {cry()}",
        f"family function lo {v('okka')} uncle adugadu 'marks entha' ani — {v('nanna')} topic change chesadu immediately {laugh()}",
        f"{v('amma')} cooking chesthu {v('undi')}, nenu help cheyyadam try chesanu — {v('amma')} 'nuvvu poni chadduvuko' annadi {laugh(0.7)}",
    ]
    return p(bank)

def joke_sarcasm():
    app = p(apps); place = p(places); vehicle = p(vehicles)
    bank = [
        f"{v('chala')} thanks {v('bro')}, {v('nuvvu')} help chesav — problem {v('chala')} worse {v('avunu')} now {laugh(0.4)}",
        f"government 'smart city' {v('ante')} {place} lo {vehicle} ki roads {v('ledu')} — very smart {laugh()}",
        f"naa wifi {v('chala')} fast {v('undi')} — speed test lo matrame, actual lo {v('ledu')} {v('bro')} {laugh()}",
        f"online class lo professor 'unmute avvandi' {v('ante')} — 50 fans, 10 dogs, 5 {v('amma')} voices {laugh(0.8)}",
        f"work from home easy {v('ante')} — {p(names_male)} {v('amma')} background lo {p(foods)} chesthu meeting lo {laugh()}",
        f"naa phone battery {v('chala')} fast poothundi, relationships kanna faster {cry()}",
        f"{app} lo order chesanu '30 mins' {v('ante')} — 2 hours lo {p(foods)} {v('vasindi')}, cold ga {v('undi')} {laugh(0.6)}",
        f"traffic lo {place} lo {v('okka')} hour stuck, GPS '2 mins away' antu {v('undi')} — GPS lying {v('bro')} {laugh()}",
        f"'gym join chestanu' ani January 1 ki fee kattanu, January 5 ki forget {v('avunu')} — annual tradition {laugh()}",
        f"diet start chesanu — {p(foods)} chusaka cancel chesanu, health is wealth but food is life {laugh(0.7)}",
        f"alarm 5 AM ki pettanu 'productive avutanu' ani, snooze chesanu 6 times — productivity achieved {laugh()}",
        f"interview ki 'punctual ga veltanu' annanu, 10 mins late {v('avunu')} — traffic blame chesanu obviously {laugh(0.5)}",
    ]
    return p(bank)

def joke_tollywood():
    hero = p(tollywood); name = p(names_male); sub = p(subjects)
    bank = [
        f"{hero} movie lo villain {v('chala')} try chesadu, hero ki {v('okka')} scratch {v('ledu')} — plot armour max level {laugh()}",
        f"naa life {hero} movie la {v('undi')} — interval ki twist, climax ki logic {v('ledu')} {v('bro')} {cry()}",
        f"{hero} dialogue {name} {p(colleges)} lo use chesadu, professor appreciate {v('chesadu')} — cinema education {laugh(0.7)}",
        f"hero bike stunt chesadu, {name} try chesadu — bike {v('undi')}, {name} hospital lo {v('undi')} {laugh()}",
        f"{hero} {v('okka')} punch lo 10 mandi ni {v('ledu')} chesadu, nenu {v('okka')} {sub} paper clear cheyyalekapoyanu {laugh(0.8)}",
        f"movie lo hero {v('okka')} song lo 5 countries lo dance chesadu, nenu {v('okka')} {p(places)} bus stop daateri {v('ledu')} {cry()}",
        f"{hero} movie review: 'logic {v('ledu')}' — fans: 'logic ante em {v('bro')}, emotion chuso' {laugh()}",
        f"villain 1000 cr spend chesadu plan ki, hero {v('okka')} punch lo finish — ROI zero {laugh(0.6)}",
        f"mass movie {v('ante')} {hero} dialogue ni {name} WhatsApp status lo pettadu — feels {v('undi')} {v('bro')} {laugh(0.4)}",
        f"movie ticket 500 rs, popcorn 300 rs, hero shirtless scene — priceless, worth it {laugh()}",
    ]
    return p(bank)

def joke_relationship():
    name = p(names_male); fname = p(names_female); sub = p(subjects)
    bank = [
        f"{name} {fname} ki 'hi' text chesadu, 3 days tarvata reply vasindi — {v('chala')} busy schedule {v('undi')} {laugh(0.5)}",
        f"crush cheppindi 'we are just friends' ani — {sub} fail kanna painful {v('avunu')} {v('bro')} {cry()}",
        f"valentine's day ki {name} alone {v('undi')}, {p(foods)} order chesadu — self love era {laugh()}",
        f"{fname} '{v('nuvvu')} {v('chala')} funny' annadi — comedy {v('avunu')} {v('ante')} {v('undi')} {v('bro')}, naaku telidhu still {laugh(0.6)}",
        f"propose chesanu, 'I think of you as a brother' annadi — {sub} result kanna worse shock {cry()}",
        f"{name} {fname} ki good morning text chesadu daily, adi read {v('avunu')} reply {v('ledu')} — read receipts cruelty {v('bro')} {cry()}",
        f"relationship status: {p(subjects)} tho {v('bro')} — at least it needs me {laugh(0.7)}",
        f"{fname} 'nuvvu change avvali' annadi, {name} hairstyle change chesadu — nenu try chesanu {v('bro')} {laugh()}",
        f"ex vasindi message 'how are you' ani, nenu {p(subjects)} fail avutunna — great timing {v('bro')} {laugh(0.5)}",
        f"{name} {fname} tho first date ki {p(places)} lo {p(foods)} tinnaru, bill split chesadu — modern love {laugh(0.6)}",
    ]
    return p(bank)

def joke_daily_life():
    name = p(names_male); food = p(foods); app = p(apps); place = p(places)
    bank = [
        f"morning 6 ki alarm, snooze, 7 ki alarm, snooze, 9 ki {v('amma')} voice — most effective alarm {laugh()}",
        f"{place} lo {v('okka')} seat dorikithe lucky day ani {v('anukunta')}, destination vastundi {v('ledu')} {laugh(0.7)}",
        f"diet start chesanu — {food} chusaka cancel {v('avunu')}, health is wealth food is life {laugh()}",
        f"barber ki 'thoda trim' annanu — half head gone {v('bro')}, lost in translation {laugh(0.8)}",
        f"phone lo 1% battery, charger room lo {v('undi')}, nenu hall lo {v('undi')} — impossible distance {cry()}",
        f"{app} lo {food} order chesanu, wrong item {v('vasindi')}, hungry {v('avunu')} tinna — hunger > ego {laugh(0.6)}",
        f"meeting lo mute {v('avunu')} matladanu, 5 mins tarvata telusindi — everyone saw {v('bro')} {laugh()}",
        f"ATM ki poina, cash {v('ledu')}, UPI try chesanu, network {v('ledu')} — broke in every way {cry()}",
        f"auto wala 'meter {v('ledu')}' {v('ante')} 3x rate adugadu — Hyderabad experience {laugh(0.5)}",
        f"Sunday night 11 PM ki Monday ki prepare avvadam start chesanu — classic {v('bro')} {laugh()}",
        f"naaku {food} {v('chala')} ishtam, {v('amma')} chesindi, vere {food} chesindi — betrayal {laugh(0.7)}",
        f"supermarket ki {v('okka')} item ki poina, 10 items tho vasina — market psychology wins {laugh()}",
    ]
    return p(bank)

humorous_gens = [
    joke_college, joke_family, joke_sarcasm,
    joke_tollywood, joke_relationship, joke_daily_life,
]

# ─────────────────────────────────────────────────────────────────
# NON-HUMOROUS GENERATORS  (4 distinct categories — plain, neutral)
# ─────────────────────────────────────────────────────────────────

def plain_daily():
    name = p(names_male); food = p(foods); place = p(places); vehicle = p(vehicles)
    bank = [
        f"nenu today {place} ki {vehicle} lo vellanu {neut()}",
        f"{name} {p(colleges)} lo {p(subjects)} class attend {v('chesadu')} {neut()}",
        f"weather today {v('chala')} hot ga {v('undi')} {place} lo",
        f"nenu {food} tinnanu, {v('chala')} {v('undi')} {neut(0.3)}",
        f"{name} library lo {p(subjects)} chadduvutunnadu",
        f"morning {food} breakfast ki chesamu {neut()}",
        f"naa {p(colleges)} ki walking distance lo {v('undi')}",
        f"nenu online class attend chesanu today, notes rasanu {neut(0.4)}",
        f"{name} {p(subjects)} assignment complete {v('chesadu')} yesterday",
        f"naa phone new update vasindi, install chesanu {neut()}",
        f"{name} new {vehicle} kinukkunnadu last month {neut(0.2)}",
        f"nenu {place} lo {p(apps)} use chesthu {v('undi')}",
        f"today {p(subjects)} lab session {v('undi')}, prepare avutunna {neut()}",
        f"{name} {p(places)} lo relatives ni chusaadaniki {v('chesadu')}",
        f"nenu {food} try chesanu first time, okay ga {v('undi')} {neut()}",
    ]
    return p(bank)

def plain_opinion():
    sub = p(subjects); place = p(places); job = p(jobs); food = p(foods)
    bank = [
        f"{sub} nerchukovadam important {v('undi')} career ki {neut(0.3)}",
        f"{place} {v('chala')} develop avutundi last few years lo",
        f"online learning convenient ga {v('undi')} {v('anukunta')} {neut()}",
        f"regular exercise {v('chala')} important {v('undi')} health ki {neut()}",
        f"nenu {p(tollywood)} movies chustanu, {v('chala')} {v('undi')} {v('ante')}",
        f"{food} {v('chala')} healthy ga {v('undi')} daily tinte {neut(0.6)}",
        f"time management important {v('undi')} students ki",
        f"technology {v('chala')} fast ga change avutundi {neut()}",
        f"nenu {sub} interesting {v('undi')} {v('ante')} {v('anukunta')}",
        f"{job} avvadam {v('chala')} kaashtam {v('undi')} kani worth it {neut()}",
        f"{place} lo traffic problem address cheyyaali {v('ante')}",
        f"reading habit {v('chala')} useful {v('undi')} long term lo {neut(0.4)}",
        f"savings cheyyadam early age lo start cheyyatam better",
        f"group study sometimes helpful {v('avunu')} {v('anukunta')} {neut()}",
        f"internships {v('chala')} important {v('undi')} final year ki {neut()}",
    ]
    return p(bank)

def plain_news():
    place = p(places)
    bank = [
        f"{place} lo new metro line start avutundi next year",
        f"government new scholarship scheme announce chesindi students ki",
        f"{place} lo new IT park build avutundi",
        f"college lo new courses start avutunnai this semester",
        f"state lo rainfall {v('chala')} {v('undi')} this monsoon",
        f"new hospital {place} lo open avutundi next month",
        f"electricity rates change avutunnai {place} lo",
        f"bus timings change chesaru {place} lo recently",
        f"new traffic rules implement avutunnai state wide",
        f"{place} lo water supply schedule change {v('avunu')}",
        f"university exams postpone chesaru this semester",
        f"state budget lo education ki more funds allocate chesaru",
        f"new flyover {place} lo ready {v('avunu')} next month",
        f"internet speed improve {v('avunu')} rural areas lo",
        f"petrol prices change {v('avunu')} this week",
    ]
    return p(bank)

def plain_instruction():
    sub = p(subjects); food = p(foods)
    bank = [
        f"{sub} prepare avvadam ki daily 2 hours chadduvukovadam {v('avunu')}",
        f"healthy ga undadam ki {food} tinate {v('chala')} {v('undi')}",
        f"exam ki notes miss avvadam {v('kaadu')}, important {v('undi')}",
        f"online form fill cheyyadaniki documents ready ga pettukovalani",
        f"bike maintain cheyyadaniki regular service important {v('undi')}",
        f"phone battery life increase ki screen brightness taginchu",
        f"resume lo {sub} skills mention cheyyadam important",
        f"bank account open ki adhar card, photos teesukuravelanu",
        f"interview ki formal dress wear cheyyadam better {v('undi')}",
        f"password strong ga pettadam security ki important",
        f"backup cheyyadam important files ki regular ga",
        f"water {v('chala')} taagadam health ki {v('chala')} {v('avunu')}",
        f"sleep 8 hours complete cheyyadam brain ki important",
        f"vegetables daily tinte immunity improve {v('avunu')}",
        f"savings account lo auto debit set cheyyadam better",
    ]
    return p(bank)

nonjoke_gens = [plain_daily, plain_opinion, plain_news, plain_instruction]

# ─────────────────────────────────────────────────────────────────
# GENERATE + SAVE
# ─────────────────────────────────────────────────────────────────

def generate(total=5000):
    samples = []
    half = total // 2

    seen = set()

    def add(text, label):
        key = text.strip().lower()
        if key not in seen:
            seen.add(key)
            samples.append({"text": text.strip(), "label": label})

    # Humorous
    attempts = 0
    while sum(1 for s in samples if s["label"]==1) < half and attempts < half*10:
        gen = humorous_gens[attempts % len(humorous_gens)]
        add(gen(), 1)
        attempts += 1

    # Non-humorous
    attempts = 0
    while sum(1 for s in samples if s["label"]==0) < half and attempts < half*10:
        gen = nonjoke_gens[attempts % len(nonjoke_gens)]
        add(gen(), 0)
        attempts += 1

    random.shuffle(samples)
    return samples

def save(samples, filename="humor_dataset_v2.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text","label"])
        w.writeheader()
        w.writerows(samples)
    print(f"✅ Saved: {filename}  ({len(samples)} samples)")

if __name__ == "__main__":
    random.seed(99)
    data = generate(5000)
    save(data)

    h = [s for s in data if s["label"]==1]
    n = [s for s in data if s["label"]==0]
    print(f"   Humorous:     {len(h)}")
    print(f"   Non-humorous: {len(n)}")
    avg_h = sum(len(s["text"].split()) for s in h) / len(h)
    avg_n = sum(len(s["text"].split()) for s in n) / len(n)
    print(f"   Avg words (humor):     {avg_h:.1f}")
    print(f"   Avg words (non-humor): {avg_n:.1f}")
    print(f"\n── Sample HUMOROUS ──")
    for s in random.sample(h, 5):
        print(f"  {s['text']}")
    print(f"\n── Sample NON-HUMOROUS ──")
    for s in random.sample(n, 5):
        print(f"  {s['text']}")