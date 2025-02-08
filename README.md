<div align="center">
    <h1 align="center">Building an XTTS Streaming API with BentoML</h1>
</div>

This is a BentoML example project, demonstrating how to build a text-to-speech inference API with streaming capability using the XTTS model.

See [here](https://docs.bentoml.com/en/latest/examples/overview.html) for a full list of BentoML example projects.

## Install dependencies

```bash
git clone https://github.com/bentoml/BentoXTTSStreaming
cd BentoXTTSSTreaming

# Recommend Python 3.11 in a virtual environment
pip install -r requirements.txt
```

## Import XTTS Model

We need to import xtts model to local BentoML model store first. You may also set the environment variable `COQUI_TTS_AGREED=1` to agree to the terms of Coqui TTS.

```bash
$ 
=1 python import_model.py
```

We can list imported model by running:

```bash
$ bentoml models list
```

## Run the BentoML Service

We have defined a BentoML Service in `service.py`. Run `bentoml serve` in your project directory to start the Service.

The server is now active at [http://localhost:3000](http://localhost:3000/). You can interact with it using the Swagger UI or in other different ways.

CURL

```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "text":"It took me quite a long time to develop a voice and now that I have it I am not going to be silent.",
  "language":"en",
  "stream_chunk_size": 20,
  "add_wav_header": true}' \
  http://localhost:3000/tts/stream -o output.wav

curl -X 'POST' \
  'http://localhost:3000/synthesize' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "It took me quite a long time to develop a voice and now that I have it I am not going to be silent.",
  "lang": "en"
}' -o output.wav
```

## Deploy to BentoCloud

After the Service is ready, you can deploy the application to BentoCloud for better management and scalability. [Sign up](https://www.bentoml.com/) if you haven't got a BentoCloud account.

Make sure you have [logged in to BentoCloud](https://docs.bentoml.com/en/latest/bentocloud/how-tos/manage-access-token.html), then run the following command to deploy it.

```bash
bentoml deploy .
```

Once the application is up and running on BentoCloud, you can access it via the exposed URL.

**Note**: For custom deployment in your own infrastructure, use [BentoML to generate an OCI-compliant image](https://docs.bentoml.com/en/latest/guides/containerization.html).
