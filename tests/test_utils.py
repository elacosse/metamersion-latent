def test_google_sheet_to_dataframe():
    from metamersion_latent.utils.oh_sheet import google_sheet_to_dataframe

    df = google_sheet_to_dataframe(
        "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms", "A1:D"
    )
    assert len(df) > 0
