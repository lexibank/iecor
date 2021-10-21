def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    assert len(list(cldf_dataset["FormTable"])) == 25918
    assert any(f["Form"] == "thatë" for f in cldf_dataset["FormTable"])


def test_parameters(cldf_dataset):
    assert len(list(cldf_dataset["ParameterTable"])) == 170


def test_clades(cldf_dataset):
    assert len(list(cldf_dataset["clades.csv"])) == 40


def test_loans(cldf_dataset):
    assert len(list(cldf_dataset["loans.csv"])) == 1039
    assert any(f["Source_languoid"] == "Romance" for f in cldf_dataset["loans.csv"])


def test_authors(cldf_dataset):
    assert any(f["Last_Name"] == "Dewey-Findell" for f in cldf_dataset["authors.csv"])


def test_languages(cldf_dataset):
    assert len(list(cldf_dataset["LanguageTable"])) == 161
