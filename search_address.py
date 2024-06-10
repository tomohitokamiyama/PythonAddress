import pandas as pd
import csv
import json
from collections import defaultdict

# 2-gramを生成する関数
def generate_ngrams(text, n=2):
    ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
    return ngrams

# 転置インデックスを構築する関数
def build_inverted_index(address_data):
    inverted_index = defaultdict(set)
    for idx, row in address_data.iterrows():
        searchable_text = (
            str(row['都道府県']) + 
            str(row['市区町村']) + 
            str(row['町域']) + 
            (str(row['京都通り名']) if pd.notna(row['京都通り名']) else '') + 
            (str(row['字丁目']) if pd.notna(row['字丁目']) else '') + 
            (str(row['事業所名']) if pd.notna(row['事業所名']) else '') + 
            (str(row['事業所住所']) if pd.notna(row['事業所住所']) else '')
        )
        ngrams = generate_ngrams(searchable_text)
        for ngram in ngrams:
            inverted_index[ngram].add(idx)
    return inverted_index

# 転置インデックスを使用して検索する関数
def search_inverted_index(keyword, inverted_index, address_data):
    ngrams = generate_ngrams(keyword)
    matched_indices = None
    for ngram in ngrams:
        if ngram in inverted_index:
            if matched_indices is None:
                matched_indices = inverted_index[ngram]
            else:
                matched_indices &= inverted_index[ngram]
        else:
            return pd.DataFrame()  # 1つでもngramが見つからない場合は一致する住所はない
    if matched_indices:
        return address_data.iloc[list(matched_indices)]
    else:
        return pd.DataFrame()  # 空の DataFrame を返す

# 転置インデックスをファイルに保存
def save_inverted_index(inverted_index, filename='inverted_index.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({k: list(v) for k, v in inverted_index.items()}, f, ensure_ascii=False, indent=2)

# 転置インデックスをファイルから読み込み
def load_inverted_index(filename='inverted_index.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    return {k: set(v) for k, v in inverted_index.items()}



# メイン関数
def main():
    
    # CSVファイルから住所データを読み込み
    address_data = pd.read_csv('zenkoku.csv', encoding='cp932', low_memory=False, dtype=str)
    

    # 欠損値を空の文字列に置き換える
    address_data.fillna('', inplace=True)

    # 列名の確認
    #print(address_data.columns)

    # 転置インデックスの構築
    inverted_index = build_inverted_index(address_data)
    
    # 転置インデックスをファイルに保存
    save_inverted_index(inverted_index)

    # 検索語を入力
    keyword = input("検索語を入力してください: ")

    # 転置インデックスを読み込み
    inverted_index = load_inverted_index()

    # 一致する住所の一覧を取得
    results = search_inverted_index(keyword, inverted_index, address_data)

    # 結果を表示
    if len(results) > 0:
        print("一致する住所の一覧:")
        print(results[['郵便番号', '都道府県', '市区町村', '町域', '京都通り名', '字丁目', '事業所名', '事業所住所']].to_string(index=False))
    else:
        print("一致する住所が見つかりませんでした。")




if __name__ == "__main__":
    main()
