# cg-manage-rds

[![Build and Release](https://github.com/rbogle/cg-manage-rds/actions/workflows/build-release.yml/badge.svg)](https://github.com/rbogle/cg-manage-rds/actions/workflows/build-release.yml)

cg-manage-rds is a command line utility for managing rds instances created by the aws-broker in cloud.gov
This utility simplifies export, import and migrations of those instances.

## Prerequisites

You will need to have the cloudfoundry cli `cf`, `ssh` and the standard database engine utilities installed for cg-manage to work.

Currently this utility supports linux and mac os installation. It has not been tested on windows but should work in the windows subsystem for linux.

## Installation

There are three options for installation:

1. Use the [homebrew](https://brew.sh/) package manager for latest release, this can be used on mac, linux, and possibly windows (not tested)

```bash
brew install cloud-gov/cloudgov/cg-manage-rds
```

1. Extract the bundled executable from the appropriate zipfile in the latest release:
  
    <https://github.com/cloud-gov/cg-manage-rds/releases/latest>

1. Use the python package manager [pip](https://pip.pypa.io/en/stable/) to install the latest directly from source in a local python environment.

```bash
pip install git+https://github.com/cloud-gov/cg-manage-rds.git
```

## Developing

See [DEVELOPING.md](./DEVELOPING.md).

## Usage

The cg-manage-rds utility has multiple subcommands to provide specific functionality. Each of these will attempt to determine the type of database automatically from your service, but can be forced to use a specific type if needed. Under the hood the utility uses the `cf` , `ssh`, and the specific db engine utilities e.g. `psql` or `mysql` to do its work, so you must have those installed for your database. The commands:

- import
- export
- clone

all attempt to install an application in your current space, create a ssh tunnel to the database(s) through that application, execute the appropriate database commands, and finally will cleanup the app, keys and ssh tunnel when finished. You can re-use a setup or prevent a cleanup by using the appropriate options for the command. Alternatively, you can choose to run `cg-manage-rds setup` or `cg-manage-rds cleanup` to only setup or teardown the database connection and tunnel if other database work is required.

```bash
cg-manage-rds --help
Usage: cg-manage-rds [OPTIONS] COMMAND [ARGS]...

  Application to export, import, or clone a rds service instance from the
  aws-broker

Options:
  -?, -h, --help  Show this message and exit.

Commands:
  check    Check local system for required utilities for a DB engine.
  cleanup  Cleanup key, app, and tunnel to a aws-rds service instance
  clone    Migrate data from one rds service to another rds service...
  export   Export data and/or schema from SOURCE aws-rds service instance
  import   Import data and/or schema to DESTINATION rds service instance
  setup    Setup app, key, and tunnel to a aws-rds service instance
```

### Exporting a database

Basic exporting will attempt to identify the engine type and export the db as a sql file `./db_backup.sql`

```bash
$ cf serivces
Getting services in org sandbox-org / space foo.bar as foo.bar@example.gov...

name                    service   plan           bound apps   last operation     broker       upgrade available
test-micro-psql-src     aws-rds   micro-psql                  create succeeded   aws-broker
test-micro-psql-dest    aws-rds   micro-psql                  create succeeded   aws-broker

$ cg-manage-rds export test-micro-psql-src

```

The export subcommand has multiple options available. For example, the file name and location can be specified with `-f` and a string of options and flags can be passed to the engine client with `-o`:

```bash
cg-manage-rds export -f ~/Backups/$(date +%m-%d-%Y)_test_backup.tar -o "-F t" test-micro-psql-src
```

export does attempt to insert a few default options to make the database backup portable; those can be removed or overwritten with the `--force-options` flag.

```shell
Usage: cg-manage-rds export [OPTIONS] SOURCE

  Export data and/or schema from SOURCE aws-rds service instance

  By default export will not preserve ownership, and will attempt to create
  objects if they do not exist.

  These defaults can be overridden with the --force-options flag.

  You can insert additional options and flags to the clients using -o
  --options.

Options:
  -e, --engine [pgsql|mysql]  Database engine type
  -f, --output-file TEXT      Output file name  [default: db_backup.sql]
  -o, --options TEXT          cli options for the backup client
  -s, --setup BOOLEAN         peform app/tunnel setup  [default: True]
  -c, --cleanup BOOLEAN       peform app/tunnel cleanup  [default: True]
  -k, --key-name TEXT         use this service key name  [default: key]
  -a, --app-name TEXT         use this app name  [default: ssh-app]
  --force-options BOOLEAN     override engine default options with yours
                              [default: False]
  -h, -?, --help              Show this message and exit.

```

### Importing a database

Basic importing will attempt to identify the engine type and import the db from a sql file `./db_backup.sql`

```bash
$ cf serivces
Getting services in org sandbox-org / space foo.bar as foo.bar@example.gov...

name                    service   plan           bound apps   last operation     broker       upgrade available
test-micro-psql-src     aws-rds   micro-psql                  create succeeded   aws-broker
test-micro-psql-dest    aws-rds   micro-psql                  create succeeded   aws-broker

$ cg-manage-rds import test-micro-psql-dest

```

The import subcommand has multiple options available. For example, the file name and location can be specified with `-f` and a string of options and flags can be passed to the engine client with `-o`:

```bash
cg-manage-rds import -f ~/Backups/$(date +%m-%d-%Y)_test_backup.tar -o "-F t" test-micro-psql-dest
```

export does attempt to insert a few default options to make the database backup portable; those can be removed or overwritten with the `--force-options` flag.

```bash
Usage: cg-manage-rds import [OPTIONS] DESTINATION

  Import data and/or schema to DESTINATION rds service instance

  By default import will not preserve ownership, and will attempt to create
  objects if they do not exist.

  These defaults can be overridden with the --force-options flag.

  You can insert additional options and flags to the clients using -o
  --options.

Options:
  -e, --engine [pgsql|mysql]  Database engine type
  -f, --input-file TEXT       Input file name  [default: db_backup.sql]
  -o, --options TEXT          cli options for the backup client
  -s, --setup BOOLEAN         peform app/tunnel setup  [default: True]
  -c, --cleanup BOOLEAN       peform app/tunnel teardown  [default: True]
  -k, --key-name TEXT         use this service key name  [default: key]
  -a, --app-name TEXT         use this app name  [default: ssh-app]
  --force-options BOOLEAN     override engine default options with yours
                              [default: False]
  -h, -?, --help              Show this message and exit.
```

### Cloning a database

The clone subcommand first performs an export from a source database and then imports to a destination database. The export is saved locally in `output-file`. You must have the destination database already created and ready before cloning. By default the database name and ownership  is not included in the export in order to enable easy import to another database created by the aws-rds broker.

```bash
Usage: cg-manage-rds clone [OPTIONS] SOURCE DESTINATION

  Migrate data from one rds service to another rds service instance.

  By default export and import will not preserve ownership, and will attempt
  to create objects if they do not exist.

  These defaults can be overridden with the --force-options flag.

  You can insert additional options and flags to the clients with either -b
  --boptions or -r --roptions.

Options:
  -e, --engine [pgsql|mysql]  Database engine type
  -f, --output-file TEXT      Output file name  [default: db_backup.sql]
  -b, --boptions TEXT         cli options for the backup client
  -r, --roptions TEXT         cli options for the restore client
  -k, --key-name TEXT         use this service key name  [default: key]
  -a, --app-name TEXT         use this app name  [default: ssh-app]
  --force-options BOOLEAN     override engine default options with yours
                              [default: False]
  -?, -h, --help              Show this message and exit.
```

### Check, Setup and Cleanup

There are several utility commands to assist working with services:

- check
- setup
- cleanup

`Check` takes a service name, attempts to determine the service's database engine type, and then looks for locallaly installed required client programs.

`Setup` pushes an application into the current space, creates a service key to the provided service and then creates a ssh tunnel to the service via the installed app. Setup will output a connection string that can be used to connect to the service using a local client e.g. `psql` or `mysql`. Using setup alone allows you to perform other manual actions on services beyond export and import.

`Cleanup` will teardown the setup for a service.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[Public Domain](LICENSE.md)
