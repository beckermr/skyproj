import os
import pytest

import matplotlib
matplotlib.use("Agg")

from matplotlib.testing.compare import compare_images, ImageComparisonFailure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

import skyproj  # noqa: E402


ROOT = os.path.abspath(os.path.dirname(__file__))


@pytest.mark.parametrize("survey_tuple", [(skyproj.DESSkyproj, "DES"),
                                          (skyproj.BlissSkyproj, "BLISS"),
                                          (skyproj.MaglitesSkyproj, "MagLiTeS"),
                                          (skyproj.DecalsSkyproj, "DECaLS")])
def test_survey_outlines(tmp_path, survey_tuple):
    """Test drawing survey outlines."""
    survey = survey_tuple[0]
    name = survey_tuple[1]

    fig = plt.figure(1, figsize=(8, 5))
    fig.clf()
    ax = fig.add_subplot(111)
    m = survey(ax=ax)
    if name == 'DES':
        m.draw_des(label=name)
    elif name == 'BLISS':
        m.draw_bliss(label=name)
    elif name == 'MagLiTeS':
        m.draw_maglites(label=name)
    elif name == 'DECaLS':
        m.draw_decals(label=name)
    m.legend()
    fname = f'{name}_survey.png'
    fig.savefig(tmp_path / fname)
    err = compare_images(os.path.join(ROOT, 'data', fname), tmp_path / fname, 10.0)
    if err:
        raise ImageComparisonFailure(err)