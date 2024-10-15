import bentoml

MODEL_ID = "coqui/XTTS-v2"
BENTO_MODEL_TAG = MODEL_ID.lower().replace("/", "--")

def import_model(model_id, bento_model_tag):

    from huggingface_hub import snapshot_download
    with bentoml.models.create(bento_model_tag) as bento_model_ref:
        snapshot_download(MODEL_ID, local_dir=bento_model_ref.path)


if __name__ == "__main__":
    import_model(MODEL_ID, BENTO_MODEL_TAG)    
