from cg_manage_rds.cmds import cf_cmds

def test_validate_cf_cli_version():
  # CF version 8 is supported
  [version, is_valid] = cf_cmds.validate_cf_cli_version("cf version 8.5.0+73aa161.2022-09-12")
  assert version == "8"
  assert(is_valid) is True
  # CF version 7 is supported
  [version, is_valid] = cf_cmds.validate_cf_cli_version("cf version 7.6.0+d1110f2.2023-02-27")
  assert version == "7"
  assert(is_valid) is True
