import os

import click

# TODO refactor this code, maybe with an oop approach


def run_commands(command, appname, env_dict):
    #  app_name=app_name, env_name=env_name, env_value=env_value
    for env_name, env_value in env_dict.items():
        os.system(
            command.format(app_name=appname, env_name=env_name, env_value=env_value)
        )


def read_env_file(file_path):
    try:
        open(file_path, "r")
    except FileNotFoundError:
        return {}
    else:
        with open(file_path, "r") as f:
            env_dict = {
                line.strip().split("=")[0]: line.strip().split("=")[1] for line in f
            }
        return env_dict


@click.command()
@click.option(
    "--env",
    default="prodconfig",
    help="The file where the env variables should be read from.",
)
@click.option(
    "--appname",
    default="",
    help="The name of your app, this is neccessary when your are\
     using the dokku cli directly instead of the dokku-toolbet wrapper",
)
def set_dokku_app_envs(env, appname):
    """Simple program that set environment variable for app deploy with dokku"""

    command = (
        "dokku config:set {app_name} {env_name}={env_value}"
        if appname
        else "dt config:set {env_name}={env_value}"
    )

    env_dict = read_env_file(file_path=env)

    if not env_dict:
        return

    run_commands(command, appname, env_dict)

    # set random secret key and admin url, comment if not needed
    defaults = {
        "DJANGO_SECRET_KEY": '"$(openssl rand -base64 64)"',
        "DJANGO_ADMIN_URL": "$(openssl rand -base64 4096 | tr -dc 'A-HJ-NP-Za-km-z2-9' | head -c 32)/",
        "WEB_CONCURRENCY": "4",
        "PYTHONHASHSEED": "random",
    }

    run_commands(command, appname, defaults)


if __name__ == "__main__":
    set_dokku_app_envs()
