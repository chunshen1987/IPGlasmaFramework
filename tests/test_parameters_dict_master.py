"""Tests of config/parameters_dict_master.py: the nucleon model is chosen by
the user dictionary (or the default) only, never by a parameter file."""

import copy
import itertools
import sys
from os import path

import pytest

sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), "..",
                             "config"))
import parameters_dict_master as master  # noqa: E402

_user_dict_count = itertools.count()


@pytest.fixture(autouse=True)
def restore_master_dicts():
    """Restores the module-level dictionaries after each test, in place,
    since Parameters_list refers to the same objects."""
    saved_ipglasma = copy.deepcopy(master.ipglasma_dict)
    saved_explicit = copy.deepcopy(master.explicit_parameters)
    yield
    master.ipglasma_dict.clear()
    master.ipglasma_dict.update(saved_ipglasma)
    master.explicit_parameters.clear()
    master.explicit_parameters.update(saved_explicit)


def load_user_dict(tmp_path, ipglasma_entries):
    """Writes a user dictionary with the given ipglasma_dict entries and
    applies it like generate_jobs.py does. Each file gets its own module
    name, since update_parameters_dict() imports it by name."""
    name = "user_dict_{}".format(next(_user_dict_count))
    user_file = tmp_path / "{}.py".format(name)
    user_file.write_text(
        "control_dict = {'initial_state_type': \"IPGlasma\"}\n"
        "ipglasma_dict = " + repr(ipglasma_entries) + "\n")
    master.update_parameters_dict(str(user_file), -1)


def write_parameter_file(tmp_path, lines):
    parameter_file = tmp_path / "parameters.dat"
    parameter_file.write_text("".join(line + "\n" for line in lines))
    return str(parameter_file)


def test_strings_keeps_its_model_with_nq_3(tmp_path):
    load_user_dict(tmp_path, {'nucleonModel': "strings", 'BG': 9.8})
    master.update_parameters_bayesian(
        write_parameter_file(tmp_path, ["BG  9.8", "Nq  3.0"]))
    assert master.ipglasma_dict['nucleonModel'] == "strings"
    assert master.ipglasma_dict['Nq'] == 3.0


def test_strings_keeps_its_model_with_old_name(tmp_path):
    load_user_dict(tmp_path, {'nucleonModel': "strings"})
    master.update_parameters_bayesian(
        write_parameter_file(tmp_path, ["useConstituentQuarkProton  3.0"]))
    assert master.ipglasma_dict['nucleonModel'] == "strings"
    assert master.ipglasma_dict['Nq'] == 3.0


def test_strings_with_other_nq_stops(tmp_path):
    load_user_dict(tmp_path, {'nucleonModel': "strings"})
    parameter_file = write_parameter_file(tmp_path, ["Nq  4.0"])
    with pytest.raises(SystemExit) as error:
        master.update_parameters_bayesian(parameter_file)
    message = str(error.value)
    assert parameter_file in message
    assert "Nq 4" in message
    assert "nucleonModel strings" in message
    assert "'nucleonModel'" in message


def test_hotspots_takes_nq(tmp_path):
    load_user_dict(tmp_path, {'nucleonModel': "hotspots", 'Nq': 2})
    master.update_parameters_bayesian(
        write_parameter_file(tmp_path, ["Nq  3.0"]))
    assert master.ipglasma_dict['nucleonModel'] == "hotspots"
    assert master.ipglasma_dict['Nq'] == 3.0


def test_hotspots_with_round_nucleons_stops(tmp_path):
    load_user_dict(tmp_path, {'nucleonModel': "hotspots"})
    parameter_file = write_parameter_file(tmp_path, ["Nq  0"])
    with pytest.raises(SystemExit) as error:
        master.update_parameters_bayesian(parameter_file)
    assert "nucleonModel hotspots" in str(error.value)


def test_default_gaussian_with_hot_spots_stops(tmp_path):
    # used to switch to hotspots silently
    load_user_dict(tmp_path, {'BG': 4.0})
    assert master.ipglasma_dict['nucleonModel'] == "gaussian"
    parameter_file = write_parameter_file(tmp_path, ["Nq  3.0"])
    with pytest.raises(SystemExit) as error:
        master.update_parameters_bayesian(parameter_file)
    message = str(error.value)
    assert parameter_file in message
    assert "nucleonModel gaussian" in message
    assert "user dictionary does not set it" in message
    assert "switched to hotspots" in message


