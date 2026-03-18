import pandas as pd
import requests
import argparse
import io
from scipy.stats import rankdata

def parse_coco_html_table(html_text):
    try:
        dfs = pd.read_html(io.StringIO(html_text))
        for df in dfs:
            if any('Delta' in str(c) for c in df.columns):
                return df
            for idx, row in df.head(3).iterrows():
                if any('Delta' in str(val) for val in row.values):
                    df.columns = row.values
                    df = df.iloc[idx + 1:].reset_index(drop=True)
                    return df
    except Exception as e:
        print(f"[-] Hiba a HTML dekódolásakor: {e}")
        return None
    return None

def send_to_coco(df_matrix, y0_value):
    matrix_str = ""
    for _, row in df_matrix.iterrows():
        row_vals = [str(int(float(x))) for x in row.values]
        matrix_str += "\t".join(row_vals) + f"\t{y0_value}\r\n"
        
    multipart_payload = {
        'matrix': (None, matrix_str),
        'job': (None, ''),
        'stair': (None, ''),
        'modell': (None, 'Y0'),
        'object': (None, ''),
        'attribute': (None, ''),
        'button2': (None, 'Futtatás') # enélkül elhal, és a STD-re fut. :(
    }
    
    url = "https://miau.my-x.hu/myx-free/coco/engine3.php"
    response = requests.post(url, files=multipart_payload)
    
    if response.status_code == 200:
        return parse_coco_html_table(response.text)
    return None

def process_raw_logs(raw_csv_path):
    print(f"1. Nyers log fájl beolvasása: {raw_csv_path}...")
    # Nyers logok beolvasása. Feltételezzük, hogy van 'Timestamp' oszlop.
    df = pd.read_csv(raw_csv_path, sep=None, engine='python')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)

    print("2. Aggregáció 10 perces időablakokká... ")
    # A Pandas resample megcsinálja a másodperces/perces adatok 10 perces blokkokba vonását
    agg_df = pd.DataFrame()
    
    # X1: RPS (Másodpercenkénti kérések = Kérések száma / 600 mp)
    agg_df['X1_RPS'] = df.resample('10min').size() / 600
    
    # X2: Kimenő adat (MB) = Bájtok szummája / (1024*1024)
    # (nyers logban a Bytes_Sent nevű oszlopban a bájtok)
    if 'Bytes_Sent' in df.columns:
        agg_df['X2_Data_MB'] = df['Bytes_Sent'].resample('10min').sum() / (1024 * 1024)
    else:
        agg_df['X2_Data_MB'] = 0

    # X5: Sikerességi ráta (%)
    if 'HTTP_Status' in df.columns:
        total_requests = df['HTTP_Status'].resample('10min').size()
        success_requests = df[df['HTTP_Status'] < 400].resample('10min').size()
        agg_df['X5_Success_Rate_%'] = (success_requests / total_requests * 100).fillna(100)
    else:
        agg_df['X5_Success_Rate_%'] = 100

    # Objektum ID-k generálása (O1, O2, O3...)
    agg_df.index = [f"O{i+1}" for i in range(len(agg_df))]
    print(f"Létrejött az Nyers OAM! Objektumok száma: {len(agg_df)}")
    return agg_df

def rank_oam(agg_df):
    """
    Rangsorolás az irány-preferenciák alapján
    X1, X2, X3, X4: Irány 0 (Minél nagyobb, annál gyanúsabb -> negatív előjel a rankdatában)
    X5: Irány 1 (Minél kisebb, annál gyanúsabb -> pozitív előjel a rankdatában)
    """
    print("[*] 3. OAM Rangsorolása az irány-preferenciák alapján (SORSZÁM logikával)...")
    ranked_orig = pd.DataFrame(index=agg_df.index)
    ranked_inv = pd.DataFrame(index=agg_df.index)
    
    for col in agg_df.columns:
        if 'X5' in col:
            # X5 - Irány: 1 (Minél kisebb, annál gyanúsabb)
            ranked_orig[col] = rankdata(agg_df[col], method='min')       # Legkisebb kapja az 1-est
            ranked_inv[col] = rankdata(-agg_df[col], method='min')       # Inverz: legnagyobb kapja az 1-est
        else:
            # X1, X2 - Irány: 0 (Minél nagyobb, annál gyanúsabb)
            ranked_orig[col] = rankdata(-agg_df[col], method='min')      # Legnagyobb kapja az 1-est
            ranked_inv[col] = rankdata(agg_df[col], method='min')        # Inverz: legkisebb kapja az 1-est

    return ranked_orig, ranked_inv

