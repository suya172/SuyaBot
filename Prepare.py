import pickle
a = []
with open('history.pkl', 'wb') as f:
    pickle.dump(a, f)
b = []
with open('channels.pkl', 'wb') as f:
    pickle.dump(b, f)
