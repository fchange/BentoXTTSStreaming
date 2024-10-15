import io
import wave
import numpy as np
import typing as t

from pydantic import BaseModel


if t.TYPE_CHECKING:
    import torch


class StreamingInputs(BaseModel):
    text: str
    language: str
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
        language: str,
        speaker_embedding: "torch.Tensor",
        gpt_cond_latent: "torch.Tensor",
        stream_chunk_size: int,
        add_wav_header: bool,
):

    chunks = model.inference_stream(
        text,
        language,
        gpt_cond_latent,
        speaker_embedding,
        stream_chunk_size=stream_chunk_size,
        enable_text_splitting=True
    )

    for i, chunk in enumerate(chunks):
        chunk = postprocess(chunk)
        if i == 0 and add_wav_header:
            yield encode_audio_common(b"")
            yield chunk.tobytes()
        else:
            yield chunk.tobytes()
