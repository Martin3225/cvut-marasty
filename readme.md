# ČVUT Marasty

Toto repo shromažďuje otázky pro přípravu na rozstřely na FIT ČVUT.

## Jak přidat otázky?
1. Vytvořte **fork** tohoto repozitáře.
2. Přidejte své otázky dle struktury popsané níže.
3. Po dokončení změn vytvořte **pull request**.
4. V CI proběhnou automatické kontroly správnosti JSON souborů a jejich umístění.
5. Otázky (resp. jejich složky) pojmenovávejte náhodným **8místným číslem** (je to limitace, ale asi nejelegantnější řešení, který mě napadlo).

## Struktura repozitáře

Data jsou uložena v adresáři `questions/` v následující hierarchii:

```text
questions/
├── [kód_předmětu]/          # Např. 'aag', 'dml', 'ma2'
│   ├── subject.json         # Definice předmětu a témat
│   └── questions/
│       └── [8místné_id]/    # Unikátní složka pro každou otázku
│           ├── question.json # Data otázky
│           ├── image.png    # (Volitelné) obrázek k zadání
│           └── quiz.png     # (Volitelné) obrázek k odpovědím
```

---

## Formát dat

### 1. Definice předmětu (`subject.json`)

Tento soubor definuje základní metadata předmětu a jeho tématické okruhy.

```json
{
    "name": "Celý název předmětu",
    "code": "zkratka",
    "description": "Stručný popis předmětu",
    "primaryColor": "#HEX_KOD",
    "secondaryColor": "#HEX_KOD",
    "topics": [
        {
            "id": "identifikator-okruhu",
            "name": "Lidsky čitelný název okruhu"
        }
    ]
}
```

**Popis polí:**
- `name`: Plný název předmětu (např. "Automaty a Gramatiky").
- `code`: Unikátní identifikátor předmětu, který odpovídá názvu jeho složky.
- `description`: Krátký text popisující předmět.
- `primaryColor` / `secondaryColor`: Barvy použité pro branding předmětu ve webové aplikaci.
- `topics`: Seznam objektů definujících okruhy otázek.
  - `id`: URL-safe identifikátor tématu.
  - `name`: Název tématu zobrazený uživateli.

---

### 2. Definice otázky (`question.json`)

Každá složka s otázkou obsahuje soubor `question.json` se samotným zadáním.

```json
{
    "question": "Zadání otázky (podporuje LaTeX)",
    "questionType": "multichoice",
    "answers": [
        {
            "text": "Text odpovědi",
            "isCorrect": false
        },
        {
            "text": "Text správné odpovědi",
            "isCorrect": true
        }
    ],
    "topics": [
        "ID okruhu"
    ],
    "originalText": "Původní text otázky pro referenci"
}
```

**Popis polí:**
- `question`: Text zadání. Pro matematiku lze použít LaTeX obalený dolary: `$a^n$`.
- `questionType`: Typ otázky, nejčastěji `multichoice`.
- `answers`: Pole objektů s odpověďmi.
  - `text`: Text odpovědi (rovněž podporuje LaTeX).
  - `isCorrect`: `true` pokud je odpověď správná, jinak `false`.
- `topics`: Seznam ID témat z `subject.json`, ke kterým se otázka vztahuje.
- `originalText`: Uchovává původní surový text (např. z Wordu/PDF) pro snadnější opravy a ladění.

---

## Média

Složka s otázkou může obsahovat volitelné soubory:
- `image.png`: Obrázek, který se zobrazí přímo pod textem zadání (může se využít např. pro zadání, které obsahuje obrázek grafu).
- `quiz.png`: Obrázek, který obsahuje screenshot z marastu / zadání. (Při mass scrapování otázek, využíváno pro lehčí kontrolu)