def test_gaussian_with_round_nucleons(tmp_path):
    load_user_dict(tmp_path, {'nucleonModel': "gaussian"})
    nq_before = master.ipglasma_dict['Nq']
    master.update_parameters_bayesian(
        write_parameter_file(tmp_path, ["Nq  0"]))
    assert master.ipglasma_dict['nucleonModel'] == "gaussian"
    assert master.ipglasma_dict['Nq'] == nq_before
    assert 'Nq' not in master.explicit_parameters


@pytest.mark.parametrize("model", ["gaussian", "hotspots", "strings"])
def test_file_without_nq_keeps_the_model(tmp_path, model):
    load_user_dict(tmp_path, {'nucleonModel': model})
    master.update_parameters_bayesian(write_parameter_file(
        tmp_path, ["m  0.3", "BG  3.5", "smearingWidth  0.5",
                   "QsmuRatio  0.7", "Kfactor  1.1"]))
    assert master.ipglasma_dict['nucleonModel'] == model
    assert master.ipglasma_dict['BG'] == 3.5
    assert master.ipglasma_dict['QsMuRatio'] == 0.7


def test_parameter_file_cannot_set_the_model(tmp_path):
    load_user_dict(tmp_path, {'nucleonModel': "hotspots"})
    with pytest.raises(SystemExit):
        master.update_parameters_bayesian(
            write_parameter_file(tmp_path, ["nucleonModel  strings"]))


def test_warning_for_parameters_the_model_does_not_read(tmp_path, capsys):
    load_user_dict(tmp_path, {'nucleonModel': "gaussian"})
    master.update_parameters_bayesian(
        write_parameter_file(tmp_path, ["BGq  0.3"]))
    master.warn_about_subnucleon_parameters()
    output = capsys.readouterr().out
    assert "BGq 0.3 is set in the parameter file" in output
    assert "nucleonModel gaussian does not read it" in output


def test_no_warning_for_strings_with_nq_3(tmp_path, capsys):
    load_user_dict(tmp_path, {'nucleonModel': "strings", 'BGq': 0.33})
    master.update_parameters_bayesian(
        write_parameter_file(tmp_path, ["Nq  3.0"]))
    capsys.readouterr()
    master.warn_about_subnucleon_parameters()
    assert "does not read" not in capsys.readouterr().out


def test_master_defaults_give_no_warning(tmp_path, capsys):
    # the defaults contain every parameter; only explicit ones count
    load_user_dict(tmp_path, {'nucleonModel': "gaussian"})
    capsys.readouterr()
    master.warn_about_subnucleon_parameters()
    assert capsys.readouterr().out == ""


def test_warning_for_values_a_posterior_set_replaces(tmp_path, capsys):
    load_user_dict(tmp_path, {'nucleonModel': "hotspots",
                              'subNucleonParamType': 2, 'BGqVar': 0.1})
    master.update_parameters_bayesian(
        write_parameter_file(tmp_path, ["BG  3.5", "Nq  3.0"]))
    capsys.readouterr()
    master.warn_about_subnucleon_parameters()
    output = capsys.readouterr().out
    assert "subNucleonParamType 2" in output
    assert "replaces the values of BG, Nq" in output
    assert "sets BGqVar to 0" in output


def test_printed_model_line(tmp_path, capsys):
    load_user_dict(tmp_path, {'nucleonModel': "strings", 'BG': 9.8,
                              'BGq': 0.33})
    capsys.readouterr()
    master.print_nucleon_model()
    output = capsys.readouterr().out
    assert "nucleonModel strings: BG 9.8, BGq 0.33, BGqVar" in output
    assert "Nq" not in output


def test_unknown_model_stops(tmp_path):
    load_user_dict(tmp_path, {'nucleonModel': "spheres"})
    with pytest.raises(SystemExit):
        master.warn_about_subnucleon_parameters()
