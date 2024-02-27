# Developing cg-manage-rds

## Setting up a local development environment

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Formatting project code using `black`

Make sure you have the virtual environment activated and then run:

```shell
black .
```

## Creating a new release

1. Create a new tag:

  ```shell
  git tag -a v0.x.x -m "Version 0.x.x"
  ```

1. Push the tag

  ```shell
  git push origin v0.x.x
  ```

1. Once a new tag is pushed, the [GitHub Actions workflow](./.github/workflows/build-release.yml) will run to:

    - Build an installable version of the package for:
      - Mac
      - Linux
      - Windows
    - Create a [GitHub release](https://github.com/cloud-gov/cg-manage-rds/releases) for the tag
    - Update the [Homebrew formula for `cg-manage-rds` in the `cloud-gov/cloudgov` tap](https://github.com/cloud-gov/homebrew-cloudgov)
