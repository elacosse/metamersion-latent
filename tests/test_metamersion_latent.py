from metamersion_latent import __version__


def test_version():
    assert __version__ == '0.1.0'


def test_google_sheet_to_dataframe():
    from metamersion_latent.oh_sheet import google_sheet_to_dataframe
    df = google_sheet_to_dataframe('1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms', 'A1:D')
    assert len(df) > 0