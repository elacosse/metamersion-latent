def test_google_sheet_to_dataframe():
    from metamersion_latent.utils.oh_sheet import google_sheet_to_dataframe

    df = google_sheet_to_dataframe(
        "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms", "A1:D"
    )
    assert len(df) > 0


def test_master_prompter():
    from metamersion_latent.llm.config import Config
    from metamersion_latent.utils.master_prompter import (
        beautify_concepts_to_stable_diffusion_prompts,
        extract_concepts_from_analysis,
    )

    config_path = "metamersion_latent/configs/chat/example.py"
    test_string = """1. Client is having vivid dreams. 
2. Client dreamt of a woman who was crying.
3. Client and woman had a relationship in the past."""
    # load config
    config = Config.fromfile(config_path)
    concepts = extract_concepts_from_analysis(test_string, config)
    assert len(concepts) > 0
    prompts = beautify_concepts_to_stable_diffusion_prompts(concepts)
    assert len(prompts) > 0
    print(prompts)
