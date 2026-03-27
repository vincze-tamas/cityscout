# Hogyan lett egy ötletből 1 nap alatt működő AI decision tool

---

## A probléma

Nomád életmód. Rengeteg város, rengeteg "top 10" lista, nulla döntés.

Minden cikk ugyanaz: Barcelona, Bali, Chiang Mai. De egyik sem mondja meg, hogy neked, most, a te feltételeid alapján melyiket válaszd. Olcsó legyen? Legyen tenger? Jó wifi? Csendes környék?

A probléma nem az információhiány. Az a baj, hogy nincs döntési réteg.

---

## A felismerés

Nem lista kell. Decision engine kell.

Valami, ami nem opciókat ad vissza, hanem értékel, rangsorol, és megmondja a következő konkrét lépést.

---

## Mit építettem

Egy nap, egy Python fájl, 487 sor.

- 30 nomád város előre definiált attribútumokkal: cost, wifi, beach, vibe, safety, visa
- A user beírja amit keres szabadszöveggel ("olcsó, tenger, jó wifi, nyugodt")
- Claude LLM pontozza mind a 30 várost a feltételek alapján
- Visszaad top 3-at: score, confidence (0–100), és egy konkrét következő lépést

Nincs adatbázis. Nincs külső API. Nincs frontend. Csak reasoning.

---

## Miért más ez

A legtöbb AI projekt a "tartalomgyártás" kategóriában ragad. Ez nem az.

Ez az operációs réteg: az AI nem segít gondolkodni, hanem átveszi a döntés terhét.

| Kereső | Decision engine |
|--------|-----------------|
| visszaad opciókat | értékel és rangsorol |
| te döntesz | megmondja a következő lépést |
| content | action |

---

## Miért nem Google vagy ChatGPT?

Google és az AI chatbotok is adnak választ. De a válaszuk: lista.
Információt kapsz. A döntést rád hagyják.

**CityScout más:**

| | Google / ChatGPT | CityScout |
|---|---|---|
| Output | lista | 1 konkrét döntés |
| Bizonyosság | nincs | confidence score (0–100) |
| Következő lépés | nincs | next step, most, konkrétan |

Nem az a cél, hogy többet tudj.
Hanem hogy gyorsabban dönts.

Ez a különbség a keresés és a decision engine között.

---

## Az eredmény

Input: `"olcsó, tenger, jó wifi, nyugodt"`

Output:
```
#1  Da Nang, Vietnam  [9.2/10 | confidence: 87%]
    Next step: Foglalj 1 hónapot My Khe beach közelében,
    coworking pass az AN Coworking Space-ben (~$80/hó).
```

1 nap build. Azonnal használható. Skálázható tudás nélkül is.

---

## A tanulság

Az AI nem tool. Operációs réteg.

Nem arra való, hogy gyorsabban írj emailt. Arra való, hogy a döntési folyamataidat automatizáld.

A CityScout egy prototípus, de a minta skálázható bármilyen döntési problémára: melyik piacra lépj be, melyik szolgáltatót válaszd, melyik ügyféltípusra fókuszálj.

Ha az AI-t csak tartalomra használod, a versenyelőnyöd minimális. Ha döntési rendszert építesz belőle, más kategória vagy.
