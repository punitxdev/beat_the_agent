import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import keras
import json

print("Loading Keras model...")
try:
    model = keras.models.load_model('agent_rlm_model.keras')
    print("--- Model Summary ---")
    model.summary()
    print("--- Inputs ---")
    for inp in model.inputs:
        print(inp)
    print("--- Outputs ---")
    for out in model.outputs:
        print(out)
except Exception as e:
    print(f"Error loading model: {e}")

print("Checking JSON file...")
try:
    with open('agent_rlm', 'r') as f:
        data = json.load(f)
        print("JSON keys:", data.keys() if isinstance(data, dict) else "Not a dict")
        if isinstance(data, dict):
            for k in list(data.keys())[:5]:
                val = data[k]
                val_type = type(val)
                val_len = len(val) if isinstance(val, (list, dict, str)) else 'N/A'
                print(f"Key: {k}, Type: {val_type}, Len: {val_len}")
except Exception as e:
    print(f"Error loading JSON: {e}")
