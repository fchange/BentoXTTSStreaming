import io
import wave
import numpy as np
import typing as t

from pydantic import BaseModel


if t.TYPE_CHECKING:
    import torch


class StreamingInputs(BaseModel):
    text: str
    add_wav_header: bool = True
    stream_chunk_size: int = 20


def postprocess(wav):
    """Post process the output waveform"""

    import torch

    if isinstance(wav, list):
        wav = torch.cat(wav, dim=0)
    wav = wav.clone().detach().cpu().numpy()
    wav = wav[None, : int(wav.shape[0])]
    wav = np.clip(wav, -1, 1)
    wav = (wav * 32767).astype(np.int16)
    return wav


def encode_audio_common(
    frame_input, sample_rate=24000, sample_width=2, channels=1
):
    wav_buf = io.BytesIO()
    with wave.open(wav_buf, "wb") as vfout:
        vfout.setnchannels(channels)
        vfout.setsampwidth(sample_width)
        vfout.setframerate(sample_rate)
        vfout.writeframes(frame_input)

    wav_buf.seek(0)
    return wav_buf.read()


def predict_streaming_generator(
        model,
        text: str,
        stream_chunk_size: int,
        add_wav_header: bool,
):
    prompt_speech_16k = load_wav('./asset/zero_shot_prompt.wav', 16000)
    # for i, j in enumerate(self.model.inference_zero_shot(
    #         '收到好友从远方寄来的生日礼物，那份意外的惊喜与深深的祝福让我心中充满了甜蜜的快乐，笑容如花儿般绽放。',
    #         '希望你以后能够做的比我还好呦。', prompt_speech_16k, stream=False)):
    for i, j in enumerate(self.model.inference_zero_shot(text, prompt_speech_16k, stream=False)):
        yield j['tts_speech'].tobytes()
