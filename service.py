from __future__ import annotations

import os
import pathlib
import typing as t
from pathlib import Path

import bentoml
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from streaming_utils import StreamingInputs, predict_streaming_generator

app = FastAPI()


def load_model():
    # SDK模型下载
    from modelscope import snapshot_download
    snapshot_download('iic/CosyVoice2-0.5B', local_dir='pretrained_models/CosyVoice2-0.5B')


@bentoml.service(
    traffic={
        "timeout": 300,
        "concurrency": 3,
    },
    resources={
        "gpu": 1,
        "gpu_type": "nvidia-l4",
    },
    workers=3,
)
@bentoml.mount_asgi_app(app, path="/tts")
class TTSStreaming:

    def __init__(self) -> None:
        from self.model.cli.cosyvoice import CosyVoice, CosyVoice2
        from self.model.utils.file_utils import load_wav
        import torchaudio


        try:
            self.model = CosyVoice2('pretrained_models/CosyVoice2-0.5B', load_jit=False, load_trt=False, fp16=False)
        except Exception as e:
            print(e)
            load_model()
            self.model = CosyVoice2('pretrained_models/CosyVoice2-0.5B', load_jit=False, load_trt=False, fp16=False)

        print("model Loaded.", flush=True)

    @app.post("/stream")
    def tts_stream(self, inp: StreamingInputs):
        gen = predict_streaming_generator(
            model=self.model,
            text=inp.text,
            stream_chunk_size=inp.stream_chunk_size,
            add_wav_header=inp.add_wav_header,
        )
        return StreamingResponse(gen, media_type="audio/wav")
