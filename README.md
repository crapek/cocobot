Íme egy professzionálisan összeállított, a szakdolgozatod mérnöki munkájára (COCO Y0 motor, 10 perces aggregáció, inverz validáció) épülő GitHub README.md fájl angol és magyar nyelven.

Ezt a szöveget egy az egyben bemásolhatod a GitHub tárolód `README.md` fájljába.

***

# 🇬🇧 English Version

## Cocobot - Automated Log Analysis & Suspicion Generation (Robot-Auditor)

This repository contains **Cocobot**, an automated, objective decision-support prototype (robot-auditor) designed for enterprise IT security. It identifies and prioritizes hidden cyber threats (e.g., slow data leaks, DDoS attacks) without human subjective bias by acting as a bridge between local log analysis and the COCO Y0 online expert engine.

### 📂 Repository Contents
*   `Cocobot.py`: The core Python script that automates the data preparation, Machine-to-Machine (M2M) HTTP POST communication, and final ranking generation.
*   `nyers_log_nagy.csv`: A sample raw network log file containing 27,982 lines, used to simulate a realistic, large-scale data source for testing purposes.

### ⚙️ How it Works
1.  **Data Aggregation:** The script uses the `pandas` library to transform raw, per-second log data into 10-minute sliding window aggregations, significantly reducing computational load while avoiding information loss.
2.  **OAM Generation:** It converts the aggregated metrics into an Object-Attribute Matrix (OAM) and ranks the attributes based on specific direction preferences (e.g., higher requests per second = more suspicious).
3.  **COCO Y0 Execution:** Emulating a multipart/form-data payload, the script submits the OAM to the COCO Y0 online expert engine via an automated HTTP POST request, utilizing a fictitious target variable (`Y0 = 100000`).
4.  **Inverse OAM Validation:** To ensure mathematical consistency and eliminate random biases, the script automatically runs a symmetrical Inverse OAM test and validates the results using Mean-Centering (`(Delta_Orig - Mean_Orig) * (Delta_Inv - Mean_Inv) <= 0`).
5.  **Terminal Output:** Outputs an instantly interpretable priority list, flagging the Top 3 most suspicious time windows.

### 🚀 Usage
**Requirements:**
```bash
pip install pandas requests scipy
```

**Running the script:**
You can run the script using the provided sample log file.
```bash
python Cocobot.py --rawfile nyers_log_nagy.csv --y0value 100000
```


---


# 🇭🇺 Magyar Verzió

## Cocobot - Automatizált Naplóelemzés és Gyanúgenerálás (Robot-Auditor)

Ez a tároló tartalmazza a **Cocobot** nevű automatizált, objektív döntéstámogató prototípust (robot-auditort), amelyet nagyvállalati IT-biztonsági környezetekhez fejlesztettünk. A rendszer emberi szubjektivitás és belemagyarázás nélkül azonosítja a rejtett kiberfenyegetéseket (pl. lassú adatszivárgás, DDoS), M2M (gép-gép) hidat képezve a lokális logelemzés és a COCO Y0 online szakértői motor között.

### 📂 A tároló tartalma
*   `Cocobot.py`: A fő Python szkript, amely teljeskörűen automatizálja az adat-előkészítést, az emulált HTTP POST kommunikációt és a végső prioritási lista generálását.
*   `nyers_log_nagy.csv`: Egy 27 982 sort tartalmazó minta nyers hálózati naplófájl, amellyel a "robot-auditor" működése valós, nagy adatvagyonon szimulálható és tesztelhető.

### ⚙️ Működési elv
1.  **Adat-aggregáció:** A szkript a `pandas` könyvtár segítségével a másodperces, nyers naplófájlokat 10 perces csúszóablakos aggregációval vonja össze, drasztikusan optimalizálva a számítási terhet információvesztés nélkül.
2.  **OAM Képzés:** Az aggregált metrikákból egy Objektum-Attribútum Mátrixot (OAM) képez, majd az attribútumokat a meghatározott irány-preferenciák alapján rangsorolja (pl. magasabb hibaarány = gyanúsabb).
3.  **COCO Y0 Futtatás:** Egy multipart/form-data űrlapküldést emulálva, a szkript HTTP POST kérés formájában beküldi a rangsorolt OAM-ot a COCO Y0 motornak egy fiktív célváltozó (`Y0 = 100000`) kíséretében.
4.  **Inverz OAM Validáció:** A matematikai torzítások kizárása érdekében a szoftver elvégzi a szimmetrikus hatások elemzését (Inverz OAM teszt), a végeredményt pedig középpontosított (Mean-Centering) validációval igazolja (`(Delta_eredeti - Átlag_eredeti) * (Delta_inverz - Átlag_inverz) <= 0`).
5.  **Terminál Kimenet:** A rendszer a terminálban azonnal értelmezhető prioritási listát generál, amely a legkritikusabb (Top 3) gyanús időablakra irányítja a figyelmet.

### 🚀 Használat
**Követelmények telepítése:**
```bash
pip install pandas requests scipy
```

**A szkript futtatása:**
A mellékelt minta naplófájl segítségével azonnal tesztelhető a rendszer működése.
```bash
python Cocobot.py --rawfile nyers_log_nagy.csv --y0value 100000
```
