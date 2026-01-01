import pickle
# 事前設定資料（人格の前提）
with open('preamble2.txt', 'r', encoding='utf-8') as f:
    preamble = f.read()

# 会話履歴（System から開始）
a = [
    {"role": "system", "content": preamble}
]
with open('history.pkl', 'wb') as f:
    pickle.dump(a, f)
b = []
with open('channels.pkl', 'wb') as f:
    pickle.dump(b, f)
