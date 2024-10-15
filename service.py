from __future__ import annotations

import os
import pathlib
import typing as t
from pathlib import Path

import bentoml
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from streaming_utils import StreamingInputs, predict_streaming_generator


BENTO_MODEL_TAG = "coqui--xtts-v2"

app = FastAPI()

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
class XTTSStreaming:

    bento_model_ref = bentoml.models.BentoModel(BENTO_MODEL_TAG)

    def __init__(self) -> None:
        import torch

        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import Xtts

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        config = XttsConfig()
        config.load_json(self.bento_model_ref.path_of("config.json"))
        self.model = Xtts.init_from_config(config)
        self.model.load_checkpoint(
            config,
            checkpoint_dir=self.bento_model_ref.path,
            eval=True,
            use_deepspeed=True if self.device == "cuda" else False
        )
        self.model.to(self.device)
        print("XTTS Loaded.", flush=True)

        cdir = pathlib.Path(__file__).parent.resolve()
        voice_path = cdir / "female.wav"
        _t = self.model.get_conditioning_latents(voice_path)
        self.gpt_cond_latent = _t[0]
        self.speaker_embedding = _t[1]

        
    @app.post("/stream")
    def tts_stream(self, inp: StreamingInputs):
        gen = predict_streaming_generator(
            model=self.model,
            text=inp.text,
            language=inp.language,
            speaker_embedding=self.speaker_embedding,
            gpt_cond_latent=self.gpt_cond_latent,
            stream_chunk_size=inp.stream_chunk_size,
            add_wav_header=inp.add_wav_header,
        )
        return StreamingResponse(gen, media_type="audio/wav")
