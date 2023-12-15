import torch
import torchaudio
from cnn import CNNNetwork
from urbansounddataset import UrbanSoundSataset
from train import AUDIO_DIR, ANNOTATIONS_FILE, SAMPLE_RATE, NUM_SAMPLES

class_mapping = [
    "air_conditioner",
    "car_horn",
    "children_playing",
    "dog_bark",
    "drilling",
    "engine_idling",
    "gun_shot",
    "jackhammer",
    "siren",
    "street_music"
]

def predict(model, input, target, class_mapping):
    model.eval()
    with torch.no_grad():
        predictions = model(input)
        # Tensor (1, 10) -> [ [0.1, 0.01, ..., 0.8] ]
        predicted_index = predictions[0].argmax(0)
        predicted = class_mapping[predicted_index]
        expected = class_mapping[target]
    return predicted, expected

if __name__ == "__main__":
    # load back the model
    cnn = CNNNetwork()
    # state_dict = torch.load("cnnnet.pth", torch.device('cpu'))
    state_dict = torch.load("feedforwardnet.pth")
    cnn.load_state_dict(state_dict)

    # load urban sound dataset
    mel_spectrogram = torchaudio.transforms.MelSpectrogram(
        sample_rate=SAMPLE_RATE, n_fft=1024, hop_length=512, n_mels=64
    )

    usd = UrbanSoundSataset(ANNOTATIONS_FILE, AUDIO_DIR, mel_spectrogram, SAMPLE_RATE, NUM_SAMPLES, "cpu")
    # get a sample from the urban sound dataset for inference
    input, target = usd[666][0], usd[666][1] # [batch size, num_channels, fr, time]
    input.unsqueeze_(0)
    # make an inference
    predicted, expected = predict(cnn, input, target, class_mapping)
    print(f"Predicted: '{predicted}', expected: '{expected}'")