def main():
    parser = argparse.ArgumentParser(description="Log fájl COCO Y0 automatizált robot-auditor")
    parser.add_argument('--rawfile', type=str, required=True, help="A NYERS naplófájl (.csv)")
    parser.add_argument('--y0value', type=int, default=100000, help="Y0 fiktív célváltozó értéke")
    args = parser.parse_args()

    # 1-2. Nyers logok aggregálása időablakokká
    agg_df = process_raw_logs(args.rawfile)
    
    # 3. Irány-függő rangsorolás (Eredeti és Inverz OAM)
    ranked_orig, ranked_inv = rank_oam(agg_df)

    # 4. COCO API Kommunikáció (Eredeti)
    print(f"\n[*] 4. EREDETI mátrix küldése a COCO-nak (Y0 = {args.y0value})...")
    result_orig = send_to_coco(ranked_orig, args.y0value)
    if result_orig is None: return

    delta_cols_orig = [c for c in result_orig.columns if 'Delta' in str(c) and 'Tény' not in str(c)]
    delta_col_orig = delta_cols_orig.pop(0)
    deltas_orig = pd.Series(result_orig[delta_col_orig].astype(float).values, index=agg_df.index)

    # 5. COCO API Kommunikáció (Inverz)
    print("[*] 5. INVERZ mátrix küldése a COCO-nak (Szimmetria teszt)...")
    result_inv = send_to_coco(ranked_inv, args.y0value)
    if result_inv is None: return
    
    delta_cols_inv = [c for c in result_inv.columns if 'Delta' in str(c) and 'Tény' not in str(c)]
    delta_col_inv = delta_cols_inv.pop(0)
    deltas_inv = pd.Series(result_inv[delta_col_inv].astype(float).values, index=agg_df.index)

    # 6. Validálás (Középpontosított Mean-Centering)
    print("\n[*] 6. Validálás (Középpontosított Delta_eredeti * Delta_inverz <= 0)...")
    mean_orig = deltas_orig.mean()
    mean_inv = deltas_inv.mean()

    validation_results = []
    for obj_id in agg_df.index:
        d_orig = deltas_orig[obj_id]
        d_inv = deltas_inv[obj_id]
        valid = ((d_orig - mean_orig) * (d_inv - mean_inv)) <= 0
        
        validation_results.append({
            'Objektum_ID': obj_id,
            'Delta_Orig': d_orig,
            'Delta_Inv': d_inv,
            'Valid': valid
        })
        
    val_df = pd.DataFrame(validation_results).sort_values(by='Delta_Orig', ascending=False)

    print("\n[*] 7. VÉGEREDMÉNY (Döntéstámogató Robot-Auditor Rangsor):")
    print("-" * 65)
    print(f"{'Hely':<5} | {'Objektum (Időablak)':<20} | {'Delta':<10} | {'Inv. Delta':<10} | {'Valid?':<6}")
    print("-" * 65)
    for i, (index, row) in enumerate(val_df.iterrows()):
        valid_str = "IGEN" if row['Valid'] else "NEM"
        # Csak a TOP 3-at jelöljük meg gyanúsként a konzolon a könnyebb olvashatóságért
        alert = " <<< GYANÚS!" if i < 3 else ""
        print(f"{i+1:<5} | {row['Objektum_ID']:<20} | {row['Delta_Orig']:<10.2f} | {row['Delta_Inv']:<10.2f} | {valid_str:<6}{alert}")
    print("-" * 65)

if __name__ == "__main__":
    main()