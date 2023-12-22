import os
import sys
import boto3
import datetime
import time
import click
import json
from sm_version_editor.util import *
from tabulate import tabulate
from botocore.exceptions import ClientError


def common_options(function):
    function = click.option(
        "-p",
        "--profile",
        help="AWS Profile to use",
        default="default",
        type=str,
        show_default=True,
    )(function)
    function = click.option(
        "-r",
        "--region",
        help="AWS Region to use",
        default="us-gov-west-1",
        type=str,
        show_default=True,
    )(function)
    return function


def secret_id_common(function):
    function = click.option(
        "--sid",
        help="Secret ID to use",
        required=True,
        type=str,
    )(function)
    return function


secret_string = click.option(
    "--secret-string",
    help="Secret String to use",
    type=str,
)

secret_file = click.option(
    "--secret-file",
    help="Secret File to use",
    type=str,
)


@click.command("list-secrets", short_help="List Secrets Ids from Secrets Manager")
@common_options
def list_secrets(profile, region):
    """
    List Secrets Ids from Secrets Manager
    """
    if os.getenv("AWS_PROFILE") is not None:
        profile = os.getenv("AWS_PROFILE")
    if os.getenv("AWS_REGION") is not None:
        region = os.getenv("AWS_REGION")
    sm = boto3.Session(profile_name=profile, region_name=region).client(
        "secretsmanager"
    )
    secrets = []
    try:
        secrets_list = sm.list_secrets()
        for secret in secrets_list["SecretList"]:
            secrets.append(
                [
                    secret["Name"],
                    secret["LastChangedDate"].strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )
        if "NextToken" in secrets_list:
            while "NextToken" in secrets_list:
                secrets_list = sm.list_secrets(NextToken=secrets_list["NextToken"])
                for secret in secrets_list["SecretList"]:
                    secrets.append(
                        [
                            secret["Name"],
                            secret["LastChangedDate"].strftime("%Y-%m-%d %H:%M:%S"),
                        ]
                    )
        click.echo(
            tabulate(
                secrets,
                headers=["Name", "Last Changed Date"],
                tablefmt="grid",
                colalign=("center", "center"),
            )
        )
    except ClientError as e:
        click.echo(e)
        sys.exit(1)


@click.command(
    "list-secret-versions",
    short_help="List Secret Version IDs for a Secret and get their Stage Labels",
)
@common_options
@click.option(
    "--sid",
    help="Secret ID to use",
    required=True,
    type=str,
)
def list_secret_versions(profile, region, sid):
    """
    List Secret Version IDs for a Secret and get their Stage Labels
    """
    if os.getenv("AWS_PROFILE") is not None:
        profile = os.getenv("AWS_PROFILE")
    if os.getenv("AWS_REGION") is not None:
        region = os.getenv("AWS_REGION")
    sm = boto3.Session(profile_name=profile, region_name=region).client(
        "secretsmanager"
    )
    secret_versions = []
    try:
        secret_versions_list = sm.list_secret_version_ids(SecretId=sid)
        for secret_version in secret_versions_list["Versions"]:
            secret_versions.append(
                [
                    secret_version["VersionId"],
                    secret_version["VersionStages"],
                    secret_version["CreatedDate"].strftime("%Y-%m-%d %H:%M:%S"),
                    secret_version["LastAccessedDate"].strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )
        if "NextToken" in secret_versions_list:
            while "NextToken" in secret_versions_list:
                secret_versions_list = sm.list_secret_version_ids(
                    SecretId=sid, NextToken=secret_versions_list["NextToken"]
                )
                for secret_version in secret_versions_list["Versions"]:
                    secret_versions.append(
                        [
                            secret_version["VersionId"],
                            secret_version["VersionStages"],
                            secret_version["CreatedDate"].strftime("%Y-%m-%d %H:%M:%S"),
                            secret_version["LastAccessedDate"].strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        ]
                    )
        secret_versions.sort(
            key=lambda x: time.mktime(time.strptime(x[2], "%Y-%m-%d %H:%M:%S")),
        )
        click.echo(
            tabulate(
                secret_versions,
                headers=[
                    "VersionId",
                    "Version Stage Labels",
                    "Created Date",
                    "Last Accessed Date",
                ],
                tablefmt="grid",
                colalign=("center", "center", "center", "center"),
            )
        )
    except ClientError as e:
        click.echo(e)
        sys.exit(1)


@click.command(
    "update-secret-version-stage", short_help="Update Secret Version Stage Labels"
)
@click.option(
    "-f",
    "--from-vid",
    help="Label will be removed from this Secret Version ID",
    type=str,
)
@click.option(
    "-t",
    "--to-vid",
    help="Label will be added to this Secret Version ID, label must not exist on another id",
    type=str,
)
@click.option(
    "-sl",
    "--stage-label",
    help="Secret Version Stage to use",
    required=True,
    type=str,
)
@common_options
@secret_id_common
def update_secret_version_stage(
    profile,
    region,
    sid,
    stage_label,
    from_vid=None,
    to_vid=None,
):
    """
    \b
    Use Cases:
    1. Remove label from a secret version id
    2. Add label to a secret version id
    3. Remove label from one secret version id and add to another secret version id

    \b
    How to use:
    Use Case 1:
    smts-secrets update-secret-version-stage --sid <secret-id> --stage-label <stage-label> --from-vid <version-id>
    Use Case 2:
    smts-secrets update-secret-version-stage --sid <secret-id> --stage-label <stage-label> --to-vid <version-id>
    Use Case 3:
    smts-secrets update-secret-version-stage --sid <secret-id> --stage-label <stage-label> --from-vid <version-id> --to-vid <version-id>
    """
    if os.getenv("AWS_PROFILE") is not None:
        profile = os.getenv("AWS_PROFILE")
    if os.getenv("AWS_REGION") is not None:
        region = os.getenv("AWS_REGION")
    sm = boto3.Session(profile_name=profile, region_name=region).client(
        "secretsmanager"
    )
    try:
        if from_vid is not None and to_vid is not None:
            sm.update_secret_version_stage(
                SecretId=sid,
                VersionStage=stage_label,
                RemoveFromVersionId=from_vid,
                MoveToVersionId=to_vid,
            )
        elif from_vid is None and to_vid is not None:
            sm.update_secret_version_stage(
                SecretId=sid, VersionStage=stage_label, MoveToVersionId=to_vid
            )
        elif from_vid is not None and to_vid is None:
            sm.update_secret_version_stage(
                SecretId=sid, VersionStage=stage_label, RemoveFromVersionId=from_vid
            )
        else:
            click.echo("You must specify a from or to version id")
            sys.exit(1)
    except ClientError as e:
        click.echo(e)
        sys.exit(1)


@click.command("get-secret-value", short_help="Get Value of a Secret")
@click.option(
    "--vid", help="Secret Version ID to use (required for old versions)", type=str
)
@click.option("--output", "-o", help="Output File", type=str, default="output.txt")
@common_options
@secret_id_common
def get_secret_value(profile, region, sid, vid=None, output=None):
    if os.getenv("AWS_PROFILE") is not None:
        profile = os.getenv("AWS_PROFILE")
    if os.getenv("AWS_REGION") is not None:
        region = os.getenv("AWS_REGION")
    sm = boto3.Session(profile_name=profile, region_name=region).client(
        "secretsmanager"
    )
    try:
        if vid is not None:
            secret_value = sm.get_secret_value(SecretId=sid, VersionId=vid)
        else:
            secret_value = sm.get_secret_value(SecretId=sid)
        try:
            if output is not None:
                with open(output, "w") as f:
                    f.write(json.dumps(json.loads(secret_value["SecretString"])) + "\n")
            else:
                click.echo(
                    json.dumps(json.loads(secret_value["SecretString"]), indent=2)
                )
        except:
            if output is not None:
                with open(output, "w") as f:
                    f.write(secret_value["SecretString"] + "\n")
            else:
                click.echo(secret_value["SecretString"])
    except ClientError as e:
        click.echo(e)
        sys.exit(1)


@click.command("update-secret-value", short_help="Update Value of a Secret")
@common_options
@secret_id_common
@secret_string
@secret_file
def update_secret_value(profile, region, sid, secret_string=None, secret_file=None):
    if os.getenv("AWS_PROFILE") is not None:
        profile = os.getenv("AWS_PROFILE")
    if os.getenv("AWS_REGION") is not None:
        region = os.getenv("AWS_REGION")
    sm = boto3.Session(profile_name=profile, region_name=region).client(
        "secretsmanager"
    )
    try:
        if secret_file is not None:
            secret_file_path = os.getcwd() + "/" + secret_file
            with open(secret_file_path, "r") as f:
                secret_string = f.read()
        try:
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sm.put_secret_value(
                SecretId=sid,
                SecretString=secret_string,
                VersionStages=[current_datetime, "AWSCURRENT"],
            )
        except:
            click.echo("Secret String could not be updated")
    except ClientError as e:
        click.echo(e)
        sys.exit(1)


@click.command("create-secret", short_help="Create a Secret")
@common_options
@secret_id_common
@secret_string
@secret_file
def create_secret(profile, region, sid, secret_string=None, secret_file=None):
    """
    Used to create a new secret in secrets manager
    and add a version stage label to the secret version id
    """
    if os.getenv("AWS_PROFILE") is not None:
        profile = os.getenv("AWS_PROFILE")
    if os.getenv("AWS_REGION") is not None:
        region = os.getenv("AWS_REGION")
    sm = boto3.Session(profile_name=profile, region_name=region).client(
        "secretsmanager"
    )
    try:
        if secret_file is not None:
            secret_file_path = os.getcwd() + "/" + secret_file
            with open(secret_file_path, "r") as f:
                secret_string = f.read()
        sm.create_secret(Name=sid, SecretString=secret_string)
        response = sm.list_secret_version_ids(SecretId=sid)
        version_id = response["Versions"][0]["VersionId"]
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_secret_version_stage(
            [
                "--profile",
                profile,
                "--region",
                region,
                "--sid",
                sid,
                "-sl",
                current_datetime,
                "--to-vid",
                version_id,
            ],
            standalone_mode=False,
        )
        click.echo(
            tabulate(
                [
                    [
                        sid,
                        version_id,
                        current_datetime,
                    ]
                ],
                headers=["Name", "VersionId", "Version Stage Label Added"],
                tablefmt="grid",
                colalign=("center", "center", "center"),
            )
        )
    except ClientError as e:
        click.echo(e)
        sys.exit(1)


@click.command(
    "delete-secret",
    short_help="Delete a Secret, default recovery window is 7 days, use --force to delete immediately",
)
@click.option(
    "--force",
    help="Force Immediate Deletion of Secret",
    is_flag=True,
    type=bool,
    show_default=True,
)
@click.option(
    "--recv-window", "-rw", help="Recovery Window in Days", default=7, type=int
)
@common_options
@secret_id_common
def delete_secret(profile, region, sid, recv_window=7, force=False):
    """Delete a Secret, default recovery window is 7 days, use --force to delete immediately"""
    if recv_window < 7:
        click.echo("Recovery Window must be at least 7 days")
        sys.exit(1)
    if os.getenv("AWS_PROFILE") is not None:
        profile = os.getenv("AWS_PROFILE")
    if os.getenv("AWS_REGION") is not None:
        region = os.getenv("AWS_REGION")
    sm = boto3.Session(profile_name=profile, region_name=region).client(
        "secretsmanager"
    )
    try:
        if not force:
            sm.delete_secret(SecretId=sid, RecoveryWindowInDays=recv_window)
            click.echo(
                "Secret Scheduled for Deletion: Recovery Window is %s days"
                % recv_window
            )
        else:
            sm.delete_secret(SecretId=sid, ForceDeleteWithoutRecovery=True)
            click.echo("Secret Deleted")
    except ClientError as e:
        click.echo(e)
        sys.exit(1)


@click.command(
    "restore-secret", short_help="Restore a Secret within the recovery window"
)
@common_options
@secret_id_common
def restore_secret(profile, region, sid):
    """Restore a Secret within the recovery window"""
    if os.getenv("AWS_PROFILE") is not None:
        profile = os.getenv("AWS_PROFILE")
    if os.getenv("AWS_REGION") is not None:
        region = os.getenv("AWS_REGION")
    sm = boto3.Session(profile_name=profile, region_name=region).client(
        "secretsmanager"
    )
    try:
        sm.restore_secret(SecretId=sid)
        click.echo("Secret Restored")
    except ClientError as e:
        click.echo(e)
        sys.exit(1)


if __name__ == "__main__":
    list_secret_versions("gdit-test", "us-gov-west-1", "gc-fcs-test-secrets-10-30-23")
